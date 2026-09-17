import fs from 'node:fs';
import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
const require=createRequire('/home/renanfranca/.local/share/deepseek-harness/package.json');
const WebSocket=require('ws');
const page=await (await fetch('http://127.0.0.1:9234/json/new?about:blank',{method:'PUT'})).json();
const socket=new WebSocket(page.webSocketDebuggerUrl);
await new Promise((resolve,reject)=>{socket.once('open',resolve);socket.once('error',reject);});
let id=0;const pending=new Map();
socket.on('message',bytes=>{const m=JSON.parse(bytes);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(m.error.message)):p.resolve(m.result);}});
const call=(method,params={})=>new Promise((resolve,reject)=>{const current=++id;pending.set(current,{resolve,reject});socket.send(JSON.stringify({id:current,method,params}));});
const log=fs.readFileSync('/home/renanfranca/.dsh/web-runtime.log','utf8');
const url=[...log.matchAll(/dsh web: (http:\/\/127\.0\.0\.1:3080\/\?token=\S+)/g)].at(-1)[1];
await call('Page.enable');
await call('Emulation.setDeviceMetricsOverride',{width:1280,height:1000,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url});
let text;
for(let attempt=0;attempt<50;attempt++) {
  const r=await call('Runtime.evaluate',{expression:'document.body?.innerText',returnByValue:true});text=r.result?.value??'';
  if(text.includes('dsh-workflow-smoke-test'))break;
  await new Promise(r=>setTimeout(r,500));
}
fs.writeFileSync('/home/renanfranca/.dsh/validation/rendered-web.txt',text,{mode:0o600});
assert.ok(text.includes('dsh-workflow-smoke-test'),'Official workspace rendered in browser');
console.log('Official Web UI rendered workspaces in Chrome');
// Only use UI interaction to verify visible navigation. Orchestration uses native APIs.
await call('Runtime.evaluate',{expression:`document.querySelector('button[aria-label="Open sidebar"]')?.click()`});
let body;
for(let attempt=0;attempt<20;attempt++) {
  body=await call('Runtime.evaluate',{expression:'document.body.innerText',returnByValue:true});
  if(body.result.value.includes('dsh-smoke-command'))break;
  await new Promise(r=>setTimeout(r,500));
}
await call('Runtime.evaluate',{expression:`[...document.querySelectorAll('button')].find(b=>/Show \\d+ more sessions/.test(b.innerText))?.click()`});
await new Promise(r=>setTimeout(r,500));
body=await call('Runtime.evaluate',{expression:'document.body.innerText',returnByValue:true});
for(const role of ['Coordinator','implementer','committer','validator','habit-curator','mutation-analyst','structural-reviewer']) {
  assert.ok(body.result.value.includes('dsh-smoke-command · '+role),role+' appears in ordinary session navigation');
}
await new Promise(r=>setTimeout(r,500));
const shot=await call('Page.captureScreenshot',{format:'png'});
fs.writeFileSync('/home/renanfranca/.dsh/validation/native-web-sessions.png',Buffer.from(shot.data,'base64'),{mode:0o600});
console.log('Private workspace and workflow sessions visibly rendered; screenshot saved privately');
await call('Page.close');socket.close();
