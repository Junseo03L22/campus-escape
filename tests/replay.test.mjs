import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';import {createVerifier} from '../server/verifier.js';import {seedFor,rankingRules,dayKey} from '../server/rankings.ts';
const fixtures=JSON.parse(readFileSync(new URL('./fixtures/fixed-ten.json',import.meta.url),'utf8'));
for(const fixture of fixtures){assert.equal(fixture.seed,seedFor(rankingRules('fixed'),fixture.stage));const game=createVerifier(fixture.seed,fixture.stage);let cursor=0,mask=0;for(let i=0;i<fixture.steps;i++){if(fixture.inputs[cursor]?.[0]===i)mask=fixture.inputs[cursor++][1];game.step(mask)}assert.equal(game.state().mode,'win','fixed stage '+fixture.stage+' can be completed with real movement');}
assert.equal(dayKey(Date.UTC(2026,9,27,14,59,59)),'2026-10-27');assert.equal(dayKey(Date.UTC(2026,9,27,15,0,0)),'2026-10-28');
console.log('PASS actual input replays complete fixed stages 7–10; Korean midnight rotates the daily challenge');
