import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';

const require=createRequire('/home/renanfranca/.local/share/deepseek-harness/package.json');
const {DeepSeekAdapter,resolveAdapterOptions}=await import(pathToFileURL(require.resolve('@deepseek-ai/dsh-llm-deepseek')).href);

test('the installed DeepSeek adapter sends role efforts and tools with the bounded output cap',async t=>{
  const requests=[];
  const originalFetch=globalThis.fetch;
  t.after(()=>{globalThis.fetch=originalFetch;});
  globalThis.fetch=async(url,options)=>{
    requests.push({url,body:JSON.parse(options.body)});
    const deltas=[
      {choices:[{index:0,delta:{role:'assistant',tool_calls:[{index:0,id:'call-1',type:'function',function:{name:'report',arguments:'{}'}}]},finish_reason:null}]},
      {choices:[{index:0,delta:{},finish_reason:'tool_calls'}]}
    ];
    return new Response(deltas.map(delta=>'data: '+JSON.stringify(delta)+'\n\n').join('')+'data: [DONE]\n\n',{headers:{'content-type':'text/event-stream'}});
  };
  const connection=resolveAdapterOptions({baseURL:'https://api.deepseek.com',thinking:'enabled',reasoningEffort:'high',maxTokens:16384});
  const adapter=new DeepSeekAdapter({
    options:()=>connection,resolveApiKey:async()=> 'fixture-key',resolveUserId:()=> 'fixture-user',
    prepareExtensions:async()=>({fields:{},accept:()=>{}})
  });
  for(const effort of ['off','low','high']) {
    const chunks=[];
    for await(const chunk of adapter.stream({provider:'deepseek-official',model:'deepseek-flash',reasoningEffort:effort,maxTokens:16384,
      messages:[{role:'user',content:[{type:'text',text:'Report the result.'}]}],tools:[{name:'report',description:'Report the result',parameters:{type:'object',properties:{}}}]})) chunks.push(chunk);
    const request=requests.at(-1);
    assert.equal(request.url,'https://api.deepseek.com/chat/completions');
    assert.deepEqual(request.body.thinking,{type:effort==='off'?'disabled':'enabled'});
    assert.equal(request.body.reasoning_effort,effort==='off'?undefined:effort);
    assert.equal(request.body.max_tokens,16384);
    assert.equal(request.body.tools[0].function.name,'report');
    assert.ok(chunks.some(chunk=>JSON.stringify(chunk).includes('report')),'non-thinking and thinking modes retain tool calls');
  }
});
