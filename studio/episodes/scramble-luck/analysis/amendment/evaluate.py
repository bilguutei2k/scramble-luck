#!/usr/bin/env python3
"""Outcome-blind amendment evaluation. All output stays beside this script.

Read incidence/status only from structure.duckdb. Never open outcome parquets.
Uses original generator, contributions, weights, selection, peer projection and
training fit. Omits unrelated F/tier calculations from R-only bootstrap draws;
benchmark verifies equality to the full engine. Python multiprocessing: 10 cores.
"""
import os
from pathlib import Path
HERE = Path(__file__).resolve().parent
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS',
             'VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'
os.environ['NUMBA_CACHE_DIR'] = str(HERE / 'numba-cache')
import sys, json, time, argparse, multiprocessing as mp, hashlib
sys.path.insert(0, str(HERE.parent))
import numpy as np
import pandas as pd
import duckdb
from scipy.stats import norm
import gate
from common import DERIVED, BETA, SEED
from engine import Structure, contributions, accumulate, moment, project, select_best

gate.CASES['boundary'] = {'tau': .0097, 'gamma': 0.}
ST = None
Z = norm.ppf(.975)

def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, allow_nan=False,
                           default=lambda x:x.item() if isinstance(x,np.generic) else str(x))+'\n')

def initialize():
    global ST
    # Reuse Structure indexing without ever opening its usual parquets. Training
    # v columns contain categorical placeholders, used by generate ONLY as masks.
    con = duckdb.connect(str(DERIVED/'structure.duckdb'), read_only=True)
    con.execute('SET threads=1')
    frames = {}
    for name, clause in [('structure.parquet','confirmation'),
                         ('training.parquet','NOT confirmation')]:
        g = con.execute('SELECT * FROM incidence WHERE '+clause+
                        ' ORDER BY competition_id,round_type_id,person_id,result_id').fetchdf()
        if name.startswith('training'):
            for j in range(1,6): g[f'v{j}'] = g[f'status{j}']
        frames[name] = g
    con.close()
    original = pd.read_parquet
    def safe_read(path, *args, **kwargs):
        key = Path(path).name
        if key not in frames: raise RuntimeError('Unexpected input: '+str(path))
        return frames[key].copy()
    pd.read_parquet = safe_read
    try: ST = Structure()
    finally: pd.read_parquet = original
    gate.ST = ST
    calibration = HERE/'boundary-calibration.json'
    if calibration.exists(): gate.CASES['boundary']['tau'] = json.loads(calibration.read_text())['tau']

class FastR:
    def __init__(self, y, ty, latent):
        self.y, self.ty, self.latent = y, ty, latent
        self.C,self.z,self.ss,self.d,_ = contributions(y)
        self.TC,self.tz,self.tss,self.td,_ = contributions(ty)
        self.row_min = np.min(np.where(np.isfinite(y),y,np.inf),axis=1)
        self.row_min[~np.isfinite(self.row_min)] = np.nan
        self.js = np.argmin(np.where(np.isfinite(y),y,np.inf),axis=1)
        order=[]; ptr=[0]
        for ix in ST.season_rows:
            order.extend(ix[np.lexsort((ST.tie_rank[ix],self.row_min[ix]))]); ptr.append(len(order))
        self.order=np.array(order,dtype=np.int64); self.ptr=np.array(ptr,dtype=np.int64)
        self.zero=np.zeros(ST.N,dtype=np.int8)
        self.tzero=np.zeros(len(ST.tg),dtype=np.int8)
        self.ones=np.ones(ST.S)
        self.rows = self.select(np.ones(ST.C), self.ones)
        self.original = self.aggregate(self.ones)
        h,rank,_ = project(self.original[0],self.original[1],self.C,self.z,
                          ST.ridx,ST.sidx,self.ones,self.rows,BETA)
        self.rows = self.rows[rank==4]
        self.x = -h[rank==4,self.js[self.rows]]
        self.point = float(self.x.mean())

    def select(self,cw,sw):
        rows,_,_=select_best(self.order,self.ptr,self.row_min,ST.cidx,ST.sidx,sw,cw)
        return rows[rows>=0]

    def aggregate(self,sw):
        return accumulate(self.C,self.z,self.ss,self.d,ST.ridx,ST.sidx,sw,ST.R,self.zero,-1)

    def oracle(self):
        _,lz,lss,_,_=contributions(np.where(np.isfinite(self.y),self.latent,np.nan))
        agg=accumulate(self.C,lz,lss,self.d,ST.ridx,ST.sidx,self.ones,ST.R,self.zero,-1)
        h,rank,_=project(agg[0],agg[1],self.C,lz,ST.ridx,ST.sidx,self.ones,self.rows,np.zeros(5))
        assert np.all(rank==4)
        return float(-np.mean(h[np.arange(len(h)),self.js[self.rows]]))

    def draw(self,cw,sw,tw):
        train=accumulate(self.TC,self.tz,self.tss,self.td,ST.tridx,ST.tsidx,sw,ST.TR,self.tzero,-1)
        beta=moment(train,tw[ST.train_comp])['beta']
        agg=self.aggregate(sw)
        reselected=self.select(cw,sw)
        # A: selected original observation has product multiplicity; zero
        # competition weight drops it rather than selecting a runner-up.
        fixed=self.rows[(sw[ST.sidx[self.rows]]*cw[ST.cidx[self.rows]])>0]
        rows=np.r_[reselected,fixed]
        h,rank,_=project(agg[0],agg[1],self.C,self.z,ST.ridx,ST.sidx,sw,rows,beta)
        value=-h[np.arange(len(rows)),self.js[rows]]
        n=len(reselected); out=[]
        for sl,product in [(slice(0,n),False),(slice(n,None),True)]:
            rr=rows[sl]; keep=rank[sl]==4
            w=sw[ST.sidx[rr]]*(cw[ST.cidx[rr]] if product else 1.)
            out.append(float(np.average(value[sl][keep],weights=w[keep])))
        # Rank-four zero-sum projection makes beta sensitivity exactly +beta_j.
        # This isolates reselection from training-position refit on same draw.
        rr=reselected; keep=rank[:n]==4; w=sw[ST.sidx[rr]]
        correction=(beta-BETA)[self.js[rr]]
        frozen=float(np.average((value[:n]-correction)[keep],weights=w[keep]))
        return out+[frozen,float(np.mean(cw>0)),int(np.sum(rank[n:]==4))]

    def analytic(self):
        e=self.x-self.point; n=len(e); rows=self.rows
        def meat(labels):
            _,inv=np.unique(labels,return_inverse=True)
            g=inv.max()+1
            return float((g/(g-1))*np.sum(np.bincount(inv,weights=e)**2)/n**2)
        vs=meat(ST.sidx[rows]); vc=meat(ST.cidx[rows])
        vi=meat(ST.sidx[rows].astype(np.int64)*ST.C+ST.cidx[rows])
        v=vs+vc-vi
        # A nonpositive estimate is invalid; do not silently clip it.
        return {'C': [self.point-Z*np.sqrt(v),self.point+Z*np.sqrt(v)] if v>0 else None,
                'D': [self.point-Z*np.sqrt(vs+vc),self.point+Z*np.sqrt(vs+vc)],
                'variance_terms': {'solver':vs,'competition':vc,'intersection':vi,'CGM':v}}

def task(args):
    case,rep,draws=args; start=time.perf_counter()
    ds=FastR(*gate.generate(ST,case,rep,arrays_only=True))
    analytic=ds.analytic()
    rng=np.random.default_rng(SEED)
    boot=np.array([ds.draw(*ST.weights(rng)) for b in range(draws)])
    q=np.quantile(boot[:,:2],[.025,.975],axis=0)
    intervals={'A':q[:,1].tolist(), 'B':(q[:,0]-boot[:,0].mean()+ds.point).tolist(),
               'C':analytic['C'],'D':analytic['D'],'original':q[:,0].tolist()}
    result={'case':case,'replicate':rep,'draws':draws,'point':ds.point,'oracle':ds.oracle(),
            'intervals':intervals,'variance_terms':analytic['variance_terms'],
            'bootstrap_mean':boot[:,:3].mean(axis=0).tolist(),
            'distinct_competition_fraction':float(boot[:,3].mean()),
            'fixed_available_mean':float(boot[:,4].mean()),'n':len(ds.rows),
            'seconds':time.perf_counter()-start}
    if draws>=1000:
        result['prefix_intervals']={}
        for b in (250,500,1000,2000):
            if b>draws:continue
            qq=np.quantile(boot[:b,:2],[.025,.975],axis=0)
            result['prefix_intervals'][str(b)]={'A':qq[:,1].tolist(),
                'B':(qq[:,0]-boot[:b,0].mean()+ds.point).tolist()}
    return result

def truth_task(args):
    case,rep,tau=args
    if tau is not None:gate.CASES[case]['tau']=tau
    return gate.truth_task((case,rep))

def benchmark():
    initialize(); start=time.perf_counter()
    from engine import Dataset
    arr=gate.generate(ST,'large_shared',0,arrays_only=True)
    ds=FastR(*arr); full=Dataset(ST,*arr)
    point=full.run(details=True)
    assert abs(ds.point-point['logR'])<1e-12
    assert abs(ds.oracle()-full.run(oracle=True)['logR'])<1e-12
    rng=np.random.default_rng(SEED); errors=[]
    for b in range(5):
        weights=ST.weights(rng)
        errors.append(abs(ds.draw(*weights)[0]-full.run(*weights)['logR']))
    assert max(errors)<1e-12
    t=time.perf_counter(); r=task(('large_shared',0,100)); elapsed=time.perf_counter()-t
    t=time.perf_counter(); gate.truth_task(('large_shared',100000)); truth_seconds=time.perf_counter()-t
    result={'R_engine_max_error':max(errors),'100_draw_seconds':elapsed,
            'truth_seconds':truth_seconds,'projected_1600_datasets_500_draws_10core_minutes':
            elapsed*5*1600/10/60,'total_seconds':time.perf_counter()-start,
            'diagnostic_100_draw':r,'N':int(ST.N),'S':int(ST.S),'C':int(ST.C),'TR':int(ST.TR)}
    save('benchmark.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='diagnostic_100_draw'}),flush=True)

def run(args):
    cases=list(gate.CASES) if args.case=='all' else [args.case]
    path=HERE/args.output
    old=[json.loads(s) for s in path.read_text().splitlines()] if path.exists() else []
    done={(r['case'],r['replicate'],r['draws']) for r in old}
    tasks=[(c,r,args.draws) for c in cases for r in range(args.start,args.start+args.reps)
           if (c,r,args.draws) not in done]
    start=time.perf_counter()
    with mp.get_context('spawn').Pool(args.workers,initializer=initialize) as pool, path.open('a') as f:
        for i,row in enumerate(pool.imap_unordered(task,tasks,chunksize=1),1):
            f.write(json.dumps(row,allow_nan=False)+'\n');f.flush()
            if i%20==0:print(json.dumps({'complete':i,'total':len(tasks),'elapsed_seconds':time.perf_counter()-start}),flush=True)
    save(path.stem+'-timing.json',{'wall_seconds':time.perf_counter()-start,'workers':args.workers,'new_datasets':len(tasks)})

def calibrate(args):
    # Independent common-random-number root calibration, followed by independent
    # truth integration. Target equation E[oracle log R(tau)] = log(1.10).
    from scipy.optimize import brentq
    history=[]; start=time.perf_counter()
    with mp.get_context('spawn').Pool(args.workers,initializer=initialize) as pool:
        def objective(tau):
            rows=list(pool.imap_unordered(truth_task,[('boundary',200000+r,tau) for r in range(args.reps)],chunksize=10))
            rows.sort(key=lambda r:r['replicate'])
            vals=np.array([r['oracle_log_R'] for r in rows])
            mean=float(vals.mean()); history.append({'tau':tau,'mean':mean,'se':float(vals.std(ddof=1)/np.sqrt(len(vals)))})
            print(json.dumps(history[-1]),flush=True)
            return mean-np.log(1.1)
        tau=brentq(objective,.008,.0121,xtol=1e-9)
        save('boundary-calibration.json',{'tau':tau,'target_log_R':float(np.log(1.1)),
             'target_R':1.1,'calibration_datasets':args.reps,'seed_start':200000,
             'history':history,'seconds':time.perf_counter()-start,
             'note':'Exact target equation, numerically calibrated; independent integration quantifies residual precision.'})
        path=HERE/'boundary-truth.jsonl'
        with path.open('w') as f:
            for r in pool.imap_unordered(truth_task,[('boundary',300000+r,tau) for r in range(10000)],chunksize=10):
                f.write(json.dumps(r)+'\n')
        vals=np.array([json.loads(s)['oracle_log_R'] for s in path.read_text().splitlines()])
        mean=float(vals.mean()); se=float(vals.std(ddof=1)/np.sqrt(len(vals)))
        save('boundary-truth.json',{'log_R':mean,'R':float(np.exp(mean)),'integration_datasets':len(vals),
            'log_R_MC_standard_error':se,'log_R_MC_999_interval':[mean-3.290527*se,mean+3.290527*se],
            'target_log_R':float(np.log(1.1)),'seconds':time.perf_counter()-start})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['benchmark','run','calibrate'])
    p.add_argument('--workers',type=int,default=10);p.add_argument('--reps',type=int,default=200)
    p.add_argument('--draws',type=int,default=500);p.add_argument('--start',type=int,default=0)
    p.add_argument('--case',default='all');p.add_argument('--output',default='replicates.jsonl')
    args=p.parse_args()
    if args.mode=='benchmark':benchmark()
    elif args.mode=='calibrate':calibrate(args)
    else:run(args)
