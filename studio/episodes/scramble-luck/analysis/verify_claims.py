#!/usr/bin/env python3
"""Verify proposed claims without opening results.json.

Point estimates: a separate numpy/scipy implementation on the independently
extracted raw rows and centisecond cells in recheck/. Intervals: recomputed
from unsummarized draw-level derived tables, not reported result summaries.
Source claims: raw WCA rows for historical marks; saved source HTML for rules
and reconstructions. All comparisons use the claim's displayed precision.
This is an independent code path, not an independent human review. Bootstrap
records remain inputs; this verifier does not claim a fresh secondary bootstrap.
Run with ideation/.venv/bin/python. Never changes proposed claim statuses.
"""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[name]='1'
import json, re, hashlib, sys, itertools, html
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import logsumexp
EP=Path(__file__).resolve().parents[1]
DER=EP/'data/derived'
BETA=np.array([-.00019098085080805892,.0015330545917410243,-.00016398101357186266,-.005728817307245912,.0045507245798848085])
SEED=20261001
M={}; E={}
def loadlines(path):
    return [json.loads(s) for s in path.read_text().splitlines() if s.strip()]
def put(key,value,evidence):
    M[key]=value;E[key]=evidence

def metric(key,point,draws=(),n=None,exponent=False,recenter=False):
    xs=np.array([np.nan if v is None else v for v in draws],float)
    xs=xs[np.isfinite(xs)]
    put(key+'.estimate',float(np.exp(point) if exponent else point),'independent raw-cell point calculation')
    if exponent:put(key+'.log_estimate',float(point),'independent mean log ratio')
    if len(xs):
        ci=np.quantile(xs,[.025,.975],method='linear')
        raw=ci.copy()
        if recenter:ci+=point-xs.mean()
        for j in range(2):
            put(f'{key}.interval_95[{j}]',float(np.exp(ci[j]) if exponent else ci[j]),'linear quantiles of draw-level records'+('; AMENDMENT-1 bootstrap-mean translation' if recenter else ''))
            if recenter:put(f'{key}.raw_percentile_interval_95[{j}]',float(np.exp(raw[j]) if exponent else raw[j]),'untranslated draw quantiles')
        put(key+'.valid_draws',len(xs),'finite draw count')
        if recenter:
            put(key+'.bootstrap_mean',float(xs.mean()),'draw mean')
            put(key+'.bootstrap_mean_displacement',float(xs.mean()-point),'draw mean minus independently calculated point')
    if n:
        for k,v in n.items():put(key+'.n.'+k,int(v),'raw-cell coverage count')

def matrices(rows,times,y=None):
    q=(times>0).astype(float);m=q.sum(1)
    if y is None:y=np.log(np.where(q,times/100,1))
    C=q[:,:,None]*np.eye(5)-q[:,:,None]*q[:,None,:]/np.maximum(m,1)[:,None,None]
    C[m<2]=0
    z=np.einsum('nij,nj->ni',C,y)
    keys=list(zip(rows.competition_id,rows.round_type_id))
    panel=pd.factorize(pd.Series(keys),sort=True)[0]
    return dict(C=C,z=z,m=m,y=y,panel=panel,P=int(panel.max()+1))

def references(rows,a):
    means=(a['y']*(a['m'][:,None]>0)).sum(1)/np.maximum(a['m'],1)
    means[a['m']==0]=np.nan
    ref=np.full(len(rows),np.nan);years=rows.year.to_numpy();comp=rows.competition_id.to_numpy()
    for ix in rows.groupby('person_id').indices.values():
        for i in ix:
            js=ix[(np.abs(years[ix]-years[i])<=2)&(comp[ix]!=comp[i])&np.isfinite(means[ix])]
            if len(js)>=2:ref[i]=np.median(means[js])
    return ref

def moments(a,mask):
    C=a['C'][mask];z=a['z'][mask];p=a['panel'][mask]
    beta=np.linalg.pinv(C.sum(0),rcond=1e-12)@z.sum(0)
    x=z-C@beta
    A=np.zeros((a['P'],5,5));V=np.zeros((a['P'],5))
    np.add.at(A,p,C);np.add.at(V,p,x)
    S=float((x*x).sum());d=float(np.maximum(a['m'][mask]-1,0).sum())
    b=((V*V).sum()-S)/((A*A).sum()-d);total=S/d
    return dict(b=b,e=total-b,total=total,beta=beta,A=A,V=V)

def tiers(rows,a):
    ref=references(rows,a);tier=np.full(len(rows),-1)
    for p in range(a['P']):
        ix=np.flatnonzero((a['panel']==p)&np.isfinite(ref)&(a['m']>=2))
        if len(ix)<6:continue
        median=np.median(ref[ix]);f=ix[ref[ix]<median];s=ix[ref[ix]>=median]
        if len(f)>=3 and len(s)>=3:tier[f]=0;tier[s]=1
    f=moments(a,tier==0);s=moments(a,tier==1)
    cov=(f['V']*s['V']).sum()/(f['A']*s['A']).sum()
    tau=(f['b']+s['b']+2*cov)/4;gamma=(f['b']+s['b']-2*cov)/4;D=(f['total']+s['total'])/2
    fit=dict(F=tau/D,gamma_over_D=gamma/D,tau=tau,gamma=gamma,D=D,cross_covariance=cov,fast_shared_variance=f['b'],slow_shared_variance=s['b'],fast_residual_variance=f['e'],slow_residual_variance=s['e'])
    counts=dict(tier_supported_finals=len(np.unique(a['panel'][tier>=0])),successful_cells=int(a['m'][tier>=0].sum()))
    return fit,counts,tier,ref,f['beta'],s['beta']

def peers(a,beta,mask=None):
    if mask is None:mask=np.ones(len(a['m']),bool)
    x=a['z']-a['C']@beta
    A=np.zeros((a['P'],5,5));V=np.zeros((a['P'],5))
    np.add.at(A,a['panel'][mask],a['C'][mask]);np.add.at(V,a['panel'][mask],x[mask])
    A=A[a['panel']]-a['C']*mask[:,None,None];V=V[a['panel']]-x*mask[:,None]
    eig,U=np.linalg.eigh(A);inv=np.divide(1,eig,out=np.zeros_like(eig),where=eig>1e-9)
    h=np.einsum('nik,nk,njk,nj->ni',U,inv,U,V)
    return h,(eig>1e-9).sum(1)==4

def selected(rows,times,roster):
    t=np.where(times>0,times,np.inf);mn=t.min(1);slots=t.argmin(1)
    d=pd.DataFrame({'row':np.arange(len(rows)),'value':mn,'comp':rows.competition_id,'round':rows.round_type_id,'slot':slots,'id':rows.id,'person':rows.person_id,'year':rows.year})
    d=d[np.isfinite(mn)&np.array([(s,y) in roster for s,y in zip(rows.person_id,rows.year)])]
    d=d.sort_values(['value','comp','round','slot','id']).drop_duplicates(['person','year'])
    return d.row.to_numpy(),slots

def point(rows,times,roster,beta=BETA,y=None):
    a=matrices(rows,times,y);fit,n,tier,ref,fb,sb=tiers(rows,a)
    h,rank=peers(a,beta);sel,slots=selected(rows,times,roster);keep=rank[sel];sel=sel[keep]
    xx=-h[sel,slots[sel]]
    n.update(available_person_years=len(sel))
    return dict(a=a,fit=fit,n=n,tier=tier,ref=ref,h=h,rank=rank,sel=sel,slots=slots,x=xx,theta=float(xx.mean()),fast_beta=fb,slow_beta=sb)

def summary(path,p,draws):
    n={k:p['n'][k] for k in ('tier_supported_finals','successful_cells')}
    metric(path+'.F_tier_aware',p['fit']['F'],[d['F'] for d in draws],n)
    metric(path+'.tier_interaction_share_gamma_over_D',p['fit']['gamma_over_D'],[d['gamma_over_D'] for d in draws],n)
    metric(path+'.R_geometric_person_year',p['theta'],[d['logR'] for d in draws],{'available_person_years':len(p['sel'])},True,True)
    for k,v in {'available_extrema':len(p['sel']), 'tier_supported_finals':n['tier_supported_finals'],'tier_successful_cells':n['successful_cells']}.items():put(path+'.coverage.'+k,v,'raw coverage')

def prediction(rows,a,k,fixed):
    rng=np.random.default_rng(np.random.SeedSequence([SEED,25,k,int(fixed)]))
    stats=[];counts=[];rankfails=0;cells=0
    tau=.0007830105490928417;e=.021684974210191423
    for p in range(a['P']):
        ix=np.flatnonzero((a['panel']==p)&(a['m']>=2))
        if len(ix)<(22 if fixed else k+2):continue
        splits=[]
        for rep in range(30):
            ixp=rng.permutation(ix);pi=ixp[:k];ti=ixp[k:]
            Ap=a['C'][pi].sum(0);At=a['C'][ti].sum(0)
            vp=a['z'][pi].sum(0)-Ap@BETA;vt=a['z'][ti].sum(0)-At@BETA
            if np.linalg.matrix_rank(Ap,tol=1e-9)<4 or np.linalg.matrix_rank(At,tol=1e-9)<4:rankfails+=1;continue
            hp=np.linalg.pinv(Ap)@vp;ht=np.linalg.pinv(At)@vt
            post=np.linalg.solve(Ap+np.eye(5)*e/tau,vp)
            f=(a['m'][ti]/(a['m'][ti]-1))[:,None]
            target=(a['z'][ti]-a['C'][ti]@BETA)*f;pred=(a['C'][ti]@post)*f
            splits.append([hp@ht,hp@hp,ht@ht,(target*target).sum(),((target-pred)**2).sum()])
        if splits:stats.append(np.mean(splits,axis=0));counts.append(len(ix));cells+=int(a['m'][ix].sum())
    stats=np.array(stats)
    def measures(v):return [v[0]/np.sqrt(v[1]*v[2]),1-v[4]/v[3]]
    brng=np.random.default_rng(np.random.SeedSequence([SEED,26,k,int(fixed)]))
    boot=[]
    for _ in range(2000):boot.append(measures(np.bincount(brng.integers(len(stats),size=len(stats)),minlength=len(stats))@stats))
    n={'finals':len(stats),'unique_solver_final_rows':sum(counts),'successful_cells_in_eligible_panels':cells,'whole_solver_splits_per_final':30,'rank_failed_splits':rankfails}
    path=f"peer_prediction.{'fixed_panels' if fixed else 'changing_panels'}[k={k}]"
    pt=measures(stats.sum(0));boot=np.array(boot)
    for j,name in enumerate(('peer_correlation','individual_prediction_R_squared')):metric(path+'.'+name,pt[j],boot[:,j],n)
    put(path+'.model_latent_reliability.estimate',tau/(tau+e/k),'frozen-parameter model extrapolation')
    for key,v in n.items():put(path+'.n.'+key,v,'independent split coverage')

def independent():
    raw=pd.read_pickle(EP/'recheck/raw_rows.pkl');t=np.load(EP/'recheck/raw_times.npy')
    train=raw.training.to_numpy();rows=raw[~train].reset_index(drop=True);times=t[~train]
    roster=rows.groupby(['person_id','year']).competition_id.nunique();roster=set(roster[roster>=5].index)
    primary=loadlines(DER/'analysis-primary.jsonl');subsets=loadlines(DER/'analysis-subsets.jsonl');common=loadlines(DER/'analysis-common-moments.jsonl')
    p=point(rows,times,roster);summary('primary',p,primary)
    metric('primary.R_fixed_selection_A_sensitivity',p['theta'],[d['fixed_selection_logR'] for d in primary],{'available_person_years':len(p['sel'])},True)
    for name,value in p['fit'].items():metric('primary.signed_variance_components.'+name,value,[d['fit_'+name] for d in primary])
    for name,beta in [('fast_position',p['fast_beta']),('slow_position',p['slow_beta'])]:
        for j in range(5):metric(f'primary.positions_by_tier.{name}[{j}]',beta[j],[d['tier_positions'][name][j] for d in common])
    a=p['a'];m=a['m'];fit=p['fit'];n=p['n']
    counts={'eligible_finals':a['P'],'included_attempt_slots':times.size,'successful_cells':int((times>0).sum()),'informative_solver_rounds':int((m>=2).sum()),'singleton_success_solver_rounds':int((m==1).sum()),'no_success_solver_rounds':int((m==0).sum()),'available_extrema':len(p['sel']),'no_success_seasons':0,'unidentified_extrema':0,'missing_skill_references_informative_solver_rounds':int((~np.isfinite(p['ref'])&(m>=2)).sum()),'tier_subset_excluded_finals':a['P']-n['tier_supported_finals'],'tier_subset_excluded_successful_cells':int(m.sum())-n['successful_cells']}
    for k,v in counts.items():put('coverage.census_measurements.'+k+'.estimate',v,'independent raw-row census')
    for k,v in {'solvers':rows.person_id.nunique(),'solver_rounds':len(rows),'solver_seasons':len(roster),'years':rows.year.nunique(),'first_year':rows.year.min(),'last_year':rows.year.max(),'seasonal_solvers':rows.iloc[p['sel']].person_id.nunique(),'incomplete_solver_rounds':int((m<5).sum()),'clipped_cells':int(((np.abs(a['y']-np.divide(a['y'].sum(1),np.maximum(m,1))[:,None])>.6)&(times>0)).sum())}.items():put('census.'+k,int(v),'raw rows and official centisecond cells')
    put('coverage.structural.extra_pool_finals',int(rows.loc[rows.extra_pool].groupby(['competition_id','round_type_id']).ngroups),'raw schedule pool flags')
    for label in ('confirmation','exploration'):put('coverage.structural.split_counts.'+label,len((EP/f'data/{label}-competition-ids.txt').read_text().splitlines()),'locked competition ID lists')
    extraction=json.loads((EP/'recheck/extraction.json').read_text())
    names={'incomplete_or_duplicate_slots_results':'incomplete_duplicate_slots_results','invalid_format_final_results':'invalid_format','invalid_regular_schedule_results':'ambiguous_regular_schedule_results','invalid_status_results_after_slot_gate':'invalid_status_results','missing_schedule_results':'missing_schedule_results','multigroup_results':'multigroup_or_no_regular_group_results','nonfinal_333_results':'nonfinal','other_event_results':'other_event'}
    for k,v in names.items():put('coverage.census_measurements.exclusions.'+k+'.estimate',extraction.get(v,0),'independent raw-export extraction exclusion census')
    for year in range(2019,2026):
        mask=rows.year.to_numpy()==year;tm=(p['tier']>=0)&mask
        for k,v in {'eligible_finals':len(np.unique(a['panel'][mask])),'tier_supported_finals':len(np.unique(a['panel'][tm])),'successful_cells':int(m[tm].sum())}.items():put(f'coverage.tier_by_year.{year}.{k}',v,'raw panel census by year')
    for k in ('absent_seasons','available_extrema','distinct_attempt_exposure','distinct_competition_fraction','equal_tier_n','fixed_selection_n','no_success_seasons','unidentified_extrema','weighted_attempt_exposure'):
        xs=np.array([d[k] for d in primary]);base='bootstrap_exposure.'+k
        for key,v in [('mean',xs.mean()),('min',xs.min()),('max',xs.max()),('draws',len(xs))]:put(base+'.'+key,float(v),'draw-level exposure summary')
        for j,v in enumerate(np.quantile(xs,[.025,.975])):put(f'{base}.central_95_range[{j}]',float(v),'central draw range, not a confidence interval')
    print('Raw primary estimates and coverage recomputed.',flush=True)
    masks={'era_2019_2022':rows.year<=2022,'era_2023_2025':rows.year>=2023,**{f'leave_year_{y}_out':rows.year!=y for y in range(2019,2026)}}
    allpoints={}
    for name,mask in masks.items():
        pp=point(rows[mask].reset_index(drop=True),times[mask],roster);allpoints[name]=pp
        summary('robustness.'+name,pp,[d[name] for d in subsets])
    complete=times.copy();complete[m<5]=0
    clipped=a['y'].copy();means=np.divide(a['y'].sum(1),np.maximum(m,1));clipped=np.where(times>0,means[:,None]+np.clip(clipped-means[:,None],-.6,.6),0)
    for name,tt,yy in [('complete_success',complete,None),('clipped_centered_logs',times,clipped)]:
        pp=point(rows,tt,roster,y=yy);allpoints[name]=pp;summary('robustness.'+name,pp,[d[name] for d in subsets])
    for name,aa in [('all_finalists',a),('complete_success',allpoints['complete_success']['a']),('clipped_centered_logs',allpoints['clipped_centered_logs']['a'])]:
        cm=moments(aa,np.ones(len(rows),bool));base='common_only_comparators.'+name
        for field,value in [('share',cm['b']/cm['total']),('within_solver_denominator',cm['total'])]:metric(base+'.'+field,value,[d[name][field] for d in common])
        for k,v in {'solver_rounds_with_contrasts':int((aa['m']>=2).sum()),'successful_cells':int(aa['m'].sum())}.items():put(base+'.coverage.'+k,v,'raw success mask')
    cb=moments(a,np.ones(len(rows),bool))['beta'];cp=point(rows,times,roster,beta=cb)
    metric('attempt_position_sensitivities.confirmation_beta.R',cp['theta'],[d['confirmation_beta']['logR'] for d in subsets],{'available_person_years':len(cp['sel'])},True,True)
    for j in range(5):metric(f'attempt_position_sensitivities.confirmation_beta.beta[{j}]',cb[j],[d['confirmation_beta']['beta'][j] for d in subsets])
    yearly=[]
    for year in range(2019,2026):
        mask=rows.year==year;rr=rows[mask].reset_index(drop=True);tt=times[mask];aa=matrices(rr,tt);beta=moments(aa,np.ones(len(rr),bool))['beta'];pp=point(rr,tt,roster,beta=beta)
        base=f'attempt_position_sensitivities.yearly_beta.by_year.{year}';summary(base,pp,[d['yearly_beta']['by_year'][str(year)] for d in subsets]);yearly.extend(pp['x'])
        for j in range(5):metric(base+f'.beta[{j}]',beta[j],[d['yearly_beta']['by_year'][str(year)]['beta'][j] for d in subsets])
    metric('attempt_position_sensitivities.yearly_beta.R',np.mean(yearly),[d['yearly_beta']['logR'] for d in subsets],{'available_person_years':len(yearly)},True,True)
    xx=p['x'];sel=p['sel'];slots=p['slots'];tier=p['tier']
    equal=[];keep=np.ones(len(sel),bool)
    for z in (0,1):
        hh,rank=peers(a,BETA,tier==z);nums=np.bincount(a['panel'],weights=(tier==z).astype(int),minlength=a['P'])
        keep &= rank[sel]&((nums[a['panel'][sel]]-(tier[sel]==z))>=3);equal.append(hh)
    ex=-((equal[0]+equal[1])/2)[sel[keep],slots[sel[keep]]]
    ag='aggregation_and_tier_sensitivities.'
    for name,value,field,nv,exponent in [('arithmetic_mean_R',np.log(np.exp(xx).mean()),'arithmetic_R',{'available_person_years':len(sel)},True),('per_solver_weighted_R',pd.Series(xx).groupby(rows.person_id.iloc[sel].to_numpy()).mean().mean(),'per_solver_logR',{'solvers':rows.person_id.iloc[sel].nunique(),'person_years':len(sel)},True),('equal_tier_R',ex.mean(),'equal_tier_logR',{'person_years':int(keep.sum())},True),('all_peer_R_on_equal_tier_subset',xx[keep].mean(),'matched_all_peer_logR',{'person_years':int(keep.sum())},True)]:metric(ag+name,value,[np.log(d[field]) if field=='arithmetic_R' else d[field] for d in primary],nv,exponent,True)
    put(ag+'equal_tier_attrition',len(sel)-int(keep.sum()),'identified equal-tier subset attrition')
    # Mechanism: mean whole-solver-excluded contrasts, then Pearson correlation.
    cross=pd.read_parquet(DER/'cross.parquet');keys=rows.assign(panel=a['panel']).groupby('panel')[['competition_id','round_type_id']].first();key=keys.competition_id+'|'+keys.round_type_id
    cs=cross.assign(key=cross.competition_id+'|'+cross.round_type_id)
    avg=np.zeros((a['P'],5));den=np.bincount(a['panel'],weights=p['rank'],minlength=a['P'])
    for j in range(5):avg[:,j]=np.bincount(a['panel'],weights=p['h'][:,j]*p['rank'],minlength=a['P'])/np.maximum(den,1)
    for label,col in [('six_face','optimal_cross_all_six_faces'),('white_yellow','optimal_cross_white_yellow')]:
        lengths=cs.pivot(index='key',columns='scramble_num',values=col).loc[key].to_numpy()
        for centered in (False,True):
            kind='centered' if centered else 'raw';name=f'{label}_{kind}_correlation';field=f"cross_{'six_faces' if label=='six_face' else label}_{kind}_correlation";ll=lengths-lengths.mean(1,keepdims=True) if centered else lengths
            value=np.corrcoef(avg.ravel(),ll.ravel())[0,1];path='optimal_cross_mechanism.'+name
            metric(path,value,[d[field] for d in primary],{'scheduled_scrambles':cross.shape[0],'identified_focal_solver_rounds':int(p['rank'].sum())})
            xs=np.array([d[field] for d in primary]);put(path+'.bootstrap_mean',xs.mean(),'cross draw mean');put(path+'.bootstrap_mean_displacement',xs.mean()-value,'cross draw mean minus raw point')
    # Exact conditional logistic model; enumerate subsets of started attempts.
    X=[];Y=[];patterns=[]
    for i,ss in enumerate(times):
        started=np.flatnonzero(ss!=-2);dnf=(ss==-1).astype(float);num=int(dnf.sum())
        if not p['rank'][i] or not 0<num<len(started):continue
        features=np.column_stack([p['h'][i]/.05,np.eye(5)[:,1:]])
        patterns.append(np.array([features[list(ix)].sum(0) for ix in itertools.combinations(started,num)]));Y.append(dnf@features)
    def objective(coef):
        loss=0.;grad=np.zeros(5)
        for pat,y in zip(patterns,Y):
            scores=pat@coef;lse=logsumexp(scores);loss+=lse-y@coef;grad+=np.exp(scores-lse)@pat-y
        return loss,grad
    opt=minimize(objective,np.zeros(5),jac=True,method='BFGS',options={'gtol':1e-7,'maxiter':200})
    assert np.max(np.abs(objective(opt.x)[1]))<2e-6
    dnf='DNF_secondary.';metric(dnf+'odds_ratio_per_005_h',opt.x[0],[d['dnf_log_odds_per_005'] for d in primary],{'identified_solver_rounds':int(p['rank'].sum()),'discordant_solver_rounds':len(patterns)},True)
    for name,value,field in [('started_attempt_DNF_rate',(times==-1).sum()/((times>0).sum()+(times==-1).sum()),'dnf_started_rate'),('DNS_slot_rate',(times==-2).mean(),'dns_slot_rate')]:metric(dnf+name,value,[d[field] for d in primary])
    for name,value in [('DNF_count',int((times==-1).sum())),('DNS_count',int((times==-2).sum())),('successful_cells',int((times>0).sum()))]:put(dnf+name,value,'official status cell count')
    binary=np.where(times==-2,0,(times==-1).astype(float));ba=matrices(rows,np.where(times==-2,0,100),binary);bfit=moments(ba,np.ones(len(rows),bool));metric(dnf+'binary_shared_covariance',bfit['b'],[d['binary_dnf_shared_covariance'] for d in primary])
    for prob in (0,.01,.05,.10,.20):
        name=f'replacement_sensitivity.p_{prob:.2f}'
        metric(name+'.scaled_tau',fit['tau']/(1-prob)**2,[d['fit_tau']/(1-prob)**2 for d in primary]);metric(name+'.share_using_original_D',fit['F']/(1-prob)**2,[d['F']/(1-prob)**2 for d in primary])
    perm=loadlines(DER/'analysis-permutation.jsonl')
    for name,field,observed in [('F_tier_aware','F',fit['F']),('gamma_over_D','gamma_over_D',fit['gamma_over_D']),('R_geometric_person_year','logR',p['theta'])]:
        xs=np.array([d[field] for d in perm]);base='permutation_negative_control.'+name
        trans=field=='logR';reference=float(np.exp(xs.mean()) if trans else xs.mean())
        for key,v in [('reference_mean',reference),('upper_tail_probability_plus_one',(1+(xs>=observed).sum())/(len(xs)+1)),('valid_draws',len(xs))]:put(base+'.'+key,float(v),'independent aggregation of permutation-level derived records; R reference is exp(mean log R)')
        for j,v in enumerate(np.quantile(xs,[.025,.975])):put(base+f'.central_95_permutation_range[{j}]',float(np.exp(v) if trans else v),'permutation range on registered endpoint scale, not sampling CI')
    deletions=loadlines(DER/'analysis-solver-deletions.jsonl');di=loadlines(DER/'analysis-deletion-intervals.jsonl')
    put('solver_deletion.deletions',len(deletions),'all-deletion table count')
    for name,field in [('F_tier_aware','F'),('R_geometric_person_year','logR')]:
        order=sorted(deletions,key=lambda d:d[field]);base='solver_deletion.metrics.'+name
        for j,dd in enumerate([order[0],order[-1]]):
            value=np.exp(dd[field]) if field=='logR' else dd[field];put(base+f'.point_range[{j}]',value,'min/max of complete deletion-level derived table')
            mask=rows.person_id!=dd['solver'];pp=point(rows[mask].reset_index(drop=True),times[mask],roster);pv=pp['theta'] if field=='logR' else pp['fit']['F'];metric(base+f'.endpoint_measurements[{j}].measurement',pv,[d[str(dd['solver_index'])][field] for d in di],{'available_person_years':len(pp['sel']),'tier_supported_finals':pp['n']['tier_supported_finals']},field=='logR',field=='logR')
    print('Sensitivity, DNF and mechanism points recomputed; rebuilding prediction splits.',flush=True)
    for fixed in (False,True):
        for k in (2,5,10,20):prediction(rows,a,k,fixed)
    # Simulation recovery and revised boundary errors, from individual datasets.
    sim=loadlines(EP/'analysis/amendment/replication.jsonl');truth=loadlines(DER/'gate-population-truth.jsonl');truths={}
    for case in {d['case'] for d in truth}:truths[case]=np.array([d['oracle_log_R'] for d in truth if d['case']==case])
    for case in ('small_shared','informative_dnf'):
        xs=np.array([d['point'] for d in sim if d['case']==case]);oracle=truths[case];mu=oracle.mean();err=xs-mu;base='frozen_simulation_stresses.quantified_MCAR_informative_DNF_stress.'+case
        se=xs.std(ddof=1)/np.sqrt(len(xs));ose=oracle.std(ddof=1)/np.sqrt(len(oracle))
        for name,value,endpoints,exponent in [('mean_estimated_R',xs.mean(),xs.mean()+np.array([-1,1])*1.95996398454*se,True),('mean_estimation_error_log_R',err.mean(),err.mean()+np.array([-1,1])*1.95996398454*se,False),('oracle_R',mu,mu+np.array([-1,1])*1.95996398454*ose,True),('dataset_error_central_95_range',err.mean(),np.quantile(err,[.025,.975]),False)]:
            put(base+'.'+name+'.estimate',float(np.exp(value) if exponent else value),'dataset-level synthetic recovery / independent truth integration')
            for j,v in enumerate(endpoints):put(base+'.'+name+f'.interval_95[{j}]',float(np.exp(v) if exponent else v),'simulation precision or error range')
    boundary=[d for d in sim if d['case']=='boundary'];line=np.log(1.10)
    put('simulation.boundary_datasets',len(boundary),'independent synthetic dataset count')
    for name,op in [('false_holds',lambda lo,hi:lo>line),('false_fails',lambda lo,hi:hi<=line)]:put('simulation.'+name,np.mean([op(*d['intervals']['B']) for d in boundary]),'procedure B separate boundary error rates')
    put('verdict.threshold',1.10,'METHOD unchanged registered threshold')
    lo=M['primary.R_geometric_person_year.interval_95[0]'];hi=M['primary.R_geometric_person_year.interval_95[1]']
    gates=a['P']>=500 and times.size>=20000 and len(sel)>=100 and n['tier_supported_finals']>=500 and n['successful_cells']>=20000 and fit['D']>0 and M['primary.R_geometric_person_year.valid_draws']>=1900
    put('verdict.outcome',('Belief holds' if lo>1.10 else 'Belief fails' if hi<=1.10 else 'Inconclusive') if gates else 'Inconclusive','registered outcome table applied after coverage and valid-draw gates')
    canonicalize(rows,times,roster,p)
    return rows,times

def canonicalize(rows,times,roster,p):
    # Canonical result paths, without consulting the reported results.
    for key,value in list(M.items()):
        k=key.replace('.central_95_range[','.central_95_draw_range[')
        k=re.sub(r'coverage.tier_by_year.(\d+)\.',r'coverage.tier_by_year[year=\1].',k)
        if k.startswith('bootstrap_exposure.'):
            k=k.removesuffix('.draws')+'.n' if k.endswith('.draws') else k
        k=k.replace('.scaled_tau.','.shared_variance_tau.').replace('.share_using_original_D.','.variance_share_with_original_D.')
        if k.startswith('permutation_negative_control.'):
            k=k.replace('.reference_mean','.estimate').replace('.upper_tail_probability_plus_one','.one_sided_alignment_tail_probability_plus_one').replace('.central_95_permutation_range[','.interval_95[')
        k=k.replace('attempt_position_sensitivities.confirmation_beta.R.','attempt_position_sensitivities.confirmation_beta.R_geometric_person_year.').replace('attempt_position_sensitivities.yearly_beta.R.','attempt_position_sensitivities.yearly_beta.R_geometric_person_year.')
        if k in ('DNF_secondary.DNF_count','DNF_secondary.DNS_count','DNF_secondary.successful_cells','aggregation_and_tier_sensitivities.equal_tier_attrition'):k+='.estimate'
        if k!=key:put(k,value,E[key])
    for name in ('confirmation_beta','yearly_beta'):
        for endpoint in ('F_tier_aware','tier_interaction_share_gamma_over_D'):
            for suffix in ('estimate','interval_95[0]','interval_95[1]','valid_draws','n.tier_supported_finals','n.successful_cells'):
                original='primary.'+endpoint+'.'+suffix
                put('attempt_position_sensitivities.'+name+'.'+endpoint+'.'+suffix,M[original],'tier position refit absorbs initial global beta; '+E[original])
    put('robustness.complete_success.masked_solver_rounds.estimate',M['census.incomplete_solver_rounds'],'count of raw incomplete solver-rounds')
    put('robustness.clipped_centered_logs.clipped_cells.estimate',M['census.clipped_cells'],'count of raw centered logs beyond clipping bounds')
    put('coverage.structural.solver_final_incidence_rows',len(rows),'raw solver-final incidence census')
    put('coverage.structural.structurally_eligible_person_years',len(roster),'raw person-years meeting five-final gate')
    for base in ('primary','robustness.complete_success','robustness.clipped_centered_logs'):
        if base=='primary':
            available=set(zip(rows.iloc[p['sel']].person_id,rows.iloc[p['sel']].year))
            selected_rows,slots=selected(rows,times,roster)
            successful=set(zip(rows.iloc[selected_rows].person_id,rows.iloc[selected_rows].year))
            for name,value in [('no_success_seasons',len(roster-successful)),('unidentified_extrema',len(successful-available)),('absent_seasons',0)]:
                put(base+'.coverage.'+name,value,'original structural roster minus independently selected/identified seasons')
                if name!='absent_seasons':put('coverage.census_measurements.'+name+'.estimate',value,'original season selection census')
    for name in ('all_finalists','complete_success','clipped_centered_logs'):
        for endpoint in ('share','within_solver_denominator'):
            for count in ('solver_rounds_with_contrasts','successful_cells'):
                original='common_only_comparators.'+name+'.coverage.'+count
                put('common_only_comparators.'+name+'.'+endpoint+'.n.'+count,M[original],E[original])
    # Every listed source statistic is a calculation from unsummarized inputs.
    for key in ('DNF_secondary.started_attempt_DNF_rate','DNF_secondary.binary_shared_covariance'):
        put(key+'.n.started_attempts',int((times!=-2).sum()),'raw started-slot census')
    put('DNF_secondary.DNS_slot_rate.n.included_attempt_slots',times.size,'raw all-slot census')
    put('DNF_secondary.binary_shared_covariance.n.solver_rounds',len(rows),'raw solver-round census')
        # Human-readable extra scope counts absent from the result summary.
    census={key.split('.',1)[1]:value for key,value in M.items() if key.startswith('census.')}
    (EP/'analysis/claim_census.json').write_text(json.dumps({'census':census},indent=2)+'\n')


def pilot_checks(claims):
    if not any(c.get('pilot_kind') for c in claims):return
    import importlib.util,tempfile
    root=EP.parents[2];path=root/'ideation/rounds/r5/pilot-S1/pilot.py'
    spec=importlib.util.spec_from_file_location('frozen_exploration_bootstrap',path)
    frozen=importlib.util.module_from_spec(spec);spec.loader.exec_module(frozen)
    rows,times,y,panel,P=frozen.load_slice();rows=rows.rename(columns={'result_id':'id'})
    a=matrices(rows,times);fit=moments(a,np.ones(len(rows),bool))
    put('fit.within_solver_share',fit['b']/fit['total'],'independent raw exploration-cell moment calculation')
    # Reselecting pilot uncertainty is rerun, with its original algorithm and seed.
    # Temporary output roots protect all existing pilot artifacts.
    C=a['C'];z=a['z'];S=(z*z).sum(1);d=np.maximum(a['m']-1,0).astype(float)
    ci=frozen.bootstrap(C,z,S,d,panel,rows,1000)
    for j,value in enumerate(ci['competition_solver']['within_solver_share']):
        put(f'bootstrap_95.competition_solver.within_solver_share[{j}]',value,'frozen 1000-draw pilot product bootstrap rerun, original seed/draw order')
    train=moments(a,rows.year.to_numpy()<2019);h,rank=peers(a,train['beta'])
    modern=rows[rows.year.between(2019,2025)]
    roster=modern.groupby(['person_id','year']).competition_id.nunique();roster=set(roster[roster>=5].index)
    selected_rows,slots=selected(rows,times,roster)
    assert rank[selected_rows].all(), 'Unidentified original pilot extreme'
    put('aggregate_unshrunk_ratio',float(np.exp(-h[selected_rows,slots[selected_rows]].mean())),'independent raw exploration selection and whole-focal peer exclusion')
    put('n',len(selected_rows),'independent pilot person-year census')
    with tempfile.TemporaryDirectory(prefix='scramble-pilot-claims-') as directory:
        frozen.OUT=Path(directory);frozen.DATA=Path(directory)
        result,_,_=frozen.extreme_analysis(rows.rename(columns={'id':'result_id'}),times,y,C,z,S,d,panel,{},B=2000)
    for j,value in enumerate(result['aggregate_unshrunk_95']):
        put(f'aggregate_unshrunk_95[{j}]',value,'frozen 2000-draw pilot refit/reselection bootstrap rerun with original seed')
    print('Exploratory pilot points independently recomputed and frozen intervals rerun.',flush=True)

def source_checks(claims):
    records=[c for c in claims if c.get('context_kind')=='record']
    if records:
        wanted={c['competition_id'] for c in records};chunks=[]
        for d in pd.read_csv(DER/'source/WCA_export_results.tsv',sep='\t',keep_default_na=False,chunksize=400000,dtype={'event_id':str}):
            chunks.append(d[(d.event_id=='333')&d.competition_id.isin(wanted)])
        table=pd.concat(chunks)
        for c in records:
            d=table[(table.competition_id==c['competition_id'])&table.person_name.str.contains(c['person_match'],regex=False)]
            col='best' if c['record_type']=='single' else 'average'
            flag='regional_single_record' if c['record_type']=='single' else 'regional_average_record'
            d=d[d[flag]=='WR'];assert len(d), f"No official WR row: {c['id']}"
            val=d[col].astype(int).min()/100
            for v in c['values']:put(c['id']+':'+v['source_url'],val,'raw official WR-flagged WCA centisecond results; historical attribution, not a current-record claim')
    sources=EP/'analysis/claim_sources';manifest=json.loads((sources/'manifest.json').read_text())
    for c in claims:
        if c.get('context_kind') not in ('regulation','reconstruction','glossary'):continue
        for v in c['values']:
            entry=manifest[v['source_url'].split('#')[0]];raw=(sources/entry['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256']
            markup=raw.decode();markup=re.sub(r'<(script|style)\b.*?</\1>','',markup,flags=re.S)
            lines=html.unescape(re.sub('<[^>]+>',' ',re.sub(r'<br\s*/?>','\n',markup)))
            text=re.sub(r'\s+',' ',lines);mode=c['source_parser'];label=v.get('label','')
            if mode=='ao5':
                fragment=re.search(r'9f8\s*\).*?(?=9f9)',text).group()
                match=re.search(r'(\d+) attempts',fragment);value=int(match.group(1)) if match else 5 if 'five' in fragment.lower() else None
                if label=='middle':
                    match=re.search(r'remaining (\d+) (?:results|attempts)',fragment);value=int(match.group(1)) if match else 3 if 'three' in fragment.lower() else None
                assert value is not None, 'Ao5 rule quantity missing'
            elif mode=='failures':
                fragment=re.search(r'9f9\s*\).*?(?=9g)',text).group();assert 'more than one' in fragment.lower();value=2
            elif mode=='random_min':
                fragment=re.search(r'4b3\s*\).*?(?=4b4)',text).group();value=int(re.search(r'at least (\d+) moves',fragment).group(1))
            elif mode=='move_tokens':
                stages={}
                for line in lines.splitlines():
                    match=re.search(r"((?:[URFDLBMESurfdlbxyz](?:[23])?'?\s+)+)//\s*(.+?)\s*$",line)
                    if match:stages[match.group(2).strip()]=len(match.group(1).split())
                if label=='total':value=sum(vv for kk,vv in stages.items() if kk!='inspection')
                else:value=stages[label]
            elif mode=='wang_stats':
                # Preserved web-tool extraction; direct HTTP was rate-limited.
                normalized=text.replace('\\n',' ').replace('\n',' ')
                value=int(re.search(r'Cross\s+(\d+)',normalized).group(1)) if label=='cross' else int(re.search(r'Free Pair\s+(\d+)',normalized).group(1))
            else:
                fragment=text
                if c.get('source_rule'):
                    rule=re.escape(c['source_rule']);match=re.search(rule+r'\s*\).*?(?= \d+[a-z]| Article |$)',text)
                    assert match, 'Missing source rule '+c['source_rule'];fragment=match.group()
                value=all(phrase.lower() in fragment.lower() for phrase in c['source_phrases'])
            put(c['id']+':'+v['source_url']+':'+label,value,'hash-checked saved source; '+mode+' parser')

def agrees(stated,value,digits):
    if digits is None or isinstance(stated,(str,bool)):return stated==value
    return np.isfinite(value) and abs(float(value)-float(stated))<=.5*10**(-digits)+1e-12

def main():
    claims=json.loads((EP/'CLAIMS.json').read_text())['claims'];independent();pilot_checks(claims)
    try:source_checks(claims)
    except Exception as error:print('Source verification error:',type(error).__name__,str(error),flush=True)
    report=[]
    for claim in claims:
        values=[]
        for v in claim['values']:
            key=v.get('key') or claim['id']+':'+v['source_url']+(':'+v.get('label','') if claim.get('context_kind')!='record' else '')
            row={**v}
            try:
                value=M[key];row.update(recomputed=value.item() if isinstance(value,np.generic) else value,evidence=E[key],passed=agrees(v['stated'],value,v['digits']))
            except Exception as error:row.update(passed=False,error=str(error))
            values.append(row)
        report.append({'id':claim['id'],'passed':bool(values) and all(v['passed'] for v in values),'values':values})
    failed=[c for c in report if not c['passed']]
    out={'all_passed':not failed,'claim_count':len(claims),'verified_claims':len(claims)-len(failed),'verified_values':sum(v['passed'] for c in report for v in c['values']),'claims':report,'note':__doc__,'input_hashes':{str(path.relative_to(EP)):hashlib.sha256(path.read_bytes()).hexdigest() for path in [EP/'recheck/raw_rows.pkl',EP/'recheck/raw_times.npy',EP/'recheck/extraction.json',*sorted(DER.glob('analysis-*.jsonl')),EP/'analysis/amendment/replication.jsonl',DER/'gate-population-truth.jsonl',DER/'cross.parquet',EP/'analysis/claim_sources/manifest.json']},'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'claims_sha256':hashlib.sha256((EP/'CLAIMS.json').read_bytes()).hexdigest()}
    (EP/'analysis/claims_check.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(f"Claims: {len(claims)}; verified: {len(claims)-len(failed)}; failed: {len(failed)}.")
    for c in failed[:12]:print(c['id'],json.dumps([v for v in c['values'] if not v['passed']],ensure_ascii=False)[:450])
    return bool(failed)
if __name__=='__main__':sys.exit(main())
