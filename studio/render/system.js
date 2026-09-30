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

/* Batch 2 L/M/N/Q and substitute demonstrations. Additions only: defaults
   reproduce the handoff geometry; options adapt the real data/safe areas. */
(function(FT){
'use strict';
const px=n=>n+'px', group=f=>FT.el(f,'ft-component');
const text=(f,cls,x,y,size,html,extra={})=>FT.el(f,cls,Object.assign({left:px(x),top:px(y),fontSize:px(size)},extra),html);
const line=(svg,x1,y1,x2,y2,color='var(--ink)',width=2)=>FT.svgEl(svg,'line',{x1,y1,x2,y2,stroke:color,'stroke-width':width,pathLength:1});
const draw=(e,p)=>{e.style.strokeDasharray='1';e.style.strokeDashoffset=1-p;e.style.opacity=+!!p;};
// L. Event order is retained when the feed codes several goals at the same
// displayed minute. 90+ is a zone, never an invented precise added-time clock.
FT.scoreTimeline=(f,o)=>{
 const v=!!o.vertical,g=group(f);
 const end=o.end,entry=Number(o.match.entry_minute.split("'")[0]);
 const time=m=>v?(o.timeStart??560)+m*(o.timeScale??9.5):216+m*15.93,zero=v?500:700,rate=v?36:40,zone=v?36:56;
 const finish=time(end)+zone,coord=margin=>v?zero+margin*rate:zero-margin*rate;
 const shade=FT.el(g,'',{left:px(v?200:time(entry)),top:px(v?time(entry):230),width:px(v?680:finish-time(entry)),height:px(v?finish-time(entry):570),background:'var(--paper-2)'});
 const svg=FT.svg(g,v?1080:1920,v?1920:1080);
 const axis=v?line(svg,zero,time(0),zero,finish):line(svg,216,zero,finish,zero);
 const band=FT.svgEl(svg,'polygon',{fill:'var(--field)',points:''}),edge=FT.svgEl(svg,'polyline',{fill:'none',stroke:'var(--ink)','stroke-width':3,points:''});
 const entryRule=v?line(svg,200,time(entry),880,time(entry),'var(--ink)',3):line(svg,time(entry),230,time(entry),820,'var(--ink)',3);
 const entryLabel=text(g,'label',v?(o.entryLabelX??210):Math.min(time(entry)+12,1500),v?time(entry)-48:196,v?32:30,'ON '+entry+'′ · '+o.match.score_at_entry.join('–'),{letterSpacing:0});
 const team=o.team,opp=o.opp;
 const legend=text(g,'label',v?72:1064,o.legendY??(v?470:98),v?32:26,'<span style="color:var(--player-a-text)">● '+o.player+'</span> · <span style="color:var(--field-text)">● '+team+' · ○ '+opp+'</span>',{letterSpacing:0,width:px(v?848:760)});
 const titles=v?[]:[text(g,'tick',96,285,26,'GOALS'),text(g,'tick',96,600,26,'AHEAD'),text(g,'tick',96,686,26,'LEVEL'),text(g,'tick',96,770,26,'BEHIND')];
 const ticks=o.ticks.map(m=>text(g,'tick',v?420:time(m)-40,v?time(m)-16:830,v?32:26,m===end?end+'+':m+'′',{width:px(v?70:80),textAlign:'center'}));
 if(v) titles.push(text(g,'tick',570,time(0)-44,32,'AHEAD →'),text(g,'tick',220,time(0)-44,32,'← BEHIND'));
 const counts={},stacks=[],totals={};o.match.goal_timeline.forEach(r=>{const m=Number(r.minute.split("'")[0]);totals[m]=(totals[m]??0)+1;});let previous=[0,0];
 const events=o.match.goal_timeline.map((r,i)=>{
  const m=Number(r.minute.split("'")[0]);let ordinal=counts[m]??0;const sameMinuteOrder=ordinal;counts[m]=ordinal+1;const duplicate=ordinal>0;
  if(o.stackClose){ordinal=0;while(stacks.some(p=>p.level===ordinal&&Math.abs(time(p.m)-time(m))<(v?36:34)))ordinal++;stacks.push({m,level:ordinal});}
  const awayGoal=r.score[1]>previous[1];previous=r.score;
  const size=v?36:34,X=v?(o.goalX??164)-ordinal*40:time(m),Y=v?time(m):300-ordinal*40;
  const dot=FT.el(g,'dot',{left:px(X-size/2),top:px(Y-size/2),width:px(size),height:px(size),boxSizing:'border-box',background:r.scorer_is_player?'var(--player-a)':awayGoal?'var(--field)':'transparent',border:awayGoal?'none':'4px solid var(--field)'});
  dot.dataset.minute=String(m);
  let label=null;
  if(r.scorer_is_player){
   const labelText=m===end?end+'+'+(totals[m]>1?' ×'+totals[m]:''):m+'′';
   if(m!==end||!duplicate)label=text(g,'label',v?(m===end?(o.endLabelX??300):72):time(m)-(m===end?-22:40),v?time(m)-(m===end?(o.endLabelOffset??20):20):(m===end?256:326),v?32:26,labelText,{color:'var(--player-a-text)',letterSpacing:0,width:px(m===end?160:(v?100:100))});
  }
  return {r,m,dot,label,index:i,sameMinuteOrder};
 });
 const ft=text(g,'number',v?800:1722,v?finish-62:coord(o.match.final_score[1]-o.match.final_score[0])-44,v?44:44,o.match.final_score.join('–'));
 const ftTitle=text(g,'tick',v?800:1722,v?finish-100:coord(o.match.final_score[1]-o.match.final_score[0])-90,v?32:26,'FT');
 const playhead=v?line(svg,200,560,880,560,'var(--ink)',2):line(svg,216,230,216,820,'var(--ink)',2);
 const entryAt=.6+entry/(end/3),afterStart=entryAt+.8;
 return {element:g,render(t){
  // Optional narration gates stop at entry, or expose an explicit event count.
  let minute=t<entryAt?Math.max(0,(t-.6)*(end/3)):t<afterStart?entry:Math.min(end,entry+(t-afterStart)*(end/6));
  if(o.phase==='entry')minute=Math.min(entry,minute);
  if(o.maxMinute!=null)minute=Math.min(o.maxMinute,minute);
  let visible=events.filter(e=>e.m<=minute);
  if(o.eventCount!=null)visible=visible.slice(0,o.eventCount);
  const points=[[v?zero:216,v?time(0):zero]];let margin=0;
  visible.forEach(e=>{const T=time(e.m);points.push(v?[coord(margin),T]:[T,coord(margin)]);margin=e.r.score[1]-e.r.score[0];points.push(v?[coord(margin),T]:[T,coord(margin)]);});
  const last=minute>=end&&o.phase!=='entry'?finish:time(minute);
  points.push(v?[coord(margin),last]:[last,coord(margin)]);
  edge.setAttribute('points',points.map(p=>p.join(',')).join(' '));band.setAttribute('points',points.concat([v?[zero,last]:[last,zero]]).map(p=>p.join(',')).join(' '));
  draw(axis,FT.p(t,0,.6));titles.concat(ticks,[legend]).forEach(e=>FT.cut(e,t,.6));
  const entered=minute>=entry;entryRule.style.opacity=entered?FT.p(t,entryAt,.3):0;entryLabel.style.opacity=entered?1:0;shade.style.opacity=entered?FT.p(t,entryAt,.4):0;
  events.forEach(e=>{const on=visible.includes(e);e.dot.style.opacity=on?1:0;e.dot.style.transform='scale('+(on?FT.p(t,.6+e.m/(end/3)+(e.m>=entry?.8+(e.m-entry)/(end/3):0)+(e.m===end?e.sameMinuteOrder*.15:0),.25):0)+')';if(e.label)e.label.style.opacity=on?1:0;});
  const done=minute>=end&&o.phase!=='entry'&&o.showFinal!==false;ft.style.opacity=ftTitle.style.opacity=+done;
  if(v){playhead.setAttribute('y1',time(minute));playhead.setAttribute('y2',time(minute));}else{playhead.setAttribute('x1',time(minute));playhead.setAttribute('x2',time(minute));}playhead.style.opacity=t>0&&t<(o.hidePlayheadAt??Infinity)?1:0;
 }};
};
// M. Names are bound to actual grid cells, never inferred from the row label.
FT.timingScenarioTable=(f,o)=>{
 const v=!!o.vertical,g=group(f),x=v?72:96,y=o.y??(v?620:300),w=v?848:1728;
 const table=FT.el(g,'ft-timing-table'+(v?' ft-timing-vertical':''),{left:px(x),top:px(y),width:px(w),gridTemplateColumns:v?'190px repeat(3,1fr)':'300px repeat(4,1fr)'});
 const s2s=[...new Set(o.cells.map(c=>c.s2))].sort((a,b)=>a-b),pairs=[...new Map(o.cells.map(c=>[c.s1+','+c.rounding,{s1:c.s1,rounding:c.rounding}])).values()].sort((a,b)=>a.s1-b.s1||a.rounding-b.rounding);
 const header=[];
 const h=(html,style={})=>header.push(FT.el(table,'ft-timing-head',Object.assign({borderBottomColor:'transparent'},style),html));
 if(v){h('1ST /<br>ROUND');s2s.forEach(s=>h('2ND<br>+'+s+'′'));}
 else {
  h('2ND-HALF',{borderBottom:'none',paddingBottom:'10px'});
  [...new Set(pairs.map(p=>p.s1))].forEach(n=>h('1ST-HALF STOPPAGE +'+n+'′',{gridColumn:'span 2',borderBottom:'2px solid var(--rule-light)',paddingBottom:'10px'}));
  h('STOPPAGE');pairs.forEach(p=>h('ROUND +'+p.rounding+'′'));
 }
 const headerRule=FT.el(g,'',{left:px(x),top:px(y+108),width:px(w),height:'3px',background:'var(--ink)',transformOrigin:'left'});
 const entries=[];
 const rowHeaders=v?pairs:s2s;
 rowHeaders.forEach((r,ri)=>{
  const label=FT.el(table,'ft-timing-label',{background:!v&&r===Math.max(...s2s)&&o.showLeaders!==false?'var(--paper-2)':'transparent'},v?'+'+r.s1+'′ / +'+r.rounding+'′':'+'+r+'′');
  (v?s2s:pairs).forEach((c,ci)=>{
   const cell=o.cells.find(z=>v?z.s1===r.s1&&z.rounding===r.rounding&&z.s2===c:z.s2===r&&z.s1===c.s1&&z.rounding===c.rounding);
   if(!cell)throw Error('Timing cell missing');
   const role=cell.leader===o.a?'a':'b',e=FT.el(table,'ft-timing-cell ft-role-'+role,{background:cell.s2===Math.max(...s2s)&&o.showLeaders!==false?'var(--paper-2)':'transparent'},'<span class="dot"></span><span>'+o.names[cell.leader]+'</span>');
   e.dataset.key=cell.key;entries.push({e,label,cell,start:1+ri*.25+ci*.06});
  });
 });
 return {element:g,render(t){headerRule.style.transform='scaleX('+FT.p(t,0,.4)+')';header.forEach(e=>e.style.opacity=FT.p(t,0,.4));entries.forEach(({e,label,cell,start})=>{label.style.opacity=+(t>=start);e.style.opacity=o.showLeaders===false?0:+(t>=start);if(o.revealLeader&&cell.leader!==o.revealLeader)e.style.opacity=0;e.style.clipPath='inset(0 '+(cell.s2===Math.max(...s2s)?(1-FT.p(t,o.bandStart??1.8,.3))*100:0)+'% 0 0)';});}};
};
// N. Default panel uses the handoff's 680px / 425px per unit and 56px bar.
// Real-data domains are explicit; no clipping/winsorisation at the axis ends.
FT.resamplingRanges=(f,o)=>{
 const v=!!o.vertical,g=group(f),svg=FT.svg(g,v?1080:1920,v?1920:1080),parts=[];
 o.panels.forEach((p,pi)=>{
  const x=p.x??(v?112:176+pi*888),y=p.y??(v?760+pi*430:490),width=p.width??(v?768:680),lo=p.domain?.[0]??-.4,hi=p.domain?.[1]??1.2,height=v?64:56;
  const X=n=>x+(n-lo)/(hi-lo)*width,base=y+130,start=p.start??pi*2.6;
  const title=text(g,'label',x,y-190,v?38:30,p.title,{width:px(width),letterSpacing:0});
  const axis=line(svg,x,base,x+width,base,'currentColor'),zero=line(svg,X(0),y-50,X(0),base+20,'currentColor',4);
  const bar=FT.el(g,'',{left:px(X(p.observed)),top:px(y),width:0,height:px(height),background:p.color??'var(--player-a)'});
  const dot=FT.el(g,'dot ft-observed-dot',{left:px(X(p.observed)-15),top:px(y+(height-30)/2),width:'30px',height:'30px'});
  const observed=text(g,'label',x,y-110,v?38:30,'OBSERVED '+FT.fmt(p.observed,p.digits??2,true),{width:px(width),letterSpacing:0});
  const ends=[text(g,'tick',X(p.low)-60,y+68,v?32:26,FT.fmt(p.low,p.digits??2),{width:'120px',textAlign:'center'}),text(g,'tick',X(p.high)-60,y+68,v?32:26,FT.fmt(p.high,p.digits??2),{width:'120px',textAlign:'center'})];
  const ticks=(p.ticks??[lo,0,hi]).map(n=>text(g,'tick',X(n)-50,base+16,v?32:26,FT.fmt(n,p.tickDigits??1),{width:'100px',textAlign:'center'}));
  const caption=text(g,'claim ft-range-caption'+(p.low<=0&&p.high>=0?' ft-range-reverse':' chip'),x,base+90,v?38:30,p.low<=0&&p.high>=0?'RESAMPLING CAN REVERSE IT':'SURVIVES RESAMPLING THE GAMES',{padding:'4px 12px'});
  parts.push(t=>{FT.cut(title,t,start);draw(axis,FT.p(t,start,.6));draw(zero,FT.p(t,start,.6));ticks.forEach(e=>FT.cut(e,t,start+.6));FT.rise(dot,t,start+.6,20,.3);FT.cut(observed,t,start+.6);const a=FT.p(t,start+.9,.7);bar.style.left=px(X(FT.lerp(p.observed,p.low,a)));bar.style.width=px((p.high-p.low)*a/(hi-lo)*width);bar.style.opacity=+!!a;ends.forEach(e=>FT.cut(e,t,start+1.6));FT.cut(caption,t,start+2);});
 });return {element:g,render:t=>parts.forEach(r=>r(t))};
};
FT.rateRanges=(f,o)=>{
 const v=!!o.vertical,g=group(f),svg=FT.svg(g,v?1080:1920,v?1920:1080),x=o.x??(v?360:540),width=o.width??(v?450:1100),X=n=>x+n/o.max*width;
 const parts=o.rows.map((r,i)=>{
  const y=(o.y??(v?640:330))+i*(v?145:120),h=v?64:56,start=.7+i*.25;
  const name=text(g,'label',v?72:96,y+12,v?32:30,r.name,{letterSpacing:0,color:r.textColor??'var(--field-text)',fontWeight:600});
  const axis=line(svg,x,y+h+12,x+width,y+h+12,'var(--rule-light)');
  const bar=FT.el(g,'',{left:px(X(r.value)),top:px(y),width:0,height:px(h),background:r.color??'var(--field)'});
  const dot=FT.el(g,'dot ft-observed-dot',{left:px(X(r.value)-15),top:px(y+(h-30)/2),width:'30px',height:'30px'});
  const low=text(g,'tick',X(r.low)-45,y+h+20,v?32:26,FT.fmt(r.low,o.digits),{width:'90px',textAlign:'center'}),high=text(g,'tick',X(r.high)-45,y+h+20,v?32:26,FT.fmt(r.high,o.digits),{width:'90px',textAlign:'center'});
  const observed=text(g,'number',v?72:1696,y,v?44:40,FT.fmt(r.value,o.digits));
  return t=>{FT.cut(name,t,start);draw(axis,FT.p(t,start,.6));FT.rise(dot,t,start+.6,20,.3);FT.cut(observed,t,start+.6);const a=FT.p(t,start+.9,.7);bar.style.left=px(X(FT.lerp(r.value,r.low,a)));bar.style.width=px((r.high-r.low)*a/o.max*width);bar.style.opacity=+!!a;[low,high].forEach(e=>FT.cut(e,t,start+1.6));};
 });return {element:g,render:t=>parts.forEach(r=>r(t))};
};
// Q. Cards keep argument order and have no combined score.
FT.measureCards=(f,o)=>{
 const v=!!o.vertical,g=group(f),gap=v?20:24,width=v?848:(1728-gap*(o.cards.length-1))/o.cards.length;
 const parts=o.cards.map((c,i)=>{
  const e=FT.el(g,'ft-measure-card'+(v?' ft-measure-vertical':''),{left:px(v?72:96+i*(width+gap)),top:px(v?(o.y??580)+i*240:(o.y??300)),width:px(width),height:px(v?220:560)});
  const content=FT.el(e,'ft-measure-content',{},'<div class="ft-measure-index">'+c.index+'</div><div class="ft-measure-name">'+c.name+'</div><div class="ft-measure-value">'+c.value+'</div><div class="ft-measure-unit">'+c.unit+'</div><div class="ft-measure-leader">'+c.leader+'</div>');
  const stamp=FT.el(e,'ft-measure-stamp',{color:c.mint?'var(--ink)':c.color??'var(--field)',background:c.mint?'var(--accent)':'transparent',borderColor:c.mint?'var(--accent)':c.color??'var(--field)'},c.stamp);
  const start=c.start??.7+i*.15;
  return t=>{e.style.clipPath='inset(0 '+(1-FT.p(t,start,.3))*100+'% 0 0)';FT.cut(content,t,c.contentStart??start+.3);const p=FT.p(t,c.stampStart??start+1,.25),s=FT.p(t,(c.stampStart??start+1)+.25,.15);stamp.style.opacity=p;stamp.style.transform='rotate('+FT.lerp(-6,-3,s)+'deg) scale('+p+')';};
 });return {element:g,render:t=>parts.forEach(r=>r(t))};
};
FT.appearanceClocks=(f,o)=>{
 const v=!!o.vertical,g=group(f),svg=FT.svg(g,v?1080:1920,v?1920:1080);
 const parts=[o.half,o.late].map((label,i)=>{
  const x=v?496:510+i*850,y=v?660+i*420:470,r=v?125:140;
  const circle=FT.svgEl(svg,'circle',{cx:x,cy:y,r,fill:'none',stroke:'var(--ink)','stroke-width':3});
  const hand=line(svg,x,y,x+(i?r*.7:0),y+(i?-r*.7:r*.85),'var(--player-a)',10);
  const name=text(g,'label',x-300,y-r-65,v?38:30,label,{width:'600px',textAlign:'center',letterSpacing:0});
  const equals=text(g,'claim',x-300,y+r+22,v?80:72,'= '+o.one+' APPEARANCE',{width:'600px',textAlign:'center'});
  return t=>{FT.cut(circle,t,.7+i*.6);FT.cut(name,t,.7+i*.6);draw(hand,FT.p(t,.7+i*.6,.6));FT.cut(equals,t,1.3+i*.6);};
 });return {element:g,render:t=>parts.forEach(r=>r(t))};
};
})(window.FT);
