// Provenance, arbitrary seeks and semantics; actual browser audit via --browser.
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const dir=dirname(fileURLToPath(import.meta.url));
const cues=JSON.parse(readFileSync(resolve(dir,'CUES.json')));
class Element {
 constructor(tag='div'){this.tagName=tag;this.style={setProperty(k,v){this[k]=v;}};this.children=[];this.dataset={};this.attributes={};this._html='';this.className='';this.classList={add:n=>this.className+=' '+n};}
 set innerHTML(v){this._html=String(v);this.children=[];if(this._html.startsWith('<span'))this.children.push(new Element('span'));}
 get innerHTML(){return this._html;}
 get firstChild(){return this.children[0];}
 appendChild(e){this.children.push(e);return e;}
 setAttribute(k,v){this.attributes[k]=String(v);}
 querySelector(q){return this.querySelectorAll(q)[0]??null;}
 querySelectorAll(q){const cls=q.slice(1);return this.children.flatMap(c=>(c.className.split(' ').includes(cls)?[c]:[]).concat(c.querySelectorAll(q)));}
}
function snapshot(e){return {tag:e.tagName,cls:e.className,style:e.style,html:e.innerHTML,attrs:e.attributes,dataset:e.dataset,children:e.children.map(snapshot)};}
let total=0,labels=0;const claims=JSON.parse(readFileSync(resolve(dir,'../CLAIMS.json'))).claims;
const results=JSON.parse(readFileSync(resolve(dir,'../analysis/results.json')));
const hash=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const dataContext=vm.createContext({window:{}});vm.runInContext(readFileSync(resolve(dir,'data.js'),'utf8'),dataContext);const data=dataContext.window.SCENE_DATA;
assert.equal(data.results_sha256,hash(resolve(dir,'../analysis/results.json')));
assert.equal(data.claims_sha256,hash(resolve(dir,'../CLAIMS.json')));
for(const [key,ids] of Object.entries(data.claim_ids))for(const id of ids)assert(claims.some(c=>c.id===id&&c.status==='proposed'),'Missing proposed claim '+key);
assert(results.primary.R_geometric_person_year.interval_95[1]<results.verdict.threshold);
assert(results.DNF_secondary.odds_ratio_per_005_h.interval_95[0]<1&&results.DNF_secondary.odds_ratio_per_005_h.interval_95[1]>1);
const story=readFileSync(resolve(dir,'../STORY.md'),'utf8');
for(const [page,info] of Object.entries(cues.scenes)){
 const document={body:new Element('body'),createElement:t=>new Element(t),createElementNS:(ns,t)=>new Element(t)};
 const context=vm.createContext({document,window:{},location:{search:'?format='+info.format},URLSearchParams,console});
 for(const script of ['../../../render/system.js','data.js','episode.js']){vm.runInContext(readFileSync(resolve(dir,script),'utf8'),context,{filename:script});if(script==='../../../render/system.js')context.FT=context.window.FT;if(script==='episode.js')context.SL=context.window.SL;}
 vm.runInContext(readFileSync(resolve(dir,page),'utf8').match(/<script>\s*([\s\S]*?)<\/script>/)[1],context,{filename:page});
 const clock=context.window.__ft;assert(clock?.ready);assert.equal(clock.width,info.format==='vertical'?1080:1920);
 assert.throws(()=>context.FT.value('missing-test-key'),/Scene value missing/);
 assert.throws(()=>context.SL.num('source_notice'),/Unclaimed numeric value/);
 for(const s of info.states){
  assert(story.includes(s.cue),'Cue is not exact narration: '+s.cue);
  clock.seek(s.still);const first=JSON.stringify(snapshot(document.body));clock.seek(0);clock.seek(s.still);assert.equal(first,JSON.stringify(snapshot(document.body)),page+' '+s.id+' seek not pure');
  assert.equal(context.window.__slState,s.id);
  const active=document.body.querySelectorAll('.sl-state').find(e=>e.dataset.state===s.id);
  if(s.phase==='exclude')active.querySelectorAll('.sl-matrix-cell').filter(e=>e.dataset.focal==='true').forEach(e=>assert.equal(e.style.opacity,.16));
  if(s.component==='gate'&&['failed','amend'].includes(s.phase)){active.querySelectorAll('.ft-measure-card').forEach((e,i)=>assert.equal(e.style.display,i<(s.phase==='failed'?1:2)?'block':'none'));}
  const source=active.querySelector('.source');assert(source,'Persistent scope required');
  const html=first;assert(!/luck\s*(?:=|is)\s*2%/i.test(html));
  labels+=(html.match(/data-value-key/g)??[]).length;
  total++;
 }
 console.log(page+': '+info.states.length+' states passed');
}
assert.equal(total,67);
const built=JSON.parse(execFileSync('python3',['-B','-c',`import importlib.util,json; s=importlib.util.spec_from_file_location('bindings',${JSON.stringify(resolve(dir,'build_data.py'))}); m=importlib.util.module_from_spec(s);s.loader.exec_module(m);print(json.dumps(m.payload()))`]).toString());
assert.deepEqual(JSON.parse(JSON.stringify(data)),built);
const browser=existsSync(resolve(dir,'browser_qa.json'))?JSON.parse(readFileSync(resolve(dir,'browser_qa.json'))):{checks:[]};
const displayed=[...new Set(browser.checks.flatMap(c=>c.labels.map(x=>x.key)))];
let precisionChecks=0;
for(const key of displayed){for(const claim of claims){for(const item of claim.values??[]){if(item.key!==key||item.digits==null||typeof item.stated!=='number')continue;assert.equal(Number(data.values[key].toFixed(item.digits)),Number(item.stated.toFixed(item.digits)),claim.id+' stated precision '+key);precisionChecks++;}}}
console.log('Displayed value precision checks: '+precisionChecks);
console.log('PASS: '+total+' cue states; hashes, regeneration, numerical provenance, semantics and seek purity.');
if(process.argv.includes('--browser'))execFileSync('python3',['-B',resolve(dir,'render_stills.py'),'--audit-only'],{stdio:'inherit'});
