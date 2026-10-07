import test from 'node:test';
import assert from 'node:assert/strict';
import {createHandler} from '../../supabase/functions/luna-tv-api/handler.mjs';
function setup({active = false, authStatus = 200, planStatus = 200} = {}) {
  const calls = [];
  const handler = createHandler({url:'https://test.invalid',key:'server-only',fetcher:async (url, options) => {
    calls.push({url,options});
    if (url.includes('/auth/v1/user')) return new Response(JSON.stringify({id:'owner-1',email:'test@example.invalid'}),{status:authStatus});
    if (url.includes('/assinaturas?')) return new Response(JSON.stringify([{plano:'Premium',status:active?'ativo':'inativo'}]),{status:planStatus});
    if (url.includes('/jogos_criados?')) return Response.json([{id:'game-1',title:'Meu jogo',kind:'memory',content:{items:['A','B']}}]);
    if (url.includes('video_url')) return Response.json([{id:9,nome:'Premium movie',categoria:'Premium::Filmes',video_url:'https://media.invalid/video.mp4'}]);
    return Response.json([{id:9,nome:'Premium movie',categoria:'Premium::Filmes'}]);
  }});
  const req = (path,token='valid') => new Request('https://test.invalid/functions/v1/luna-tv-api/'+path,{headers:token?{Authorization:'Bearer '+token}:{}});
  return {handler,calls,req};
}
test('requires login before any query',async()=>{const {handler,calls,req}=setup();assert.equal((await handler(req('catalog',null))).status,401);assert.equal(calls.length,0);});
test('invalid/expired session cannot reach database',async()=>{const {handler,calls,req}=setup({authStatus:401});assert.equal((await handler(req('play?id=9'))).status,401);assert.equal(calls.length,1);});
test('catalog excludes media URLs and marks locked premium',async()=>{const {handler,calls,req}=setup();const r=await (await handler(req('catalog'))).json();assert.equal(r.items[0].locked,true);assert.equal(r.items[0].id,'9');assert.equal(calls.some(c=>c.url.includes('select=')&&c.url.includes('video_url')),false);});
test('inactive subscription cannot play premium',async()=>{const {handler,req}=setup();assert.equal((await handler(req('play?id=9'))).status,403);});
test('active subscription can play, with fresh ownership lookup',async()=>{const {handler,calls,req}=setup({active:true});const r=await handler(req('play?id=9'));assert.equal(r.status,200);assert.match((await r.json()).url,/video.mp4/);assert.ok(calls.some(c=>c.url.includes('user_id=eq.owner-1')));});
test('subscription lookup failure is closed',async()=>{const {handler,req}=setup({active:true,planStatus:500});assert.equal((await handler(req('play?id=9'))).status,503);});
test('rejects arbitrary IDs and write operations',async()=>{const {handler,req}=setup();assert.equal((await handler(req('play?id=1%26select=*'))).status,400);assert.equal((await handler(new Request('https://test.invalid/catalog',{method:'POST'}))).status,405);});
test('games are always scoped to verified user, ignoring requested owner',async()=>{const {handler,calls,req}=setup();const response=await handler(req('games?user_id=other'));assert.equal(response.status,200);const query=calls.find(c=>c.url.includes('/jogos_criados?'));assert.match(query.url,/user_id=eq.owner-1/);assert.ok(!query.url.includes('other'));});
test('CORS preflight does not query data',async()=>{const {handler,calls}=setup();const r=await handler(new Request('https://test.invalid',{method:'OPTIONS'}));assert.equal(r.status,204);assert.equal(calls.length,0);});
