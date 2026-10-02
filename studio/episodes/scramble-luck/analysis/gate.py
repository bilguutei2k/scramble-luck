#!/usr/bin/env python3
"""Outcome-blind, whole-pipeline known-truth validation on real incidence.

Usage: gate.py --benchmark; gate.py [--workers 10]. 200 datasets/process,
500 bootstrap draws/dataset, method fallback order fixed by METHOD.md.
Workers use only sign-only structure and synthetic training outcomes. Checkpoint
JSONL bulk records are under data/derived; gate.json and GATE.md are reviewable.
"""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import argparse, time, json, multiprocessing as mp, importlib.util
import numpy as np
from numba import njit
from common import OUT, DERIVED, PILOT, FROZEN, SEED, BETA, sha, dump, progress, code_hashes
from engine import Structure, Dataset, contributions, accumulate, moment, project

CASES = {
    'null': {'tau':0.,'gamma':0.},
    'small_shared': {'tau':.0014,'gamma':0.},
    'large_shared': {'tau':.0121,'gamma':0.},
    'shared_plus_tier_interaction': {'tau':.0014,'gamma':.0025},
    'informative_dnf': {'tau':.0014,'gamma':0.},
    'random_replacement_10_percent': {'tau':.0014,'gamma':0.},
    'pure_attempt_slot_shock': {'tau':.0121,'gamma':0.},
}
REPS=200;DRAWS=500
ST=None
POP_TRUTH_DRAWS=10000

def initialize():
    global ST
    ST=Structure()

@njit(cache=True)
def true_tiers(skill,sidx,round_rows,rptr,R):
    tier=np.empty(len(sidx))
    for r in range(R):
        ix=round_rows[rptr[r]:rptr[r+1]]
        median=np.median(skill[sidx[ix]])
        for i in ix:tier[i]=1. if skill[sidx[i]]<median else -1.
    return tier

def generate(st,case,rep,arrays_only=False):
    case_index=list(CASES).index(case)
    rng=np.random.default_rng(np.random.SeedSequence([SEED,case_index,rep]))
    p=CASES[case]
    skill=rng.normal(np.log(12),.30,st.S)
    shared=rng.normal(0,np.sqrt(p['tau']),(st.R,5));shared-=shared.mean(1,keepdims=True)
    interaction=rng.normal(0,np.sqrt(p['gamma']),(st.R,5));interaction-=interaction.mean(1,keepdims=True)
    # True tier is baseline skill, not a tier inferred from confirmation outcomes.
    tier=true_tiers(skill,st.sidx,st.round_rows,st.rptr,st.R)
    latent=shared[st.ridx]+tier[:,None]*interaction[st.ridx]
    if case=='random_replacement_10_percent':
        replacement=rng.random((st.N,5))<.10
        other=rng.normal(0,np.sqrt(p['tau']),(st.N,5))
        latent=np.where(replacement,other,latent)
    residual_sd=np.sqrt(np.where(tier>0,.018,.026))
    eps=rng.normal(size=(st.N,5))*residual_sd[:,None]
    y=skill[st.sidx,None]+rng.normal(0,.04,(st.N,1))+BETA+latent+eps
    q=st.status==1
    if case=='informative_dnf':
        # Preserve each real result's DNF count and DNS positions. DNF locations
        # favour difficult shared slots: conditional odds multiply by exp(12*s).
        score=12*shared[st.ridx]+rng.gumbel(size=(st.N,5))
        score[st.status==-2]=-np.inf
        dnfs=(st.status==-1).sum(1)
        ranking=np.argsort(-score,axis=1)
        q=(st.status!=-2)
        for k in range(5):
            rows=np.where(dnfs>k)[0];q[rows,ranking[rows,k]]=False
    y[~q]=np.nan
    train_values=st.tg[[f'v{j}' for j in range(1,6)]].to_numpy()
    ts=rng.normal(0,np.sqrt(FROZEN['hyperparameters']['shared_variance']),(st.TR,5))
    ts-=ts.mean(1,keepdims=True)
    ty=skill[st.tsidx,None]+rng.normal(0,.04,(len(st.tg),1))+BETA+ts[st.tridx]+rng.normal(0,np.sqrt(FROZEN['hyperparameters']['residual_variance']),(len(st.tg),5))
    ty[train_values<=0]=np.nan
    if arrays_only:return y,ty,latent
    return Dataset(st,y,ty,latent)

@njit(cache=True)
def oracle_selected(row_min,season_rows,season_ptr):
    chosen=np.full(len(season_ptr)-1,-1,dtype=np.int64)
    for s in range(len(chosen)):
        best=np.inf
        for p in range(season_ptr[s],season_ptr[s+1]):
            i=season_rows[p]
            if row_min[i]<best:best=row_min[i];chosen[s]=i
    return chosen[chosen>=0]

def truth_task(args):
    case,rep=args
    y,ty,latent=generate(ST,case,rep,arrays_only=True)
    C,z,S,d,means=contributions(y)
    _,lz,lss,_,_=contributions(np.where(np.isfinite(y),latent,np.nan))
    lst=accumulate(C,lz,lss,d,ST.ridx,ST.sidx,np.ones(ST.S),ST.R,np.zeros(ST.N,dtype=np.int8),-1)
    row_min=np.min(np.where(np.isfinite(y),y,np.inf),axis=1)
    selected=oracle_selected(row_min,np.concatenate(ST.season_rows),np.r_[0,np.cumsum([len(x) for x in ST.season_rows])])
    h,rank,_=project(lst[0],lst[1],C,lz,ST.ridx,ST.sidx,np.ones(ST.S),selected,np.zeros(5))
    keep=rank==4;rows=selected[keep];js=np.argmin(np.where(np.isfinite(y[rows]),y[rows],np.inf),axis=1)
    return {'case':case,'replicate':rep,'oracle_log_R':float(-np.mean(h[keep,js]))}

def population_truth(pool):
    checkpoint=DERIVED/'gate-population-truth.jsonl'
    rows=[json.loads(s) for s in checkpoint.read_text().splitlines()] if checkpoint.exists() else []
    done={(x['case'],x['replicate']) for x in rows}
    cases=[x for x in CASES if x not in ('null','pure_attempt_slot_shock')]
    tasks=[(case,100000+rep) for case in cases for rep in range(POP_TRUTH_DRAWS) if (case,100000+rep) not in done]
    progress(f'Integrating process-level oracle log R with {POP_TRUTH_DRAWS:,} independent synthetic datasets/process; seeds disjoint from validation and calibration.')
    with checkpoint.open('a') as f:
        for result in pool.imap_unordered(truth_task,tasks,chunksize=10):
            f.write(json.dumps(result)+'\n');rows.append(result)
            if len(rows)%2000==0:f.flush();progress(f'Population-truth integration: {len(rows)}/{len(cases)*POP_TRUTH_DRAWS} independent datasets complete.')
    truths={'null':{'log_R':0.,'R':1.,'integration_datasets':0,'log_R_MC_standard_error':0.,'log_R_MC_999_interval':[0.,0.]}}
    for case in cases:
        x=np.array([r['oracle_log_R'] for r in rows if r['case']==case]);assert len(x)==POP_TRUTH_DRAWS
        mean=float(x.mean());se=float(x.std(ddof=1)/np.sqrt(len(x)))
        truths[case]={'log_R':mean,'R':float(np.exp(mean)),'integration_datasets':len(x),'log_R_MC_standard_error':se,
                      'log_R_MC_999_interval':[mean-3.290527*se,mean+3.290527*se]}
    truths['pure_attempt_slot_shock']={**truths['large_shared'],'same_distribution_as':'large_shared; interpreted as synchronized slot shock'}
    dump('population-truth.json',truths)
    return truths

def fixture_checks():
    """Compare independently optimized implementation with hashed frozen code."""
    assert sha(PILOT/'pilot.py')==FROZEN['algorithm_hashes']['pilot.py']
    assert sha(PILOT/'validate.py')==FROZEN['algorithm_hashes']['validate.py']
    spec=importlib.util.spec_from_file_location('frozen_pilot',PILOT/'pilot.py')
    pilot=importlib.util.module_from_spec(spec);spec.loader.exec_module(pilot)
    rng=np.random.default_rng(SEED+761)
    ridx=np.repeat(np.arange(60),12);sidx=np.tile(np.arange(12),60)
    y=rng.normal(size=(len(ridx),5));y[rng.random(y.shape)<.08]=np.nan
    C,z,S,d,_=contributions(y);pc,pz,ps,pd=pilot.contributions(y)
    checks=[{'name':'frozen_missing_pattern_contributions','pass':bool(all(np.allclose(a,b) for a,b in zip((C,z,S,d),(pc,pz,ps,pd))))}]
    sw=rng.integers(0,4,12).astype(float);cw=rng.integers(0,4,60).astype(float)
    st=accumulate(C,z,S,d,ridx,sidx,sw,60,np.zeros(len(ridx),dtype=np.int8),-1)
    pst=pilot.aggregate(pc,pz,ps,pd,ridx,60,sw[sidx]);noise=pilot.aggregate(pc,pz,ps,pd,ridx,60,sw[sidx]**2)[0]
    old,_=pilot.moment(pst,cw,noise);new=moment(st,cw)
    checks.append({'name':'frozen_squared_solver_weight_noise_trace','pass':bool(np.allclose(new['b'],old['shared_variance']) and np.allclose(new['beta'],old['position'])),'maximum_absolute_error':float(abs(new['b']-old['shared_variance']))})
    # Unshrunk projection from pilot extreme_analysis, full focal multiplicity excluded.
    rows=np.arange(0,len(ridx),7)
    h,rank,Ap=project(st[0],st[1],C,z,ridx,sidx,sw,rows,BETA)
    vp=st[1][ridx[rows]]-z[rows]*sw[sidx[rows],None]-np.einsum('nij,j->ni',Ap,BETA)
    independent=np.einsum('nij,nj->ni',np.linalg.pinv(Ap,rcond=1e-10),vp)
    checks.append({'name':'frozen_unshrunk_extreme_peer_projection','pass':bool(np.allclose(h,independent)),'maximum_absolute_error':float(np.max(np.abs(h-independent)))})
    checks.append({'name':'centering_trace_identities','pass':bool(np.allclose(np.trace(C,axis1=1,axis2=2),d) and np.allclose(np.einsum('nij,njk->nik',C,C),C))})
    from engine import tier_fit, select_best
    tiers=np.tile(np.r_[np.zeros(6),np.ones(6)],60).astype(np.int8)
    sf=accumulate(C,z,S,d,ridx,sidx,sw,60,tiers,0)
    ss=accumulate(C,z,S,d,ridx,sidx,sw,60,tiers,1)
    wf=sw[sidx]*(tiers==0);ws=sw[sidx]*(tiers==1)
    pf=pilot.aggregate(C,z,S,d,ridx,60,wf);ps=pilot.aggregate(C,z,S,d,ridx,60,ws)
    nf=pilot.aggregate(C,z,S,d,ridx,60,wf**2)[0];ns=pilot.aggregate(C,z,S,d,ridx,60,ws**2)[0]
    old=pilot.tier_moment(pf,ps,cw,nf,ns);new=tier_fit(sf,ss,cw)
    checks.append({'name':'frozen_tier_moment_and_residual_variances','pass':bool(np.allclose(new['tau'],old['shared_variance']) and np.allclose(new['gamma'],old['interaction_variance']) and np.allclose(new['fast_residual_variance'],old['fast_residual']) and np.allclose(new['slow_residual_variance'],old['slow_residual']))})
    chosen,absent,no_success=select_best(np.array([0,1,2,3,4,5]),np.array([0,3,6]),
        np.array([1.,2.,3.,np.nan,np.nan,np.nan]),np.array([0,1,2,0,1,2]),np.zeros(6,dtype=np.int64),np.ones(1),np.array([0.,2.,1.]))
    checks.append({'name':'seasonal_reselection_fixed_roster_and_no_runner_up_for_missing_success','pass':bool(chosen.tolist()==[1,-1] and absent==0 and no_success==1)})
    assert all(x['pass'] for x in checks)
    return checks

def task(args):
    case,rep,method=args;t=time.perf_counter()
    ds=generate(ST,case,rep)
    point=ds.run();truth=ds.run(oracle=True)
    rng=np.random.default_rng(SEED) # Each dataset exact seed and competition→solver order.
    draws=np.empty((DRAWS,3));missing=np.zeros(DRAWS);available=np.zeros(DRAWS)
    for b in range(DRAWS):
        result=ds.run(*ST.weights(rng,method))
        draws[b]=[result['logR'],result['F'],result['gamma_over_D']]
        missing[b]=result['absent_seasons'];available[b]=result['available_extrema']
    valid=np.isfinite(draws[:,0]);ci=np.quantile(draws[valid,0],[.025,.975]) if valid.any() else np.array([np.nan,np.nan])
    return {'case':case,'replicate':rep,'method':method,'estimated_log_R':point['logR'],
       'oracle_log_R':truth['logR'],'log_R_error':point['logR']-truth['logR'],
       'log_R_interval_95':ci.tolist(),'truth_covered':bool(ci[0]<=truth['logR']<=ci[1]),
       'valid_R_draws':int(valid.sum()),'valid_F_draws':int(np.isfinite(draws[:,1]).sum()),
       'valid_gamma_draws':int(np.isfinite(draws[:,2]).sum()),
       'mean_absent_seasons_per_draw':float(missing.mean()),'mean_available_extrema_per_draw':float(available.mean()),
       'point_available_extrema':point['available_extrema'],'point_F':point['F'],
       'point_gamma_over_D':point['gamma_over_D'],'seconds':time.perf_counter()-t}

def summarize(rows,method,truths):
    out={}
    for case in CASES:
        records=[x for x in rows if x['case']==case and x['method']==method]
        if len(records)!=REPS:continue
        truth=truths[case]['log_R']
        estimate_mean=float(np.mean([x['estimated_log_R'] for x in records]))
        bias=estimate_mean-truth
        ci=np.array([x['log_R_interval_95'] for x in records])
        coverage=float(np.mean((ci[:,0]<=truth)&(truth<=ci[:,1])))
        low,high=truths[case]['log_R_MC_999_interval']
        breaks=ci.ravel();breaks=breaks[(breaks>=low)&(breaks<=high)]
        grid=np.r_[low,high,truth,breaks,breaks-1e-12,breaks+1e-12]
        grid=grid[(grid>=low)&(grid<=high)]
        numeric_coverage=np.mean((ci[:,0,None]<=grid)&(grid<=ci[:,1,None]),axis=0)
        valid=all(x['valid_R_draws']==DRAWS and x['valid_F_draws']==DRAWS and x['valid_gamma_draws']==DRAWS for x in records)
        judged=case!='pure_attempt_slot_shock'
        out[case]={'datasets':len(records),'bootstrap_draws_per_dataset':DRAWS,'absolute_bias_log_R':abs(bias),
          'signed_bias_log_R':bias,'coverage_95':coverage,'bias_pass':abs(bias)<=.005,
          'coverage_pass':.92<=coverage<=.99,'all_pipeline_draws_valid':valid,
          'judged':judged,'pass':bool((not judged) or (abs(bias)<=.005 and .92<=coverage<=.99 and valid)),
          'mean_estimated_R':float(np.exp(np.mean([x['estimated_log_R'] for x in records]))),
          'population_true_R':truths[case]['R'],
          'population_log_R_integration_SE':truths[case]['log_R_MC_standard_error'],
          'coverage_range_over_truth_integration_999_interval':[float(numeric_coverage.min()),float(numeric_coverage.max())],
          'finite_oracle_attribution_bias_log_R':float(np.mean([x['log_R_error'] for x in records])),
          'finite_oracle_diagnostic_coverage':float(np.mean([x['truth_covered'] for x in records])),
          'mean_oracle_R':float(np.exp(np.mean([x['oracle_log_R'] for x in records]))),
          'mean_F':float(np.mean([x['point_F'] for x in records])),
          'mean_gamma_over_D':float(np.mean([x['point_gamma_over_D'] for x in records])),
          'mean_pipeline_seconds':float(np.mean([x['seconds'] for x in records]))}
    return out

def report(methods,checks,benchmark,selected,complete,truths):
    gate_pass=selected is not None and complete
    out={'gate_passed':gate_pass,'verdict_if_failed':'inconclusive: uncertainty not validated',
      'positive_confirmation_times_read':False,'frozen_model_id':FROZEN['id'],
      'selected_bootstrap':selected,'datasets_per_process':REPS,'bootstrap_draws_per_dataset':DRAWS,
      'seed':SEED,'acceptance':{'max_absolute_bias_log_R':.005,'coverage_min':.92,'coverage_max':.99,'slot_shock_judged':False},
      'fallback_order':['pigeonhole','competition_only','solver_only'],'methods':methods,
      'fallback_futility_rule':'Initial pigeonhole: all seven processes completed. Reject fallback after a fully completed 200-dataset process fails; accept fallback only after all seven complete and all judged processes pass.',
      'dataset_counts_by_method':{method:{case:sum(json.loads(line)['case']==case for line in (DERIVED/f'gate-{method}.jsonl').read_text().splitlines()) for case in CASES} for method in methods},
      'synthetic_fixture_checks':checks,'benchmark':benchmark,'complete':complete,'code_sha256':code_hashes(),
      'process_parameters':CASES,'population_truth':truths,
      'truth_definition':'Process expectation of original-selection oracle log R, integrated using 10,000 independent synthetic datasets/process; finite-oracle attribution coverage retained as diagnostic; see DEVIATIONS.md.',
      'informative_dnf_stress':'Each real solver-final DNF count/DNS locations retained; conditional DNF position odds proportional to exp(12*shared_slot).',
      'mcar_stress':'All other cases retain observed DNF/DNS masks independently of generated times.'}
    dump('gate.json',out)
    lines=['# Pre-confirmation validation gate','',
           '**PASS**' if gate_pass else ('**FAIL: inconclusive: uncertainty not validated**' if complete else '**IN PROGRESS**'),'',
           'No positive confirmation solve time has been read. The gate uses real solver-final incidence and sign-only status masks with synthetic log times.',
           '',f'Each process: {REPS} independent datasets; {DRAWS} exact cluster-bootstrap draws per dataset. Seed {SEED}. Ten worker processes; numerical libraries limited to one thread each.',
           '', 'Every draw recomputes training positions/moments, weighted skill references, tier moments with squared-weight noise traces, focal-solver-excluded peer contrasts, fixed-roster seasonal minimum selection and geometric R.',
           '', 'Sampling truth is the process expectation of oracle log R at originally selected extrema. It is integrated using 10,000 independent synthetic datasets/process with disjoint seeds; null truth is exactly zero. Integration SE and the coverage range over its 99.9% Monte Carlo interval are reported. Finite-dataset oracle coverage is retained as an attribution diagnostic. See DEVIATIONS.md for underspecified contract details and the implementation correction.',
           '',f"Measured warm pipeline time: {benchmark['seconds_per_pipeline_run']:.4f} seconds. Planned pigeonhole CPU time: {benchmark['estimated_cpu_hours']:.2f} hours; ideal ten-core wall time: {benchmark['estimated_ten_core_wall_minutes']:.1f} minutes.",
           '', '| Bootstrap | Process | Bias log R | Coverage | Mean true R | Mean estimated R | Decision |',
           '|---|---|---:|---:|---:|---:|---|']
    for method, cases in methods.items():
        for name,x in cases.items():
            decision=('reported only: slot shock absorbed' if not x['judged'] else ('pass' if x['pass'] else 'FAIL'))
            lines.append(f"| {method} | {name} | {x['signed_bias_log_R']:.6f} | {x['coverage_95']:.1%} | {x['population_true_R']:.5f} | {x['mean_estimated_R']:.5f} | {decision} |")
    lines += ['',f'Selected method: {selected or "none"}.', '',
              'Acceptance requires absolute log-R bias ≤0.005 and 95% coverage between 92% and 99% in each judged process. A bias failure prevents fallback rescue; coverage fallback order is competition-only then solver-only.',
              '', 'Initial pigeonhole validation completes all seven processes. A fallback is rejected as soon as one full 200-dataset process fails: remaining processes cannot rescue its requirement to pass every process. Acceptance of a fallback still requires all seven complete processes. Partial cancelled fallback datasets remain in the bulk checkpoints but never decide acceptance. See DEVIATIONS.md.',
              '', 'All frozen-code fixture, focal exclusion, missing-pattern and squared-noise-trace checks pass.',
              '', 'Generated raw replicate records and timing/exposure diagnostics: data/derived/gate-*.jsonl. No simulated positive values are confused with confirmation observations.',
              '', 'If this gate fails, confirmation remains unopened and step 4 is not run. A registered and committed amendment would be required to proceed.']
    (OUT/'GATE.md').write_text('\n'.join(lines)+'\n')

def benchmark():
    initialize();t=time.perf_counter();ds=generate(ST,'small_shared',9999);prepared=time.perf_counter()-t
    ds.run();rng=np.random.default_rng(SEED);timings=[]
    for _ in range(10):
        t=time.perf_counter();ds.run(*ST.weights(rng));timings.append(time.perf_counter()-t)
    seconds=float(np.median(timings));total=len(CASES)*REPS*DRAWS*seconds
    out={'dataset_preparation_seconds':prepared,'seconds_per_pipeline_run':seconds,'runs_measured':10,
         'estimated_cpu_hours':total/3600,'estimated_ten_core_wall_minutes':total/10/60,
         'structure':{'finals':ST.R,'solver_finals':ST.N,'eligible_seasons':len(ST.season_keys),'solver_ids_training_confirmation_union':ST.S}}
    dump('gate-benchmark.json',out)
    progress(f"Step 3 benchmark: {seconds:.4f} s/full warm pipeline; 700,000 draws ≈{total/3600:.2f} CPU-hours, ideal ten-core ≈{total/600:.1f} min. Dataset prep {prepared:.2f} s.")
    return out

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--benchmark',action='store_true');parser.add_argument('--workers',type=int,default=10);args=parser.parse_args()
    checks=fixture_checks();bench=benchmark()
    if args.benchmark:return
    progress('Step 3 gate started: seven DGPs × 200 datasets × 500 draws, full pipeline; checkpointing each dataset, ten cores.')
    methods={};selected=None;bias_failed=False
    context=mp.get_context('spawn')
    with context.Pool(args.workers,initializer=initialize) as pool:
        truths=population_truth(pool)
        for method in ('pigeonhole','competition_only','solver_only'):
            checkpoint=DERIVED/f'gate-{method}.jsonl'
            rows=[json.loads(s) for s in checkpoint.read_text().splitlines()] if checkpoint.exists() else []
            done={(x['case'],x['replicate']) for x in rows}
            report(methods,checks,bench,None,False,truths)
            with checkpoint.open('a') as f:
                for case in CASES:
                    tasks=[(case,rep,method) for rep in range(REPS) if (case,rep) not in done]
                    for result in pool.imap_unordered(task,tasks,chunksize=1):
                        f.write(json.dumps(result,allow_nan=False)+'\n');f.flush();rows.append(result)
                        if len(rows)%20==0:
                            elapsed=sum(x['seconds'] for x in rows)/len(rows)
                            progress(f"Gate {method}: {len(rows)}/{len(CASES)*REPS} datasets complete; mean {elapsed:.1f} s/dataset/worker. Confirmation times unopened.")
                    if method!='pigeonhole':
                        partial=summarize(rows,method,truths)
                        completed=partial[case]
                        if completed['judged'] and not completed['pass']:
                            progress(f'Fallback {method} decisively rejected by completed process {case}; remaining processes cannot rescue an all-process gate.')
                            break
            methods[method]=summarize(rows,method,truths)
            judged=[x for x in methods[method].values() if x['judged']]
            bias_failed=any(not x['bias_pass'] for x in judged)
            if len(methods[method])==len(CASES) and all(x['pass'] for x in judged):selected=method;break
            if bias_failed:break
            progress(f'Gate {method} failed interval coverage; proceeding to fixed fallback order.')
    report(methods,checks,bench,selected,True,truths)
    progress(f'Step 3 gate complete: {"PASS, "+selected if selected else "FAIL — inconclusive: uncertainty not validated"}. Confirmation positive solve times remain unopened. Gate commit required next.')

if __name__=='__main__':main()
