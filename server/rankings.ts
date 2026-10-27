import { createVerifier } from './verifier.js';
export const RULES='campus-10-v2';
export function dayKey(now=Date.now()){return new Date(now+9*3600000).toISOString().slice(0,10)}
export function rankingRules(mode='fixed'){return mode==='daily'?RULES+':daily:'+dayKey():RULES+':fixed'}
export function seedFor(rules:string,stage:number){let seed=2166136261;for(const char of rules+'/'+stage){seed=Math.imul(seed^char.charCodeAt(0),16777619)}return seed>>>0}

const cookieName='campus_player';
const json=(data:unknown,status=200,headers:Record<string,string>={})=>Response.json(data,{status,headers:{'Cache-Control':'no-store',...headers}});
function playerFrom(request:Request){const match=request.headers.get('cookie')?.match(/(?:^|;\s*)campus_player=([a-f0-9-]{36})(?:;|$)/);return match?.[1]??null}
function validOrigin(request:Request){const origin=request.headers.get('origin');return !origin||origin===new URL(request.url).origin}
async function body(request:Request){if(Number(request.headers.get('content-length'))>131072)throw Error('too_large');const text=await request.text();if(text.length>131072)throw Error('too_large');return JSON.parse(text)}
export async function handleRankings(request:Request,db:any){
 const url=new URL(request.url);
 try{
 if(request.method==='GET'&&url.pathname==='/api/rankings'){
  const competition=url.searchParams.get('mode')||'fixed';if(!['fixed','daily'].includes(competition))return json({error:'올바른 기록 모드를 선택하세요.'},400);const rules=rankingRules(competition);
  const stage=Number(url.searchParams.get('stage'));if(!Number.isInteger(stage)||stage<1||stage>10)return json({error:'올바른 단계를 선택하세요.'},400);
  const rows=await db.prepare('SELECT nickname, score, remaining, created FROM stage_scores WHERE stage=? AND rules=? ORDER BY score DESC, created ASC, player ASC LIMIT 20').bind(stage,rules).all();
  const player=playerFrom(request);let mine=null;
  if(player){const own=await db.prepare('SELECT nickname, score, remaining, created, player FROM stage_scores WHERE player=? AND stage=? AND rules=?').bind(player,stage,rules).first();if(own){const above=await db.prepare('SELECT COUNT(*) AS total FROM stage_scores WHERE stage=? AND rules=? AND (score>? OR (score=? AND created<?) OR (score=? AND created=? AND player<?))').bind(stage,rules,own.score,own.score,own.created,own.score,own.created,player).first();mine={nickname:own.nickname,score:own.score,rank:Number(above.total)+1}}}
  return json({stage,rules,competition,date:competition==='daily'?dayKey():null,rows:rows.results,mine});
 }
 if(request.method!=='POST')return json({error:'지원하지 않는 요청입니다.'},405);
 if(!validOrigin(request))return json({error:'허용되지 않는 요청입니다.'},403);
 if(url.pathname==='/api/runs'){
  const input=await body(request),stage=input.stage;if(!Number.isInteger(stage)||stage<1||stage>10)return json({error:'올바른 단계를 선택하세요.'},400);
  const competition=input.mode??'fixed';if(!['fixed','daily'].includes(competition))return json({error:'올바른 기록 모드를 선택하세요.'},400);const rules=rankingRules(competition);
  const player=playerFrom(request)??crypto.randomUUID(),now=Date.now();
  const recent=await db.prepare('SELECT COUNT(*) AS total FROM rank_runs WHERE player=? AND started>?').bind(player,now-60000).first();if(Number(recent.total)>=12)return json({error:'잠시 후 다시 도전해주세요.'},429);
  const id=crypto.randomUUID(),seed=seedFor(rules,stage);
  await db.batch([db.prepare('DELETE FROM rank_runs WHERE started<?').bind(now-86400000),db.prepare('INSERT INTO rank_runs (id,player,stage,seed,rules,started,used) VALUES (?,?,?,?,?,?,0)').bind(id,player,stage,seed,rules,now)]);
  return json({id,seed,stage,rules,mode:competition,date:competition==='daily'?dayKey():null},200,{'Set-Cookie':`${cookieName}=${player}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=31536000`});
 }
 if(url.pathname==='/api/scores'){
  const input=await body(request),player=playerFrom(request);if(!player)return json({error:'도전을 새로 시작해주세요.'},401);
  const nickname=typeof input.nickname==='string'?input.nickname.normalize('NFKC').trim():'';
  if(Array.from(nickname).length<2||Array.from(nickname).length>16||!/^[\p{L}\p{N} _.-]+$/u.test(nickname))return json({error:'닉네임은 한글·영문·숫자 등 2~16자로 입력하세요.'},400);
  if(typeof input.id!=='string'||input.id.length>64)return json({error:'잘못된 도전 기록입니다.'},400);
  const run=await db.prepare('SELECT * FROM rank_runs WHERE id=? AND player=?').bind(input.id,player).first();
  const now=Date.now();if(!run||run.used||![rankingRules('fixed'),rankingRules('daily')].includes(run.rules)||now-run.started>900000)return json({error:'만료되었거나 이미 등록한 기록입니다. 다시 도전해주세요.'},409);
  const {steps,inputs}=input,maxSteps=((run.stage===4||run.stage===10?90:run.stage>=7?75:60)+(run.stage===7||run.stage===10?3:0))*60+1;
  if(!Number.isInteger(steps)||steps<1||steps>maxSteps||!Array.isArray(inputs)||inputs.length>maxSteps||now-run.started<steps/60*1000-1500)return json({error:'플레이 기록을 확인할 수 없습니다.'},400);
  let prev=-1;for(const item of inputs){if(!Array.isArray(item)||item.length!==2||!Number.isInteger(item[0])||item[0]<0||item[0]<=prev||item[0]>=steps||!Number.isInteger(item[1])||item[1]<0||item[1]>63)return json({error:'플레이 입력이 올바르지 않습니다.'},400);prev=item[0]}
  const engine=createVerifier(run.seed,run.stage);let cursor=0,mask=0;
  for(let frame=0;frame<steps;frame++){if(inputs[cursor]?.[0]===frame){mask=inputs[cursor][1];cursor++}engine.step(mask);if(engine.state().mode!=='play'&&frame!==steps-1)return json({error:'완료 이후 입력이 포함되어 있습니다.'},400)}
  const state=engine.state();if(state.mode!=='win')return json({error:'클리어한 기록만 등록할 수 있습니다.'},400);
  const score=Math.round(state.time*100+run.stage*200),remaining=Math.max(0,Math.round(state.time*1000));
  const saved=await db.batch([
   db.prepare('INSERT INTO stage_scores (player,stage,rules,nickname,score,remaining,created) SELECT ?,?,?,?,?,?,? FROM rank_runs WHERE id=? AND player=? AND used=0 ON CONFLICT(player,stage,rules) DO UPDATE SET nickname=excluded.nickname,score=excluded.score,remaining=excluded.remaining,created=excluded.created WHERE excluded.score>stage_scores.score').bind(player,run.stage,run.rules,nickname,score,remaining,now,run.id,player),
   db.prepare('UPDATE rank_runs SET used=1 WHERE id=? AND player=? AND used=0 RETURNING id').bind(run.id,player)
  ]);
  if(!saved[1].results?.length)return json({error:'이미 등록된 기록입니다.'},409);
  return json({ok:true,stage:run.stage,score,competition:run.rules.includes(':daily:')?'daily':'fixed',message:'기록을 확인했습니다. 단계별 개인 최고점이 순위에 반영됩니다.'});
 }
 return json({error:'찾을 수 없는 요청입니다.'},404);
 }catch(error){if(error instanceof SyntaxError)return json({error:'요청 형식이 올바르지 않습니다.'},400);if(error instanceof Error&&error.message==='too_large')return json({error:'플레이 기록이 너무 큽니다.'},413);console.error('ranking request failed',error instanceof Error?error.message:'unknown');return json({error:'순위표 연결에 문제가 있습니다. 잠시 후 다시 시도해주세요.'},500)}
}
