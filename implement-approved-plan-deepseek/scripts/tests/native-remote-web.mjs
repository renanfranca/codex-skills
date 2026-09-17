import fs from 'node:fs';
import https from 'node:https';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
const require=createRequire('/home/renanfranca/.local/share/deepseek-harness/package.json');
const WebSocket=require('ws');
const state=JSON.parse(execFileSync('tailscale',['status','--json'],{encoding:'utf8'}));
const dns=state.Self.DNSName.replace(/\.$/,''),ip=state.TailscaleIPs[0];
const lookup=(_host,options,cb)=>options?.all?cb(null,[{address:ip,family:4}]):cb(null,ip,4);
const base='https://'+dns;
const log=fs.readFileSync('/home/renanfranca/.dsh/web-runtime.log','utf8');
const path=[...log.matchAll(/dsh web: http:\/\/127\.0\.0\.1:3080(\/\?token=\S+)/g)].at(-1)[1];
function get(path,headers={}) {
  return new Promise((resolve,reject)=>{
    https.get(base+path,{lookup,headers},res=>{
      const chunks=[];res.on('data',b=>chunks.push(b));res.on('end',()=>resolve({status:res.statusCode,headers:res.headers,body:Buffer.concat(chunks).toString()}));
    }).on('error',reject);
  });
}
assert.equal((await get('/')).status,401);
const login=await get(path);assert.ok([302,303].includes(login.status));
const cookie=login.headers['set-cookie'].map(s=>s.split(';')[0]).join('; ');
const headers={Cookie:cookie,Origin:base};
const index=await get('/',headers);assert.equal(index.status,200);
const assets=[...index.body.matchAll(/(?:src|href)=["'](\.\/assets\/[^"']+)["']/g)].map(x=>x[1].slice(1));
for(const asset of assets) assert.equal((await get(asset,headers)).status,200);
assert.equal((await get('/api/dsh-workflow/console',{...headers,Origin:'https://untrusted.invalid'})).status,403);
console.log('Private HTTPS, native auth, Origin fence and '+assets.length+' official assets passed');
const socket=new WebSocket('wss://'+dns+'/api/remote.mux',{headers,lookup});
await new Promise((resolve,reject)=>{
  const timer=setTimeout(()=>{socket.close();reject(Error('Remote WebSocket timeout'));},25000);
  socket.on('error',reject);
  socket.on('open',()=>socket.send(JSON.stringify({type:'open',streamId:'events',endpoint:'$events',payload:{args:{}}})));
  socket.on('message',bytes=>{
    try {
      const frame=JSON.parse(bytes.toString());
      if(frame.streamId==='events'&&frame.value?.type==='ready') {
        console.log('Authenticated private WSS official Remote events ready');
        socket.send(JSON.stringify({type:'open',streamId:'workspaces',endpoint:'workspace/follow',payload:{args:{}}}));
      }
      if(frame.streamId==='workspaces'&&frame.type==='item') {
        assert.ok(JSON.stringify(frame.value).includes('dsh-workflow-smoke-test'));
        console.log('Official workspace feed includes private fixture and persistent sessions');
        clearTimeout(timer);socket.close();resolve();
      }
      if(frame.type==='error') throw Error(JSON.stringify(frame));
    } catch(error) {clearTimeout(timer);socket.close();reject(error);}
  });
});
