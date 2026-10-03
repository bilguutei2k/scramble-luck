/* Proposed scenes. Measurements use claim-bound result keys; geometry is schematic. */
(function(FT){
'use strict';
const SL=window.SL={},V=FT.value,F=FT.fmt;
const R='primary.R_geometric_person_year',FV='primary.F_tier_aware';
const T=(g,cls,x,y,size,html,extra={})=>FT.el(g,cls,Object.assign({left:x+'px',top:y+'px',fontSize:size+'px'},extra),html);
const rule=(g,x,y,w,h=2,color='var(--ink)')=>FT.el(g,'',{left:x+'px',top:y+'px',width:w+'px',height:h+'px',background:color,transformOrigin:'left'});
SL.num=(key,{digits=0,percent=false,integer=false}={})=>{
 const claims=window.SCENE_DATA.claim_ids[key];if(!claims?.length)throw Error('Unclaimed numeric value: '+key);
 const val=V(key)*(percent?100:1),text=integer?Math.round(val).toLocaleString('en-US'):F(val,digits);
 return '<span class="sl-value" data-value-key="'+key+'" data-claims="'+claims.join(' ')+'">'+text+'</span>';
};
const n=(g,v,key,unit,{x=v?72:96,y=v?610:370,size=v?220:260,digits=0,percent=false,integer=false,color='var(--player-a)'}={})=>{
 const value=T(g,'number',x,y,size,SL.num(key,{digits,percent,integer}),{color});
 const u=T(g,'label',x,y+size+50,v?32:30,unit,{width:(v?848:1728)+'px'});
 const animate=t=>{FT.rise(value,t,.7,12,.5);FT.cut(u,t,1.2);};(g._numberAnimations??=[]).push(animate);return animate;
};
const cap=(g,v,text,y=v?1100:760,size=v?44:44)=>T(g,'caption',v?72:96,y,size,text,{width:(v?848:1728)+'px'});
const link=(url,title)=>'<a href="'+url+'">'+title+'</a>';
const urls={wired:'https://www.wired.com/video/watch/almost-impossible-why-solving-a-rubik-s-cube-in-under-3-seconds-is-almost-impossible',du:'https://ruwix.com/blog/yusheng-du-record-347/',park:'https://ruwix.com/blog/max-park-rubik-single-record-313/',reco:'https://reco.nz/solve/9155',glossary:'https://www.cubeskills.com/tools/glossary',wca:'https://www.worldcubeassociation.org/regulations/history/official/2025-07-17/#9f8',replacement:'https://www.worldcubeassociation.org/regulations/history/official/2025-07-17/#11e1'};
SL.header=(g,v,kicker,lines,{night=false,size=v?100:106}={})=>{
 const k=FT.kicker(g,kicker+' · PROPOSED',{x:v?72:96,y:v?220:96,size:v?32:30,color:night?'var(--paper)':'var(--player-a-text)'});
 const h=FT.claim(g,lines,{x:v?72:96,y:v?285:156,size,color:night?'var(--paper)':'var(--ink)'});h.style.width=(v?848:1728)+'px';
 return t=>{FT.rise(k,t,0);h.at(t,.2);};
};
SL.scope=(g,v,{claims='SL-C001 · SL-C144',source='WCA frozen results · method + review',note='Successful season bests · equal-person-year geometric R',kind='study'}={})=>{
 const years=SL.num('derived.first_year')+'–'+SL.num('derived.last_year');
 let rows;
 if(v){
  const scope=kind==='record'?['Published historical reconstruction','Illustrative · no record attribution']:kind==='slot'?['One-group finals · '+years,'Scheduled positions · no assignment audit']:['One-group average-of-five finals',years+' · at least five finals / season'];
  rows=[['SCOPE',scope[0]],['',scope[1]],['',kind==='record'?'Seasonal study · shared comparison':kind==='slot'?'Successful times · failures separate':'Successful times · shared scramble/slot'],['SOURCE',source],['',claims],['STATUS','PRE-LOCK DRAFT · CLAIMS PROPOSED']];
 }else rows=[['SOURCE',source],['SCOPE','One-group average-of-five finals · '+years+' · successful times'],['METHOD',note+' · '+claims]];
 return FT.source(g,rows,{x:v?72:96,y:v?1218:854,width:v?848:1728,size:v?32:24});
};
SL.cards=(g,v,cards,{y=v?610:340,height=430}={})=>{
 const chart=FT.measureCards(g,{vertical:v,y,cards:cards.map((c,i)=>({index:c.id??'METHOD',name:c.name,value:c.value??'',unit:c.unit??'',leader:c.leader??'',stamp:c.stamp??'',color:c.color??'var(--field)',start:.7+i*.15,contentStart:.7+i*.15,stampStart:1.4+i*.15}))});
 chart.element.querySelectorAll('.ft-measure-card').forEach((e,i)=>{e.style.height=(v?180:height)+'px';if(v)e.style.top=(y+i*200)+'px';if(cards[i].id)e.dataset.claims=cards[i].id;if(!cards[i].stamp)e.querySelector('.ft-measure-stamp').style.display='none';});
 return t=>chart.render(t);
};
SL.register=def=>FT.scene({duration:def.duration,background:def.background??'paper',formats:{[def.vertical?'vertical':'landscape']:(f)=>{
 const v=!!def.vertical;if(v)f.classList.add('sl-portrait');
 FT.el(f,'caption',{opacity:0,fontSize:'44px'},'Prime all local caption fonts');
 const states=def.states.map(s=>{const g=FT.el(f,'sl-state');g.dataset.state=s.id;return {...s,g,render:SL[s.component](g,v,s.phase)};});
 return t=>{let index=0;states.forEach((s,i)=>{if(t>=s.at)index=i;});states.forEach((s,i)=>{s.g.style.display=i===index?'block':'none';const local=window.__narratedAssembly?60:Math.max(0,t-s.at);s.render(local);(s.g._numberAnimations??[]).forEach(r=>r(local));});const grain=f.querySelector('.grain');if(v&&grain)grain.style.setProperty('--grain-shift',(Math.floor(t*30/2)%149)+'px');window.__slState=states[index].id;};
}}});
SL.open=(g,v,phase)=>{
 const head=SL.header(g,v,'The belief',phase==='question'?['Shared by the field?']:['A lucky scramble?'],{night:true});
 if(phase==='hook'){
  T(g,'claim',96,365,150,'A TIMER STOPS.<br>A RECORD FALLS.',{lineHeight:'.95',color:'var(--paper)'});cap(g,false,'An appealing explanation: a lucky scramble.',736);SL.scope(g,false,{claims:'SL-C104 · SL-C146',source:link(urls.du,'Ruwix Du article')+' · '+link(urls.wired,'WIRED video/transcript'),note:'Historical records · publication context'});return t=>head(t);
 }
 if(phase==='wired'||phase==='ruwix'){
  const wired=phase==='wired';
  T(g,'label',96,354,30,wired?'WIRED · VIDEO + TRANSCRIPT':'RUWIX · HISTORICAL DU COVERAGE',{color:'var(--field)'});
  cap(g,false,wired?'“The fact is, sometimes you just<br>get a lucky scramble.”':'“Lucky scramble? Maybe.”',440,68);
  cap(g,false,wired?'Publication attribution; context in the linked transcript.':'The article also credited skill.',692,44);
 }else if(phase==='record'){
  if(window.SCENE_DATA.values['context.du.seconds']!==undefined)n(g,false,'context.du.seconds','SECONDS · YUSHENG DU · THEN-WORLD-RECORD',{y:340,size:280,digits:2});
  else{T(g,'claim',96,390,140,'YUSHENG DU',{color:'var(--player-a)'});cap(g,false,'A then-world-record single.',570);}
  cap(g,false,'A historical illustration; not a record attribution.',730);
 }else{
  const c=SL.cards(g,false,[{id:'SL-C148',name:'This solution',unit:'A shortcut in one route',stamp:'Reconstruction'},{id:'SL-C148',name:'Shared by the field?',unit:'Peers also beat their own pace?',stamp:'Comparison needed'}]);
  SL.scope(g,false,{claims:'SL-C104 · SL-C146 · SL-C148',source:link(urls.du,'Ruwix Du article')+' · '+link(urls.wired,'WIRED video/transcript'),note:'Historical illustration ≠ aggregate attribution'});return t=>{head(t);c(t);};
 }
 SL.scope(g,false,{claims:phase==='record'?'SL-C104':'SL-C146',source:link(urls.du,'Ruwix Du article')+' · '+link(urls.wired,'WIRED video/transcript'),note:'Exact publication excerpts · dates in linked originals; not solve dates'});return t=>head(t);
};
SL.stages=(g,v,phase)=>{
 const park=phase.startsWith('park'),skip=phase==='park-skip'||phase==='park-align';
 const head=SL.header(g,v,park?'The reconstruction':'The basics',park?[phase==='park-align'?'Alignment still remains':skip?'A PLL skip in this route':'Replay the chosen route']:['What is being skipped?']);
 if(phase==='scramble'){
  const c=SL.cards(g,false,[{id:'SL-C135 · SL-C147',name:'Scramble',unit:'Move sequence → starting state',stamp:'Random generation'},{id:'SL-C135',name:'Human difficulty',unit:'Random ≠ equally difficult',stamp:'Separate question'}]);SL.scope(g,false,{claims:'SL-C135 · SL-C147',source:link(urls.glossary,'CubeSkills glossary')+' · WCA regulations',note:'Definition · no fabricated observations'});return t=>{head(t);c(t);};
 }
 if(phase==='pll'){
  const c=SL.cards(g,false,[{id:'SL-C147',name:'PLL skip',unit:'Relative positions already correct',stamp:'No permutation algorithm'},{id:'SL-C147',name:'Top-face alignment',unit:'An adjustment may remain',stamp:'Not whole-layer skip'}]);SL.scope(g,false,{claims:'SL-C147',source:link(urls.glossary,'CubeSkills glossary'),note:'Orientation precedes permutation · final alignment may remain'});return t=>{head(t);c(t);};
 }
 if(phase==='cross'){
  const svg=FT.svg(g);const ox=600,oy=360,s=82;
  for(let row=0;row<3;row++)for(let col=0;col<3;col++)FT.svgEl(svg,'rect',{x:ox+col*s,y:oy+row*s,width:s-5,height:s-5,fill:(row===1||col===1)?'var(--player-a)':'var(--paper-2)',stroke:'var(--ink)','stroke-width':3});
  ['A','B','C','D'].forEach((letter,i)=>{for(let j=0;j<2;j++){const xx=1030+i*185+j*65;FT.svgEl(svg,'rect',{x:xx,y:660,width:56,height:56,fill:'var(--paper-2)',stroke:'var(--ink)','stroke-width':2});T(g,'label',xx+18,671,28,letter);}});
  T(g,'label',1030,385,32,'EDGES + CENTER');T(g,'caption',1030,448,44,'Corners remain<br>unsolved.',{width:'690px'});T(g,'label',1030,594,30,'SIDE STICKER / MATCHING CENTER');T(g,'label',96,710,30,'DEFINITION SCHEMATIC · NOT A SOLVE');
 }else if(phase==='average'){
  const count=V('derived.scheduled_positions'),width=300;
  const labels=['FASTEST','MIDDLE','MIDDLE','MIDDLE','SLOWEST'];
  labels.forEach((s,i)=>{const x=96+i*348;rule(g,x,380,width,230,'transparent').style.border='3px solid var(--ink)';T(g,'claim',x+24,422,52,s);if(i===0||i===count-1)rule(g,x+15,493,width-30,6,'var(--player-a)');});
  cap(g,false,'Discard the extremes. Average the middle.',694);T(g,'label',96,772,26,'FORMAT SCHEMATIC · THIS STUDY USES SINGLES');
 }else{
  const names=park?['DOUBLE EXTENDED CROSS','F2L','OLL','PLL']:['CROSS','F2L','OLL','PLL'];
  const units=park?['Cross + additional pairs','Finish first two layers','Orientation still used',skip?'Permutation algorithm skipped':'Check permutation stage']:['Edge pieces + center','First two layers','Orient last layer','Permute last layer'];
  if(v){
   const c=SL.cards(g,true,[{id:'SL-C138',name:'PLL skip',unit:'No permutation algorithm'},{id:'SL-C138',name:'Top alignment',unit:'Final face adjustment remains'}],{y:750});
   if(window.__narratedAssembly){
    [['skip',780,'PERMUTATION?','REPLAY THE CHOSEN ROUTE'],['align',980,'FINAL ALIGNMENT?','CHECK THE REMAINING MOVE']].forEach(([id,y,title,note])=>{const q=FT.el(g,'sl-pending-'+id,{inset:'0'});T(q,'claim',104,y,48,title,{width:'780px',position:'absolute'});T(q,'label',104,y+70,32,note,{width:'780px',position:'absolute'});});
   }
   if(window.SCENE_DATA.values['context.park.seconds']===undefined)T(g,'label',72,570,32,'MAX PARK · THEN-WORLD-RECORD');
   if(window.SCENE_DATA.values['context.park.seconds']!==undefined)n(g,true,'context.park.seconds','SECONDS · MAX PARK · THEN-RECORD',{y:535,size:140,digits:2});
   SL.scope(g,true,{kind:'record',claims:'SL-C105 · SL-C138',source:link(urls.park,'Ruwix reconstruction')});return t=>{head(t);c(t);};
  }
  const c=SL.cards(g,false,names.map((name,i)=>({id:park?'SL-C138 · SL-C147':'SL-C147',name,unit:units[i],stamp:skip&&i===3?'PLL SKIP':'',color:i===3&&skip?'var(--player-a)':'var(--field)'})),{height:365});
  if(park&&window.SCENE_DATA.values['context.park.seconds']===undefined)T(g,'label',96,740,30,'MAX PARK · THEN-WORLD-RECORD');
  if(park&&window.SCENE_DATA.values['context.park.seconds']!==undefined)T(g,'label',96,740,30,SL.num('context.park.seconds',{digits:2})+' SECONDS · MAX PARK · THEN-WORLD-RECORD');
  if(phase==='park-align')T(g,'claim',1040,738,52,'FINAL TOP ALIGNMENT',{color:'var(--player-a-text)'});
  SL.scope(g,false,{claims:park?'SL-C105 · SL-C138 · SL-C147':'SL-C147',source:link(park?urls.park:urls.glossary,park?'Ruwix reconstruction':'CubeSkills glossary')+(park?' · '+link(urls.reco,'reco.nz published moves'):''),note:park?'No stage durations · not a whole-last-layer skip':'CFOP definitions · no stage durations'});return t=>{head(t);c(t);};
 }
 SL.scope(g,false,{claims:phase==='average'?'SL-C130':'SL-C147',source:link(phase==='average'?urls.wca:urls.glossary,phase==='average'?'WCA average-of-five rule':'CubeSkills glossary'),note:'Teaching schematic · no invented times'});return t=>head(t);
};
SL.paths=(g,v,phase)=>{
 const head=SL.header(g,v,'The flaw',phase==='execution'?['Opportunity and execution']:['A skip belongs to a route']);
 const c=SL.cards(g,v,[{id:'SL-C148',name:'This solution',unit:phase==='execution'?'Recognize → execute':'Chosen path → skip',stamp:'One route'},{id:'SL-C148',name:'Shared by the field?',unit:phase==='execution'?'Not measured separately here':'Other paths → other opportunities',stamp:'Comparison needed'}],{y:v?630:350,height:370});
 if(!v){cap(g,false,phase==='execution'?'Peers must be compared with their own pace.':'Different routes from the same starting state.',758);rule(g,959,350,3,370);}
 SL.scope(g,v,{claims:'SL-C148',kind:v?'record':'study',source:'Registered method · SCHEMATIC',note:'SCHEMATIC · paths have no fabricated times'});return t=>{head(t);c(t);};
};
SL.population=(g,v,phase)=>{
 const head=SL.header(g,false,'The population',phase==='seasons'?['The seasonal comparison']:phase==='split'?['Hold confirmation apart']:['Which finals count?']);
 let content=()=>{};
 if(phase==='eligibility')content=SL.cards(g,false,[{id:'SL-C003 · SL-C133',name:'One-group finals',unit:'Common scheduled scrambles in this sample',stamp:'Scope matters'},{id:'SL-C148',name:'Seasonal eligibility',unit:'At least five eligible finals',stamp:'Successful singles'}]);
 if(phase==='finals')content=n(g,false,'coverage.census_measurements.eligible_finals.estimate','ELIGIBLE FINALS',{integer:true});
 if(phase==='slots')content=n(g,false,'coverage.census_measurements.included_attempt_slots.estimate','SCHEDULED ATTEMPT SLOTS',{integer:true,size:225});
 if(phase==='seasons'){content=n(g,false,'coverage.census_measurements.available_extrema.estimate','AVAILABLE SOLVER-SEASONS',{integer:true});cap(g,false,'At least five eligible finals per solver-season.',740);}
 if(phase==='split'){
  const c=SL.cards(g,false,[{id:'SL-C004',name:'Idea-stage pilot',unit:'Exploration competitions',stamp:'Separate sample'},{id:'SL-C004',name:'Confirmation',unit:'Locked competition hash split',stamp:'Held out'}]);content=c;cap(g,false,'Split label ≠ fraction surviving all filters.',780);
 }
 SL.scope(g,false,{claims:phase==='split'?'SL-C004':'SL-C002 · SL-C003 · SL-C133',note:'One-group shared schedule · five-final seasonal eligibility'});return t=>{head(t);content(t);};
};
// Five-column matrix: categorical teaching marks, never synthetic observations.
SL.matrix=(g,v,phase)=>{
 const replacement=phase==='replacement',centered=phase==='center'||phase==='columns'||phase==='exclude'||phase==='noise';
 const contrasted=['columns','exclude','noise'].includes(phase),excluded=phase==='exclude'||phase==='noise',head=SL.header(g,v,'The peer comparison',replacement?['Scheduled ≠ actual']:excluded?['Remove the entire focal row']:phase==='columns'?['Read down each column']:centered?['Compare peers with themselves']:['Listen to the peers'],{size:v?92:100});
 const x=v?72:96,y=v?660:350,labelW=v?205:360,colW=v?128:250,rowH=v?80:76,count=V('derived.scheduled_positions');
 const letters=['A','B','C','D','E'],rows=['FOCAL','PEER A','PEER B','PEER C'];
 T(g,'label',x,y-54,v?32:28,contrasted?'ILLUSTRATIVE · PEER-MEASURED CONTRAST':'SCHEMATIC · SCHEDULED POSITIONS');
 letters.slice(0,count).forEach((s,i)=>T(g,'label',x+labelW+i*colW,y,v?32:30,s,{width:colW+'px',textAlign:'center'}));
 const cells=[];rows.forEach((name,r)=>{
  const yy=y+52+r*rowH,focal=r===0;T(g,'label',x,yy+20,v?28:30,name,{color:focal?'var(--player-a-text)':'var(--field-text)'});
  rule(g,x,yy+rowH-2,labelW+count*colW,2,'var(--rule-light)');
  for(let c=0;c<count;c++){
   const xx=x+labelW+c*colW,cell=FT.el(g,'sl-matrix-cell',{left:(xx+10)+'px',top:(yy+8)+'px',width:(colW-20)+'px',height:(rowH-18)+'px',background:focal?'var(--player-a)':contrasted?(c===1?'var(--paper)':c===3?'var(--field)':'color-mix(in srgb, var(--paper) 60%, var(--field) 40%)'):'var(--paper-2)'});cell.dataset.focal=String(focal);if(contrasted&&!focal)cell.dataset.contrast='illustrative';cells.push({cell,r,c});
   T(cell,'label',0,10,v?32:36,replacement&&r===2&&c===3?'○':centered?(c===1?'↓':c===3?'↑':'—'):'•',{width:'100%',textAlign:'center',color:focal||contrasted?'var(--ink)':'var(--field-text)'});
   if(replacement&&r===2&&c===3){cell.style.background='transparent';cell.style.border='3px dashed var(--ink)';cell.dataset.replacement='illustrative';}
  }
 });
 if(excluded){rule(g,x,y+90,labelW+count*colW,6,'var(--ink)');if(phase==='exclude')T(g,'label',x,y+52+rows.length*rowH+22,v?32:30,'FOCAL ROW EXCLUDED · NOT JUST ITS BEST CELL');}
 if(phase==='columns'){T(g,'label',x,y+52+rows.length*rowH+20,28,'ILLUSTRATIVE');letters.slice(0,count).forEach((letter,i)=>T(g,'label',x+labelW+i*colW,y+52+rows.length*rowH+20,26,i===1?'↓ FAVORABLE':i===3?'↑ UNFAVORABLE':'—',{width:colW+'px',textAlign:'center'}));}
 if(phase==='noise')T(g,'label',96,730,30,'FINITE-PEER NOISE CORRECTED · UNCERTAINTY RETAINED');
 if(centered&&!v)cap(g,false,'Shared scramble/slot component · finite-peer noise corrected.',786,40);
 if(replacement)T(g,'label',x,y+52+rows.length*rowH+24,v?32:30,'○ ILLUSTRATIVE REPLACEMENT · DIFFERENT SCRAMBLE',{width:(v?848:1728)+'px'});
 SL.scope(g,v,{claims:replacement?'SL-C134 · SL-C148':'SL-C148',kind:replacement?'slot':v?'record':'study',source:replacement?link(urls.replacement,'WCA replacement rule'):'Registered method · SCHEMATIC',note:'Focal solver excluded · own-final centering · no displayed times'});
 return t=>{head(t);cells.forEach(({cell,r,c})=>{FT.rise(cell,t,.8+c*.05+r*.08,0,.4);if(excluded&&r===0)cell.style.opacity=.16;});};
};
SL.adjust=(g,v,phase)=>{
 const head=SL.header(g,false,'The seasonal best',phase==='measures'?['Two questions. Two measures.']:phase==='weight'?['Equal weight per solver-season']:['Keep the observed best selected']);
 if(phase==='measures'){
  const c=SL.cards(g,false,[{id:'SL-C148',name:'F · variance share',unit:'Successful log-time variation',stamp:'Not seconds'},{id:'SL-C148',name:'R · time ratio',unit:'Adjusted / observed seasonal best',stamp:'Not total luck'}]);SL.scope(g,false,{claims:'SL-C002 · SL-C148',note:'Neither measure separates personal luck from execution'});return t=>{head(t);c(t);};
 }
 const left=T(g,'claim',96,365,76,'OBSERVED BEST',{width:'700px'}),arrow=T(g,'claim',820,414,140,'→'),right=T(g,'claim',1060,365,76,phase==='select'?'KEEP THIS<br>ATTEMPT SELECTED':'ESTIMATED<br>ADJUSTED TIME',{width:'750px',color:'var(--player-a-text)'});
 T(g,'label',96,594,30,phase==='select'?'FASTEST SUCCESSFUL FINAL SOLVE OF THE SEASON':phase==='weight'?'R = GEOMETRIC MEAN OF ADJUSTED / OBSERVED':'REMOVE THE ESTIMATED SHARED CONTRAST');
 cap(g,false,phase==='select'?'Do not reselect the fastest adjusted solve.':phase==='weight'?'Each available solver-season contributes equally.':'A favorable shared contrast makes the estimate longer.',720);
 SL.scope(g,false,{claims:'SL-C002 · SL-C148',note:'Estimated shared-scramble-adjusted time · not a causal replay'});return t=>{head(t);FT.rise(left,t,.7,0);FT.rise(arrow,t,1.1,0);FT.rise(right,t,1.4,0);};
};
SL.gate=(g,v,phase)=>{
 if(phase==='setup'){const head=SL.header(g,false,'Honest uncertainty',['Validate the uncertainty']);const c=SL.cards(g,false,[{id:'SL-C148',name:'Simulation gate',unit:'Recover known truths in simulations',stamp:'Before confirmation'},{id:'SL-C148',name:'Uncertainty procedure',unit:'Check the method before the verdict',stamp:'Specified processes'}]);SL.scope(g,false,{claims:'SL-C148',note:'Simulation validation precedes use of confirmation results'});return t=>{head(t);c(t);};}
 const head=SL.header(g,false,'Honest uncertainty',phase==='fixed'?['A separate sensitivity']:['The original gate failed']);
 const cards=phase==='fixed'?[{id:'SL-C025',name:'Fixed selection',unit:'Reported as a sensitivity',stamp:'No verdict authority'},{id:'SL-C024 · SL-C148',name:'Primary interval',unit:'Reselect bests in resampling',stamp:'Amended procedure'}]:[{id:'SL-C148',name:'Original gate',unit:'Did not recover specified truths',stamp:'Failed',color:'var(--player-a)'},{id:'SL-C148',name:'Amendment registered',unit:'Owner-approved before confirmation times',stamp:'Revised gate'},{id:'SL-C024 · SL-C148',name:'Confirmation',unit:'Specified simulation checks passed',stamp:'Amended contract'}];
 const c=SL.cards(g,false,cards,{height:395});const show=phase==='failed'?1:phase==='amend'?2:cards.length;const nodes=g.querySelectorAll('.ft-measure-card');nodes.forEach((e,i)=>e.style.display=i<show?'block':'none');
 if(phase==='passed')cap(g,false,'Reselect bests. Center bootstrap differences on the estimate.',782,38);
 SL.scope(g,false,{claims:'SL-C024 · SL-C025 · SL-C148',source:'METHOD amendment · analysis review',note:'Specified simulations only · no exact first-access timestamp'});return t=>{head(t);c(t);};
};
// N grammar with an explicit nonzero reference; real coordinates, separate label lanes.
SL.ratio=(g,v,phase)=>{
 const lineOnly=phase==='line',pointOnly=phase==='point',verdict=phase==='verdict',plain=phase==='plain'||verdict,head=SL.header(g,v,'The decision scale',verdict?['The shared adjustment']:lineOnly?['The registered line']:['The shared adjustment']);
 const key=R,lo=V('derived.neutral_ratio'),reference=V('verdict.threshold'),hi=reference+(reference-lo)*.12;
 const x0=v?100:216,w=v?780:1450,y=v?1025:590,h=v?54:56,X=n=>x0+(n-lo)/(hi-lo)*w;
 const axis=rule(g,x0,y+125,w),ref=rule(g,X(reference),y-88,4,230);ref.classList.add('sl-reference');
 T(g,'label sl-reference',v?72:1370,v?(plain?950:885):455,v?32:28,'REGISTERED LINE '+SL.num('verdict.threshold',{digits:2}),{width:(v?848:450)+'px'});
 T(g,'tick',x0,y+144,v?32:26,SL.num('derived.neutral_ratio',{digits:2}));
 const bar=rule(g,X(V(key+'.estimate')),y,0,h,'var(--player-a)'),dot=FT.el(g,'dot ft-observed-dot',{left:(X(V(key+'.estimate'))-17)+'px',top:(y+h/2-17)+'px',width:'34px',height:'34px'});
 bar.classList.add('sl-interval');dot.classList.add('sl-point');
 const elements=[];
 if(!lineOnly){
  elements.push(T(g,'number sl-primary',v?72:96,v?550:350,plain?(v?104:110):130,plain?'ABOUT '+SL.num('derived.adjustment_percent',{integer:true})+'%'+(v?'<br>':' ')+'LONGER':SL.num(key+'.estimate',{digits:4}),{color:'var(--player-a)',width:(v?848:1728)+'px'}));
  elements.push(T(g,'label',v?72:96,v?(plain?795:708):505,v?32:30,(plain?'R = '+SL.num(key+'.estimate',{digits:4})+' · ':'R · ')+'ADJUSTED / OBSERVED'));
  if(!pointOnly)elements.push(T(g,'label',v?72:780,v?(plain?847:775):(plain?490:375),v?32:28,'LOW '+SL.num(key+'.interval_95[0]',{digits:4})+' · HIGH '+SL.num(key+'.interval_95[1]',{digits:4}),{width:(v?848:1044)+'px'}));
  if(!pointOnly)elements.push(T(g,'label',v?72:780,v?(plain?899:838):(plain?540:438),v?32:28,'AMENDED '+SL.num('derived.confidence')+'% INTERVAL',{width:(v?848:1044)+'px'}));
 }
 if(verdict){
  const mint=T(g,'claim chip',v?620:96,v?1155:775,v?40:54,'BELIEF FAILS',{padding:'5px 14px'});elements.push(mint);
 }else if(!v)cap(g,false,lineOnly?'Estimated adjusted time '+SL.num('derived.threshold_percent',{integer:true})+'% longer.':pointOnly?'Point estimate · amended interval follows.':plain?'Equal-person-year seasonal adjustment · estimated, not a replay.':'The whole amended interval sits below the line.',778,40);
 SL.scope(g,v,{claims:'SL-C001 · SL-C144',note:'Amended confirmatory interval · registered decision rule'});
 return t=>{head(t);axis.style.transform='scaleX('+FT.p(t,.7,.6)+')';FT.rise(ref,t,.7,0);const a=lineOnly||pointOnly?0:FT.p(t,1,.7),low=V(key+'.interval_95[0]'),high=V(key+'.interval_95[1]');bar.style.left=X(FT.lerp(V(key+'.estimate'),low,a))+'px';bar.style.width=((high-low)*a/(hi-lo)*w)+'px';bar.style.opacity=a;dot.style.opacity=lineOnly?0:FT.p(t,.7,.3);elements.forEach(e=>FT.rise(e,t,.7,0));};
};
SL.checks=(g,v,phase)=>{
 const head=SL.header(g,false,'The checks',phase==='F'?['A detectable shared component']:phase==='coverage'?['Coverage matters']:phase==='robust'?['Checks stay below the line']:phase==='matched'?['Compare the same subset']:['Geometry offers a diagnostic']);
 if(phase==='F'){
  n(g,false,FV+'.estimate','% OF SUCCESSFUL LOG-TIME VARIANCE',{percent:true,digits:4,size:220});
  T(g,'label',96,690,30,'INTERVAL '+SL.num(FV+'.interval_95[0]',{percent:true,digits:4})+'–'+SL.num(FV+'.interval_95[1]',{percent:true,digits:4})+'%');cap(g,false,'Balanced tiers. Not a percentage of seconds.',742);
 }else if(phase==='coverage'){
  const c=SL.cards(g,false,[{id:'SL-C005',name:'Tier-supported finals',value:SL.num(FV+'.n.tier_supported_finals',{integer:true}),unit:'FINALS'},{id:'SL-C005',name:'Successful cells',value:SL.num(FV+'.n.successful_cells',{integer:true}),unit:'SUCCESSFUL TIMES'},{id:'SL-C015',name:'Unsupported finals',value:SL.num('coverage.census_measurements.tier_subset_excluded_finals.estimate',{integer:true}),unit:'EXCLUDED FROM TIER COMPARISON'}]);SL.scope(g,false,{claims:'SL-C005 · SL-C015 · SL-C145',note:'Tier support restricts coverage'});return t=>{head(t);c(t);};
 }else  if(phase==='cross'){
  const c=SL.cards(g,false,[{id:'SL-C077',name:'Optimal cross length',unit:'Positive link with shared contrast',stamp:'UNVALIDATED DIAGNOSTIC',color:'var(--ink)'},{id:'SL-C148',name:'Shared slot conditions',unit:'Geometry does not isolate the slot',stamp:'Confound remains'}]);SL.scope(g,false,{claims:'SL-C077 · SL-C148',note:'No calibrated cross interval claim · no endpoints shown'});return t=>{head(t);c(t);};
 }else{
  const matched=phase==='matched',rows=matched?[
   ['ALL PEERS','aggregation_and_tier_sensitivities.all_peer_R_on_equal_tier_subset','SL-C051'],['EQUAL TIERS','aggregation_and_tier_sensitivities.equal_tier_R','SL-C053']
  ]:[['COMPLETE SUCCESS','robustness.complete_success.R_geometric_person_year','SL-C036'],['CLIPPED CONTRASTS','robustness.clipped_centered_logs.R_geometric_person_year','SL-C035']];
  const x=620,w=900,lo=V('derived.neutral_ratio'),ref=V('verdict.threshold'),X=n=>x+(n-lo)/(ref-lo)*w;
  rows.forEach(([name,key,id],i)=>{const yy=380+i*178;T(g,'label',96,yy,30,name);T(g,'number',96,yy+48,44,SL.num(key+'.estimate',{digits:4}));rule(g,x,yy+100,w,2,'var(--rule-light)');rule(g,X(V(key+'.interval_95[0]')),yy+40,(V(key+'.interval_95[1]')-V(key+'.interval_95[0]'))/(ref-lo)*w,44,'var(--field)');FT.el(g,'dot ft-observed-dot',{left:(X(V(key+'.estimate'))-15)+'px',top:(yy+47)+'px',width:'30px',height:'30px'});T(g,'tick',620,yy-2,26,SL.num(key+'.interval_95[0]',{digits:4})+'–'+SL.num(key+'.interval_95[1]',{digits:4}));});
  rule(g,X(ref),340,4,350);T(g,'label',1400,714,26,'LINE '+SL.num('verdict.threshold',{digits:2}));
  cap(g,false,matched?'Matched n = '+SL.num('aggregation_and_tier_sensitivities.equal_tier_R.n.person_years',{integer:true})+' · omitted '+SL.num('aggregation_and_tier_sensitivities.equal_tier_attrition.estimate',{integer:true})+' seasonal bests.':'Individual-solver deletions also stay below the decision line.',766,40);
 }
 SL.scope(g,false,{claims:phase==='F'?'SL-C005 · SL-C145':phase==='matched'?'SL-C051 · SL-C053':'SL-C035 · SL-C036 · SL-C050',note:phase==='F'?'F = variance share · successful log times':'Translated sensitivity intervals descriptive · no new verdict'});return t=>head(t);
};
SL.limits=(g,v,phase)=>{
 if(phase==='replacement')return SL.matrix(g,v,'replacement');
 const head=SL.header(g,v,'What remains unknown',phase==='dnf'?['Failures are a separate endpoint']:phase==='personal'?['Personal luck remains unknown']:phase==='success'?['Successful times. Separate failures.']:['The slot travels with the scramble'],{size:v?94:100});
 if(phase==='dnf'){
  const key='DNF_secondary.odds_ratio_per_005_h',lo=.94,hi=1.1,x=520,w=1150,y=545,X=n=>x+(n-lo)/(hi-lo)*w;
  T(g,'number',96,358,120,SL.num(key+'.estimate',{digits:4}));T(g,'label',96,510,30,'DNF ODDS RATIO');T(g,'label',520,385,30,'INTERVAL '+SL.num(key+'.interval_95[0]',{digits:4})+'–'+SL.num(key+'.interval_95[1]',{digits:4}));
  rule(g,x,y+80,w);rule(g,X(V('derived.neutral_ratio')),y-32,4,135);rule(g,X(V(key+'.interval_95[0]')),y,(V(key+'.interval_95[1]')-V(key+'.interval_95[0]'))/(hi-lo)*w,56,'var(--field)');FT.el(g,'dot ft-observed-dot',{left:(X(V(key+'.estimate'))-15)+'px',top:(y+13)+'px',width:'30px',height:'30px'});
  T(g,'tick',X(V('derived.neutral_ratio'))-80,y+106,26,'NO ASSOCIATION '+SL.num('derived.neutral_ratio',{digits:2}));
  T(g,'label',96,690,26,SL.num(key+'.n.identified_solver_rounds',{integer:true})+' IDENTIFIED ROWS · '+SL.num(key+'.n.discordant_solver_rounds',{integer:true})+' DISCORDANT');
  cap(g,false,'The interval includes no association.',760);SL.scope(g,false,{claims:'SL-C074 · SL-C075',note:'Per '+SL.num('derived.dnf_h_increment',{digits:2})+' higher h · success conditioning may understate shared difficulty'});return t=>head(t);
 }
 if(phase==='success'){
  const c=SL.cards(g,v,[{id:'SL-C148',name:'Successful times',unit:'Primary F and R use successes',stamp:'Conditioned sample'},{id:'SL-C148',name:'Failures',unit:'Separate endpoint · no invented time',stamp:'DNF is not a duration'}],{y:v?620:355,height:390});SL.scope(g,v,{claims:'SL-C148',kind:v?'slot':'study',source:'Registered method · success conditioning',note:'No universal bound on missing failure times'});return t=>{head(t);c(t);};
 }
 const cards=phase==='personal'?[{id:'SL-C148',name:'Remaining variation',unit:'Execution, opportunities, penalties, errors',stamp:'Not assigned to luck'},{id:'SL-C148',name:'Personal luck',unit:'Cannot separate it from execution',stamp:'Unidentified'}]:[{id:'SL-C148',name:'Scramble geometry',unit:'Scheduled position is observed',stamp:'Shared comparison'},{id:'SL-C148',name:'Slot conditions',unit:'Warm-up, nerves, changing conditions',stamp:'Cannot isolate'}];
 const c=SL.cards(g,v,cards,{y:v?620:355,height:390});
 if(!v)cap(g,false,phase==='personal'?'A PLL skip does not reveal the whole field’s advantage.':'Shared scramble/slot component',778,42);
 SL.scope(g,v,{claims:'SL-C148',kind:v?'slot':'study',source:'Registered method · limitations',note:'Success-only estimate · no actual-assignment audit'});return t=>{head(t);c(t);};
};
SL.takeaway=(g,v,phase)=>{
 const head=SL.header(g,v,'The takeaway',phase==='record'?['This cannot settle one record']:phase==='notice'?['Inspect the evidence']:phase==='verdict'?['Belief fails']:['About '+SL.num('derived.adjustment_percent',{integer:true})+'% longer'],{night:!v,size:v?100:112});
 if(phase==='adjustment'){
  const value=n(g,v,'derived.adjustment_percent','% LONGER · ESTIMATED ADJUSTED TIME',{digits:0,y:v?620:360,size:v?240:280});
  cap(g,v,'Shared scramble/slot component',v?1020:730,44);SL.scope(g,v,{claims:'SL-C001 · SL-C144',source:'WCA results · amended method',note:'Equal-person-year average · not a record’s total luck'});return t=>{head(t);value(t);};
 }
 if(phase==='verdict'){
  T(g,'claim sl-value',v?72:96,v?620:360,v?68:84, '<span data-value-key="verdict.permitted_claim" data-claims="SL-C001">'+V('verdict.permitted_claim')+'</span>',{width:(v?848:1728)+'px',lineHeight:'.98',color:v?'var(--ink)':'var(--accent)'});
  cap(g,v,'A particular record’s luck remains unresolved.',v?1040:705,v?44:44);
 }else if(phase==='record'){
  T(g,'claim',96,375,104,'WHOSE SHORTCUT?',{color:'var(--player-a)'});cap(g,false,'What comparison would measure it?',570);
 }else{
  T(g,'label',96,350,30,link('../METHOD.md','METHOD + AMENDMENT')+' · '+link('../analysis/FINDINGS.md','FINDINGS')+' · '+link('../analysis/review.md','REVIEW'));
  T(g,'caption',96,448,44,'Sources and all the checks<br>are linked with the video.',{width:'1728px'});
  const notice=V('source_notice');T(g,'source',96,718,24,'<span data-source-key="source_notice">'+notice+'</span>',{width:'1728px',paddingTop:'18px'});
 }
 SL.scope(g,v,{claims:'SL-C001 · SL-C144 · SL-C148',source:v?'WCA results · amended method':'WCA results · method · sources · review',note:'Eligible successful seasonal bests · claims proposed'});return t=>head(t);
};
SL.shortA=(g,v,phase)=>{
 const head=SL.header(g,true,'Shared seasonal adjustment',phase==='hook'?['How much help','was shared?']:['One record’s luck','remains unresolved']);
 const c=SL.cards(g,true,phase==='hook'?[{id:'SL-C148',name:'Season-best final solves',unit:'Shared scramble/slot component'},{id:'SL-C148',name:'The narrower question',unit:'Estimated adjusted / observed time'}]:[{id:'SL-C148',name:'Slot conditions are bundled',unit:'Cannot isolate scramble geometry'},{id:'SL-C148',name:'Personal luck + execution',unit:'Cannot separate them here'}],{y:620});
 SL.scope(g,true,{claims:'SL-C001 · SL-C144 · SL-C148',source:'WCA results · amended method'});return t=>{head(t);c(t);};
};
SL.shortB=(g,v)=>{
 const head=SL.header(g,true,'Route versus shared pattern',['Whose shortcut?']);
 const c=SL.cards(g,true,[{id:'SL-C148',name:'Reconstruction',unit:'Explains a chosen route'},{id:'SL-C148',name:'Peer comparison',unit:'Measures a shared pattern'},{id:'SL-C148',name:'Personal luck',unit:'Not separable from execution'}],{y:580});
 SL.scope(g,true,{kind:'record',claims:'SL-C138 · SL-C148',source:link(urls.park,'Ruwix reconstruction')});return t=>{head(t);c(t);};
};
SL.shortC=(g,v,phase)=>{
 const head=SL.header(g,true,'The naming limit',phase==='component'?['Shared scramble/slot','component']:['Successes and failures','are separate']);
 const c=SL.cards(g,true,phase==='component'?[{id:'SL-C148',name:'Scramble + slot conditions',unit:'Both can enter the shared estimate'},{id:'SL-C148',name:'Scheduled position',unit:'Cannot isolate geometry'}]:[{id:'SL-C148',name:'Successful times',unit:'Primary F and R'},{id:'SL-C148',name:'Failures',unit:'Separate endpoint · no invented time'},{id:'SL-C148',name:'A particular record',unit:'Its total luck is unresolved'}],{y:580});
 SL.scope(g,true,{kind:'slot',claims:'SL-C134 · SL-C148',source:'WCA results · registered method'});return t=>{head(t);c(t);};
};
})(window.FT);
