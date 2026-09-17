// Integration test only: accepts the exact fixture plan already authorized by the user.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
const require=createRequire('/home/renanfranca/.local/share/deepseek-harness/package.json');
const WebSocket=require('ws');
const [sid,planPath]=process.argv.slice(2);
if(!sid||!planPath) throw Error('session ID and expected fixture plan path required');
const expected=fs.readFileSync(planPath,'utf8').trim();
const log=fs.readFileSync('/home/renanfranca/.dsh/web-runtime.log','utf8');
const url=[...log.matchAll(/dsh web: (http:\/\/127\.0\.0\.1:3080\/\?token=\S+)/g)].at(-1)?.[1];
const login=await fetch(url,{redirect:'manual'});
const cookie=login.headers.getSetCookie().map(s=>s.split(';')[0]).join('; ');
const headers={Cookie:cookie,Origin:'http://127.0.0.1:3080','Content-Type':'application/json'};
const socket=new WebSocket('ws://127.0.0.1:3080/api/remote.mux',{headers});
let clientId,approved=false;
async function rpc(method,args) {
  const reply=await fetch('http://127.0.0.1:3080/api/'+method,{method:'POST',headers,body:JSON.stringify({type:'client-request',rpcId:crypto.randomUUID(),method,payload:{args}})});
  const body=await reply.json();if(!body.result?.ok)throw Error(JSON.stringify(body));return body.result.value;
}
const timer=setTimeout(()=>{console.error('Plan review timed out');socket.close();process.exitCode=1;},180000);
socket.on('open',()=>socket.send(JSON.stringify({type:'open',streamId:'plan-test',endpoint:'$events',payload:{args:{}}})));
socket.on('message',async bytes=>{
  try {
    const frame=JSON.parse(bytes.toString()),e=frame.value;
    if(e?.type==='ready') {clientId=e.clientId;console.log('Official Remote WebSocket ready');}
    if(e?.type==='waterfall'&&e.agentId===sid&&e.event==='user-questions/request') {
      const questions=e.request.questions;
      if(questions.length!==1||questions[0].intent?.kind!=='plan-review'||questions[0].detail?.trim()!==expected) throw Error('Fixture plan differs from the explicitly authorized exact plan; no automatic approval');
      const q=questions[0];
      await rpc('$events/result',{clientId,eventId:e.eventId,outcome:{kind:'result',value:{answers:[{id:q.id,selected:[q.intent.approve]}]}}});
      approved=true;console.log('Exact fixture plan approved through official Remote event API');
      clearTimeout(timer);setTimeout(()=>socket.close(),2500);
    }
  } catch(error) {console.error(error.message);clearTimeout(timer);socket.close();process.exitCode=1;}
});
socket.on('error',error=>{console.error(error.message);clearTimeout(timer);process.exitCode=1;});
socket.on('close',()=>{clearTimeout(timer);if(!approved)process.exitCode=1;});
