/* Frame clock and shared pieces for "The Fairer Test" scenes.
   A scene is a pure function of time: render(t) sets every element for time t,
   so any frame can be rendered alone and a render is repeatable. Motion values
   follow studio/design-system/README.md ("Motion"). */
(function () {
  'use strict';
  const FT = {};

  function bezier(x1, y1, x2, y2) {
    const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
    const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
    const sx = (t) => ((ax * t + bx) * t + cx) * t;
    const sy = (t) => ((ay * t + by) * t + cy) * t;
    return (x) => {
      if (x <= 0) return 0;
      if (x >= 1) return 1;
      let lo = 0, hi = 1, t = x;
      for (let i = 0; i < 40; i++) {
        if (sx(t) < x) lo = t; else hi = t;
        t = (lo + hi) / 2;
      }
      return sy(t);
    };
  }

  FT.settle = bezier(0.2, 0.8, 0.2, 1);           // the system's one easing curve
  FT.linear = (x) => Math.min(Math.max(x, 0), 1);
  // Progress of an animation that starts at `start` and lasts `dur` seconds, 0..1.
  FT.p = (t, start, dur, ease = FT.settle) => (dur <= 0 ? (t >= start ? 1 : 0) : ease((t - start) / dur));
  FT.lerp = (a, b, p) => a + (b - a) * p;

  // Numbers use a real minus sign; units live in separate labels.
  FT.fmt = (v, digits = 1, sign = false) => {
    let s = Math.abs(v).toFixed(digits);
    if (v < 0 && Number(s) !== 0) s = '−' + s;
    else if (sign && v > 0) s = '+' + s;
    return s;
  };

  FT.value = (key) => {
    const v = window.SCENE_DATA && window.SCENE_DATA.values[key];
    if (v === undefined) throw new Error('Scene value missing from data.js: ' + key);
    return v;
  };
  FT.series = (key) => {
    const v = window.SCENE_DATA && window.SCENE_DATA.series[key];
    if (v === undefined) throw new Error('Scene series missing from data.js: ' + key);
    return v;
  };

  FT.meta = (key) => {
    const v = window.SCENE_DATA && window.SCENE_DATA.meta && window.SCENE_DATA.meta[key];
    if (v === undefined) throw new Error('Scene meta missing from data.js: ' + key);
    return v;
  };

  FT.el = (parent, cls, style, html) => {
    const e = document.createElement('div');
    if (cls) e.className = cls;
    Object.assign(e.style, style || {});
    if (html != null) e.innerHTML = html;
    parent.appendChild(e);
    return e;
  };

  // Fade in and rise; used for kickers (rise 12px) and chart labels.
  FT.rise = (e, t, start, rise = 12, dur = 0.5) => {
    const p = FT.p(t, start, dur);
    e.style.opacity = p;
    e.style.transform = 'translateY(' + (1 - p) * rise + 'px)';
  };
  // Hard cut on (captions, the "BUT" tag).
  FT.cut = (e, t, start) => { e.style.visibility = t >= start ? 'visible' : 'hidden'; };

  FT.kicker = (frame, text, s) =>
    FT.el(frame, 'kicker', { left: s.x + 'px', top: s.y + 'px', fontSize: s.size + 'px', color: s.color || 'var(--player-a-text)' }, text);

  // Claim lines are given explicitly and mask-wipe up 80 ms apart.
  FT.claim = (frame, lines, s) => {
    const box = FT.el(frame, 'claim', { left: s.x + 'px', top: s.y + 'px', fontSize: s.size + 'px',
      lineHeight: String(s.lh || 0.88), color: s.color || 'inherit' });
    const inner = lines.map((html) => {
      const line = FT.el(box, 'line', { paddingBottom: '0.04em' });
      const span = document.createElement('span');
      span.innerHTML = html;
      line.appendChild(span);
      return span;
    });
    box.at = (t, start) => inner.forEach((span, i) => {
      const p = FT.p(t, start + i * 0.08, 0.5);
      span.style.transform = 'translateY(' + (1 - p) * 110 + '%)';
    });
    return box;
  };

  // Source / scope strip: static, on screen whenever the data is.
  FT.source = (frame, rows, s) => {
    const html = rows.map(([k, v]) => '<b>' + k + '</b>&nbsp;&nbsp;' + v).join('<br>');
    return FT.el(frame, 'source', { left: s.x + 'px', width: s.width + 'px', top: s.y + 'px', fontSize: s.size + 'px',
      paddingTop: '14px' }, html);
  };

  FT.grain = (frame) => FT.el(frame, 'grain');

  const SAFE = { landscape: { top: 96, bottom: 96, left: 96, right: 96 },
                 vertical: { top: 220, bottom: 420, left: 72, right: 160 } };

  // Register a scene: formats it supports, background, duration (seconds, or {landscape, vertical}), build and render.
  FT.scene = (def) => {
    const params = new URLSearchParams(location.search);
    const name = params.get('format') || Object.keys(def.formats)[0];
    const format = def.formats[name];
    if (!format) throw new Error('Scene does not support format ' + name);
    const size = name === 'vertical' ? { w: 1080, h: 1920 } : { w: 1920, h: 1080 };
    const frame = document.createElement('div');
    frame.className = 'frame ' + (def.background || 'paper');
    Object.assign(frame.style, { width: size.w + 'px', height: size.h + 'px' });
    document.body.appendChild(frame);
    const ctx = { format: name, w: size.w, h: size.h, safe: SAFE[name] };
    const render = format(frame, ctx);
    FT.grain(frame);
    if (params.get('safe') === '1') {
      const s = SAFE[name];
      FT.el(frame, 'safe', { left: s.left + 'px', top: s.top + 'px', right: s.right + 'px', bottom: s.bottom + 'px' });
    }
    const duration = typeof def.duration === 'object' ? def.duration[name] : def.duration;
    window.__ft = { ready: true, duration, width: size.w, height: size.h, format: name,
                    seek: (t) => { render(t); return true; } };
    render(Number(params.get('t') || duration));
  };

  window.FT = FT;
})();

/* Batch 2 components. Additive API: the original scene clock and primitives
   above are unchanged. All data coordinates use unrounded inputs. */
(function (FT) {
  'use strict';
  const px = n => n + 'px';
  const group = f => FT.el(f, 'ft-component');
  const text = (f, cls, x, y, size, html, extra = {}) => FT.el(f, cls,
    Object.assign({left:px(x), top:px(y), fontSize:px(size)}, extra), html);
  const rule = (f,x,y,w,h=2,color='var(--ink)') => FT.el(f,'', {left:px(x),top:px(y),width:px(w),height:px(h),background:color,transformOrigin:'left'});
  FT.svg = (parent, w=1920,h=1080) => {
    const e = document.createElementNS('http://www.w3.org/2000/svg','svg');
    e.setAttribute('width',w); e.setAttribute('height',h);
    Object.assign(e.style,{position:'absolute',left:0,top:0}); parent.appendChild(e); return e;
  };
  FT.svgEl = (parent, tag, attrs) => {
    const e = document.createElementNS('http://www.w3.org/2000/svg',tag);
    Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v)); parent.appendChild(e); return e;
  };
  const draw = (e,t,start,dur) => { e.style.strokeDasharray='1'; e.style.strokeDashoffset=1-FT.p(t,start,dur); e.style.opacity=t>=start?1:0; };
  FT.cast = (f,names,s={}) => {
    const e = FT.el(f,'ft-cast',{right:px(s.right??96),top:px(s.y??92)},
      names.map((n,i)=>'<span>'+String.fromCharCode(65+i)+' · '+n+'</span>').join(''));
    return t=>{ e.style.opacity=t<0?0:t<=2.6?FT.p(t,0,.4):1-FT.p(t,2.6,.4); };
  };
  FT.pitch = (f,{x=900,y=190,width=1100,night=true}={}) => {
    const e=FT.el(f,'',{left:px(x),top:px(y),width:px(width),height:px(Math.round(width*68/105))});
    e.innerHTML='<svg viewBox="0 0 105 68" width="100%" height="100%" fill="none" stroke="'+(night?'#2A2622':'#C9BCA4')+'" stroke-width="0.35"><rect x="0.5" y="0.5" width="104" height="67"/><line x1="52.5" y1="0.5" x2="52.5" y2="67.5"/><circle cx="52.5" cy="34" r="9.15"/><rect x="0.5" y="13.85" width="16.5" height="40.3"/><rect x="88" y="13.85" width="16.5" height="40.3"/><rect x="0.5" y="24.84" width="5.5" height="18.32"/><rect x="99" y="24.84" width="5.5" height="18.32"/><path d="M17 26.7 A9.15 9.15 0 0 1 17 41.3"/><path d="M88 26.7 A9.15 9.15 0 0 0 88 41.3"/></svg>';
    return e;
  };
  FT.footballTitle = (f,{vertical=false}={}) => {
    const g=group(f), scale=vertical?.65:1, ox=vertical?-720:0, oy=vertical?720:0;
    const pos=(x,y,w)=>({left:px(ox+x*scale),top:px(oy+y*scale),width:px(w*scale),height:px(w*scale)});
    const disc=FT.el(g,'ft-football-disc',pos(1180,180,720));
    const ball=FT.el(g,'',pos(1260,260,560));
    ball.innerHTML='<svg viewBox="0 0 560 560" width="100%" height="100%"><defs><clipPath id="ft-ball-clip"><circle cx="280" cy="280" r="275"/></clipPath></defs><circle cx="280" cy="280" r="275" fill="#F3EBDD"/><g clip-path="url(#ft-ball-clip)" fill="#1C1916" stroke="#1C1916" stroke-width="10" stroke-linejoin="round"><polygon points="280,210 346.6,258.4 321.1,336.6 238.9,336.6 213.4,258.4"/><path d="M280 210 V90 M346.6 258.4 L460.7 221.3 M321.1 336.6 L391.7 433.7 M238.9 336.6 L168.3 433.7 M213.4 258.4 L99.3 221.3" fill="none"/>'+[[280,30,180],[517.8,202.7,252],[426.9,482.3,324],[133.1,482.3,36],[42.2,202.7,108]].map(([x,y,r])=>'<polygon points="0,-60 57,-18.5 35.3,48.5 -35.3,48.5 -57,-18.5" transform="translate('+x+','+y+') rotate('+r+')"/>').join('')+'</g><circle cx="280" cy="280" r="275" fill="none" stroke="#1C1916" stroke-width="10"/></svg>';
    const chip=text(g,'number',ox+1700*scale,oy+700*scale,64*scale,'?',{padding:'8px 18px',background:'var(--paper)',color:'var(--ink)'});
    const stars=[[1170,150,120,'var(--paper)'],[1250,800,84,'var(--paper)'],[1790,210,56,'var(--accent)']].map(([x,y,w,c])=>FT.el(g,'',Object.assign(pos(x,y,w),{color:c}),'<svg viewBox="0 0 100 100" width="100%" height="100%"><path d="M50 0 L55 42 L85 15 L58 45 L100 50 L58 55 L85 85 L55 58 L50 100 L45 58 L15 85 L42 55 L0 50 L42 45 L15 15 L45 42 Z" fill="currentColor"/></svg>'));
    return t=>{const p=FT.p(t,0,.6);disc.style.transform='scale('+FT.lerp(.9,1,p)+')';disc.style.opacity=p;ball.style.transform='rotate('+FT.lerp(-20,0,p)+'deg)';ball.style.opacity=p;FT.cut(chip,t,.5);chip.style.transform='rotate(-4deg)';stars.forEach((s,i)=>{const p=FT.p(t,.6+i*.08,.1,FT.linear);s.style.transform='scale('+p+')';s.style.opacity=p;});};
  };
  // Exact-x swarm: middle observations placed first, so both stay on level 0.
  FT.swarm = (rows,x,central=[],baseY=680) => {
    const placed=[];
    [...rows.filter(p=>central.includes(p.code)),...rows.filter(p=>!central.includes(p.code))].forEach(p=>{
      const X=x(p.rate.value); let level=0;
      while(placed.some(q=>q.level===level&&Math.abs(q.x-X)<24)) level++;
      placed.push({row:p,x:X,y:baseY-level*26,level});
    }); return placed;
  };
  FT.middleGap = (f,o) => {
    const v=!!o.vertical,g=group(f),x0=o.x0??(v?72:160),x1=o.x1??(v?920:1760),lo=o.lo??(v?.1:0),hi=o.hi??(v?.9:1),axisY=o.axisY??(v?1150:700),baseY=axisY-20;
    const x=r=>x0+(r-lo)/(hi-lo)*(x1-x0), sz=v?32:30;
    const axis=rule(g,x0,axisY,x1-x0), svg=FT.svg(g,v?1080:1920,v?1920:1080);
    const ticks=[lo,lo+(hi-lo)/2,hi].map((n,i)=>text(g,'tick',i===0?x0:i===2?x1-110:x(n)-55,axisY+(o.tickOffset??(v?126:16)),v?32:26,FT.fmt(n,2),{width:'110px',textAlign:i===0?'left':i===2?'right':'center'}));
    const unit=text(g,'label',x0,axisY+(o.unitOffset??(v?175:60)),sz,'GOALS PER '+o.norm);
    const dots=FT.swarm(o.rows,x,o.central,baseY).map((p,i)=>{
      const e=FT.el(g,'dot',{left:px(p.x-11),top:px(p.y-11),width:'22px',height:'22px',background:'var(--field)'});
      const central=o.central.includes(p.row.code);
      if(central) e.style.boxShadow='0 0 0 3px var(--ink)';
      return {e,start:central?2+i*.12:1+((i*17)%31)/31*.9};
    });
    const mx=x(o.median), ring=FT.el(g,'ft-median-ring',{left:px(mx-15),top:px(baseY-15),width:'30px',height:'30px'});
    const line=rule(g,mx-2,v?880:452,4,baseY-(v?880:452)-32,'var(--player-a)');
    const median=text(g,'label',mx-170,v?780:360,v?38:30,'MEDIAN '+FT.fmt(o.median,2),{width:'340px',textAlign:'center',color:'var(--player-a-text)'});
    const mint=text(g,'claim chip',mx-90,v?832:406,sz,'NOBODY',{padding:'3px 12px'});
    const names=o.central.map((code,i)=>{
      const p=o.rows.find(p=>p.code===code), X=x(p.rate.value), name=o.names[i];
      const Y=o.nameY??(v?1180:470), tx=i===0?X-(v?310:380):X+14, width=v?300:360;
      const e=text(g,'label ft-named-field',tx,Y,sz,name+'<br>'+FT.fmt(p.rate.value,2),{width:px(width),textAlign:i===0?'right':'left',letterSpacing:'0'});
      const l=FT.svgEl(svg,'line',{x1:X,y1:baseY+15,x2:X,y2:Y-8,stroke:'var(--ink)','stroke-width':2});
      return {e,l};
    });
    const count=text(g,'tick',x1-220,v?720:600,sz,'n = '+o.rows.length,{width:'220px',textAlign:'right'});
    return {element:g,x,render(t){axis.style.transform='scaleX('+FT.p(t,.7,.6)+')';ticks.concat([unit,count]).forEach(e=>FT.rise(e,t,.7,0));dots.forEach(({e,start})=>FT.rise(e,t,start,20,.3));names.forEach(({e,l},i)=>{FT.rise(e,t,2+i*.3,0,.25);l.style.opacity=FT.p(t,2+i*.3,.25);});FT.rise(ring,t,2.3,0,.3);FT.rise(line,t,2.6,0,.25);FT.rise(median,t,2.6,0,.25);mint.style.clipPath='inset(0 '+(1-FT.p(t,2.9,.3))*100+'% 0 0)';}};
  };
  FT.cutoffPanel = (f,o) => {
    const v=!!o.vertical,g=group(f),svg=FT.svg(g,v?1080:1920,v?1920:1080),base=o.base??(v?1240:800);
    const x=m=>(v?200:300)+m/o.maxMinutes*(v?640:1300),y=n=>base-n*(v?50:36),left=v?112:216,right=v?900:1696;
    const axes=[rule(g,left,base,right-left),rule(g,left,v?640:380,2,base-(v?640:380))];
    const belief=FT.svgEl(svg,'line',{x1:left,y1:y(o.belief),x2:right,y2:y(o.belief),stroke:'var(--field-text)','stroke-width':4,'stroke-dasharray':'10 8'});
    const beliefText=text(g,'label',left+16,y(o.belief)-44,v?32:26,o.belief+' GOALS · THE BELIEF',{letterSpacing:0,color:'var(--field-text)'});
    const labels=[text(g,'label',v?72:96,base+16,v?32:30,'MIN ≥',{letterSpacing:0}),text(g,'tick',v?72:96,base+58,v?32:26,'PLAYERS')];
    const zero=text(g,'tick',left-52,base-20,v?32:26,FT.fmt(o.zero,0));
    const points=o.rows.map((r,i)=>{
      const X=x(r.minutes),Y=y(r.median_goals.value);
      const dot=FT.el(g,'dot',{left:px(X-(v?16:14)),top:px(Y-(v?16:14)),width:px(v?32:28),height:px(v?32:28),background:'var(--ink)'});
      const n=text(g,'number',X-64,o.labelBelowBelief&&r.median_goals.value<o.belief?Y+22:Y-80,v?64:56,FT.fmt(r.median_goals.value,0),{width:'128px',textAlign:'center'});
      const min=text(g,'label',X-(v?65:80),base+16,v?32:30,r.minutes.toLocaleString('en-US'),{width:px(v?130:160),textAlign:'center',letterSpacing:0});
      const count=text(g,'tick',X-60,base+58,v?32:26,String(r.n),{width:'120px',textAlign:'center'});
      const segment=i?FT.svgEl(svg,'line',{x1:x(o.rows[i-1].minutes),y1:y(o.rows[i-1].median_goals.value),x2:X,y2:Y,stroke:'var(--ink)','stroke-width':6,pathLength:1}):null;
      return {dot,n,min,count,segment,start:1.2+i*.4+(i===o.rows.length-1?.2:0)};
    });
    const own=o.rows.find(r=>r.minutes===o.ownCut),idx=o.rows.indexOf(own);
    const mint=text(g,'label',x(own.minutes)+32,y(own.median_goals.value)+(o.ownLabelOffset??36),v?38:30,'OUR CUT',{padding:'3px 10px'});
    let mean=[];
    if(o.mean){const X=x(o.mean.minutes),Y=y(o.mean.value);mean=[rule(g,X-16,Y,32,4),text(g,'label',X-200,Y-64,v?32:30,'MEAN '+FT.fmt(o.mean.value,1),{letterSpacing:0})];}
    return {element:g,render(t){axes.forEach(e=>e.style.transform='scaleX('+FT.p(t,.7,.6)+')');belief.style.opacity=FT.p(t,.7,.5);beliefText.style.opacity=FT.p(t,.7,.5);labels.concat([zero]).forEach(e=>FT.rise(e,t,.7,0));points.forEach(({dot,n,min,count,segment,start})=>{FT.rise(dot,t,start,20,.3);FT.cut(n,t,start+.3);FT.cut(min,t,start);FT.cut(count,t,start);if(segment)draw(segment,t,start,.3);});mint.style.clipPath='inset(0 '+(1-FT.p(t,3.4,.3))*100+'% 0 0)';points[idx].n.style.background=t>=3.4?'var(--accent)':'transparent';/* mint is one grouped verdict */mean.forEach(e=>FT.rise(e,t,4.1,0));}};
  };
  FT.seasonsRow = (f,o) => {
    const v=!!o.vertical,g=group(f),svg=FT.svg(g,v?1080:1920,v?1920:1080),x=i=>(v?150:360)+i*(v?120:210),topBase=v?960:490,rateBase=o.rateBase??(v?1380:850);
    const gy=n=>topBase-n*(v?25:18.33),ry=n=>rateBase-n*(v?640:560),left=v?90:300,right=v?906:1680;
    const axes=[rule(g,left,topBase,right-left),rule(g,left,rateBase,right-left)];
    const zeros=[text(g,'tick',v?72:180,topBase-15,v?32:26,FT.fmt(o.zero??0,0)),text(g,'tick',v?72:180,rateBase-15,v?32:26,FT.fmt(o.zero??0,0))];
    const belief=FT.svgEl(svg,'line',{x1:left,y1:gy(o.belief),x2:right,y2:gy(o.belief),stroke:'var(--field-text)','stroke-width':4,'stroke-dasharray':'10 8'});
    const label=text(g,'tick',v?72:1696,gy(o.belief)-(v?50:16),v?32:26,o.belief+' GOALS');
    const topTitle=text(g,'label',v?72:96,v?608:236,v?32:26,'MEDIAN SEASON GOALS',{letterSpacing:0});
    const rateTitle=text(g,'label',v?72:96,v?1006:530,v?32:26,'MEDIAN GOALS PER '+o.norm,{letterSpacing:0});
    const top=[],steps=[],names=[],counts=[],context=[];
    o.rows.forEach((r,i)=>{
      const X=x(i),G=gy(r.median_goals.value),R=ry(r.median_rate.value),half=v?60:105;
      if(i)top.push({e:FT.svgEl(svg,'line',{x1:x(i-1),y1:gy(o.rows[i-1].median_goals.value),x2:X,y2:G,stroke:'var(--ink)','stroke-width':4,pathLength:1}),start:1+i*.12});
      top.push({e:FT.el(g,'dot',{left:px(X-9),top:px(G-9),width:'18px',height:'18px',background:'var(--ink)'}),start:1+i*.12});
      top.push({e:text(g,'number',X-55,o.goalLabelBelow?G+18:G-48,v?32:30,FT.fmt(r.median_goals.value,Number.isInteger(r.median_goals.value)?0:1),{width:'110px',textAlign:'center',letterSpacing:0}),start:1+i*.12});
      const start=2.3+i*.12+(i>=4?.3:0);
      steps.push({e:FT.svgEl(svg,'line',{x1:X-half,y1:R,x2:X+half,y2:R,stroke:'var(--ink)','stroke-width':6,pathLength:1}),start});
      if(i)steps.push({e:FT.svgEl(svg,'line',{x1:X-half,y1:ry(o.rows[i-1].median_rate.value),x2:X-half,y2:R,stroke:'var(--ink)','stroke-width':6,pathLength:1}),start,dur:i===4?.25:.12});
      steps.push({e:text(g,'number',X-55,R-44,v?32:30,FT.fmt(r.median_rate.value,2),{width:'110px',textAlign:'center',letterSpacing:0}),start});
      const year=r.season.split('-').map(s=>s.slice(-2)).join('/');
      names.push(text(g,'tick',X-55,rateBase+12,v?30:26,year,{width:'110px',textAlign:'center'}));
      counts.push(text(g,'tick',X-55,rateBase+46,v?32:26,String(r.n),{width:'110px',textAlign:'center'}));
      context.push(text(g,'tick',X-60,rateBase+82,v?32:24,r.league_goals.toLocaleString('en-US'),{width:'120px',textAlign:'center'}));
    });
    const mint=text(g,'claim chip',v?440:1100,v?1014:(o.mintY??540),v?38:30,'STEP UP · '+o.stepSeason,{padding:'3px 12px'});
    return {element:g,render(t){axes.forEach((e,i)=>e.style.opacity=i?+(t>=2.2):+(t>=.7));names.forEach(e=>FT.cut(e,t,.7));counts.forEach(e=>FT.cut(e,t,1));context.forEach(e=>FT.cut(e,t,o.contextStart??8));FT.cut(topTitle,t,.7);FT.cut(rateTitle,t,2.2);zeros.forEach((e,i)=>FT.cut(e,t,i?2.2:.7));FT.cut(belief,t,.7);FT.cut(label,t,.7);top.forEach(({e,start})=>e.tagName==='line'?draw(e,t,start,.12):FT.rise(e,t,start,0,.12));steps.forEach(({e,start,dur})=>e.tagName==='line'?draw(e,t,start,dur??.12):FT.rise(e,t,start,0,.12));mint.style.clipPath='inset(0 '+(1-FT.p(t,3.6,.3))*100+'% 0 0)';}};
  };
  // Parameterised versions of the original bars / table / arrow grammar.
  FT.bars = (f,rows,{x=96,y=320,width=1728,scale,digits=0,start=1,labelWidth=360,fromRows=null,fromScale=scale}={}) => {
    const g=group(f),parts=rows.map((r,i)=>{
      const Y=y+i*110,barX=x+labelWidth+28;
      const name=text(g,'label',x,Y+20,30,r.name,{width:px(labelWidth),color:r.textColor??'var(--field-text)',fontWeight:600,letterSpacing:0});
      const bar=rule(g,barX,Y,r.value*scale,76,r.color??'var(--field)');
      const val=text(g,'number',barX+r.value*scale+28,Y+16,40,FT.fmt(r.value,digits));
      const oldIndex=fromRows?fromRows.findIndex(p=>p.name===r.name):i;
      const oldWidth=fromRows?fromRows[oldIndex].value*fromScale:0;
      return {name,bar,val,start:start+i*.06,Y,oldY:y+oldIndex*110,oldWidth,width:r.value*scale};
    });return {element:g,render(t){parts.forEach(p=>{FT.rise(p.name,t,p.start,0);const a=FT.p(t,p.start,.5);p.bar.style.width=px(FT.lerp(p.oldWidth,p.width,a));p.bar.style.opacity=+(t>=p.start);const dy=FT.lerp(p.oldY,p.Y,a)-p.Y;p.bar.style.transform='translateY('+dy+'px)';p.name.style.transform='translateY('+dy+'px)';p.val.style.transform='translateY('+dy+'px)';FT.cut(p.val,t,p.start+.5);});}};
  };
  FT.smallTable = (f,headers,rows,s={}) => {
    const e=FT.el(f,'ft-table',{left:px(s.x??96),top:px(s.y??350),width:px(s.width??1728),gridTemplateColumns:s.columns??'1.6fr 1fr 1fr 1fr'});
    headers.forEach((h,i)=>FT.el(e,'ft-th',{textAlign:i?'right':'left'},h));
    rows.forEach(r=>r.forEach((v,i)=>FT.el(e,'ft-td'+(i?'':' ft-name'),{},v)));
    return e;
  };
  FT.beforeAfter = (f,o) => {
    const v=!!o.vertical,g=group(f),size=v?128:240;
    const first=text(g,'number',v?72:96,v?870:430,size,FT.fmt(o.before,o.digits??0),{color:'var(--field-text)'});
    const arrow=text(g,'claim',v?410:740,v?856:452,v?130:180,'→');
    const second=text(g,'number',v?560:1048,v?870:430,size,FT.fmt(o.after,o.digits??0),{color:'var(--player-a)'});
    return {element:g,render(t){FT.rise(first,t,.7,24);FT.rise(arrow,t,1.2,0,.4);FT.rise(second,t,1.5,0);second.textContent=FT.fmt(FT.lerp(o.before,o.after,FT.p(t,1.5,.7)),o.digits??0);}};
  };
})(window.FT);
