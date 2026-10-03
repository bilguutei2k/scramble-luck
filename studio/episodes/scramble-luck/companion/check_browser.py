"""Chromium interaction/geometry QA through the agent-browser CLI.

Launch agent-browser with a disposable socket directory first; then run this.
Writes captures and the machine-readable audit into renders/companion.
"""
import json
import os
import subprocess
from pathlib import Path

EP = Path(__file__).resolve().parent.parent
OUT = EP / "renders/companion"
ENV = dict(os.environ, NPM_CONFIG_CACHE="/private/tmp/scramble-companion-npm",
           AGENT_BROWSER_SOCKET_DIR="/private/tmp/scramble-companion-browser")
CLI = ["npx", "--yes", "agent-browser", "--namespace", "scramble-companion"]


def run(*args, code=None):
    p = subprocess.run(CLI + list(args), env=ENV, input=code, text=True, capture_output=True, check=True)
    if "--json" in args:
        result = json.loads(p.stdout)
        if not result["success"]:
            raise RuntimeError(result)
        return result["data"].get("result", result["data"])
    return p.stdout.strip()


SWEEP = r"""(async()=>{
await document.fonts.ready;
const d=JSON.parse(document.getElementById('episode-data').textContent),select=document.getElementById('version');
const checks=[];const f=n=>n.toFixed(4),ci=r=>r.interval.map(f).join('–');
for(const v of d.variants){select.value=v.id;select.dispatchEvent(new Event('change',{bubbles:true}));
 const details=document.querySelector('details');details.open=true;
 const expectedPoint=v.kind==='range'?[Math.min(...v.rows.map(r=>r.estimate)),Math.max(...v.rows.map(r=>r.estimate))].map(f).join('–'):f(v.rows[0].estimate);
 const points=[...document.querySelectorAll('#marks .dot')];
 const scale=n=>32+(n-1)/(d.threshold+(d.threshold-1)*.08-1)*636;
 const geometries=v.rows.every((r,i)=>Math.abs(Number(points[i].getAttribute('cx'))-scale(r.estimate))<1e-9);
 const overflow=[...document.querySelectorAll('.shell *')].filter(e=>{const s=getComputedStyle(e),b=e.getBoundingClientRect();return s.display!=='none'&&b.width>0&&(b.left < -1||b.right>innerWidth+1)}).map(e=>e.tagName+'#'+e.id);
 const replacement=v.kind==='replacement';
 const style=getComputedStyle(select),canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');ctx.font=style.fontWeight+' '+style.fontSize+' '+style.fontFamily;
 const optionWidth=ctx.measureText(select.selectedOptions[0].textContent).width,availableWidth=select.clientWidth-parseFloat(style.paddingLeft)-parseFloat(style.paddingRight);
 const optionFits=optionWidth<=availableWidth;
 const ok=document.getElementById('point').textContent===expectedPoint && (v.kind==='range'||document.getElementById('interval').textContent===ci(v.rows[0])) && optionFits && points.length===v.rows.length && geometries && overflow.length===0 && document.documentElement.scrollWidth===innerWidth && document.querySelector('.verdict').textContent==='Belief fails' && document.getElementById('selection-label').textContent===v.label && v.label.endsWith(v.id==='registered'?'decides the verdict':'cannot change the verdict') && document.getElementById('replacement').hidden!==replacement && (!replacement||document.getElementById('replacement').textContent.includes((v.replacement.estimate*100).toFixed(4)+'%'));
 checks.push({id:v.id,passed:ok,point:expectedPoint,plottedPoints:points.length,optionFits,optionWidth,availableWidth,overflow});details.open=false;
}
select.value='registered';select.dispatchEvent(new Event('change',{bubbles:true}));
const bounds=document.querySelector('.shell').getBoundingClientRect();
return {width:innerWidth,theme:document.documentElement.dataset.theme,height:document.documentElement.scrollHeight,gutter:bounds.left,checks,networkResources:performance.getEntriesByType('resource').filter(x=>/^https?:/.test(x.name)).length,fontChecks:{headline:document.fonts.check('900 68px "Big Shoulders Display"'),mono:document.fonts.check('600 32px "IBM Plex Mono"'),serif:document.fonts.check('500 18px "Source Serif 4"')},passed:checks.every(c=>c.passed)};
})()"""


def main():
    reports = []
    run("reload")
    for width, height in ((390, 844), (1440, 1000)):
        run("set", "viewport", str(width), str(height))
        for theme in ("paper", "night"):
            run("eval", "--stdin", "--json", code=f"document.documentElement.dataset.theme!=='{theme}' && document.getElementById('theme').click()")
            audit = run("eval", "--stdin", "--json", code=SWEEP)
            reports.append(audit)
            run("eval", "window.scrollTo(0,0)")
            run("screenshot", str(OUT / f"{width}-{theme}.png"), "--full")
            if width == 390:
                run("screenshot", str(OUT / f"{width}-{theme}-top.png"))
            run("scrollintoview", "#test-title")
            run("screenshot", str(OUT / f"{width}-{theme}-control.png"))
        run("select", "#version", "years")
        run("scrollintoview", "#readout")
        run("screenshot", str(OUT / f"{width}-night-years.png"))
        run("select", "#version", "p_0.20")
        run("scrollintoview", "#readout")
        run("screenshot", str(OUT / f"{width}-night-replacement.png"))
    error_log = run("errors")
    console_log = run("console")
    (OUT / "browser-audit.json").write_text(json.dumps({"engine": "headless Chromium", "reports": reports,
        "errors": error_log, "console": console_log}, indent=2) + "\n")
    total = sum(len(r["checks"]) for r in reports)
    passed = all(r["passed"] and not r["networkResources"] and all(r["fontChecks"].values()) for r in reports)
    print(f"Chromium: {total} selection/theme/viewport states; {'PASS' if passed else 'FAIL'}; audit and screenshots saved.")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
