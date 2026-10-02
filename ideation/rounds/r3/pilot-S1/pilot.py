#!/usr/bin/env python3
"""Reproduce S1 from the immutable WCA snapshot. All outcomes are slice-only.

Run from the repository workspace with .venv/bin/python rounds/r3/pilot-S1/pilot.py
Subcommands: prepare, analyze, report, all (default).
"""
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/s1-matplotlib')
import argparse, hashlib, json, urllib.request, zipfile
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DATA = ROOT / 'data/S1'
RAW = DATA / 'raw'
URL = 'https://exports.worldcubeassociation.org/results/WCA_export_v2_273_20260930T000036Z.tsv.zip'
SEED = 20261001
RULE = 'Competitions whose int(sha256(competition_id).hexdigest(),16) % 5 == 0 (a 20% hashed sample of all WCA competitions, every year). The other 80% are confirmatory and must not be used for outcome analysis. Within the slice, use 3x3 rounds where attempts can be mapped to scrambles (single scramble group, five attempts); also report how much of the confirmatory data meets that condition (outcome-blind count).'

def in_slice(competition_id):
    return int(hashlib.sha256(competition_id.encode('utf-8')).hexdigest(), 16) % 5 == 0

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(2**20), b''): h.update(b)
    return h.hexdigest()

def dump(name, x):
    (OUT / name).write_text(json.dumps(x, indent=2, ensure_ascii=False, default=lambda o: o.item() if hasattr(o, 'item') else str(o))+'\n')

def progress(s):
    with (OUT/'PILOT.md').open('a') as f: f.write('\n'+s+'\n')
    print(s[:650], flush=True)

def con():
    c = duckdb.connect(str(DATA/'coverage.duckdb'))
    c.execute("SET threads=8; SET memory_limit='12GB'")
    return c

def tsv(name):
    p = RAW/f'WCA_export_{name}.tsv'
    return f"read_csv('{p}', delim='\t', header=true, all_varchar=true, quote='', escape='', nullstr='', strict_mode=true)"

def prepare():
    DATA.mkdir(parents=True, exist_ok=True); RAW.mkdir(exist_ok=True)
    archive = DATA/URL.rsplit('/',1)[-1]
    if not archive.exists():
        urllib.request.urlretrieve(URL, archive.with_suffix('.part'))
        archive.with_suffix('.part').rename(archive)
    with zipfile.ZipFile(archive) as z:
        for n in ['competitions','results','result_attempts','scrambles','round_types']:
            f = f'WCA_export_{n}.tsv'
            if not (RAW/f).exists(): z.extract(f, RAW)
        for f in ['README.md','metadata.json']:
            if not (RAW/f).exists(): z.extract(f, RAW)
    dump('source-manifest.json', {'url':URL, 'files':[{'path':str(p.relative_to(ROOT)), 'bytes':p.stat().st_size, 'sha256':sha(p)} for p in [archive,*sorted(RAW.iterdir())]], 'metadata':json.loads((RAW/'metadata.json').read_text())})
    c = con()
    c.execute(f"CREATE OR REPLACE TABLE comps AS SELECT id, year::INT AS year_value, month::INT AS month_value, day::INT AS day_value, cancelled FROM {tsv('competitions')}")
    ids = [r[0] for r in c.execute('SELECT id FROM comps ORDER BY id').fetchall()]
    selected = [i for i in ids if in_slice(i)]
    p = OUT/'exploration-competition-ids.txt'
    p.write_text(''.join(i+'\n' for i in selected), encoding='utf-8')
    split = pd.DataFrame({'id':ids, 'explore':[in_slice(i) for i in ids]})
    c.register('split',split)
    c.execute('CREATE OR REPLACE TABLE membership AS SELECT * FROM split')
    assert len(ids)==len(set(ids))
    # No result times, average, best, rank or record flags are selected here.
    c.execute(f"CREATE OR REPLACE TABLE r AS SELECT id::BIGINT result_id, competition_id, round_type_id, person_id, format_id FROM {tsv('results')} WHERE event_id='333'")
    c.execute(f"CREATE OR REPLACE TABLE rt AS SELECT id round_type_id, final='1' is_final FROM {tsv('round_types')}")
    c.execute(f"CREATE OR REPLACE TABLE s AS SELECT id scramble_id, competition_id, round_type_id, group_id, is_extra='1' extra, scramble_num::INT attempt_number, scramble FROM {tsv('scrambles')} WHERE event_id='333'")
    c.execute('''CREATE OR REPLACE TABLE round_map AS
        SELECT competition_id, round_type_id,
        count(*) FILTER (WHERE NOT extra) regular_rows,
        count(DISTINCT group_id) FILTER (WHERE NOT extra) n_groups,
        count(DISTINCT attempt_number) FILTER (WHERE NOT extra) regular_numbers,
        min(attempt_number) FILTER (WHERE NOT extra) min_num,
        max(attempt_number) FILTER (WHERE NOT extra) max_num,
        count(*) FILTER (WHERE extra) extra_pool_rows,
        count(*) FILTER (WHERE NOT extra AND (group_id IS NULL OR scramble IS NULL)) missing
        FROM s GROUP BY ALL''')
    # Outcome-blind presence check: deliberately project no value field.
    c.execute(f'''CREATE OR REPLACE TABLE attempt_shape AS
        SELECT a.result_id::BIGINT result_id, count(*) n, count(DISTINCT a.attempt_number) nd,
        min(a.attempt_number::INT) lo, max(a.attempt_number::INT) hi
        FROM (SELECT result_id, attempt_number FROM {tsv('result_attempts')}) a
        JOIN r ON a.result_id::BIGINT=r.result_id GROUP BY a.result_id''')
    c.execute('''CREATE OR REPLACE TABLE eligible AS
        SELECT r.*, cp.year_value AS year, cp.month_value AS month, cp.day_value AS day, m.explore, rt.is_final, rm.extra_pool_rows
        FROM r JOIN comps cp ON r.competition_id=cp.id
        JOIN membership m ON m.id=r.competition_id
        JOIN rt USING(round_type_id) JOIN round_map rm USING(competition_id,round_type_id)
        JOIN attempt_shape a USING(result_id)
        WHERE r.format_id='a' AND a.n=5 AND a.nd=5 AND a.lo=1 AND a.hi=5
        AND rm.n_groups=1 AND rm.regular_rows=5 AND rm.regular_numbers=5
        AND rm.min_num=1 AND rm.max_num=5 AND rm.missing=0''')
    def records(q): return c.execute(q).fetchdf().to_dict('records')
    coverage = {
        'competitions_total':len(ids), 'competitions_exploration':len(selected), 'competitions_confirmation':len(ids)-len(selected),
        'ids_sha256':sha(p),
        'all_333':records('''SELECT explore, count(*) result_rows, sum(a.n) attempt_rows,
          count(DISTINCT (competition_id,round_type_id)) rounds,
          count(*) FILTER (WHERE rt.is_final) final_result_rows,
          count(DISTINCT (competition_id,round_type_id)) FILTER (WHERE rt.is_final) final_rounds
          FROM r JOIN membership m ON m.id=r.competition_id JOIN rt USING(round_type_id)
          LEFT JOIN attempt_shape a USING(result_id) GROUP BY explore ORDER BY explore'''),
        'eligible':records('''SELECT explore, is_final, count(*) result_rows, count(*)*5 attempt_rows,
          count(DISTINCT competition_id) competitions,
          count(DISTINCT (competition_id,round_type_id)) rounds,
          count(DISTINCT person_id) solvers,
          count(DISTINCT (competition_id,round_type_id)) FILTER (WHERE extra_pool_rows>0) rounds_with_extra_pool
          FROM eligible GROUP BY ALL ORDER BY explore,is_final'''),
        'coverage_by_year':records('''WITH totals AS (SELECT m.explore, cp.year_value AS year, count(*) total_results
          FROM r JOIN membership m ON m.id=r.competition_id JOIN comps cp ON cp.id=r.competition_id GROUP BY ALL),
          elig AS (SELECT explore, year, count(*) eligible_results, count(*) FILTER (WHERE is_final) final_results FROM eligible GROUP BY ALL)
          SELECT * FROM totals LEFT JOIN elig USING(explore,year) ORDER BY explore,year'''),
        'single_group_no_extra':records('''SELECT explore, count(DISTINCT (competition_id,round_type_id)) rounds,
          count(*)*5 attempts FROM eligible WHERE extra_pool_rows=0 GROUP BY explore'''),
        'eligible_seasons_structural':records('''SELECT explore, count(*) solver_seasons_at_least_5_finals FROM
          (SELECT explore, person_id, year, count(*) nf FROM eligible WHERE is_final GROUP BY ALL HAVING nf>=5)
          GROUP BY explore'''),
        'extra_pool_distribution':records('''SELECT extra_pool_rows,count(*) rounds FROM round_map
          WHERE n_groups=1 AND regular_rows=5 GROUP BY ALL ORDER BY extra_pool_rows''')}
    dump('coverage.json',coverage)
    md = f'''# S1 exploration slice — locked before outcome analysis

Exact user rule: **{RULE}**

```python
def in_slice(competition_id: str) -> bool:
    return int(hashlib.sha256(competition_id.encode('utf-8')).hexdigest(), 16) % 5 == 0
```

Implemented in `pilot.py:in_slice` and `prepare`. All original IDs in the frozen competitions table are eligible for hashing, including cancelled / no-results competitions. No year limit. UTF-8, no normalization. Manifest: `exploration-competition-ids.txt`, sorted lexicographically, one ID per line, LF terminated.

- All competition IDs: {len(ids):,}; exploration: {len(selected):,}; confirmation: {len(ids)-len(selected):,}.
- SHA-256 of exploration ID list: `{sha(p)}`.
- Source: {URL}; metadata date: {json.loads((RAW/'metadata.json').read_text())['export_date']}. Raw hashes: `source-manifest.json`.

## Outcome-blind row counts

All 3x3 results / attempt-row presence:
```json
{json.dumps(coverage['all_333'],indent=2)}
```
Single-group, exactly five regular scramble numbers 1–5, average-of-five result, exactly five attempt rows numbered 1–5:
```json
{json.dumps(coverage['eligible'],indent=2)}
```

The membership, schema and these counts were written before selecting any attempt value. Confirmation queries select no value, best, average, rank or record field. Detailed year balance is in `coverage.json`. All time analysis uses only `exploration-attempts.parquet`, created with `WHERE e.explore` inside the SQL scan. No confirmation outcome table is created.

## Mapping limitation

There is no group_id / scramble_id in the results or attempts tables. A unique regular scramble group gives a defensible **scheduled** mapping through attempt_number = scramble_num; it does not verify replacement attempts. Extra scramble rows describe a pool, not usage. `rounds_with_extra_pool` is reported separately. No exact-record attribution will be claimed without external per-attempt audit. Analysis eligibility and successful-time model counts are reported in PILOT.md, separately from this pre-outcome lock.
'''
    (OUT/'SLICE.md').write_text(md)
    progress(f"3. Outcome-blind slice lock complete: {len(selected):,}/{len(ids):,} competition IDs, SHA-256 {sha(p)}. Structural mapping and holdout counts saved to coverage.json / SLICE.md. No times analyzed yet.")
    # Only now select times, filtered by the locked exploration membership.
    c.execute(f'''COPY (SELECT e.*, a.attempt_number::INT attempt_number,
        a.value::INT AS value, s.scramble_id, s.scramble
        FROM eligible e JOIN {tsv('result_attempts')} a ON a.result_id::BIGINT=e.result_id
        JOIN s ON s.competition_id=e.competition_id AND s.round_type_id=e.round_type_id
          AND s.attempt_number=a.attempt_number::INT AND NOT s.extra
        WHERE e.explore) TO '{DATA/'exploration-attempts.parquet'}' (FORMAT PARQUET)''')
    n, bad = c.execute(f"SELECT count(*),count(*) FILTER(WHERE NOT explore) FROM read_parquet('{DATA/'exploration-attempts.parquet'}')").fetchone()
    assert bad==0
    progress(f"4. Wrote {n:,} scheduled-mapped exploration attempts only. Ready for successful-time crossed-model analysis; confirmation outcomes remain unused.")
    c.close()

def fit_mom(stats, weights=None):
    """Balanced two-way crossed random effects with a pooled position effect.
    y[r,i,j] = mu[r] + solver_round[r,i] + position[j] + scramble[r,j] + e.
    ANOVA moments allow unequal competitor counts across rounds.
    """
    w = np.ones(len(stats)) if weights is None else weights
    n=stats['n'].to_numpy()
    cols=stats[[f'c{j}' for j in range(5)]].to_numpy()
    beta=np.sum(cols*(w*n)[:,None],axis=0)/np.sum(w*n)
    beta-=beta.mean()
    e=np.sum(w*stats.sse)/np.sum(w*(n-1)*4)
    b=max(0., (np.sum(w*n*np.sum((cols-beta)**2,axis=1))-4*np.sum(w)*e)/(4*np.sum(w*n)))
    a=max(0., (np.sum(w*stats.ssa)-np.sum(w*(n-1))*e)/(5*np.sum(w*(n-1))))
    return {'solver_round_variance':float(a), 'scramble_variance':float(b), 'residual_variance':float(e),
            'total_share':float(b/(a+b+e)), 'within_solver_share':float(b/(b+e)),
            'scramble_log_sd':float(np.sqrt(b)), 'position':beta.tolist()}

def panels(frame, min_peers=6, winsor=False):
    round_stats=[]; chunks=[]
    for rid,g in frame.groupby('round_key',sort=False):
        n=len(g)
        if n<min_peers: continue
        y=np.log(g[[f'v{j}' for j in range(1,6)]].to_numpy()/100.)
        if winsor:
            d=y-y.mean(axis=1,keepdims=True)
            d=np.clip(d,-0.6,0.6)
            y=d+y.mean(axis=1,keepdims=True)
        row=y.mean(axis=1,keepdims=True); col=y.mean(axis=0); grand=y.mean()
        e=y-row-col[None,:]+grand
        s={'round_key':rid,'competition_id':g.competition_id.iloc[0], 'year':int(g.year.iloc[0]),
           'n':n,'sse':float((e**2).sum()),'ssa':float(5*((row-grand)**2).sum())}
        s.update({f'c{j}':float(col[j]-grand) for j in range(5)})
        round_stats.append(s); chunks.append((g,y))
    return pd.DataFrame(round_stats),chunks

def boot_variance(stats,B=2000):
    rng=np.random.default_rng(SEED)
    comp,cidx=np.unique(stats.competition_id, return_inverse=True)
    vals=[]
    for _ in range(B):
        # Resample whole competitions, including every round and every solver.
        w=np.bincount(rng.integers(0,len(comp),len(comp)),minlength=len(comp))[cidx]
        vals.append(fit_mom(stats,w))
    return {k:np.quantile([v[k] for v in vals],[.025,.975]).tolist()
            for k in ['total_share','within_solver_share','scramble_log_sd','scramble_variance']}

def boot_crossed(chunks,B=2000):
    """Pigeonhole competition + solver bootstrap, with duplicate noise correction.
    Replicate weights alter the effective number of independent peers, not create
    fake independent copies of a solver's residual. Returns conservative pilot CI.
    """
    frame=pd.concat([g for g,y in chunks],ignore_index=True)
    y=np.concatenate([y for g,y in chunks])
    row=y.mean(axis=1); z=y-row[:,None]
    comps,ridx=np.unique(frame.competition_id,return_inverse=True)
    solvers,sidx=np.unique(frame.person_id,return_inverse=True)
    R=len(comps)
    assert R==len(chunks), 'This implementation is for one final per competition'
    rng=np.random.default_rng(SEED+3); draws=[]
    for rep in range(B):
        sw=np.bincount(rng.integers(0,len(solvers),len(solvers)),minlength=len(solvers))[sidx].astype(float)
        cw=np.bincount(rng.integers(0,R,R),minlength=R).astype(float)
        W=np.bincount(ridx,weights=sw,minlength=R)
        W2=np.bincount(ridx,weights=sw**2,minlength=R)
        keep=W>0
        inv=np.divide(1.,W,out=np.zeros(R),where=keep)
        dfrow=W-W2*inv
        cw=cw*(dfrow>0)
        cols=np.column_stack([np.bincount(ridx,weights=sw*z[:,j],minlength=R)*inv for j in range(5)])
        beta=(cols*(cw*W)[:,None]).sum(axis=0)/(cw*W).sum(); beta-=beta.mean()
        zz=np.bincount(ridx,weights=sw*(z*z).sum(axis=1),minlength=R)
        sse=zz-W*(cols*cols).sum(axis=1)
        e=float((cw*sse).sum()/(4*(cw*dfrow).sum()))
        b=max(0.,float(((cw*W*((cols-beta)**2).sum(axis=1)).sum()-4*e*(cw*W2*inv).sum())/(4*(cw*W).sum())))
        r1=np.bincount(ridx,weights=sw*row,minlength=R)
        r2=np.bincount(ridx,weights=sw*row**2,minlength=R)
        ssa=5*(r2-r1*r1*inv)
        a=max(0.,float(((cw*ssa).sum()-e*(cw*dfrow).sum())/(5*(cw*dfrow).sum())))
        draws.append((b/(a+b+e),b/(b+e),np.sqrt(b)))
    return {k:np.quantile(np.array(draws)[:,j],[.025,.975]).tolist() for j,k in enumerate(['total_share','within_solver_share','scramble_log_sd'])}

def adjust(chunks, model):
    beta=np.asarray(model['position']); b=model['scramble_variance']; e=model['residual_variance']
    records=[]
    for g,y in chunks:
        n=len(g)
        z=y-y.mean(axis=1,keepdims=True)-beta
        peer=(z.sum(axis=0)[None,:]-z)/(n-1)
        shrink=b/(b+e/(n-1)) if b>0 else 0.
        bhat=shrink*peer
        posterior_sd=np.sqrt(.8*b*(1-shrink))
        out=g.loc[g.index.repeat(5), ['person_id','competition_id','round_type_id','round_key','result_id','year','month','day']].copy().reset_index(drop=True)
        out['attempt_number']=np.tile(np.arange(1,6),n)
        out['seconds']=np.exp(y).ravel()
        out['peer_log_effect']=bhat.ravel()
        out['unshrunk_peer_log_effect']=peer.ravel()
        out['shrinkage']=shrink
        out['peer_n']=n-1
        out['effect_posterior_sd']=posterior_sd
        out['adjusted_seconds']=out.seconds*np.exp(-out.peer_log_effect)
        records.append(out)
    return pd.concat(records,ignore_index=True)

def season_extremes(attempts, cohort=None, start=2019,end=2025, minimum=5):
    a=attempts[(attempts.year>=start)&(attempts.year<=end)]
    if cohort is not None: a=a[a.person_id.isin(cohort)]
    eligible=a.groupby(['person_id','year']).result_id.nunique()
    eligible=eligible[eligible>=minimum].reset_index()[['person_id','year']]
    a=a.merge(eligible,on=['person_id','year'])
    if a.empty: return a
    return a.sort_values(['seconds','competition_id','attempt_number']).groupby(['person_id','year'],sort=False).head(1).copy()

def boot_extremes(attempts, cohort=None,B=2000):
    """Reselect each seasonal minimum in every competition/solver bootstrap.
    Round peer estimates frozen; nuisance refitting is not claimed here.
    At least-five gate fixed to original eligible solver-season list.
    """
    observed=season_extremes(attempts,cohort)
    if len(observed)<2: return {'n':len(observed),'ratio':None,'ci':None}
    keys=list(zip(observed.person_id,observed.year))
    a=attempts[(attempts.year.between(2019,2025)) & attempts.person_id.isin(observed.person_id)]
    rng=np.random.default_rng(SEED+1)
    comp,ci=np.unique(a.competition_id,return_inverse=True)
    solv,si=np.unique(observed.person_id,return_inverse=True)
    lookup={k:j for j,k in enumerate(comp)}
    # One best attempt per competition and solver-season is sufficient for reselection.
    tmp=a.sort_values('seconds').groupby(['person_id','year','competition_id'],sort=False).head(1)
    groups={k:(g.seconds.to_numpy(), -g.peer_log_effect.to_numpy(), np.array([lookup[x] for x in g.competition_id])) for k,g in tmp.groupby(['person_id','year']) if k in set(keys)}
    solver_lookup={s:i for i,s in enumerate(solv)}
    vals=[]
    for _ in range(B):
        cw=np.bincount(rng.integers(0,len(comp),len(comp)),minlength=len(comp))
        sw=np.bincount(rng.integers(0,len(solv),len(solv)),minlength=len(solv))
        num=den=0.
        for k,(times,effects,idx) in groups.items():
            valid=cw[idx]>0
            weight=sw[solver_lookup[k[0]]]
            if not valid.any() or weight==0: continue
            j=np.argmin(np.where(valid,times,np.inf))
            num+=effects[j]*weight; den+=weight
        if den: vals.append(num/den)
    log_ratio=float(-observed.peer_log_effect.mean())
    se=float(np.std(vals,ddof=1))
    # Standard bootstrap includes changed exposure/selection; percentile output.
    return {'n':len(observed),'solvers':int(observed.person_id.nunique()),'competitions':int(observed.competition_id.nunique()),
            'ratio':float(np.exp(log_ratio)), 'log_ratio':log_ratio,
            'ci':np.exp(np.quantile(vals,[.025,.975])).tolist(),'bootstrap_log_se':se,
            'bootstrap_mean_ratio':float(np.exp(np.mean(vals))), 'bootstrap_reselect':True,
            'uncertainty_scope':'Competition + solver resampling, minimum reselection, fixed eligible seasons and fitted peer effects; not full nuisance-refit bootstrap.'}

def extreme_difficulty_summary(attempts,extremes,B=2000):
    threshold=float(attempts.peer_log_effect.quantile(.1))
    easy=extremes.peer_log_effect.to_numpy()<=threshold
    logratio=-extremes.peer_log_effect.to_numpy()
    comps,ci=np.unique(extremes.competition_id,return_inverse=True)
    solvers,si=np.unique(extremes.person_id,return_inverse=True)
    rng=np.random.default_rng(SEED+4); draws=[]
    for _ in range(B):
        cw=np.bincount(rng.integers(0,len(comps),len(comps)),minlength=len(comps))[ci]
        sw=np.bincount(rng.integers(0,len(solvers),len(solvers)),minlength=len(solvers))[si]
        w=cw*sw
        if w.sum() and w[easy].sum():
            draws.append((float(np.sum(w*easy)/w.sum()),float(np.sum(w[easy]*logratio[easy])/w[easy].sum())))
    return {'n':len(extremes),'easy_n':int(easy.sum()),'easy_fraction':float(easy.mean()),
        'easy_fraction_ci':np.quantile(np.array(draws)[:,0],[.025,.975]).tolist(),
        'easy_extreme_ratio':float(np.exp(logratio[easy].mean())),
        'easy_extreme_ratio_ci':np.exp(np.quantile(np.array(draws)[:,1],[.025,.975])).tolist(),
        'peer_difficulty_decile_threshold':threshold,
        'uncertainty_scope':'Competition + solver bootstrap of fixed observed extrema; fitted difficulty and classification frozen.'}

def analyze():
    assert (OUT/'SLICE.md').exists()
    c=con(); pq=DATA/'exploration-attempts.parquet'
    n,bad=c.execute(f"SELECT count(*),count(*) FILTER(WHERE NOT explore) FROM read_parquet('{pq}')").fetchone()
    assert bad==0
    # SQL performs all filtering and wide reshaping before pandas receives panels.
    c.execute(f"CREATE OR REPLACE TEMP VIEW x AS SELECT * FROM read_parquet('{pq}')")
    counts=c.execute('''SELECT is_final,count(*) attempts,count(*) FILTER(WHERE value>0) successful,
        count(*) FILTER(WHERE value=-1) dnf,count(*) FILTER(WHERE value=-2) dns,
        count(*) FILTER(WHERE value=0) absent FROM x GROUP BY ALL ORDER BY is_final''').fetchdf().to_dict('records')
    panel=c.execute('''SELECT competition_id, round_type_id, person_id,result_id,year,month,day,is_final,
        competition_id||'|'||round_type_id round_key,
        max(value) FILTER(WHERE attempt_number=1) v1,max(value) FILTER(WHERE attempt_number=2) v2,
        max(value) FILTER(WHERE attempt_number=3) v3,max(value) FILTER(WHERE attempt_number=4) v4,
        max(value) FILTER(WHERE attempt_number=5) v5
        FROM x GROUP BY ALL HAVING count(*)=5 AND min(value)>0''').fetchdf()
    main,chunks=panels(panel[panel.is_final])
    model=fit_mom(main)
    cis=boot_variance(main)
    crossed_cis=boot_crossed(chunks)
    dump('variance-results.json', {'model':'Crossed solver-round by scramble random effects, pooled position fixed effect, ANOVA moments on balanced successful five-attempt panels',
         'model_counts':{'rounds':len(main),'competitions':int(main.competition_id.nunique()),'solver_rounds':int(main.n.sum()),'attempts':int(main.n.sum()*5)},'fit':model,'ci':cis,'crossed_bootstrap_ci':crossed_cis,'statuses':counts})
    progress(f"5. Main finals crossed model: {len(main):,} rounds / {int(main.n.sum()*5):,} successful attempts. Shared scramble share = {100*model['total_share']:.2f}% of total log-time variance, {100*model['within_solver_share']:.2f}% within solver-round. Competition-bootstrap CIs saved.")
    # Priors learned on exploration-only pre-2019 finals, frozen for later seasons.
    training=main[main.year<2019]
    prior=fit_mom(training)
    attempts=adjust(chunks,prior)
    assert all(in_slice(i) for i in attempts.competition_id.unique())
    attempts.to_parquet(DATA/'exploration-adjusted.parquet',index=False)
    # Proxy cohort, selected only with slice pre-2019 mapped round outcomes.
    pre=panel[panel.year<=2018].copy()
    pre['official_average_cs']=(pre[[f'v{j}' for j in range(1,6)]].sum(axis=1)-pre[[f'v{j}' for j in range(1,6)]].max(axis=1)-pre[[f'v{j}' for j in range(1,6)]].min(axis=1))/3
    enough=pre.groupby('person_id').size(); enough=enough[enough>=10].index
    cohort=pre[pre.person_id.isin(enough)].groupby('person_id').official_average_cs.min().nsmallest(100).index.tolist()
    (OUT/'exploratory-cohort-ids.txt').write_text('\n'.join(cohort)+'\n')
    c.register('proxy_ids',pd.DataFrame({'person_id':cohort}))
    # Held-out cohort activity is outcome-blind: count row presence, never time.
    blind=c.execute('''SELECT explore, count(*) solver_seasons, count(DISTINCT person_id) solvers FROM
        (SELECT e.explore,e.person_id,e.year,count(*) nf FROM eligible e JOIN proxy_ids USING(person_id)
        WHERE e.is_final AND e.year BETWEEN 2019 AND 2025 GROUP BY ALL HAVING nf>=5) GROUP BY explore''').fetchdf().to_dict('records')
    period=c.execute('''SELECT explore, is_final,
        CASE WHEN year<2019 THEN 'pre2019' WHEN year<=2025 THEN '2019-2025' ELSE '2026' END period,
        count(DISTINCT (competition_id,round_type_id)) rounds,count(*)*5 attempts FROM eligible GROUP BY ALL ORDER BY explore,period,is_final''').fetchdf().to_dict('records')
    dump('outcome-blind-cohort-coverage.json',{'proxy_cohort_activity':blind,'target_period_coverage':period,
        'note':'Only presence and format/mapping fields from confirmation. Exact 2018 cohort is unavailable without historical ranking outcomes.'})
    extreme=season_extremes(attempts,cohort)
    all_extreme=season_extremes(attempts,None)
    boot=boot_extremes(attempts,cohort)
    broadboot=boot_extremes(attempts,None)
    extreme.to_csv(OUT/'proxy-cohort-seasonal-extremes.csv',index=False)
    all_extreme.to_csv(OUT/'all-solver-seasonal-extremes.csv',index=False)
    dump('extreme-results.json', {'training_prior':prior,'training_rounds':len(training),'cohort':'100 best pre-2019 slice eligible 3x3 averages, >=50 successful mapped attempts; not the prescribed full-population 2018 ranking',
        'proxy':boot,'all_solvers':broadboot})
    progress(f"6. Leave-one-solver-out adjustments (pre-2019 slice prior frozen): {len(extreme)} proxy top-100 solver-season minima; ratio {boot['ratio']}, CI {boot['ci']}. Exact historical cohort cannot be reconstructed outcome-blind; proxy results are exploratory.")
    # Specifications are exploratory, with no outcome-based choice of primary.
    specs=[]
    tests={'all_rounds':panel, 'finals_2019_2022':panel[panel.is_final & panel.year.between(2019,2022)],
           'finals_2023_2025':panel[panel.is_final & panel.year.between(2023,2025)],
           'finals_pre2019':panel[panel.is_final & (panel.year<2019)],
           'finals_at_least_12':panel[panel.is_final], 'finals_winsorized':panel[panel.is_final]}
    # No-DNF round sensitivity (remove every incomplete-success round).
    clean=c.execute('''SELECT competition_id||'|'||round_type_id round_key FROM x
           WHERE is_final GROUP BY ALL HAVING min(value)>0''').fetchdf().round_key
    tests['finals_no_nonpositive']=panel[panel.is_final & panel.round_key.isin(clean)]
    for name,frame in tests.items():
        st,ch=panels(frame,min_peers=12 if name=='finals_at_least_12' else 6,winsor=name=='finals_winsorized')
        if len(st)==0: continue
        mo=fit_mom(st)
        adj=adjust(ch,prior)
        ex=season_extremes(adj,cohort)
        specs.append({'spec':name,'rounds':len(st),'attempts':int(st.n.sum()*5),**mo,'extremes':len(ex),
                      'ratio':float(np.exp(-ex.peer_log_effect.mean())) if len(ex) else None})
    # Within solver independently permute five positions: destroys common signal.
    rng=np.random.default_rng(SEED+2)
    place=[]
    for rep in range(100):
        ss=[]
        for g,y in chunks:
            yp=np.take_along_axis(y,np.argsort(rng.random(y.shape),axis=1),axis=1)
            row=yp.mean(axis=1,keepdims=True); col=yp.mean(axis=0); grand=yp.mean()
            er=yp-row-col[None,:]+grand
            s={'n':len(g),'sse':float((er**2).sum()),'ssa':float(5*((row-grand)**2).sum())}
            s.update({f'c{j}':float(col[j]-grand) for j in range(5)}); ss.append(s)
        place.append(fit_mom(pd.DataFrame(ss))['within_solver_share'])
    # Caution: common permutation of scramble labels within each round is invariant.
    dump('robustness.json',{'specifications':specs,'independent_solver_position_permutation':{'replicates':100,
           'observed_within_share':model['within_solver_share'],'null_95_interval':np.quantile(place,[.025,.975]).tolist(),
           'p_plus_one':float((1+np.sum(np.array(place)>=model['within_solver_share']))/101)},
           'placebo_fix':'A common label permutation within a round merely renames scramble effects. Independently permute each solver row instead.'})
    # Rankings include EVERY main-panel successful attempt in the comparison pool.
    attempts['raw_rank']=attempts.seconds.rank(method='min').astype(int)
    attempts['adjusted_rank']=attempts.adjusted_seconds.rank(method='min').astype(int)
    top=attempts.sort_values(['seconds','competition_id','attempt_number']).head(20).copy()
    names=c.execute(f'''SELECT r.person_id,any_value(r.person_name) person_name
        FROM {tsv('results')} r JOIN membership m ON r.competition_id=m.id
        WHERE m.explore AND r.event_id='333' GROUP BY r.person_id''').fetchdf()
    top=top.merge(names,on='person_id',how='left')
    top['adjusted_low']=top.adjusted_seconds*np.exp(-1.96*top.effect_posterior_sd)
    top['adjusted_high']=top.adjusted_seconds*np.exp(1.96*top.effect_posterior_sd)
    top.to_csv(OUT/'top-singles.csv',index=False)
    # Broad mapped-round raw leaderboard to reveal selection scope.
    broad=c.execute('''SELECT x.person_id,x.competition_id,x.round_type_id,x.is_final,x.attempt_number,x.value/100.0 AS seconds
         FROM x WHERE value>0 ORDER BY value,competition_id,attempt_number LIMIT 20''').fetchdf()
    broad=broad.merge(names,on='person_id',how='left'); broad.to_csv(OUT/'all-mapped-rounds-top-singles.csv',index=False)
    allstats,allchunks=panels(panel)
    alladj=adjust(allchunks,prior)
    alladj['raw_rank']=alladj.seconds.rank(method='min').astype(int)
    alladj['adjusted_rank']=alladj.adjusted_seconds.rank(method='min').astype(int)
    alltop=alladj.sort_values('seconds').head(20).merge(names,on='person_id',how='left')
    alltop.to_csv(OUT/'all-rounds-adjusted-top-singles.csv',index=False)
    # Stability of broadly supported extremes; top-100 proxy too small to govern design.
    leave_year=[]
    for yr in sorted(all_extreme.year.unique()):
        ex=all_extreme[all_extreme.year!=yr]
        leave_year.append({'excluded_year':int(yr),'n':len(ex),'ratio':float(np.exp(-ex.peer_log_effect.mean()))})
    leave_solver=[]
    for person in all_extreme.person_id.unique():
        ex=all_extreme[all_extreme.person_id!=person]
        leave_solver.append(float(np.exp(-ex.peer_log_effect.mean())))
    easy=attempts.nsmallest(max(1,len(attempts)//10),'peer_log_effect')
    hard=attempts.nlargest(max(1,len(attempts)//10),'peer_log_effect')
    bestfive=attempts.sort_values('seconds').groupby('result_id',sort=False).head(1)
    dump('secondary-findings.json',{'leave_one_year':leave_year,
        'leave_one_solver_ratio_range':[min(leave_solver),max(leave_solver)],
        'best_of_five_n':len(bestfive),'best_of_five_ratio':float(np.exp(-bestfive.peer_log_effect.mean())),
        'all_season_minima_easy_decile_fraction':float((all_extreme.peer_log_effect<=attempts.peer_log_effect.quantile(.1)).mean()),
        'easy_decile_mean_adjustment':float(np.exp(-easy.peer_log_effect.mean())),
        'hard_decile_mean_adjustment':float(np.exp(-hard.peer_log_effect.mean())),
        'extreme_easy_summary':extreme_difficulty_summary(attempts,all_extreme)})
    # Cross-peer reproducibility: split solver IDs by hash, no target solve selected.
    agree=[]
    for g,y in chunks:
        mask=np.array([int(hashlib.sha256(p.encode()).hexdigest(),16)%2==0 for p in g.person_id])
        if min(mask.sum(),(~mask).sum())<3: continue
        z=y-y.mean(axis=1,keepdims=True)-np.asarray(model['position'])
        agree.append((z[mask].mean(axis=0),z[~mask].mean(axis=0)))
    qa=np.array([a for a,b in agree]).ravel(); qb=np.array([b for a,b in agree]).ravel()
    cross_peer=float(np.corrcoef(qa,qb)[0,1])
    power={}
    for label,bo in [('proxy',boot),('all_solvers',broadboot)]:
        if bo.get('bootstrap_log_se'):
            se=bo['bootstrap_log_se']/2 # Four times as many competitions, optimistic.
            mu=bo['log_ratio']
            cutoff=max(np.log(1.10),1.96*se)
            power[label]={'assumed_confirmation_log_se':se,'assumed_competition_multiplier':4,
                          'observed_effect_pass_probability':float(norm.sf((cutoff-mu)/se)),
                          'power_if_true_ratio_1_10':float(norm.sf((cutoff-np.log(1.10))/se)),
                          'power_if_true_ratio_1_12':float(norm.sf((cutoff-np.log(1.12))/se))}
    dump('analysis-summary.json', {'variance':model,'variance_ci':cis,'crossed_bootstrap_ci':crossed_cis,'counts':counts,'main_rounds':len(main),
         'main_attempts':int(main.n.sum()*5),'main_solvers':int(attempts.person_id.nunique()),
         'proxy':boot,'all_solvers':broadboot,'cross_peer_correlation':cross_peer,'cross_peer_rounds':len(agree),
         'power':power,'top_single':top.iloc[0].to_dict()})
    chart_variance(model,cis,specs)
    chart_extremes(top,boot,broadboot)
    chart_peers(qa,qb,cross_peer)
    progress(f"7. Robustness, independent-row permutation placebo, split-peer replication, full-pool adjusted rankings, and three PNG draft charts saved. Split-peer correlation = {cross_peer:.3f}. Report synthesis next.")
    c.close()

def chart_variance(m,ci,specs):
    fig,ax=plt.subplots(1,2,figsize=(12,5),gridspec_kw={'width_ratios':[1,1.6]})
    colors=['#65758b','#dd854b','#58a9a0']
    vals=[m['solver_round_variance'],m['scramble_variance'],m['residual_variance']]
    ax[0].bar(['Solver +\nround skill','Shared\nscramble','Residual'],np.array(vals)/sum(vals)*100,color=colors)
    ax[0].set_ylabel('Share of log-time variance (%)'); ax[0].set_title('Same round, five shared scrambles')
    display=[('All eligible finals',m['within_solver_share'],ci['within_solver_share'])]
    for s in specs:
        if s['spec'] in ['all_rounds','finals_2019_2022','finals_2023_2025','finals_winsorized']:
            display.append((s['spec'].replace('_',' '),s['within_solver_share'],None))
    for j,(label,value,bounds) in enumerate(display):
        ax[1].scatter(value*100,j,color='#dd854b',s=60)
        if bounds: ax[1].plot(np.array(bounds)*100,[j,j],color='#dd854b',lw=3)
    ax[1].set_yticks(range(len(display)),[v[0] for v in display]); ax[1].invert_yaxis()
    ax[1].set_xlabel('Shared scramble share of within-solver variance (%)'); ax[1].set_title('Fairer test: hold current solver skill fixed')
    fig.suptitle('How much do the scrambles move everyone together?',fontsize=16)
    fig.text(.01,.015,'Exploratory 20% competition hash slice • successful five-solve panels • scheduled mapping, replacements unverified',fontsize=9)
    fig.tight_layout(rect=[0,.06,1,.94]); fig.savefig(OUT/'01-shared-scramble.png',dpi=180); plt.close(fig)

def chart_extremes(top,bo,broad):
    t=top.head(10).copy(); fig,axes=plt.subplots(1,2,figsize=(13,6),gridspec_kw={'width_ratios':[1.8,1]})
    ax=axes[0]
    for j,row in enumerate(t.itertuples()):
        ax.plot([row.seconds,row.adjusted_seconds],[j,j],color='#aaa',lw=2)
        ax.scatter(row.seconds,j,color='#65758b',s=45,label='Official single' if j==0 else None)
        ax.errorbar(row.adjusted_seconds,j,xerr=[[row.adjusted_seconds-row.adjusted_low],[row.adjusted_high-row.adjusted_seconds]],fmt='o',color='#dd854b',ms=5,label='Peer scramble adjustment' if j==0 else None)
    labels=[f'{r.person_name.split(" (")[0]}\n{r.competition_id} / #{r.attempt_number}' for r in t.itertuples()]
    ax.set_yticks(range(len(t)),labels,fontsize=8); ax.invert_yaxis(); ax.set_xlabel('Seconds'); ax.legend(loc='lower right',fontsize=9)
    ax.set_title('Obvious answer → fairer comparison')
    ax=axes[1]
    for j,(label,result) in enumerate([('Slice-selected top 100',bo),('All qualifying solvers',broad)]):
        if result['ratio'] is None: continue
        v=100*(result['ratio']-1); lo,hi=100*(np.array(result['ci'])-1)
        ax.plot([lo,hi],[j,j],color='#dd854b',lw=3); ax.scatter(v,j,color='#dd854b',s=60)
    ax.set_yticks([0,1],['Proxy top 100','All solvers']); ax.set_ylim(-.6,1.6); ax.invert_yaxis()
    ax.axvline(0,color='#aaa'); ax.axvline(10,color='#65758b',ls='--',label='Proposed materiality gate: 10%')
    ax.set_xlim(min(-1,ax.get_xlim()[0]),max(11,ax.get_xlim()[1])); ax.set_xlabel('Time added by scramble adjustment (%)'); ax.set_title('Seasonal bests: how big is the boost?'); ax.legend(fontsize=8)
    fig.suptitle('The fastest mapped finals in the exploration slice',fontsize=16)
    fig.text(.01,.012,'Left bands: approximate scramble-effect posterior only; right bands: competition + solver bootstrap with minimum reselection. Not official adjusted records.',fontsize=8)
    fig.tight_layout(rect=[0,.06,1,.94]); fig.savefig(OUT/'02-extremes-and-ranks.png',dpi=180); plt.close(fig)

def chart_peers(a,b,corr):
    fig,ax=plt.subplots(figsize=(8,6))
    ax.hexbin(a*100,b*100,gridsize=55,mincnt=1,cmap='YlOrBr',extent=(-35,35,-35,35))
    ax.axhline(0,color='#999',lw=.6); ax.axvline(0,color='#999',lw=.6)
    ax.set_xlabel('Half A: average relative log-time (%)'); ax.set_ylabel('Half B: average relative log-time (%)')
    ax.set_title(f'Do different peers agree which scramble was easy?\nSplit-peer correlation = {corr:.3f}')
    fig.text(.01,.01,'Exploration finals only • solvers split by hashed ID • each solver centered within round • all solves, without extreme selection',fontsize=8)
    fig.tight_layout(rect=[0,.04,1,1]); fig.savefig(OUT/'03-peer-replication.png',dpi=180); plt.close(fig)

if __name__=='__main__':
    arg=argparse.ArgumentParser(); arg.add_argument('step',nargs='?',default='all',choices=['prepare','analyze','report','all'])
    args=arg.parse_args()
    if args.step in ['prepare','all']: prepare()
    if args.step in ['analyze','all']: analyze()
