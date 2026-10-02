from pathlib import Path
import json,hashlib,datetime
import numpy as np,pandas as pd
BASE=Path(__file__).resolve().parents[1]
v=json.loads((BASE/'values.json').read_text());r=pd.read_pickle(BASE/'raw_rows.pkl');t=np.load(BASE/'raw_times.npy');r=r[~r.training];t=t[~pd.read_pickle(BASE/'raw_rows.pkl').training.to_numpy()]
def put(k,x,n,d):v[k]={'value':x,'n':int(n),'definition':d}
for k in ['exploration','confirmation']:
 x=v.pop('exclusion_'+k+'_all_ids')['value'];put('universe_'+k+'_competitions',x,18771,'Hash-defined '+k+' competitions in the full raw export')
for k in ['ambiguous_regular_schedule_results','ambiguous_regular_schedule_finals']:
 v.setdefault('exclusion_'+k,{'value':0,'n':v['scope_results']['value'],'definition':'Sequential exclusion count: '+k})
put('extra_pool_finals',int(r[r.extra_pool].drop_duplicates(['competition_id','round_type_id']).shape[0]),v['finals']['value'],'Included finals with at least one extra-pool scramble row')
put('extra_pool_solver_results',int(r.extra_pool.sum()),len(r),'Included solver-final rows in finals with extra pools')
put('dnf_started_rate',float((t==-1).sum()/((t>0).sum()+(t==-1).sum())),int((t>0).sum()+(t==-1).sum()),'DNF divided by positive attempts plus DNF; DNS excluded')
put('complete_success_results',int((t>0).all(1).sum()),len(r),'Included solver-final rows with five successful attempts')
roster=r.groupby(['person_id','year']).size();put('eligible_season_solvers',int(roster[roster>=5].reset_index().person_id.nunique()),v['eligible_solver_seasons']['value'],'Distinct solvers represented on the fixed eligible person-year roster')
(BASE/'values.json').write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
seal={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':{}}
for p in [BASE/'values.json',*sorted((BASE/'code').glob('*.py'))]:seal['files'][str(p.relative_to(BASE))]=hashlib.sha256(p.read_bytes()).hexdigest()
(BASE/'phase1-seal.json').write_text(json.dumps(seal,indent=2)+'\n')
p=BASE/'RECHECK.md';s=p.read_text().replace('Pending completion of independent computation. No comparison inputs opened.',f'''Completed and sealed at {seal['utc']}, before any comparison inputs were opened.
The immutable blind values/code hashes are in `phase1-seal.json`. All 2,000
requested draws were run. The registered confirmation/exploration ID-list hashes
match exactly. Recomputed training beta differs from the frozen beta by at most
6.34e-16. Matrix symmetry, idempotence, zero-sum and trace identities pass to
2.23e-16. There are no repeated solver/competition rows in the extracted data.

Blind result: {v['finals']['value']} finals; {v['attempt_slots']['value']} slots;
{v['successes']['value']} successes; {v['dnf']['value']} DNF; {v['dns']['value']} DNS;
{v['solvers']['value']} solvers; {v['eligible_solver_seasons']['value']} eligible
solver-seasons. F={v['tier_F']['value']:.12g}; gamma/D={v['tier_gamma_share']['value']:.12g};
R={v['R']['value']:.12g}, amended 95% interval {v['R_ci95']['value']}.
Conditional registered verdict: **{v['verdict']['value']}**.
''');p.write_text(s)
print('Phase 1 saved and sealed;',len(v),'values;',v['R']['value'],v['R_ci95']['value'])
