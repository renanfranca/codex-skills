import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {NativeWorkflow,atomic,ROLES,DEFAULT_ROLE_REASONING_EFFORTS} from '../dsh-workflow-plugin.mjs';

const EFFORTS={implementer:'low',committer:'low',validator:'off','habit-curator':'off','mutation-analyst':'off','structural-reviewer':'low'};
const DEFAULT={provider:'example-provider',model:'example-model',reasoningEffort:'low'};

function fixture(t) {
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'dsh-orchestration-test-'));
  t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
  const git=(...args)=>execFileSync('git',args,{cwd:root,encoding:'utf8'}).trim();
  git('init','-b','main');git('config','user.name','Fixture');git('config','user.email','fixture@example.invalid');
  fs.writeFileSync(path.join(root,'existing.txt'),'original');git('add','.');git('commit','-m','test: fixture');
  const transport=path.join(root,'transport.json'),ledger=path.join(root,'ledger.json');
  const coordinator={status:'idle',session:{id:'coordinator',header:{cwd:root}}};
  const worker={status:'idle',whenIdle:()=>new Promise(()=>{}),session:{id:'implementer',snapshotEvents:()=>[
    {type:'user/message',data:{source:{kind:'user',rpcId:'assignment'}}},
    {type:'assistant/message',data:{message:{content:[{type:'text',text:'Finished'}]}}},
    {type:'turn/end',data:{reason:{kind:'completed'}}}
  ]}};
  const agents=Object.fromEntries(ROLES.map(role=>[role,{...worker,session:{...worker.session,id:role}}]));
  const created=[], models=[], prompts=[];
  let defaultModel={...DEFAULT};
  const ctx={
    agentDefaultModel:{currentSelection:()=>({...defaultModel}),saveSelection:async selection=>{defaultModel={...selection};}},
    permissionPresets:{current:()=> 'danger-full-access',resolve:()=>({sandbox:'danger-full-access',approval:'never'})},
    workspaceController:{create:async()=>({workspace:{workspaceId:'workspace'}})},
    sessionController:{
      create:async args=>{assert.ok(!(args.workspaceId&&args.cwd),'native create accepts workspaceId or cwd');created.push(args);return {sessionId:args.sessionId};},
      resolveAgent:async id=>({agent:agents[id]}),selectModel:async args=>{models.push(args);const {sessionId,...selected}=args;await ctx.agentDefaultModel.saveSelection(selected);return {selected};},rename:async()=>{},prompt:async args=>prompts.push(args)
    }
  };
  const state={transport,ledger,repo:root,slug:'fixture',branch:'main',coordinator:'coordinator',sessions:Object.fromEntries(ROLES.map(role=>[role,role])),assignments:[],baseSha:git('rev-parse','HEAD')};
  state.assignments.push({assignmentId:'active',role:'implementer',sessionId:'implementer',requestId:'assignment',status:'accepted'});
  atomic(transport,state);atomic(ledger,{phase:'implementing',checkout_lease:{owner:'implementer'}});
  const host=new NativeWorkflow(ctx,{home:path.join(root,'home'),roleReasoningEfforts:EFFORTS});host.ledger=()=>({});
  host.registry.sessions.coordinator={role:'coordinator',transport};host.registry.sessions.implementer={role:'implementer',transport};
  return {host,state,worker,agents,coordinator,root,git,created,models,prompts};
}

test('six ordinary sessions use the DSH default and role efforts without changing the global default',async t=>{
  const f=fixture(t);await f.host.reconcile(f.coordinator,f.state);
  assert.equal(f.created.length,6);assert.deepEqual(f.created.map(x=>x.sessionId),ROLES);
  assert.ok(f.created.every(x=>x.agentPreset==='deepseek-standard'));
  assert.ok(f.models.every(x=>x.provider===DEFAULT.provider&&x.model===DEFAULT.model&&x.reasoningEffort===EFFORTS[x.sessionId]));
  assert.deepEqual(f.host.defaultSelection(),DEFAULT);
});

test('unconfigured roles use the shipped low-effort policy while host overrides still win',async t=>{
  const f=fixture(t);
  f.host.config.roleReasoningEfforts={};
  await f.host.configureModels(f.coordinator,f.state);
  assert.deepEqual(f.models.map(x=>x.sessionId),ROLES);
  assert.deepEqual(f.models.map(x=>x.reasoningEffort),ROLES.map(role=>DEFAULT_ROLE_REASONING_EFFORTS[role]));
  assert.deepEqual(DEFAULT_ROLE_REASONING_EFFORTS,{...EFFORTS});
  assert.equal(DEFAULT_ROLE_REASONING_EFFORTS['implementer'],'low');
  assert.equal(DEFAULT_ROLE_REASONING_EFFORTS['structural-reviewer'],'low');
  assert.equal(DEFAULT_ROLE_REASONING_EFFORTS['validator'],'off');
  f.models.length=0;
  f.host.config.roleReasoningEfforts={implementer:'high'};
  await f.host.configureModels(f.coordinator,f.state);
  assert.equal(f.models.find(x=>x.sessionId==='implementer').reasoningEffort,'high');
  assert.equal(f.models.find(x=>x.sessionId==='structural-reviewer').reasoningEffort,'low');
});

test('unauthorized edits to already dirty files are rejected and retain the lease',async t=>{
  const f=fixture(t);f.state.assignments=[];atomic(f.state.transport,f.state);fs.writeFileSync(path.join(f.root,'existing.txt'),'earlier authorized delta');
  await f.host.dispatch(f.coordinator,{role:'implementer',assignmentId:'behavior',files:['new.txt'],prompt:'Implement new behavior'},new AbortController().signal);
  const s=JSON.parse(fs.readFileSync(f.state.transport));s.assignments[0].requestId='assignment';atomic(f.state.transport,s);
  fs.writeFileSync(path.join(f.root,'existing.txt'),'unauthorized overwrite');
  await assert.rejects(f.host.collect(f.coordinator,{assignmentId:'behavior'}),/Unexpected changed paths/);
  assert.equal(JSON.parse(fs.readFileSync(f.state.ledger)).checkout_lease.owner,'implementer');
});

test('specialists cannot dispatch or mutate ledger authority',async t=>{
  const f=fixture(t);
  await assert.rejects(f.host.control(f.worker,{argv:['release','--owner','implementer']}),/Only the registered Coordinator/);
  await assert.rejects(f.host.dispatch(f.worker,{role:'validator'}),/Only the registered Coordinator/);
});

test('managed checkout tools are denied without the matching role lease',t=>{
  const f=fixture(t);
  assert.equal(f.host.guard({agent:f.worker,name:'read'}),undefined);
  assert.match(f.host.guard({agent:f.coordinator,name:'bash'}),/lease/);
  assert.equal(f.host.guard({agent:f.coordinator,name:'workflow_control'}),undefined);
});

test('Coordinator can maintain its native todo list while a worker holds the checkout',t=>{
  const f=fixture(t);
  assert.equal(f.host.guard({agent:f.coordinator,name:'todo_write'}),undefined);
});

test('a worker response cannot release a lease while its background job remains active',async t=>{
  const f=fixture(t);f.host.ctx.jobs={list:()=>[{status:'running'}]};
  f.state.assignments.push({assignmentId:'behavior',role:'implementer',sessionId:'implementer',requestId:'assignment',files:['existing.txt'],startHead:f.git('rev-parse','HEAD'),startPaths:[]});atomic(f.state.transport,f.state);
  await assert.rejects(f.host.collect(f.coordinator,{assignmentId:'behavior'}),/background job/);
});

test('inspected interruption cancellation retains authority and performs no prompt replay',async t=>{
  const f=fixture(t),dir=path.join(f.root,'.agent/tmp');fs.mkdirSync(dir,{recursive:true});
  const diagnostic=path.join(dir,'interruption.md');fs.writeFileSync(diagnostic,'Checkout, HEAD and process state inspected; no commit was made.');
  f.state.assignments.push({assignmentId:'interrupted',role:'implementer',sessionId:'implementer',status:'interrupted'});atomic(f.state.transport,f.state);
  const result=await f.host.recover(f.coordinator,{assignmentId:'interrupted',diagnosticPath:diagnostic,reason:'Continue the unfinished behavior in the same worker session after inspection.'});
  assert.equal(result.success,false);assert.equal(result.leaseRetained,true);assert.equal(f.prompts.length,0);
  assert.equal(JSON.parse(fs.readFileSync(f.state.ledger)).checkout_lease.owner,'implementer');
  assert.equal(JSON.parse(fs.readFileSync(f.state.transport)).assignments.find(a=>a.assignmentId==='interrupted').status,'collected');
});

test('merged workflow sessions remain informational after plan/ledger archival',t=>{
  const f=fixture(t);fs.unlinkSync(f.state.ledger);
  assert.equal(f.host.status(f.worker).phase,'archived');
  assert.match(f.host.guard({agent:f.worker,name:'write'}),/lease/);
  assert.equal(f.host.guard({agent:f.worker,name:'skill'}),undefined);
});

test('parallel Coordinator operations serialize and an error does not lock future work',async t=>{
  const f=fixture(t),order=[];
  await Promise.all([
    f.host.exclusive(f.coordinator,async()=>{order.push('first');await new Promise(r=>setTimeout(r,10));order.push('first-complete');}),
    f.host.exclusive(f.coordinator,async()=>{order.push('second');})
  ]);
  assert.deepEqual(order,['first','first-complete','second']);
  await assert.rejects(f.host.exclusive(f.coordinator,async()=>{throw Error('failure');}),/failure/);
  assert.equal(await f.host.exclusive(f.coordinator,async()=> 'recovered'),'recovered');
});

test('ledger argv cannot redirect state using equals syntax or argparse abbreviations',async t=>{
  const f=fixture(t);
  await assert.rejects(f.host.control(f.coordinator,{argv:['--state=/tmp/other.json','show']}),/state override/);
  await assert.rejects(f.host.control(f.coordinator,{argv:['--sta=/tmp/other.json','show']}),/state override/);
});

test('direct human conversation cannot acquire checkout authority inside a specialist lease',t=>{
  const f=fixture(t);
  f.worker.session.snapshotEvents=()=>[{type:'user/message',data:{source:{kind:'user',rpcId:'human-conversation'}}}];
  assert.match(f.host.guard({agent:f.worker,name:'write'}),/assignment/);
  assert.equal(f.host.guard({agent:f.worker,name:'skill'}),undefined);
});

test('waiting without outstanding work fails instead of silently suspending Coordinator',async t=>{
  const f=fixture(t);f.state.assignments=[];atomic(f.state.transport,f.state);
  await assert.rejects(f.host.wait(f.coordinator),/No outstanding assignment/);
  assert.equal(JSON.parse(fs.readFileSync(f.state.transport)).waiting,undefined);
});

test('an interrupted assignment directs Coordinator to recovery instead of an unwakeable wait',async t=>{
  const f=fixture(t);f.state.assignments[0].status='interrupted';atomic(f.state.transport,f.state);
  await assert.rejects(f.host.wait(f.coordinator),/recover/);
});

test('progress text without a terminal event cannot be collected as completion',async t=>{
  const f=fixture(t);f.agents.implementer.session.snapshotEvents=()=>[
    {type:'user/message',data:{source:{kind:'user',rpcId:'assignment'}}},
    {type:'assistant/message',data:{message:{content:[{type:'text',text:'Starting validation'}]}}}
  ];
  await assert.rejects(f.host.collect(f.coordinator,{assignmentId:'active'}),/terminal/);
  assert.equal(JSON.parse(fs.readFileSync(f.state.ledger)).checkout_lease.owner,'implementer');
});

test('failed and cancelled turns cannot become accepted specialist gates',async t=>{
  const f=fixture(t);
  for(const ending of [{terminal:{kind:'error',error:{code:402}}},{recovery:'cancelled-after-inspection'}]) {
    f.state.assignments=[{role:'implementer',status:'collected',...ending}];atomic(f.state.transport,f.state);
    await assert.rejects(f.host.control(f.coordinator,{argv:['record-gate','--status','passed']}),/failure|successful/);
  }
});


test('a failed specialist selection preserves the DSH default and leaves configuration retryable',async t=>{
  const f=fixture(t), select=f.host.ctx.sessionController.selectModel;
  f.host.ctx.sessionController.selectModel=async args=>{await select(args);if(args.sessionId==='validator') throw Error('model unavailable');return {selected:{provider:args.provider,model:args.model,reasoningEffort:args.reasoningEffort}};};
  await assert.rejects(f.host.configureModels(f.coordinator,f.state),/model unavailable/);
  assert.deepEqual(f.host.defaultSelection(),DEFAULT);
  assert.equal(f.prompts.length,0);
  f.host.ctx.sessionController.selectModel=select;
  await f.host.configureModels(f.coordinator,f.state);
  assert.deepEqual(f.host.defaultSelection(),DEFAULT);
});

test('configuring saved sessions never sends introductory prompts or changes workflow phase or lease',async t=>{
  const f=fixture(t),before=fs.readFileSync(f.state.transport,'utf8'),ledgerBefore=fs.readFileSync(f.state.ledger,'utf8');
  f.host.ctx.sessionController.resolveAgent=async id=>({agent:id==='coordinator'?f.coordinator:f.agents[id]});
  const value=await f.host.console({op:'workflow.configure-models',args:{sessionId:'coordinator'}});
  assert.equal(f.models.length,7);assert.equal(f.prompts.length,0);assert.equal(f.created.length,0);
  assert.equal(fs.readFileSync(f.state.transport,'utf8'),before);
  assert.equal(fs.readFileSync(f.state.ledger,'utf8'),ledgerBefore);
  assert.equal(value.phase,'implementing');
  assert.deepEqual(f.host.defaultSelection(),DEFAULT);
});

test('configuration refuses active sessions before making any model selections',async t=>{
  const f=fixture(t);f.agents.validator.status='running';
  await assert.rejects(f.host.configureModels(f.coordinator,f.state),/idle sessions/);
  assert.equal(f.models.length,0);assert.equal(f.prompts.length,0);
});

test('the operator model selector respects its requested route instead of replacing it',async t=>{
  const f=fixture(t), requested={sessionId:'implementer',provider:'another-provider',model:'another-model',reasoningEffort:'low'};
  await f.host.console({op:'session.model',args:requested});
  assert.deepEqual(f.models,[requested]);
});

test('a distinct default selected by the user during configuration is retained',async t=>{
  const f=fixture(t),userChoice={provider:'user-provider',model:'user-model',reasoningEffort:'low'};
  await f.host.withDefaultSelection(async(original,select)=>{
    await select('validator',{...original,reasoningEffort:'off'});
    await f.host.ctx.agentDefaultModel.saveSelection(userChoice);
  });
  assert.deepEqual(f.host.defaultSelection(),userChoice);
});

test('a Web model choice between two specialist selections survives the remaining selections',async t=>{
  const f=fixture(t),userChoice={provider:'user-provider',model:'user-model',reasoningEffort:'low'};
  await f.host.withDefaultSelection(async(original,select)=>{
    await select('validator',{...original,reasoningEffort:'off'});
    await f.host.ctx.agentDefaultModel.saveSelection(userChoice);
    await select('structural-reviewer',original);
  });
  assert.deepEqual(f.host.defaultSelection(),userChoice);
});

test('a Web choice made while native specialist selection is awaiting admission is preserved',async t=>{
  const f=fixture(t),userChoice={provider:'user-provider',model:'user-model',reasoningEffort:'low'};
  let admitted,release;
  const admission=new Promise(resolve=>{admitted=resolve;}),gate=new Promise(resolve=>{release=resolve;});
  const nativeSelect=f.host.ctx.sessionController.selectModel;
  f.host.ctx.sessionController.selectModel=async args=>{admitted();await gate;return nativeSelect(args);};
  const configured=f.host.configureModels(f.coordinator,f.state);
  await admission;
  await f.host.ctx.agentDefaultModel.saveSelection(userChoice);
  release();await configured;
  assert.deepEqual(f.host.defaultSelection(),userChoice);
  assert.ok(f.models.every(selection=>selection.provider===DEFAULT.provider&&selection.model===DEFAULT.model));
});

test('unloading the workflow restores native default persistence',async t=>{
  const f=fixture(t);
  f.host.restoreDefaultWriter();
  const requested={provider:'user-provider',model:'user-model',reasoningEffort:'low'};
  await f.host.ctx.sessionController.selectModel({sessionId:'validator',...requested});
  assert.deepEqual(f.host.defaultSelection(),requested);
});

test('resuming an idle workflow reuses its six identities without replaying introductions',async t=>{
  const f=fixture(t);
  f.state.assignments=[];atomic(f.state.transport,f.state);
  for(const role of ROLES) {
    const events=f.agents[role].session.snapshotEvents();
    f.agents[role].session.snapshotEvents=()=>[...events,{type:'user/message',data:{source:{kind:'user',rpcId:'intro-'+role}}}];
  }
  await f.host.resume(f.coordinator);
  assert.deepEqual(f.created.map(created=>created.sessionId),ROLES);
  assert.equal(f.prompts.length,0);
  assert.equal(JSON.parse(fs.readFileSync(f.state.ledger)).checkout_lease.owner,'implementer');
  assert.deepEqual(f.host.defaultSelection(),DEFAULT);
});

test('resuming an active workflow retains its worker monitor and defers model changes',async t=>{
  const f=fixture(t);
  f.agents.implementer.status='running';
  for(const role of ROLES) {
    const events=f.agents[role].session.snapshotEvents();
    f.agents[role].session.snapshotEvents=()=>[...events,{type:'user/message',data:{source:{kind:'user',rpcId:'intro-'+role}}}];
  }
  await f.host.resume(f.coordinator);
  assert.equal(f.models.length,0);assert.equal(f.prompts.length,0);
  assert.ok(f.host.watching.has('assignment'));
  assert.equal(JSON.parse(fs.readFileSync(f.state.transport)).assignments[0].status,'accepted');
  assert.equal(JSON.parse(fs.readFileSync(f.state.ledger)).checkout_lease.owner,'implementer');
  assert.deepEqual(f.host.defaultSelection(),DEFAULT);
});
