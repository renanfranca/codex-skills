import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {pathToFileURL, fileURLToPath} from 'node:url';

export const ROLES = Object.freeze(['implementer','committer','validator','habit-curator','mutation-analyst','structural-reviewer']);
const HERE = path.dirname(fileURLToPath(import.meta.url));
const read = p => JSON.parse(fs.readFileSync(p,'utf8'));
const digest = s => crypto.createHash('sha256').update(s).digest('hex');
export function atomic(p,value) {
  fs.mkdirSync(path.dirname(p), {recursive:true,mode:0o700});
  const tmp=p+'.'+crypto.randomUUID()+'.tmp';
  fs.writeFileSync(tmp,JSON.stringify(value,null,2)+'\n',{mode:0o600});
  fs.renameSync(tmp,p);
}
function git(cwd,...args) { return execFileSync('git',args,{cwd,encoding:'utf8',maxBuffer:8*1024*1024}).trim(); }
function paths(cwd) {
  const names=execFileSync('git',['status','--porcelain=v1','-z','--untracked-files=all'],{cwd});
  const out=[]; const rows=names.toString().split('\0');
  for(let i=0;i<rows.length;i++) if(rows[i]) {
    out.push(rows[i].slice(3));
    if(/[RC]/.test(rows[i].slice(0,2))) out.push(rows[++i]);
  }
  return [...new Set(out)].sort();
}
function fileFingerprint(cwd,name) {
  const target=path.join(cwd,name);
  try {
    const stat=fs.lstatSync(target);
    return digest(String(stat.mode)+':'+(stat.isSymbolicLink()?fs.readlinkSync(target):fs.readFileSync(target)));
  } catch(error) { if(error.code==='ENOENT') return 'absent'; throw error; }
}
function response(events,requestId) {
  let admitted=false, texts=[],terminal;
  for(const e of events) {
    const d=e.data?.message ?? e.data;
    if(e.type==='user/message' && (d?.source?.rpcId===requestId || e.data?.source?.rpcId===requestId)) { admitted=true; texts=[]; }
    if(admitted && e.type==='user/message' && d?.source?.kind==='user' && d?.source?.rpcId!==requestId) break;
    if(admitted && e.type==='assistant/message') {
      for(const c of d?.content ?? []) if(c.type==='text') texts.push(c.text);
    }
    if(admitted && e.type==='turn/end') terminal=e.data.reason;
  }
  return {admitted,text:texts.join('\n'),terminal};
}

export class NativeWorkflow {
  constructor(ctx,config) {
    this.ctx=ctx; this.config=config; this.stopped=false;
    this.registryPath=path.join(config.home,'workflow-registry.json');
    this.registry=fs.existsSync(this.registryPath)?read(this.registryPath):{version:1,sessions:{},approvals:{}};
    this.busy=new Map(); this.watching=new Set();
    this.selectionQueue=Promise.resolve();
  }
  async exclusive(agent,operation) {
    const key=agent.session.id,previous=this.busy.get(key)??Promise.resolve();
    let done;const gate=new Promise(resolve=>{done=resolve;});this.busy.set(key,gate);
    await previous;
    try { return await operation(); }
    finally { done();if(this.busy.get(key)===gate)this.busy.delete(key); }
  }
  saveRegistry() { atomic(this.registryPath,this.registry); }
  info(agent) {
    const link=this.registry.sessions[agent.session.id];
    if(!link) return undefined;
    const t=read(link.transport);
    return {link,t,ledger:fs.existsSync(t.ledger)?read(t.ledger):{phase:'archived',checkout_lease:null}};
  }
  requireCoordinator(agent) {
    const i=this.info(agent);
    if(!i || i.link.role!=='coordinator' || i.t.coordinator!==agent.session.id) throw Error('Only the registered Coordinator may control this workflow');
    return i;
  }
  checkPermission(agent) {
    if(this.ctx.permissionPresets.current(agent.session)!=='danger-full-access') throw Error('Native danger-full-access / never is required');
    const knobs=this.ctx.permissionPresets.resolve('danger-full-access');
    if(knobs.sandbox!=='danger-full-access'||knobs.approval!=='never') throw Error('Permission preset does not grant the approved native knobs');
  }
  approve(agent,markdown) {
    this.registry.approvals[agent.session.id]={markdown,sha256:digest(markdown),at:new Date().toISOString()}; this.saveRegistry();
  }
  async finishApprovedPlan(agent) {
    await agent.whenIdle();
    if(this.stopped) return;
    const approved=this.registry.approvals[agent.session.id];
    if(!approved) return;
    const last=agent.session.snapshotEvents().filter(e=>e.type==='plan/mode').at(-1);
    if(last?.data.active!==true || last.time>Date.parse(approved.at)) return;
    const pm=this.ctx.agentPresets.serviceFor(agent,'planMode');
    if(pm?.get(agent).active) {
      // Public set() cancels an uncommitted selection before committing at idle.
      if(pm.get(agent).pending===false) pm.set(agent,true);
      pm.set(agent,false);
    }
  }
  ledger(t,argv) {
    const result=execFileSync('python3',[path.join(HERE,'workflow_state.py'),'--state',t.ledger,...argv],{encoding:'utf8',maxBuffer:8*1024*1024});
    return result.trim()?JSON.parse(result):read(t.ledger);
  }
  async agent(id) {
    const result=await this.ctx.sessionController.resolveAgent(id);
    if(result.error) throw Error(result.error.message ?? 'Unable to resume native session');
    return result.agent;
  }
  defaultSelection() {
    const selection=this.ctx.agentDefaultModel.currentSelection();
    if(!selection.provider || !selection.model) throw Error('Configure a default model in DSH before starting the workflow');
    return {...selection};
  }
  roleEffort(role) {
    const effort=this.config.roleReasoningEfforts?.[role];
    if(!['off','low','high','max'].includes(effort)) throw Error('Configure roleReasoningEfforts for '+role);
    return effort;
  }
  async withDefaultSelection(operation) {
    const previous=this.selectionQueue;
    let done;
    this.selectionQueue=new Promise(resolve=>{done=resolve;});
    await previous;
    let original,last;
    try {
      original=this.defaultSelection();
      return await operation(original,async(sessionId,selection)=>{
        last={...selection};
        const {selected}=await this.ctx.sessionController.selectModel({sessionId,...selection});
        last={...selected};
        return selected;
      });
    } finally {
      try {
        // Do not replace a distinct default the user selected during this operation.
        const current=this.ctx.agentDefaultModel.currentSelection();
        if(original && last && current.provider===last.provider && current.model===last.model && current.reasoningEffort===last.reasoningEffort) {
          await this.ctx.agentDefaultModel.saveSelection(original);
        }
      } finally { done(); }
    }
  }
  async configureModels(coordinator,t,{includeCoordinator=false,deferActive=false}={}) {
    return this.withDefaultSelection(async(original,select)=>{
      const targets=Object.entries(t.sessions).map(([role,id])=>({role,id,selection:{provider:original.provider,model:original.model,reasoningEffort:this.roleEffort(role)}}));
      if(includeCoordinator) targets.unshift({role:'coordinator',id:coordinator.session.id,selection:original});
      for(const target of targets) {
        const agent=target.role==='coordinator'?coordinator:await this.agent(target.id);
        if(deferActive && (agent.status!=='idle' || this.ctx.jobs?.list(agent).some(j=>['running','stopping'].includes(j.status)))) return;
        if(agent.status!=='idle') throw Error('Model configuration requires idle sessions: '+target.role);
        this.checkPermission(agent); this.checkJobs(agent);
      }
      const registrations={};
      for(const target of targets) {
        const selected=await select(target.id,target.selection);
        if(target.role!=='coordinator') registrations[target.role]={session_id:target.id,provider:selected.provider,model:selected.model,effort:selected.reasoningEffort??'off'};
      }
      const ledger=this.ledger(t,['show']);
      if(ledger.schema_version===3) this.ledger(t,['migrate-models','--selections',JSON.stringify(registrations),'--reason','Use the DSH default model and configured role reasoning efforts']);
      else for(const [role,selection] of Object.entries(registrations)) this.ledger(t,['register-session','--role',role,'--session-id',selection.session_id,'--provider',selection.provider,'--model',selection.model,'--effort',selection.effort]);
      return registrations;
    });
  }
  async start(agent,args) {
    this.checkPermission(agent);
    if(this.info(agent)) { const i=this.requireCoordinator(agent); if(i.t.slug!==args.slug) throw Error('Use a new Coordinator session for a different workflow'); return this.resume(agent); }
    const pm=agent.ctx.get('planMode') ?? this.ctx.agentPresets.serviceFor(agent,'planMode');
    const planState=pm?.get(agent);
    if(planState && (planState.pending??planState.active)) throw Error('Approve the plan and leave /plan before starting implementation');
    const human=agent.session.snapshotEvents().filter(e=>e.type==='user/message').map(e=>JSON.stringify(e.data));
    if(!human.some(s=>s.includes('/implement-approved-plan-deepseek'))) throw Error('An explicit human skill invocation is required');
    if(!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(args.slug)||!args.branch || args.branch.includes('/')) throw Error('Use a kebab-case slug and feature branch without slashes');
    const repo=fs.realpathSync(agent.session.header.cwd);
    git(repo,'check-ref-format','--branch',args.branch);
    if(git(repo,'status','--porcelain=v1','--untracked-files=all')) throw Error('Checkout must be clean; preserve unrelated changes');
    let approved=this.registry.approvals[agent.session.id];
    if(args.approvedPlanPath) {
      const markdown=fs.readFileSync(path.resolve(repo,args.approvedPlanPath),'utf8');
      if(!approved || approved.sha256!==digest(markdown)) {
        const answer=await this.ctx.userQuestions.ask({agent,signal:args.signal,questions:[{id:'workflow-plan',header:'Approved plan',question:'Approve this exact plan for implementation?',detail:markdown,options:[{label:'Approve'},{label:'Keep planning'}],intent:{kind:'plan-review',approve:'Approve'}}]});
        if(answer.answers?.[0]?.selected?.length!==1 || answer.answers[0].selected[0]!=='Approve' || answer.answers[0].custom!==undefined) throw Error('The plan was not approved');
        this.approve(agent,markdown); approved=this.registry.approvals[agent.session.id];
      }
    }
    if(!approved) throw Error('No captured approved plan; use /plan or provide approvedPlanPath');
    const base=args.base ?? 'main', baseSha=git(repo,'rev-parse','--verify',base+'^{commit}');
    const current=git(repo,'branch','--show-current');
    if(current!==args.branch) {
      let exists=false; try { git(repo,'rev-parse','--verify','refs/heads/'+args.branch); exists=true; } catch {}
      if(exists) throw Error('Feature branch already exists; reconcile it explicitly rather than reusing unrelated work');
      git(repo,'switch','-c',args.branch,baseSha);
    }
    const exclude=path.resolve(repo,git(repo,'rev-parse','--git-path','info/exclude'));
    const old=fs.existsSync(exclude)?fs.readFileSync(exclude,'utf8'):'';
    if(!old.split('\n').includes('/.agent/tmp/')) fs.appendFileSync(exclude,'\n/.agent/tmp/\n');
    const dir=path.join(repo,'.agent/tmp'); fs.mkdirSync(dir,{recursive:true,mode:0o700});
    const plan=path.join(dir,args.slug+'.md'), ledger=path.join(dir,args.slug+'.dsh-workflow.json'), transport=path.join(dir,args.slug+'.dsh-orchestration.json');
    if(fs.existsSync(transport)) throw Error('This slug already belongs to a saved workflow; open its original Coordinator');
    fs.writeFileSync(plan,approved.markdown,{mode:0o600,flag:'wx'});
    const t={version:1,slug:args.slug,repo,branch:args.branch,base,baseSha,plan,ledger,transport,coordinator:agent.session.id,
      sessions:Object.fromEntries(ROLES.map(role=>[role,"session-"+crypto.randomUUID()])),assignments:[],createdAt:new Date().toISOString()};
    atomic(transport,t);
    this.ledger(t,['init','--slug',args.slug,'--plan',plan,'--repo',repo,'--branch',args.branch,'--base',base,'--base-sha',baseSha,'--provider',this.defaultSelection().provider]);
    this.registry.sessions[agent.session.id]={role:'coordinator',transport};
    for(const [role,id] of Object.entries(t.sessions)) this.registry.sessions[id]={role,transport};
    this.saveRegistry();
    await this.ctx.sessionController.rename({sessionId:agent.session.id,title:args.slug+' · Coordinator'});
    return this.reconcile(agent,t);
  }
  async reconcile(coordinator,t,{deferActiveModels=false}={}) {
    const {workspace}=await this.ctx.workspaceController.create({path:t.repo});
    for(const role of ROLES) {
      const id=t.sessions[role];
      await this.ctx.sessionController.create({workspaceId:workspace.workspaceId,sessionId:id,agentPreset:'deepseek-standard'});
    }
    await this.configureModels(coordinator,t,{deferActive:deferActiveModels});
    for(const role of ROLES) {
      const id=t.sessions[role],worker=await this.agent(id);
      await this.ctx.sessionController.rename({sessionId:id,title:t.slug+' · '+role});
      const requestId='intro-'+id;
      if(!response(worker.session.snapshotEvents(),requestId).admitted) await this.ctx.sessionController.prompt({sessionId:id,requestId,mode:'queue',content:[{type:'text',text:`You are the persistent ${role} session for workflow ${t.slug}. Only Coordinator ${t.coordinator} grants checkout assignments. Do not read files, execute terminal commands, commit, contact peers or change workflow state now. Reply only ROLE_READY ${role}. Future assignments reuse this session.`}]},new AbortController().signal);
    }
    return this.status(coordinator);
  }
  status(agent) {
    const i=this.info(agent); if(!i) return {managed:false,defaultModel:this.defaultSelection()};
    return {managed:true,role:i.link.role,coordinator:i.t.coordinator,sessions:i.t.sessions,repo:i.t.repo,branch:i.t.branch,plan:i.t.plan,ledger:i.t.ledger,
      phase:i.ledger.phase,lease:i.ledger.checkout_lease,assignments:i.t.assignments,models:i.ledger.sessions,defaultModel:this.defaultSelection()};
  }
  async dispatch(agent,args,signal) {
    const {t,ledger}=this.requireCoordinator(agent); this.checkPermission(agent);
    if(!ROLES.includes(args.role)||!args.assignmentId||!Array.isArray(args.files)) throw Error('Specify role, assignmentId and explicit authorized file prefixes');
    if(args.files.some(p=>typeof p!=='string'||!p||path.isAbsolute(p)||p.split('/').includes('..'))) throw Error('Authorized paths must be relative and confined to this repository');
    if(ledger.checkout_lease?.owner!==args.role) throw Error('Acquire this specialist lease before dispatch');
    if(git(t.repo,'branch','--show-current')!==t.branch) throw Error('Checkout branch changed');
    if(t.assignments.some(a=>a.status!=='collected' && a.assignmentId!==args.assignmentId)) throw Error('Collect outstanding assignment before dispatching another');
    let a=t.assignments.find(a=>a.assignmentId===args.assignmentId);
    if(a && (a.role!==args.role || a.prompt!==args.prompt || JSON.stringify(a.files)!==JSON.stringify(args.files))) throw Error('Assignment identity conflicts');
    if(a?.status==='collected') return a;
    const worker=await this.agent(t.sessions[args.role]); this.checkPermission(worker);
    if(!a) {
      if(worker.status!=='idle') throw Error('Specialist must be idle before accepting a new checkout assignment');
      const startPaths=paths(t.repo);
      a={assignmentId:args.assignmentId,role:args.role,sessionId:worker.session.id,requestId:crypto.randomUUID(),prompt:args.prompt,files:args.files,
        phase:ledger.phase,status:'pending',startHead:git(t.repo,'rev-parse','HEAD'),startPaths,
        startFiles:Object.fromEntries(startPaths.map(p=>[p,fileFingerprint(t.repo,p)])),createdAt:new Date().toISOString()};
      t.assignments.push(a); atomic(t.transport,t);
    }
    if(!response(worker.session.snapshotEvents(),a.requestId).admitted) await this.ctx.sessionController.prompt({sessionId:a.sessionId,requestId:a.requestId,mode:'queue',content:[{type:'text',text:
      `COORDINATOR ASSIGNMENT ${a.assignmentId}\nRepository: ${t.repo}\nBranch: ${t.branch}\nApproved plan: ${t.plan}\nImmutable base_sha: ${t.baseSha}\nPhase: ${a.phase}\nLease owner: ${a.role}\nAuthorized file prefixes: ${JSON.stringify(a.files)}\n${a.role==='committer'?'Only commit the explicitly assigned delta.':'Do not commit.'}\nDo not dispatch work or contact other sessions. Read applicable assigned native skills and repository instructions. Report concrete commands, outcomes and artifact paths.\n\n${a.prompt}`} ]},signal);
    a.status='accepted'; atomic(t.transport,t); this.watch(t,a,worker);
    return {accepted:true,assignmentId:a.assignmentId,sessionId:a.sessionId,requestId:a.requestId};
  }
  watch(t,a,worker) {
    if(this.watching.has(a.requestId)) return;
    this.watching.add(a.requestId);
    worker.whenIdle().then(async()=>{
      if(this.stopped||!fs.existsSync(t.transport)) return;
      const coordinator=await this.agent(t.coordinator);
      await this.exclusive(coordinator,async()=>{
        const latest=read(t.transport), saved=latest.assignments.find(x=>x.requestId===a.requestId);
        if(!saved||saved.status==='collected') return;
        saved.status=response(worker.session.snapshotEvents(),a.requestId).terminal?'completed':'interrupted';
        atomic(t.transport,latest);
        if(latest.waiting) await this.notify(latest,saved);
      });
    }).catch(()=>{}).finally(()=>this.watching.delete(a.requestId));
  }
  async notify(t,a) {
    if(a.notified) return;
    await this.ctx.sessionController.prompt({sessionId:t.coordinator,requestId:'result-'+a.requestId,mode:'queue',content:[{type:'text',text:
      `DSH workflow ${a.status}: ${a.role}, assignment ${a.assignmentId}, session ${a.sessionId}. ${a.status==='interrupted'?'Call workflow_resume, inspect histories, checkout and processes, then workflow_recover with diagnostic evidence. Retain the lease; this is not a successful result.':'Call workflow_collect. Inspect terminal outcome, evidence and authorized scope, record the required ledger evidence under the worker lease, release only after collection, then continue the approved serialized workflow.'} No new approval is needed for already authorized work.`}]},new AbortController().signal);
    const latest=read(t.transport), saved=latest.assignments.find(x=>x.requestId===a.requestId); if(saved) saved.notified=true; latest.waiting=false; atomic(t.transport,latest);
  }
  async wait(agent) {
    const {t}=this.requireCoordinator(agent);
    const outstanding=t.assignments.filter(x=>x.status!=='collected');
    if(!outstanding.length) throw Error('No outstanding assignment; continue the workflow instead of waiting');
    if(outstanding.some(a=>a.status==='interrupted')) throw Error('An assignment is interrupted; resume and recover it while retaining its lease');
    if(outstanding.some(a=>a.status==='completed'&&a.notified)) throw Error('The result was already reported; collect and verify it instead of waiting again');
    t.waiting=true; atomic(t.transport,t);
    const a=t.assignments.find(x=>x.status==='completed'); if(a) await this.notify(t,a);
    return {waiting:true,coordinator:t.coordinator};
  }
  async collect(agent,args) {
    const {t,ledger}=this.requireCoordinator(agent);
    const a=t.assignments.find(x=>x.assignmentId===args.assignmentId); if(!a) throw Error('Unknown assignment');
    const worker=await this.agent(a.sessionId);
    if(worker.status!=='idle') throw Error('Worker remains active; wait before collecting');
    this.checkJobs(worker);
    const r=response(worker.session.snapshotEvents(),a.requestId);
    if(!r.admitted||!r.terminal) throw Error('No durable terminal assignment response; reconcile interruption instead of claiming success');
    if(!r.text.trim()&&r.terminal.kind!=='error') throw Error('No durable assignment text; reconcile interruption instead of claiming success');
    if(ledger.checkout_lease?.owner!==a.role && a.status!=='collected') throw Error('Assignment lease was lost');
    if(git(t.repo,'branch','--show-current')!==t.branch) throw Error('Branch differs from approved workflow');
    const head=git(t.repo,'rev-parse','HEAD');
    const committed=git(t.repo,'diff','--name-only',a.startHead,'HEAD').split('\n').filter(Boolean);
    const candidates=[...new Set([...paths(t.repo),...a.startPaths,...committed])];
    const changed=candidates.filter(p=>!a.startPaths.includes(p)||a.startFiles?.[p]!==fileFingerprint(t.repo,p)||committed.includes(p));
    const unexpected=changed.filter(p=>!p.startsWith('.agent/tmp/') && !a.files.some(prefix=>p===prefix || p.startsWith(prefix.endsWith('/')?prefix:prefix+'/')));
    if(unexpected.length) throw Error('Unexpected changed paths: '+unexpected.join(', '));
    if(a.role!=='committer' && head!==a.startHead) throw Error('Specialist committed without Committer authority');
    a.status='collected'; a.collectedAt=new Date().toISOString(); a.endHead=head; a.changedPaths=changed; a.result=r.text;a.terminal=r.terminal;
    atomic(t.transport,t); return {assignmentId:a.assignmentId,role:a.role,result:r.text,terminal:r.terminal,head,changedPaths:changed,scopeVerified:true,
      completedSuccessfully:r.terminal.kind==='completed'};
  }
  async control(agent,args) {
    const {t}=this.requireCoordinator(agent);
    if(!Array.isArray(args.argv)||!args.argv.length||args.argv.some(x=>typeof x!=='string'||x.startsWith('--state'))) throw Error('Provide ledger argv without state override');
    if(!['show','acquire','release','transition','record-commit','record-gate','record-habit','record-habit-observation','record-mutation','record-pr','record-ci'].includes(args.argv[0])) throw Error('Identity, state override and cleanup operations are not available through unrestricted ledger control');
    if(['record-gate','record-habit','record-mutation','record-commit'].includes(args.argv[0])) {
      const owner=read(t.ledger).checkout_lease?.owner;
      if(owner&&owner!=='coordinator') {
        const last=t.assignments.filter(a=>a.role===owner).at(-1);
        if(!last||last.status!=='collected') throw Error('Collect terminal specialist evidence before recording a checkout gate');
        const status=args.argv[args.argv.indexOf('--status')+1];
        if(last.terminal?.kind!=='completed'&&status!=='failed') throw Error('A specialist gate needs a successful terminal turn; failure or recovery cannot be recorded as passed or accepted');
      }
    }
    if(args.argv[0]==='release') {
      const l=read(t.ledger), role=l.checkout_lease?.owner;
      if(role && role!=='coordinator') {
        const w=await this.agent(t.sessions[role]);
        if(w.status!=='idle') throw Error('Cannot release an active worker lease');
        this.checkJobs(w);
        if(t.assignments.some(a=>a.role===role&&a.status!=='collected')) throw Error('Collect the assignment and verify scope before releasing');
      }
    }
    return this.ledger(t,args.argv);
  }
  async resume(agent) {
    const {t}=this.requireCoordinator(agent); this.checkPermission(agent);
    if(!fs.existsSync(t.ledger)) throw Error('This merged workflow was archived; its sessions remain available for conversation');
    await this.reconcile(agent,t,{deferActiveModels:true});
    for(const a of t.assignments.filter(x=>x.status!=='collected')) {
      const worker=await this.agent(a.sessionId), r=response(worker.session.snapshotEvents(),a.requestId);
      if(worker.status==='running') this.watch(t,a,worker);
      else a.status=r.terminal?'completed':'interrupted';
    }
    t.waiting=false; atomic(t.transport,t); return this.status(agent);
  }
  async recover(agent,args) {
    const {t,ledger}=this.requireCoordinator(agent);
    const a=t.assignments.find(x=>x.assignmentId===args.assignmentId);
    if(!a||a.status!=='interrupted') throw Error('Recover only an interrupted assignment after workflow_resume');
    if(ledger.checkout_lease?.owner!==a.role) throw Error('The interrupted assignment must retain its original lease');
    const worker=await this.agent(a.sessionId);
    if(worker.status!=='idle') throw Error('Worker is still active');
    this.checkJobs(worker);
    const evidence=fs.realpathSync(path.resolve(t.repo,args.diagnosticPath));
    if(!evidence.startsWith(fs.realpathSync(path.join(t.repo,'.agent/tmp'))+path.sep)||!fs.readFileSync(evidence,'utf8').trim()||!args.reason?.trim()) throw Error('Provide non-empty ignored diagnostic evidence and a Coordinator decision');
    if(git(t.repo,'branch','--show-current')!==t.branch) throw Error('Resolve checkout branch mismatch before recovering');
    a.status='collected';a.recovery='cancelled-after-inspection';a.diagnosticPath=evidence;a.diagnosticSha256=digest(fs.readFileSync(evidence));
    a.result='Interrupted assignment cancelled after Coordinator inspection: '+args.reason;a.endHead=git(t.repo,'rev-parse','HEAD');a.collectedAt=new Date().toISOString();
    atomic(t.transport,t);
    return {assignmentId:a.assignmentId,recovery:a.recovery,leaseRetained:true,success:false,diagnosticPath:evidence,head:a.endHead,
      next:'Inspect authorized scope and real side effects; record failure/correction as applicable before explicitly releasing or issuing a new assignment to the same session. No prompt replay was performed.'};
  }
  async cleanup(agent,args) {
    this.checkPermission(agent);
    const managed=this.info(agent);
    if(managed) this.requireCoordinator(agent);
    else if(!agent.session.snapshotEvents().some(e=>e.type==='user/message'&&JSON.stringify(e.data).includes('/implement-approved-plan-deepseek'))) throw Error('Only an explicitly invoked Coordinator may reconcile earlier plans');
    const repo=fs.realpathSync(agent.session.header.cwd),state=fs.realpathSync(path.resolve(repo,args.ledgerPath));
    const dir=fs.realpathSync(path.join(repo,'.agent/tmp'));
    if(path.dirname(state)!==dir||!state.endsWith('.dsh-workflow.json')) throw Error('Cleanup is confined to native workflow ledgers in this checkout');
    const ledger=read(state),pr=ledger.pull_request;
    if(fs.realpathSync(ledger.repository)!==repo||!pr) throw Error('Ledger repository or recorded PR does not match');
    const github=JSON.parse(execFileSync('gh',['pr','view',String(pr.number),'--repo',pr.repository,'--json','state,mergedAt,url'],{encoding:'utf8'}));
    if(github.state!=='MERGED'||!github.mergedAt||!Number.isFinite(Date.parse(github.mergedAt))||github.url!==pr.url) throw Error('GitHub does not confirm an unambiguous matching MERGED PR; preserve all artifacts');
    return this.ledger({ledger:state},['cleanup','--github-status','MERGED','--repo',pr.repository,'--number',String(pr.number)]);
  }
  guard(exec) {
    const agent=exec.agent; if(!agent) return undefined;
    const i=this.info(agent); if(!i) return undefined;
    if(['skill','ask_user_question','todo_write'].includes(exec.name)||exec.name.startsWith('workflow_')) return undefined;
    if(i.ledger.checkout_lease?.owner!==i.link.role) return 'Checkout tools require this session role to hold the Coordinator-granted lease';
    if(i.link.role!=='coordinator') {
      const current=agent.session.snapshotEvents().filter(e=>e.type==='user/message'&&e.data.source?.kind==='user').at(-1)?.data.source.rpcId;
      if(!i.t.assignments.some(a=>a.role===i.link.role&&a.requestId===current&&a.status!=='collected')) return 'Checkout tools require the current Coordinator assignment; direct human conversation does not grant workflow authority';
    }
    if(exec.name==='exit_plan_mode') return 'An approved implementation workflow does not return automatically to Plan Mode';
    return undefined;
  }
  checkJobs(agent) {
    if(this.ctx.jobs?.list(agent).some(j=>['running','stopping'].includes(j.status))) throw Error('A specialist background job remains active; keep its lease and collect the job first');
  }
  attach(agent) {
    const original=agent.ctx.tools.get('exit_plan_mode',agent);
    if(original) agent.ctx.tools.register({...original,execute:async(args,execution)=>{
      const result=await original.execute(args,execution);
      if(result?.approved===true) { this.approve(agent,args.plan); execution.concludeTurn(); this.finishApprovedPlan(agent).catch(error=>console.error('Plan finalization failed:',error.message)); }
      return result;
    }});
    this.finishApprovedPlan(agent).catch(error=>console.error('Plan recovery failed:',error.message));
    agent.ctx.systemPrompt.section({name:'dsh-workflow:authority',order:9500,text:()=>{
      const i=this.info(agent);
      if(!i) return 'After native plan approval stop and wait for the explicit /implement-approved-plan-deepseek invocation. Approval alone does not begin repository implementation.';
      return `Native DSH workflow ${i.t.slug}. Your role is ${i.link.role}; Coordinator session ${i.t.coordinator} is the sole authority. Phase ${i.ledger.phase}; lease ${i.ledger.checkout_lease?.owner ?? 'none'}. ${i.link.role==='coordinator'?'Use workflow_* tools and continue the approved plan autonomously. Wait through workflow_wait, not repeated polling.':'No coordination, peer messages or ledger mutations. Informational human conversation is allowed; checkout tools require your Coordinator assignment and lease.'}`;
    }});
  }
  async console(request,signal) {
    const {op,args={}}=request;
    if(op==='session.create') return this.ctx.sessionController.create({...args,agentPreset:'deepseek-standard'});
    if(op==='session.list') return this.ctx.sessionController.list({},signal);
    if(op==='session.rename') return this.ctx.sessionController.rename(args);
    if(op==='session.prompt') return this.ctx.sessionController.prompt(args,signal);
    if(op==='session.model') return this.ctx.sessionController.selectModel(args);
    if(op==='session.resume') { const a=await this.agent(args.sessionId); this.checkPermission(a); return {sessionId:a.session.id,status:a.status,permissions:'danger-full-access',defaultModel:this.defaultSelection()}; }
    if(op==='workflow.configure-models') {
      const coordinator=await this.agent(args.sessionId),{t}=this.requireCoordinator(coordinator);
      await this.configureModels(coordinator,t,{includeCoordinator:true});
      return this.status(coordinator);
    }
    if(op==='session.history') { const a=await this.agent(args.sessionId); return {sessionId:a.session.id,status:a.status,events:a.session.snapshotEvents()}; }
    if(op==='workspace.create') return this.ctx.workspaceController.create(args);
    if(op==='workspace.list') {
      const lifetime=new AbortController();
      try { for await(const frame of this.ctx.workspaceController.follow(lifetime.signal)) return frame; }
      finally { lifetime.abort(); }
    }
    if(op==='session.inspect') {
      const a=await this.agent(args.sessionId),events=a.session.snapshotEvents();
      return {sessionId:a.session.id,status:a.status,cwd:a.session.header.cwd,agentPreset:a.session.header.agentPreset,
        selection:events.filter(e=>e.type==='model/selection').at(-1)?.data??null,
        activeJobs:this.ctx.jobs?.list(a).filter(j=>['running','stopping'].includes(j.status)).length??0,
        requests:events.filter(e=>e.type==='request/header').map(e=>e.data.header.config),
        tools:events.filter(e=>e.type==='tool/call').map(e=>e.data.name),
        replies:events.filter(e=>e.type==='assistant/message').flatMap(e=>(e.data.message?.content??e.data.content??[]).filter(c=>c.type==='text').map(c=>c.text)),
        plan:this.ctx.agentPresets.serviceFor(a,'planMode')?.get(a),workflow:this.status(a)};
    }
    if(op==='command') { const a=await this.agent(args.sessionId); return this.ctx.commands.execute(a,args.line,[],signal); }
    if(op==='workflow.status') return this.status(await this.agent(args.sessionId));
    if(op==='catalog') return this.ctx.sessionController.modelCatalog();
    throw Error('Unknown operator operation');
  }
}

export const name='deepseek-approved-plan-workflow';
export const inject=['sessionController','workspaceController','permissionPresets','agentPresets','agentDefaultModel','tools','systemPrompt','commands','userQuestions','connection','jobs'];
export async function apply(ctx,config) {
  const require=createRequire(path.join(config.runtimeRoot,'package.json'));
  const {defineTool}=await import(pathToFileURL(require.resolve('@deepseek-ai/dsh-tools')).href);
  const host=new NativeWorkflow(ctx,config);
  ctx.effect(()=>()=>{host.stopped=true;});
  ctx.tools.guard(execution=>host.guard(execution));
  ctx.on('agent/created',({agent})=>host.attach(agent));
  const str=(description,required=true)=>({type:'string',description,...(required?{required:true}:{})});
  const argv={type:'array',items:{type:'string'},required:true};
  const specs=[
    ['workflow_start','Start explicit approved plan and create exactly six persistent top-level sessions.',{slug:str('Workflow slug'),branch:str('Feature branch'),base:str('Declared base',false),approvedPlanPath:str('Optional externally approved Markdown file',false)},(a,e)=>host.start(e.agent,{...a,signal:e.signal})],
    ['workflow_status','Read workflow, registered sessions, phase, lease and assignments.',{},(a,e)=>host.status(e.agent)],
    ['workflow_dispatch','Coordinator sends an assignment to an existing specialist under its active lease.',{role:str('Registered role'),assignmentId:str('Unique assignment identity'),files:{...argv,description:'Explicit authorized relative paths or directory prefixes'},prompt:str('Task, required skills and expected evidence')},(a,e)=>host.dispatch(e.agent,a,e.signal)],
    ['workflow_collect','Coordinator collects an idle specialist result and verifies checkout scope.',{assignmentId:str('Assignment identity')},(a,e)=>host.collect(e.agent,a)],
    ['workflow_control','Coordinator operates the guarded behavioral ledger using argv, without shell interpolation.',{argv},(a,e)=>host.control(e.agent,a)],
    ['workflow_wait','Conclude Coordinator turn until Host reports specialist completion in this same session.',{},async(a,e)=>{const v=await host.wait(e.agent);e.concludeTurn();return v;}],
    ['workflow_resume','Reconcile original Coordinator and six session IDs after interruption; retain unresolved leases.',{},(a,e)=>host.resume(e.agent)]
    ,['workflow_recover','Cancel an inspected interrupted assignment without replay or success claim; retain its lease.',{assignmentId:str('Interrupted assignment'),diagnosticPath:str('Non-empty ignored diagnostic report'),reason:str('Coordinator routing decision')},(a,e)=>host.recover(e.agent,a)]
    ,['workflow_cleanup','Clean only an earlier native plan/ledger pair after independent matching GitHub MERGED confirmation.',{ledgerPath:str('Exact earlier .dsh-workflow.json path')},(a,e)=>host.cleanup(e.agent,a)]
  ];
  for(const [tool,description,parameters,execute] of specs) ctx.tools.register(defineTool({name:tool,description,parameters,
    output:{schema:{type:'object',additionalProperties:true},render:(_args,value)=>[{type:'text',text:JSON.stringify(value)}]},
    execute:(args,execution)=>tool==='workflow_status'?execute(args,execution):host.exclusive(execution.agent,()=>execute(args,execution))}));
  ctx.connection.fetch.register({path:'/api/dsh-workflow/console',methods:['POST'],requestBody:'buffered',fetch:async request=>{
    try { return Response.json({ok:true,value:await host.console(await request.json(),request.signal)}); }
    catch(error) { return Response.json({ok:false,error:error.message},{status:400}); }
  }});
}
