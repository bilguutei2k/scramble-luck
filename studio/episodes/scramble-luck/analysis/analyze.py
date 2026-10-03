#!/usr/bin/env python3
"""Amended confirmatory analysis. Bulk outcomes/checkpoints are gitignored.

Run: ideation/.venv/bin/python studio/episodes/scramble-luck/analysis/analyze.py
Each block is resumable. Exactly 2,000 shared product draws, seed 20261001.
"""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS',
             'VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import sys, json, time, datetime, itertools, multiprocessing as mp
if __name__ in ('__main__','__mp_main__'):sys.modules['analyze']=sys.modules[__name__]
from pathlib import Path
import numpy as np
import pandas as pd
import duckdb
from scipy.optimize import minimize
from numba import njit
from common import OUT, EP, DERIVED, BETA, FROZEN, SEED, NOTICE, sha, dump, progress, code_hashes
from engine import (Structure, Dataset, contributions, accumulate, moment, project,
                    tier_fit, select_best, refs_tiers)

DRAWS=2000
ST=DS=CDS=KDS=VALUES=CROSS=WEIGHTS=LOGISTIC=None
SUBSETS={}

def clean(x):
    if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple,np.ndarray)):return [clean(v) for v in x]
    if isinstance(x,(np.integer,)):return int(x)
    if isinstance(x,(np.floating,float)):return float(x) if np.isfinite(x) else None
    if isinstance(x,np.bool_):return bool(x)
    return x

def bulk(name,obj):
    p=DERIVED/name
    tmp=p.with_suffix(p.suffix+'.tmp')
    tmp.write_text(json.dumps(clean(obj),sort_keys=True,allow_nan=False)+'\n');tmp.replace(p)

def provenance_and_open():
    """Main pipeline first-time read of observed confirmation magnitudes."""
    from gate import fixture_checks
    checks=fixture_checks()
    m=json.loads((EP/'data/wca-manifest.json').read_text())
    assert sha(EP/m['local_path'])==m['sha256']
    lists={}
    for label in ('exploration','confirmation'):
        p=EP/m['split'][label+'_ids']; assert sha(p)==m['split'][label+'_ids_sha256']
        lists[label]=p.read_text().splitlines()
        assert lists[label]==sorted(set(lists[label]))
        import hashlib
        assert all((int(hashlib.sha256(v.encode()).hexdigest(),16)%5==0)==(label=='exploration') for v in lists[label])
    assert not set(lists['confirmation'])&set(lists['exploration'])
    raw=DERIVED/'source'
    hashes={}
    for row in FROZEN['sources']['files'][1:]:
        p=raw/Path(row['path']).name
        assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
        hashes[p.name]=row['sha256']
    for name in ('summary.json','replication-summary.json'):
        a=json.loads((OUT/'amendment'/name).read_text())
        assert a['procedure_pass']['B']
    if not (DERIVED/'confirmation-values.parquet').exists():
        con=duckdb.connect(str(DERIVED/'structure.duckdb'),read_only=True)
        con.execute('SET threads=10')
        # Timestamp is persisted immediately before the first value SELECT.
        stamp=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='microseconds')
        bulk('first-confirmation-open.json',{'first_open_utc':stamp,'scope':'main analysis pipeline only','action':'main pipeline first magnitude SELECT immediately follows this persisted timestamp'})
        progress(f'Step 4: MAIN PIPELINE FIRST OPEN of confirmation solve-time magnitudes at {stamp}; approved amendment commit 5496074 verified; original and independent B gates pass.')
        src=str(raw/'WCA_export_result_attempts.tsv')
        wide=','.join(f'max(CAST(a.value AS BIGINT)) FILTER(WHERE CAST(a.attempt_number AS INTEGER)={j}) v{j}' for j in range(1,6))
        query=f"""SELECT r.result_id,{wide} FROM read_csv('{src}',delim='\\t',header=true,all_varchar=true,quote='',nullstr='') a
                 JOIN eligible r ON a.result_id=r.result_id WHERE r.confirmation GROUP BY r.result_id"""
        values=con.execute(query).fetchdf();con.close()
        values.to_parquet(DERIVED/'confirmation-values.parquet',index=False)
    else:
        assert (DERIVED/'first-confirmation-open.json').exists()
    dump('analysis-provenance.json',{'source_hashes_rechecked':hashes,
         'archive_sha256':m['sha256'],'split_counts':{k:len(v) for k,v in lists.items()},
         'frozen_fixture_checks':checks,'first_open':{**json.loads((DERIVED/'first-confirmation-open.json').read_text()),'scope':'main analysis pipeline first magnitude SELECT only'},
         'method_sha256':sha(EP/'METHOD.md'),'amendment_sha256':sha(OUT/'amendment/AMENDMENT-1.md')})

def make_logistic(status):
    rows=[];patterns=[];observed=[];nconf=[]
    for i,ss in enumerate(status):
        started=np.flatnonzero(ss!=-2);m=int(np.sum(ss==-1))
        if not (0<m<len(started)):continue
        comb=list(itertools.combinations(started,m));pat=np.zeros((10,5))
        for c,ix in enumerate(comb):pat[c,list(ix)]=1
        rows.append(i);patterns.append(pat);observed.append((ss==-1).astype(float));nconf.append(len(comb))
    return np.array(rows),np.array(patterns),np.array(observed),np.array(nconf)

@njit(cache=True)
def conditional_objective(coef,features,observed,nconf,weights):
    loss=0.;grad=np.zeros(5)
    for i in range(len(weights)):
        w=weights[i]
        if w<=0:continue
        nc=nconf[i];scores=np.zeros(nc);top=-1e100
        for c in range(nc):
            for j in range(5):scores[c]+=features[i,c,j]*coef[j]
            top=max(top,scores[c])
        norm=0.
        for c in range(nc):scores[c]=np.exp(scores[c]-top);norm+=scores[c]
        obs=0.
        for j in range(5):obs+=observed[i,j]*coef[j];grad[j]-=w*observed[i,j]
        loss+=w*(top+np.log(norm)-obs)
        for c in range(nc):
            for j in range(5):grad[j]+=w*scores[c]/norm*features[i,c,j]
    total=weights.sum()
    return loss/total,grad/total

def logistic_fit(h,rank,cw,sw):
    rows,pat,obs,nc=LOGISTIC
    features=np.zeros((len(rows),10,5));observed=np.zeros((len(rows),5))
    features[:,:,0]=np.einsum('nij,nj->ni',pat,h[rows])/.05
    features[:,:,1:]=pat[:,:,1:];observed[:,0]=np.sum(obs*h[rows],axis=1)/.05;observed[:,1:]=obs[:,1:]
    w=cw[ST.cidx[rows]]*sw[ST.sidx[rows]]*(rank[rows]==4)
    if w.sum()==0:return np.nan,False,0
    fit=minimize(conditional_objective,np.zeros(5),args=(features,observed,nc,w),jac=True,
                 method='BFGS',options={'gtol':1e-7,'maxiter':100})
    grad=conditional_objective(fit.x,features,observed,nc,w)[1]
    ok=bool(np.max(np.abs(grad))<2e-6 and np.all(np.isfinite(fit.x)))
    return float(fit.x[0]) if ok else np.nan,ok,int(np.sum(w>0))

def initialize():
    global ST,DS,CDS,KDS,VALUES,CROSS,WEIGHTS,LOGISTIC,SUBSETS
    ST=Structure()
    v=pd.read_parquet(DERIVED/'confirmation-values.parquet').set_index('result_id')
    VALUES=v.loc[ST.g.result_id,[f'v{j}' for j in range(1,6)]].to_numpy()
    assert np.array_equal(np.where(VALUES>0,1,VALUES),ST.status)
    y=np.log(np.where(VALUES>0,VALUES/100,np.nan))
    tv=ST.tg[[f'v{j}' for j in range(1,6)]].to_numpy();ty=np.log(np.where(tv>0,tv/100,np.nan))
    DS=Dataset(ST,y,ty)
    complete=np.all(np.isfinite(y),axis=1)
    CDS=Dataset(ST,np.where(complete[:,None],y,np.nan),ty)
    ky=np.where(np.isfinite(y),DS.means[:,None]+np.clip(y-DS.means[:,None],-.6,.6),np.nan)
    KDS=Dataset(ST,ky,ty)
    cr=pd.read_parquet(DERIVED/'cross.parquet')
    ck=cr.competition_id+'|'+cr.round_type_id
    keys=(ST.g.competition_id+'|'+ST.g.round_type_id).groupby(ST.ridx).first()
    CROSS=np.stack([cr.assign(key=ck).pivot(index='key',columns='scramble_num',values=col).loc[keys].to_numpy()
                    for col in ('optimal_cross_all_six_faces','optimal_cross_white_yellow')])
    WEIGHTS=tuple(np.load(DERIVED/f'bootstrap-{v}.npy',mmap_mode='r') for v in ('competition','solver','training')) if (DERIVED/'bootstrap-competition.npy').exists() else None
    LOGISTIC=make_logistic(ST.status)
    SUBSETS={'era_2019_2022':np.isin(ST.years,range(2019,2023)),
             'era_2023_2025':np.isin(ST.years,range(2023,2026))}
    SUBSETS.update({f'leave_year_{year}_out':ST.years!=year for year in range(2019,2026)})

def run(ds,cw,sw,tw,original=False,beta_mode='training'):
    out=ds.run(None if original else cw,None if original else sw,None if original else tw,details=True)
    if beta_mode!='training' and not original:
        if beta_mode=='frozen':beta=BETA
        elif beta_mode=='confirmation':beta=moment(out['allst'],cw[ST.round_comp])['beta']
        else:raise ValueError(beta_mode)
        rows=out['rows'];h,rank,_=project(out['allst'][0],out['allst'][1],ds.C,ds.z,ST.ridx,ST.sidx,sw,rows,beta)
        assert np.all(rank==4)
        out['h']=h;out['effects']=h[np.arange(len(rows)),ds.js[rows]]
        out['logR']=float(-np.average(out['effects'],weights=out['weights'])) if len(rows) else np.nan
        out['beta']=beta
    return out

def projected_tier(ds,out,t,sw,rows):
    tiers=out['tiers']
    agg=accumulate(ds.C,ds.z,ds.ss,ds.d,ST.ridx,ST.sidx,sw,ST.R,tiers,t)
    w=sw[ST.sidx[rows]]*(tiers[rows]==t)
    A=agg[0][ST.ridx[rows]]-ds.C[rows]*w[:,None,None]
    V=agg[1][ST.ridx[rows]]-ds.z[rows]*w[:,None]-np.einsum('nij,j->ni',A,out['beta'])
    eig,U=np.linalg.eigh(A);rank=np.sum(eig>1e-9,axis=1)
    h=np.einsum('nij,nj->ni',U,np.einsum('nji,nj->ni',U,V)/np.where(eig>1e-9,eig,np.inf))
    count=np.bincount(ST.ridx,weights=((tiers==t)&(sw[ST.sidx]>0)&(ds.d>0)).astype(float),minlength=ST.R)
    peers=count[ST.ridx[rows]]-((tiers[rows]==t)&(sw[ST.sidx[rows]]>0)&(ds.d[rows]>0))
    return h,(rank==4)&(peers>=3)

def extras(ds,out,cw,sw,tw):
    rows=out['rows'];x=-out['effects'];w=out['weights']
    ss=ST.sidx[rows];sums=np.bincount(ss,weights=x,minlength=ST.S);ns=np.bincount(ss,minlength=ST.S)
    have=ns>0
    result={'arithmetic_R':float(np.average(np.exp(x),weights=w)),
            'per_solver_logR':float(np.average(sums[have]/ns[have],weights=sw[have]))}
    hf,kf=projected_tier(ds,out,0,sw,rows);hs,ks=projected_tier(ds,out,1,sw,rows);keep=kf&ks
    result.update(equal_tier_logR=float(-np.average(((hf+hs)/2)[keep,ds.js[rows[keep]]],weights=w[keep])) if keep.any() else np.nan,
                  matched_all_peer_logR=float(np.average(x[keep],weights=w[keep])) if keep.any() else np.nan,
                  equal_tier_n=int(keep.sum()),per_solver_n=int(have.sum()))
    allrows=np.arange(ST.N)
    h,rank,_=project(out['allst'][0],out['allst'][1],ds.C,ds.z,ST.ridx,ST.sidx,sw,allrows,out['beta'])
    active=(rank==4)&(sw[ST.sidx]>0)&(cw[ST.cidx]>0)
    result['identified_solver_rounds']=int(active.sum())
    # A fixed-selection procedure, independently equivalent to amendment FastR.draw.
    origrows=ORIGINAL_ROWS
    fixed=origrows[(cw[ST.cidx[origrows]]*sw[ST.sidx[origrows]]>0)&(rank[origrows]==4)]
    fw=cw[ST.cidx[fixed]]*sw[ST.sidx[fixed]]
    result['fixed_selection_logR']=float(np.average(-h[fixed,ds.js[fixed]],weights=fw)) if len(fixed) else np.nan
    result['fixed_selection_n']=len(fixed)
    # Each included scheduled scramble gets one focal-averaged peer contrast.
    focalw=sw[ST.sidx]*active
    den=np.bincount(ST.ridx,weights=focalw,minlength=ST.R)
    avg=np.stack([np.bincount(ST.ridx,weights=focalw*h[:,j],minlength=ST.R)/np.where(den>0,den,1) for j in range(5)],axis=1)
    rw=cw[ST.round_comp]*(den>0)
    def corr(a,b,weights):
        ww=np.repeat(weights,5);aa=a.ravel();bb=b.ravel();total=ww.sum()
        am=np.sum(ww*aa)/total;bm=np.sum(ww*bb)/total
        return float(np.sum(ww*(aa-am)*(bb-bm))/np.sqrt(np.sum(ww*(aa-am)**2)*np.sum(ww*(bb-bm)**2)))
    for n,cross in zip(('six_faces','white_yellow'),CROSS):
        result[f'cross_{n}_raw_correlation']=corr(avg,cross,rw)
        result[f'cross_{n}_centered_correlation']=corr(avg,cross-cross.mean(1,keepdims=True),rw)
    result['cross_scrambles_n']=int(5*np.sum(rw>0))
    coef,ok,n=logistic_fit(h,rank,cw,sw)
    result.update(dnf_log_odds_per_005=coef,dnf_fit_converged=ok,dnf_discordant_panels=n)
    binary=np.where(ST.status!=-2,(ST.status==-1).astype(float),np.nan)
    C,z,ss,d,_=contributions(binary)
    b=moment(accumulate(C,z,ss,d,ST.ridx,ST.sidx,sw,ST.R,np.zeros(ST.N,dtype=np.int8),-1),cw[ST.round_comp])
    result['binary_dnf_shared_covariance']=b['b'] if b else np.nan
    started=(ST.status!=-2);dnf=(ST.status==-1);dns=ST.status==-2
    wt=cw[ST.cidx]*sw[ST.sidx]
    result['dnf_started_rate']=float(np.sum(wt[:,None]*dnf)/np.sum(wt[:,None]*started))
    result['dns_slot_rate']=float(np.sum(wt[:,None]*dns)/(5*wt.sum()))
    result['distinct_competition_fraction']=float(np.mean(cw>0))
    result['weighted_attempt_exposure']=float(5*wt.sum())
    result['distinct_attempt_exposure']=int(5*np.sum(wt>0))
    result.update({f'fit_{k}':v for k,v in (out['fit'] or {}).items() if np.isscalar(v)})
    return result

ORIGINAL_ROWS=None
def worker_init():
    global ORIGINAL_ROWS
    initialize();ORIGINAL_ROWS=DS.run(details=True)['rows']

def small(out):
    return {k:out[k] for k in ('logR','F','gamma_over_D','available_extrema','absent_seasons','no_success_seasons','unidentified_extrema','tier_supported_finals','tier_successful_cells')}

def task_primary(b):
    cw,sw,tw=[np.array(v[b],dtype=float) for v in WEIGHTS]
    out=run(DS,cw,sw,tw)
    return {'draw':b,**small(out),**extras(DS,out,cw,sw,tw)}

def task_subsets(b):
    cw,sw,tw=[np.array(v[b],dtype=float) for v in WEIGHTS]
    result={'draw':b}
    for name,mask in SUBSETS.items():
        cm=cw*np.bincount(ST.cidx,weights=mask,minlength=ST.C).astype(bool)
        result[name]=small(run(DS,cm,sw,tw))
    result['complete_success']=small(run(CDS,cw,sw,tw))
    result['clipped_centered_logs']=small(run(KDS,cw,sw,tw))
    allout=run(DS,cw,sw,tw,beta_mode='confirmation')
    result['confirmation_beta']=small(allout)
    result['confirmation_beta']['beta']=allout['beta']
    yearly={};weighted=0.;total=0
    for year in range(2019,2026):
        cm=cw*np.bincount(ST.cidx,weights=ST.years==year,minlength=ST.C).astype(bool)
        out=run(DS,cm,sw,tw,beta_mode='confirmation');yearly[str(year)]={**small(out),'beta':out['beta']}
        if len(out['rows']):weighted+=out['logR']*out['weights'].sum();total+=out['weights'].sum()
    result['yearly_beta']={'logR':weighted/total,'by_year':yearly}
    return result

def task_delete(s):
    cw=np.ones(ST.C);sw=np.ones(ST.S);tw=np.ones(ST.TC);sw[s]=0
    return {'solver':str(ST.solvers[s]),'solver_index':int(s),**small(run(DS,cw,sw,tw,beta_mode='frozen'))}

DELETE_ENDPOINTS=[]
def task_delete_intervals(b):
    cw,sw,tw=[np.array(v[b],dtype=float) for v in WEIGHTS]
    out={'draw':b}
    for s in DELETE_ENDPOINTS:
        w=sw.copy();w[s]=0
        out[str(s)]=small(run(DS,cw,w,tw))
    return out

def common_fields(ds,cw,sw):
    agg=accumulate(ds.C,ds.z,ds.ss,ds.d,ST.ridx,ST.sidx,sw,ST.R,np.zeros(ST.N,dtype=np.int8),-1)
    fit=moment(agg,cw[ST.round_comp])
    return {'share':fit['b']/fit['total'],'shared_variance':fit['b'],
            'within_solver_denominator':fit['total'],'residual_variance':fit['e'],
            'position':fit['beta'],'contrast_degrees':fit['contrast_degrees']}

def task_common(b):
    cw,sw,tw=[np.array(v[b],dtype=float) for v in WEIGHTS]
    fit=DS.run(cw,sw,tw,details=True)['fit']
    return {'draw':b,'tier_positions':{k:fit[k] for k in ('fast_position','slow_position')},**{name:common_fields(ds,cw,sw) for name,ds in
            [('all_finalists',DS),('complete_success',CDS),('clipped_centered_logs',KDS)]}}

def task_permutation(b):
    rng=np.random.default_rng(np.random.SeedSequence([SEED,700,b]))
    order=np.argsort(rng.random((ST.N,5)),axis=1)
    y=np.take_along_axis(DS.y,order,axis=1)
    ds=Dataset(ST,y,DS.ty)
    out=ds.run();return {'draw':b,**small(out)}

def block(pool,name,tasks,fn):
    path=DERIVED/f'analysis-{name}.jsonl'
    old=[json.loads(s) for s in path.read_text().splitlines()] if path.exists() else []
    key='solver_index' if name=='solver-deletions' else 'draw'
    done={r[key] for r in old};todo=[x for x in tasks if x not in done]
    start=time.perf_counter();progress(f'Step 4 block {name}: {len(done)} checkpointed; {len(todo)} tasks remaining on ten cores.')
    with path.open('a') as f:
        for i,r in enumerate(pool.imap_unordered(fn,todo,chunksize=5),1):
            f.write(json.dumps(clean(r),allow_nan=False)+'\n');old.append(clean(r))
            if i%100==0:f.flush()
            if i%500==0:progress(f'Step 4 {name}: {len(old)} tasks checkpointed; elapsed {time.perf_counter()-start:.1f}s.')
    old.sort(key=lambda r:r[key]);progress(f'Step 4 block {name} COMPLETE: {len(old)} tasks, {time.perf_counter()-start:.1f}s this run.')
    return old

def metric(value,draws,n,interval='percentile',transform=None):
    x=np.array([v if v is not None else np.nan for v in draws],dtype=float);x=x[np.isfinite(x)]
    ci=np.quantile(x,[.025,.975],method='linear') if len(x) else np.full(2,np.nan)
    raw=ci.copy()
    if interval=='recentered':ci+=value-x.mean()
    out={'estimate':value,'n':n,'interval_95':ci,'interval_method':interval,'valid_draws':len(x),'requested_draws':len(draws)}
    out['measurement_status']='estimable' if len(x)>=1900 else 'inconclusive measurement: fewer than 1900 valid draws; displayed interval is diagnostic'
    if interval=='recentered':out.update(raw_percentile_interval_95=raw,bootstrap_mean=float(x.mean()),bootstrap_mean_displacement=float(x.mean()-value))
    if transform=='exp':
        out['log_estimate']=value;out['estimate']=np.exp(value);out['interval_95']=np.exp(ci)
        if interval=='recentered':out['raw_percentile_interval_95']=np.exp(raw);out['log_raw_percentile_interval_95']=raw
    return clean(out)

def summary(point,draws):
    out={'F_tier_aware':metric(point['F'],[r['F'] for r in draws],{'tier_supported_finals':point['tier_supported_finals'],'successful_cells':point['tier_successful_cells']}),
            'tier_interaction_share_gamma_over_D':metric(point['gamma_over_D'],[r['gamma_over_D'] for r in draws],{'tier_supported_finals':point['tier_supported_finals'],'successful_cells':point['tier_successful_cells']}),
            'R_geometric_person_year':metric(point['logR'],[r['logR'] for r in draws],{'available_person_years':point['available_extrema']},'recentered','exp'),
            'coverage':{k:point[k] for k in ('available_extrema','absent_seasons','no_success_seasons','unidentified_extrema','tier_supported_finals','tier_successful_cells')}}
    out['coverage_gates']={'F_interpretation':bool(point['tier_supported_finals']>=500 and point['tier_successful_cells']>=20000),
                           'R_available_extrema':bool(point['available_extrema']>=100)}
    if not out['coverage_gates']['F_interpretation']:
        out['F_tier_aware']['measurement_status']='inconclusive measurement: tier coverage gate fails; interval is diagnostic'
        out['tier_interaction_share_gamma_over_D']['measurement_status']='inconclusive measurement: tier coverage gate fails; interval is diagnostic'
    if not out['coverage_gates']['R_available_extrema']:
        out['R_geometric_person_year']['measurement_status']='inconclusive measurement: fewer than 100 available extrema; interval is diagnostic'
    return out

def main():
    global ORIGINAL_ROWS,WEIGHTS,DELETE_ENDPOINTS
    provenance_and_open();initialize()
    point=DS.run(details=True);ORIGINAL_ROWS=point['rows']
    if WEIGHTS is None:
        rng=np.random.default_rng(SEED);ww=[ST.weights(rng) for _ in range(DRAWS)]
        for j,n in enumerate(('competition','solver','training')):
            np.save(DERIVED/f'bootstrap-{n}.npy',np.array([v[j] for v in ww],dtype=np.uint16))
        del ww
        WEIGHTS=tuple(np.load(DERIVED/f'bootstrap-{v}.npy',mmap_mode='r') for v in ('competition','solver','training'))
    one=(np.ones(ST.C),np.ones(ST.S),np.ones(ST.TC))
    ext=extras(DS,point,*one)
    bulk('analysis-point.json',{**small(point),**ext,'fit':point['fit'],'training_fit':{k:v for k,v in point['training_fit'].items() if k not in ('A','V')}})
    progress(f"Step 4 observed-point block complete: {ST.R} finals; {len(point['rows'])} available extrema; {point['tier_supported_finals']} tier-supported finals. No threshold decision before intervals.")
    with mp.get_context('spawn').Pool(10,initializer=worker_init) as pool:
        primary=block(pool,'primary',range(DRAWS),task_primary)
        bulk('analysis-primary-summary.json',summary(point,primary))
        subsets=block(pool,'subsets',range(DRAWS),task_subsets)
        deletions=block(pool,'solver-deletions',np.unique(ST.sidx),task_delete)
        for k in ('F','logR'):
            valid=[r for r in deletions if r[k] is not None]
            DELETE_ENDPOINTS.extend([min(valid,key=lambda r:r[k])['solver_index'],max(valid,key=lambda r:r[k])['solver_index']])
        DELETE_ENDPOINTS=sorted(set(DELETE_ENDPOINTS))
        bulk('analysis-deletion-endpoints.json',DELETE_ENDPOINTS)
        # A fresh pool receives the data-selected endpoint list through its initializer.
    with mp.get_context('spawn').Pool(10,initializer=endpoint_init) as pool:
        delete_intervals=block(pool,'deletion-intervals',range(DRAWS),task_delete_intervals)
        common=block(pool,'common-moments',range(DRAWS),task_common)
        perm=block(pool,'permutation',range(1000),task_permutation)
    from analysis_reports import prediction, finish
    pred=prediction(DS,ST)
    progress('Step 4 peer-prediction block COMPLETE: 30 whole-solver splits and 2,000 competition draws at k=2,5,10,20; changing and fixed panels.')
    finish(ST,DS,CDS,KDS,point,ext,primary,subsets,deletions,delete_intervals,common,perm,pred)

def endpoint_init():
    global DELETE_ENDPOINTS
    worker_init();DELETE_ENDPOINTS=json.loads((DERIVED/'analysis-deletion-endpoints.json').read_text())

if __name__=='__main__':main()
