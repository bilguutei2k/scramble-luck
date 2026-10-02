"""Post-unblinding diagnosis only; does not replace sealed blind values."""
import json
import numpy as np,pandas as pd
from derive import BASE,arrays,reference,tier_stats
r=pd.read_pickle(BASE/'raw_rows.pkl');t=np.load(BASE/'raw_times.npy');keep=~r.training.to_numpy();r=r[keep].reset_index(drop=True);t=t[keep]
sol=json.loads((BASE.parent/'analysis/results.json').read_text());out={}
for lo,hi in [(2019,2022),(2023,2025)]:
 keep=r.year.between(lo,hi).to_numpy();rr=r[keep].reset_index(drop=True);a=arrays(rr,t[keep]);ref=reference(rr,a);st=tier_stats(rr,a,ref)
 target=sol['robustness'][f'era_{lo}_{hi}'];out[f'{lo}_{hi}']={}
 for key,path in [('F',('F_tier_aware','estimate')),('gamma_share',('tier_interaction_share_gamma_over_D','estimate')),('finals',('coverage','tier_supported_finals')),('successes',('coverage','tier_successful_cells'))]:
  val=st[key];other=target[path[0]][path[1]];out[f'{lo}_{hi}'][key]={'within_era_reference_recheck':val,'sol':other,'matches':bool(np.isclose(val,other,rtol=1e-6,atol=0))}
(BASE/'era-reference-diagnostic.json').write_text(json.dumps(out,indent=2)+'\n')
# Monte Carlo error of bootstrap distribution summaries, with independent fixed diagnostic seed.
b=np.load(BASE/'bootstrap.npz');rng=np.random.default_rng(20261002);M=1000
samples=[];fixed=[];means=[];absent=[];comps=[]
for _ in range(M):
 ix=rng.integers(len(b['logR']),size=len(b['logR']));x=b['logR'][ix];samples.append(np.quantile(x-x.mean(),[.025,.975]));fixed.append(np.quantile(b['fixed_logR'][ix],[.025,.975]));means.append(x.mean());absent.append(b['absent'][ix].mean());comps.append(b['distinct_competitions'][ix].mean())
mc={'method':'1000 independent resamples of 2000 blind draws; diagnostic seed 20261002; endpoint SE on log scale. Difference tolerance is 4*sqrt(2)*SE (two independent equal-sized Monte Carlo estimates). This is not a scientific sampling interval.','replicates':M,'centered_endpoint_se':np.std(samples,axis=0,ddof=1).tolist(),'fixed_endpoint_se':np.std(fixed,axis=0,ddof=1).tolist(),'mean_logR_se':float(np.std(means,ddof=1)),'absent_mean_se':float(np.std(absent,ddof=1)),'competition_mean_se':float(np.std(comps,ddof=1))}
# Raw percentiles have no recentering covariance.
raw=[]
for _ in range(M):raw.append(np.quantile(rng.choice(b['logR'],len(b['logR'])),[.025,.975]))
mc['raw_endpoint_se']=np.std(raw,axis=0,ddof=1).tolist()
(BASE/'monte-carlo-tolerance.json').write_text(json.dumps(mc,indent=2)+'\n')
print('Era discrepancies reproduced:',sum(v['matches'] for era in out.values() for v in era.values()),'of 8')
print('Centered endpoint Monte Carlo SE:',mc['centered_endpoint_se'])
