#!/usr/bin/env python3
"""Slice-only S1 measurement validation. Run with .venv/bin/python.

Commands: sources, simulation, analyze, report, all. Sources reuses round-3
extraction code, after verifying the frozen archive. No holdout outcomes read.
"""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/s1-r5-mpl')
from pathlib import Path
import importlib.util, hashlib, json, argparse, urllib.request, zipfile
import duckdb, numpy as np, pandas as pd
from scipy.special import expit
from scipy.stats import norm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
DATA=ROOT/'data/S1'
OLD=ROOT/'rounds/r3/pilot-S1'
SEED=20261001

def dump(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x))+'\n')

def progress(message):
    with (OUT/'PILOT.md').open('a') as f:f.write('\n'+message+'\n')
    if (OUT/'PROGRESS.md').exists():
        with (OUT/'PROGRESS.md').open('a') as f:f.write('\n'+message+'\n')
    print(message[:500],flush=True)

def in_slice(competition_id):
    return int(hashlib.sha256(competition_id.encode('utf-8')).hexdigest(),16)%5==0

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(2**20),b''):h.update(b)
    return h.hexdigest()

def sources():
    # Write the lock before even extracting outcome rows. Reuse exact r3 code.
    (OUT/'SLICE.md').write_text((OLD/'SLICE.md').read_text()+
        '\n## Round 5 reuse\nExact round-3 locked slice reused, every year. The held-out 80% remains unopened for outcome analysis. Implementation: pilot.py:in_slice and the imported round-3 prepare function. No post-outcome membership changes.\n')
    m=json.loads((OLD/'source-manifest.json').read_text())
    archive=ROOT/m['files'][0]['path']; DATA.mkdir(exist_ok=True,parents=True)
    if not archive.exists():
        urllib.request.urlretrieve(m['url'],str(archive)+'.part')
        Path(str(archive)+'.part').rename(archive)
    assert sha(archive)==m['files'][0]['sha256'],'Frozen archive mismatch'
    with zipfile.ZipFile(archive) as z:
        for row in m['files'][1:]:
            p=ROOT/row['path']
            if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);z.extract(p.name,p.parent)
            assert sha(p)==row['sha256'],str(p)
    (OUT/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    spec=importlib.util.spec_from_file_location('r3',OLD/'pilot.py')
    r3=importlib.util.module_from_spec(spec);spec.loader.exec_module(r3);r3.OUT=OUT
    r3.prepare()
    with (OUT/'SLICE.md').open('a') as f:
        f.write('\n## Round 5 implementation\nExact round-3 locked membership reused. The extraction function is `rounds/r3/pilot-S1/pilot.py:prepare`, imported by `rounds/r5/pilot-S1/pilot.py:sources` with its output directory redirected here. Round-5 `in_slice` and `load_slice` independently assert membership before any outcome fit. Simulation reads only structural `panel-sizes.csv` first. The held-out 80% remains unused for outcome analysis; only structural counts are read.\n')
    assert sha(OUT/'exploration-competition-ids.txt')=='b5f6426bffbbf01c4d742cbe65f083cb4cbb5a134a5b60c3fe9fa312d028b7a4'
    c=duckdb.connect(str(DATA/'coverage.duckdb'),read_only=True)
    c.execute('SELECT competition_id,round_type_id,count(*) n FROM eligible WHERE explore AND is_final GROUP BY ALL ORDER BY competition_id,round_type_id').fetchdf().to_csv(OUT/'panel-sizes.csv',index=False)
    dump('source-verification.json',{'all_raw_hashes_match_r3':True,'slice_ids_sha256':sha(OUT/'exploration-competition-ids.txt')})
    progress('Sources and slice independently verified. All confirmation queries were structural; outcome extraction is restricted inside SQL to explore=true.')

def contributions(y):
    """C_i = diag(valid)-valid valid'/m. Keep every valid solve in DNF panels.
    Within solver-round centering cancels its skill/conditions. m=1 gives zero
    information for the time contrasts, but the row remains in failure analysis.
    """
    valid=np.isfinite(y); m=valid.sum(1); denom=np.maximum(m,1)
    C=np.eye(5)[None,:,:]*valid[:,:,None]-valid[:,:,None]*valid[:,None,:]/denom[:,None,None]
    z=np.where(valid,y-np.nansum(y,axis=1)[:,None]/denom[:,None],0.)
    return C,z,(z*z).sum(1),np.maximum(m-1,0).astype(float)

def rowmean(y):
    n=np.isfinite(y).sum(1)
    return np.divide(np.nansum(y,axis=1),n,out=np.full(len(n),np.nan),where=n>0)

def aggregate(C,v,S,d,ridx,R,weights=None):
    w=np.ones(len(d)) if weights is None else weights
    A=np.zeros((R,5,5)); V=np.zeros((R,5)); ss=np.zeros(R); dd=np.zeros(R)
    np.add.at(A,ridx,C*w[:,None,None]);np.add.at(V,ridx,v*w[:,None])
    np.add.at(ss,ridx,S*w);np.add.at(dd,ridx,d*w)
    return A,V,ss,dd

def moment(st,weights=None,noise_A=None):
    """Exact missing-pattern noise correction. No nonnegative clipping in CIs.
    E(S)=d(tau+e); E(||H'C y||²)=tau tr(A²)+e tr(A).
    Replicate solver weights need A(w²) in the noise term, not A(w).
    """
    A,V,S,d=st;w=np.ones(len(d)) if weights is None else weights
    beta=np.linalg.pinv(np.einsum('r,rij->ij',w,A))@np.einsum('r,rj->j',w,V)
    V=V-np.einsum('rij,j->ri',A,beta)
    S=S-2*np.einsum('rj,j->r',st[1],beta)+np.einsum('i,rij,j->r',beta,A,beta)
    t2=np.einsum('rij,rji->r',A,A)
    dn=d if noise_A is None else np.trace(noise_A,axis1=1,axis2=2)
    total=np.sum(w*S)/np.sum(w*d)
    den=np.sum(w*(t2-dn))
    tau=np.sum(w*((V*V).sum(1)-total*dn))/den
    residual=total-tau
    return {'shared_variance':float(tau),'residual_variance':float(residual),
            'within_solver_share':float(tau/total),'shared_log_sd':float(np.sqrt(max(0,tau))),
            'position':beta.tolist()},(A,V,S,d)

def interval(st):
    """Competition sandwich interval, used to measure simulation coverage."""
    fit,zst=moment(st);A,V,S,d=zst;t2=np.einsum('rij,rji->r',A,A)
    tau=fit['shared_variance'];total=tau+fit['residual_variance']
    influence=((V*V).sum(1)-total*d-tau*(t2-d))-d*(S.sum()/d.sum()-total)
    # delta contribution from estimating total variance
    influence=((V*V).sum(1)-total*d-tau*(t2-d))-(S-total*d)
    se=np.sqrt(len(d)/(len(d)-1)*np.sum(influence**2))/np.sum(t2-d)
    return tau,np.array([tau-1.96*se,tau+1.96*se])

def tier_moment(stF,stS,weights=None,noiseF=None,noiseS=None):
    f,F=moment(stF,weights,noiseF);s,S=moment(stS,weights,noiseS)
    w=np.ones(len(F[3])) if weights is None else weights
    cross=float(np.sum(w*np.einsum('ri,ri->r',F[1],S[1]))/np.sum(w*np.einsum('rij,rji->r',F[0],S[0])))
    bF=f['shared_variance'];bS=s['shared_variance']
    return {'fast_variance':bF,'slow_variance':bS,'cross_covariance':cross,
        'shared_variance':(bF+bS+2*cross)/4,
        'interaction_variance':(bF+bS-2*cross)/4,
        'cross_tier_latent_correlation':cross/np.sqrt(max(1e-15,bF*bS)),
        'fast_residual':f['residual_variance'],'slow_residual':s['residual_variance']}

def tier_interval(stF,stS):
    fit=tier_moment(stF,stS)
    f,F=moment(stF);s,T=moment(stS)
    def influence(st,ff):
        A,V,S,d=st;den=np.einsum('rij,rji->r',A,A)-d
        return ((V*V).sum(1)-S-ff['shared_variance']*den)/den.sum()
    iF=influence(F,f);iS=influence(T,s)
    dc=np.einsum('rij,rji->r',F[0],T[0])
    iC=(np.einsum('ri,ri->r',F[1],T[1])-fit['cross_covariance']*dc)/dc.sum()
    out={}
    for key,sign in [('shared_variance',1),('interaction_variance',-1)]:
        inf=(iF+iS+2*sign*iC)/4
        se=np.sqrt(len(inf)/(len(inf)-1)*np.sum(inf**2))
        out[key]=[fit[key]-1.96*se,fit[key]+1.96*se]
    return fit,out

def simulation(reps=400):
    # ONLY structural sizes: no real attempt value is read before simulation.
    sizes=pd.read_csv(OUT/'panel-sizes.csv').n.to_numpy();R=len(sizes)
    ridx=np.repeat(np.arange(R),sizes);N=len(ridx);rng=np.random.default_rng(SEED)
    tier=np.concatenate([np.where(np.arange(n)%2==0,1.,-1.) for n in sizes])
    cases=[('null',0.,0.,'none'),('small_shared',.0009,0.,'none'),
      ('large_shared',.004,0.,'none'),('shared_and_tier',.0009,.0025,'none'),
      ('tier_only',0.,.0025,'none'),('MCAR_DNF',.0009,0.,'mcar'),
      ('informative_DNF',.0009,0.,'informative')]
    outputs=[]
    for name,tau,gamma,missing in cases:
        estimates=[];covers=[];tier_est=[];old_est=[];corrs=[]
        for rep in range(reps):
            common=rng.normal(0,np.sqrt(tau),(R,5));interaction=rng.normal(0,np.sqrt(gamma),(R,5))
            eps=rng.normal(0,np.sqrt(.0222),(N,5))
            y=common[ridx]+tier[:,None]*interaction[ridx]+eps
            if missing=='mcar':y[rng.random(y.shape)<.015]=np.nan
            if missing=='informative':
                prob=expit(-4.55+4*eps+8*common[ridx])
                y[rng.random(y.shape)<prob]=np.nan
            C,v,S,d=contributions(y);st=aggregate(C,v,S,d,ridx,R)
            b,ci=interval(st);estimates.append(b);covers.append(ci[0]<=tau<=ci[1])
            # Original complete-case balanced ANOVA, including its min-6 gate.
            good=np.isfinite(y).all(1);ns=np.bincount(ridx,weights=good,minlength=R)
            yy=np.nan_to_num(y)*good[:,None];z=yy-yy.mean(1,keepdims=True)
            vs=np.zeros((R,5));np.add.at(vs,ridx,z);cc=vs/np.maximum(ns[:,None],1)
            resid=z-cc[ridx]*good[:,None];sse=np.bincount(ridx,weights=(resid**2).sum(1),minlength=R)
            ok=ns>=6;beta=np.sum(cc[ok]*ns[ok,None],axis=0)/ns[ok].sum()
            e=sse[ok].sum()/(4*(ns[ok]-1).sum())
            old_est.append(max(0,(np.sum(ns[ok]*((cc[ok]-beta)**2).sum(1))-4*ok.sum()*e)/(4*ns[ok].sum())))
            if gamma:
                sf=aggregate(C,v,S,d,ridx,R,(tier==1).astype(float));ss=aggregate(C,v,S,d,ridx,R,(tier==-1).astype(float))
                t=tier_moment(sf,ss);tier_est.append([t['shared_variance'],t['interaction_variance']])
            # Random balanced halves, same real panel sizes. Corr computed across r,j.
            ix=np.concatenate([rng.permutation(n)<n//2 for n in sizes])
            aa=aggregate(C,v,S,d,ridx,R,ix.astype(float));bb=aggregate(C,v,S,d,ridx,R,(~ix).astype(float))
            a=np.einsum('rij,rj->ri',np.linalg.pinv(aa[0]),aa[1])
            bhalf=np.einsum('rij,rj->ri',np.linalg.pinv(bb[0]),bb[1])
            corrs.append(np.corrcoef(a.ravel(),bhalf.ravel())[0,1])
        med=float(np.median(sizes));h1=med//2;h2=med-h1
        expected=float(tau/np.sqrt((tau+.0222/h1)*(tau+.0222/h2))) if gamma==0 else None
        out={'scenario':name,'shared_truth':tau,'tier_interaction_truth':gamma,'residual_truth':.0222,
          'replicates':reps,'revised_common_mean':float(np.mean(estimates)),'revised_common_bias':float(np.mean(estimates)-tau),
          'competition_sandwich_95_coverage':float(np.mean(covers)),
          'coverage_MC_se':float(np.sqrt(np.mean(covers)*(1-np.mean(covers))/reps)),
          'original_estimator_mean':float(np.mean(old_est)),
          'original_bias':float(np.mean(old_est)-tau),'split_peer_correlation_mean':float(np.mean(corrs)),
          'split_peer_correlation_simulation_95':np.quantile(corrs,[.025,.975]).tolist(),
          'median_panel_analytic_correlation':expected}
        if tier_est:out['tier_aware_recovery']={'shared_mean':float(np.mean(tier_est,axis=0)[0]),'interaction_mean':float(np.mean(tier_est,axis=0)[1])}
        outputs.append(out);dump('simulation.json',{'panel_rounds':R,'solver_rounds':N,'seed':SEED,'results':outputs})
        progress(f'Simulation saved: {name}; common bias {out["revised_common_bias"]:.6f}; coverage {out["competition_sandwich_95_coverage"]:.3f}; split-peer r {out["split_peer_correlation_mean"]:.3f}.')

def load_slice():
    c=duckdb.connect();c.execute("SET threads=8;SET memory_limit='8GB'")
    f=DATA/'exploration-attempts.parquet'
    bad=c.execute(f"SELECT count(*) FILTER(WHERE NOT explore) FROM read_parquet('{f}')").fetchone()[0];assert bad==0
    # Wide minimal slice-only table; no full-export outcome DataFrame.
    cols=','.join(f'max(value) FILTER(WHERE attempt_number={j}) v{j}' for j in range(1,6))
    g=c.execute(f"SELECT competition_id,round_type_id,result_id,person_id,year,month,day,extra_pool_rows,{cols} FROM read_parquet('{f}') WHERE is_final AND explore GROUP BY ALL ORDER BY competition_id,round_type_id,person_id").fetchdf()
    assert all(in_slice(x) for x in g.competition_id.unique())
    g['round_key']=g.competition_id+'|'+g.round_type_id
    values=g[[f'v{j}' for j in range(1,6)]].to_numpy()
    y=np.full(values.shape,np.nan);valid=values>0;y[valid]=np.log(values[valid]/100)
    ridx=pd.factorize(g.round_key,sort=True)[0];R=ridx.max()+1
    return g,values,y,ridx,R

def bootstrap(C,v,S,d,ridx,g,B=1000):
    rng=np.random.default_rng(SEED+10);R=ridx.max()+1
    st=aggregate(C,v,S,d,ridx,R);_,sidx=np.unique(g.person_id,return_inverse=True);ns=sidx.max()+1
    independent=[];crossed=[]
    for b in range(B):
        cw=np.bincount(rng.integers(0,R,R),minlength=R)
        independent.append(moment(st,cw)[0])
        sw=np.bincount(rng.integers(0,ns,ns),minlength=ns)[sidx].astype(float)
        bst=aggregate(C,v,S,d,ridx,R,sw)
        A2=aggregate(C,v,S,d,ridx,R,sw**2)[0]
        crossed.append(moment(bst,cw,A2)[0])
    keys=['shared_variance','within_solver_share','shared_log_sd']
    return {scope:{k:np.quantile([x[k] for x in draws],[.025,.975]).tolist() for k in keys}
            for scope,draws in [('competition',independent),('competition_solver',crossed)]}

def peer_effects(C,v,ridx,tau,e,beta):
    R=ridx.max()+1;A,V,_,_=aggregate(C,v,np.zeros(len(v)),np.zeros(len(v)),ridx,R)
    Ap=A[ridx]-C;vp=V[ridx]-v-np.einsum('nij,j->ni',Ap,beta)
    precision=Ap+np.eye(5)[None,:,:]*(e/max(tau,1e-12))
    mean=np.linalg.solve(precision,vp[:,:,None])[:,:,0]
    covariance=e*np.linalg.inv(precision)
    P=np.eye(5)-np.ones((5,5))/5
    covariance=np.einsum('ij,njk,kl->nil',P,covariance,P)
    return mean,covariance

def reliability(C,v,S,d,ridx,g,fit,repeats=30):
    rng=np.random.default_rng(SEED+20);R=ridx.max()+1;tau=max(0,fit['shared_variance']);e=fit['residual_variance'];beta=np.array(fit['position'])
    panel=[np.where(ridx==r)[0] for r in range(R)]
    panel=[ix[d[ix]>=1] for ix in panel]
    maxk=max(len(ix) for ix in panel)-2;rows=[];fixed=[]
    for k in range(2,maxk+1):
        stats=[];fixedstats=[];nrounds=sum(len(ix)>=k+2 for ix in panel)
        for rep in range(repeats):
            rowstats=[];fx=[]
            for ix in panel:
                n=len(ix)
                if n<k+2:continue
                ix=rng.permutation(ix);a=ix[:k];b=ix[k:]
                Aa=C[a].sum(0);Ab=C[b].sum(0)
                va=v[a].sum(0)-Aa@beta;vb=v[b].sum(0)-Ab@beta
                sa=np.linalg.pinv(Aa)@va;sb=np.linalg.pinv(Ab)@vb
                post=np.linalg.solve(Aa+np.eye(5)*e/max(tau,1e-12),va)
                factor=(d[b]+1)/d[b]
                z=(v[b]-np.einsum('nij,j->ni',C[b],beta))*factor[:,None]
                pred=np.einsum('nij,j->ni',C[b],post)*factor[:,None]
                sst=(z*z).sum();sse=((z-pred)**2).sum()
                # Across 5 centered scrambles: sums are sufficient for correlation.
                cur=[sa@sb,sa@sa,sb@sb,sst,sse,(n-k),1]
                rowstats.append(cur)
                if n>=20 and k<=18:fx.append(cur)
            if rowstats:stats.append(np.sum(rowstats,axis=0))
            if fx:fixedstats.append(np.sum(fx,axis=0))
        def summarize(arr):
            arr=np.array(arr);pooled=arr.sum(0);r=pooled[0]/np.sqrt(pooled[1]*pooled[2])
            rh=tau/(tau+e/(pooled[5]/pooled[6]))
            return {'k':k,'rounds':nrounds,'random_splits':repeats,'peer_correlation':float(r),
              'individual_prediction_R2':float(1-pooled[4]/pooled[3]),
              'model_latent_reliability':float(tau/(tau+e/k)),
              'empirical_latent_reliability_approx':float(r*r/max(rh,1e-12)),
              'split_MC_range':np.quantile(arr[:,0]/np.sqrt(arr[:,1]*arr[:,2]),[.025,.975]).tolist()}
        rows.append(summarize(stats))
        if fixedstats:
            x=summarize(fixedstats);x['rounds']=sum(len(ix)>=20 for ix in panel);fixed.append(x)
    extrap=[{'k':k,'latent_reliability':float(tau/(tau+e/k)),'max_individual_prediction_R2':float(tau/(tau+e))} for k in [5,10,20,50,100,200]]
    out={'all_panels':rows,'fixed_large_panels':fixed,'extrapolation':extrap,
      'peers_for_50pct_reliability':float(e/max(tau,1e-12)),'peers_for_80pct_reliability':float(4*e/max(tau,1e-12)),
      'frozen_parameters':fit,
      'note':'Hyperparameters and position effects learned only on pre-2019 exploration finals. Peer prediction uses only 2019–2025 exploration finals and holds out entire solvers within each final. Target time baseline uses its OTHER valid solves, never the target solve. Monte Carlo ranges measure random split variation, not sampling uncertainty. k-dependent eligible panels change composition; fixed-large-panel curve controls it. Extrapolation assumes exchangeable peers, stable residual variance, correct assignment and no tier interaction.'}
    dump('reliability.json',out)
    reliability_intervals(C,v,d,ridx,fit,out)
    return out

def reliability_intervals(C,v,d,ridx,fit,out,B=1000,repeats=30):
    """Competition uncertainty, averaging random splits before bootstrapping."""
    tau=max(1e-12,fit['shared_variance']);e=fit['residual_variance'];beta=np.array(fit['position'])
    rng=np.random.default_rng(SEED+25);R=ridx.max()+1
    panel=[np.where((ridx==r)&(d>=1))[0] for r in range(R)]
    results=[]
    for k in [2,5,10,20]:
        stat=[]
        for ix in panel:
            if len(ix)<k+2:continue
            splits=[]
            for _ in range(repeats):
                ii=rng.permutation(ix);a=ii[:k];b=ii[k:]
                Aa=C[a].sum(0);Ab=C[b].sum(0)
                va=v[a].sum(0)-Aa@beta;vb=v[b].sum(0)-Ab@beta
                sa=np.linalg.pinv(Aa)@va;sb=np.linalg.pinv(Ab)@vb
                post=np.linalg.solve(Aa+np.eye(5)*e/tau,va)
                fac=((d[b]+1)/d[b])[:,None]
                z=(v[b]-np.einsum('nij,j->ni',C[b],beta))*fac
                pred=np.einsum('nij,j->ni',C[b],post)*fac
                splits.append([sa@sb,sa@sa,sb@sb,(z*z).sum(),((z-pred)**2).sum()])
            stat.append(np.mean(splits,axis=0))
        stat=np.array(stat);draw=[]
        for _ in range(B):
            s=stat[rng.integers(0,len(stat),len(stat))].sum(0)
            draw.append([s[0]/np.sqrt(s[1]*s[2]),1-s[4]/s[3]])
        sums=stat.sum(0);results.append({'k':k,'rounds':len(stat),
          'peer_correlation':float(sums[0]/np.sqrt(sums[1]*sums[2])),
          'peer_correlation_competition_95':np.quantile(np.array(draw)[:,0],[.025,.975]).tolist(),
          'individual_prediction_R2':float(1-sums[4]/sums[3]),
          'individual_prediction_R2_competition_95':np.quantile(np.array(draw)[:,1],[.025,.975]).tolist()})
    out['representative_k_uncertainty']=results
    out['uncertainty_scope']='Competition bootstrap conditional on pre-2019 parameters, peer splits averaged first; solver repetition and skill-baseline uncertainty are not included in these predictive intervals.'
    dump('reliability.json',out)

def skill_interaction(g,y,C,v,S,d,ridx,R,B=1000):
    # Skill is computed from OTHER finals; never the focal scramble or round.
    means=rowmean(y);ref=np.full(len(g),np.nan)
    for _,ix in g.groupby('person_id').groups.items():
        ix=np.array(list(ix));years=g.year.to_numpy()[ix]
        for j,i in enumerate(ix):
            other=ix[(np.abs(years-years[j])<=2)&(ix!=i)]
            if len(other)>=2:ref[i]=np.nanmedian(means[other])
    fast=np.zeros(len(g),bool);keep=np.zeros(len(g),bool)
    for r in range(R):
        ix=np.where((ridx==r)&np.isfinite(ref)&(d>=1))[0]
        if len(ix)<6:continue
        f=ref[ix]<np.median(ref[ix]);
        if min(f.sum(),(~f).sum())<3:continue
        keep[ix]=True;fast[ix]=f
    F=aggregate(C,v,S,d,ridx,R,(keep&fast).astype(float));T=aggregate(C,v,S,d,ridx,R,(keep&~fast).astype(float))
    good=(F[3]>0)&(T[3]>0);F=tuple(a[good] for a in F);T=tuple(a[good] for a in T)
    fit=tier_moment(F,T);rng=np.random.default_rng(SEED+30);draw=[];crossed=[]
    _,sidx=np.unique(g.person_id,return_inverse=True);ns=sidx.max()+1
    for _ in range(B):
        cw=np.bincount(rng.integers(0,good.sum(),good.sum()),minlength=good.sum());draw.append(tier_moment(F,T,cw))
        sw=np.bincount(rng.integers(0,ns,ns),minlength=ns)[sidx].astype(float)
        wf=sw*(keep&fast);ws=sw*(keep&~fast)
        bf=tuple(x[good] for x in aggregate(C,v,S,d,ridx,R,wf));bs=tuple(x[good] for x in aggregate(C,v,S,d,ridx,R,ws))
        nf=aggregate(C,v,S,d,ridx,R,wf**2)[0][good];nt=aggregate(C,v,S,d,ridx,R,ws**2)[0][good]
        crossed.append(tier_moment(bf,bs,cw,nf,nt))
    ci={k:np.quantile([a[k] for a in draw],[.025,.975]).tolist() for k in fit}
    crossedci={k:np.quantile([a[k] for a in crossed],[.025,.975]).tolist() for k in fit}
    out={'model':fit,'competition_bootstrap_95':ci,'competition_solver_bootstrap_95':crossedci,'rounds':int(good.sum()),'solver_rounds':int(keep.sum()),
        'admissible_display':{'interaction_variance':max(0,fit['interaction_variance']),
          'cross_tier_latent_correlation':float(np.clip(fit['cross_tier_latent_correlation'],-1,1))},
        'definition':'Faster/slower half by median log time in at least two OTHER slice finals within +/-2 calendar years. Both tiers need >=3 informative peers. No method field exists; no method claim is tested.',
        'limitations':'Skill reference uses future as well as past exploration finals; tier effect is exploratory, composition-selected and not a method effect. Residual permits tier-specific variance. Interactions within either tier remain unidentified. Raw moment estimates can be negative or correlations can exceed one due to sampling; those are diagnostics, not physical estimates.'}
    dump('interaction.json',out);return out

def dnf_analysis(g,values,C,v,ridx,fit,B=1000):
    # Binary companion to successful-time contrasts; no imputed DNF time.
    D=(values==-1).astype(float);attempted=(values>0)|(values==-1)
    Y=np.where(attempted,D,np.nan);CD,vd,sd,dd=contributions(Y)
    ds=moment(aggregate(CD,vd,sd,dd,ridx,ridx.max()+1))[0]
    rng=np.random.default_rng(SEED+31);st=aggregate(CD,vd,sd,dd,ridx,ridx.max()+1);draw=[]
    for _ in range(B):
        w=np.bincount(rng.integers(0,len(st[3]),len(st[3])),minlength=len(st[3]));draw.append(moment(st,w)[0]['shared_variance'])
    m,_=peer_effects(C,v,ridx,max(0,fit['shared_variance']),fit['residual_variance'],fit['position'])
    # Peer time-difficulty versus target DNF: aggregate covariance only.
    mask=attempted;center=m[mask]-m[mask].mean();binary=D[mask]
    slope=np.sum(center*(binary-binary.mean()))/np.sum(center**2)
    a=np.zeros(len(st[3]));b=np.zeros(len(a));np.add.at(a,ridx,np.sum(np.where(mask,(m-m[mask].mean())*(D-binary.mean()),0),axis=1));np.add.at(b,ridx,np.sum(np.where(mask,(m-m[mask].mean())**2,0),axis=1))
    slopes=[]
    for _ in range(B):
        w=np.bincount(rng.integers(0,len(a),len(a)),minlength=len(a));slopes.append(np.sum(w*a)/np.sum(w*b))
    out={'DNF':int(D.sum()),'DNS':int((values==-2).sum()),'valid':int((values>0).sum()),'absent':int((values==0).sum()),
      'DNF_rate_among_started':float(D.sum()/attempted.sum()),'binary_shared_variance':ds['shared_variance'],
      'binary_shared_variance_competition_95':np.quantile(draw,[.025,.975]).tolist(),
      'peer_log_difficulty_DNF_risk_slope':float(slope),'slope_competition_95':np.quantile(slopes,[.025,.975]).tolist(),
      'scope':'Descriptive binary peer-covariance companion, not a joint likelihood or a latent DNF-time reconstruction. DNS excluded from started denominator, reported separately; all successful cells of DNF panels retained. Informative missingness is probed by simulation and sensitivity.'}
    dump('dnf.json',out);return out

def extreme_analysis(g,values,y,C,v,S,d,ridx,fit,B=2000):
    # Hyperparameters ONLY pre-2019 exploration data. Fit no heldout outcomes.
    pre=g.year.to_numpy()<2019;R=ridx.max()+1
    train=aggregate(C,v,S,d,ridx,R,pre.astype(float));active=train[3]>0;train=tuple(x[active] for x in train)
    frozen=moment(train)[0];tau=max(0,frozen['shared_variance']);e=frozen['residual_variance']
    mu,cov=peer_effects(C,v,ridx,tau,e,frozen['position'])
    Af,Vf,_,_=aggregate(C,v,S,d,ridx,R)
    peerA=Af[ridx]-C
    peerV=Vf[ridx]-v-np.einsum('nij,j->ni',peerA,np.array(frozen['position']))
    unshrunk=np.einsum('nij,nj->ni',np.linalg.pinv(peerA),peerV)
    a=g.loc[g.index.repeat(5)].reset_index(drop=True).copy();a['attempt_number']=np.tile(np.arange(1,6),len(g))
    a['seconds']=np.where(values.ravel()>0,values.ravel()/100,np.nan)
    a['peer_log_effect']=mu.ravel();a['peer_se']=np.sqrt(np.diagonal(cov,axis1=1,axis2=2)).ravel()
    a['unshrunk_peer_log_effect']=unshrunk.ravel()
    a['own_log_deviation']=(v-np.einsum('nij,j->ni',C,np.array(frozen['position']))).ravel()
    a['adjusted_seconds']=a.seconds*np.exp(-a.peer_log_effect)
    a=a[a.seconds.notna()];a.to_parquet(DATA/'r5-exploration-adjusted.parquet',index=False)
    modern=a[a.year.between(2019,2025)]
    structural=g[g.year.between(2019,2025)].groupby(['person_id','year']).result_id.nunique()
    keys=set(structural[structural>=5].index)
    eligible=modern[[ (p,yr) in keys for p,yr in zip(modern.person_id,modern.year)]].copy()
    best=eligible.sort_values(['seconds','competition_id','attempt_number']).groupby(['person_id','year']).head(1)
    # Full refit uncertainty via pre-2019 competition bootstrap; target composition
    # kept fixed to original seasons; resample entire target competitions/reselect.
    grouped=[x for _,x in eligible.sort_values(['seconds','competition_id','attempt_number']).groupby(['person_id','year'])]
    comps,ci=np.unique(eligible.competition_id,return_inverse=True);clook={x:i for i,x in enumerate(comps)}
    solvers=np.unique(best.person_id);slook={x:i for i,x in enumerate(solvers)}
    recordgroups=[]
    for z in grouped:
        row=z.index.to_numpy()//5 # original index retained after filtering
        attempt=z.attempt_number.to_numpy()-1
        recordgroups.append((z.person_id.iloc[0],np.array([clook[x] for x in z.competition_id]),row,attempt))
    rng=np.random.default_rng(SEED+40);draw=[];unshrunk_draw=[]
    # Avoid millions of matrix solves: precompute unshrunk leave-one-out GLS.
    A,V,_,_=aggregate(C,v,S,d,ridx,R);Ap=A[ridx]-C
    # Cache eigensystems so every nuisance-refit bootstrap updates all predictions.
    eig,U=np.linalg.eigh(Ap);base=V[ridx]-v
    pinv_peerA=np.linalg.pinv(peerA)
    for rep in range(B):
        tw=np.bincount(rng.integers(0,len(train[3]),len(train[3])),minlength=len(train[3]));ff=moment(train,tw)[0]
        tb=max(1e-12,ff['shared_variance']);ee=ff['residual_variance'];beta=np.array(ff['position'])
        vv=base-np.einsum('nij,j->ni',Ap,beta)
        coeff=np.einsum('nji,nj->ni',U,vv)/(eig+ee/tb)
        mm=np.einsum('nij,nj->ni',U,coeff)
        uu=np.einsum('nij,nj->ni',pinv_peerA,vv)
        cw=np.bincount(rng.integers(0,len(comps),len(comps)),minlength=len(comps))
        sw=np.bincount(rng.integers(0,len(solvers),len(solvers)),minlength=len(solvers))
        num=den=unum=0.
        for solver,cix,rows,js in recordgroups:
            present=np.where(cw[cix]>0)[0];w=sw[slook[solver]]
            if len(present) and w:
                q=present[0];num-=w*mm[rows[q],js[q]];unum-=w*uu[rows[q],js[q]];den+=w
        if den:draw.append(num/den);unshrunk_draw.append(unum/den)
    logratio=float(-best.peer_log_effect.mean());ratio=float(np.exp(logratio))
    gap=float(-best.own_log_deviation.mean());shared=-float(best.peer_log_effect.mean())
    # Direct observed-extreme decomposition, conditional on estimated round skill.
    # Full residual is NOT execution luck: it contains unmeasured interactions.
    out={'n':len(best),'solvers':int(best.person_id.nunique()),'competitions':int(best.competition_id.nunique()),
      'eligible_structural_solver_seasons':len(keys),'eligible_seasons_without_any_valid_time':len(keys)-len(best),
      'solver_rounds_with_nonidentified_peer_contrasts':int((np.sum(np.linalg.eigvalsh(peerA)>1e-9,axis=1)<4).sum()),
      'ratio':ratio,'competition_solver_refit_reselection_95':np.exp(np.quantile(draw,[.025,.975])).tolist(),
      'bootstrap_log_se':float(np.std(draw,ddof=1)),'mean_fastest_seconds':float(np.exp(np.log(best.seconds).mean())),
      'within_round_log_speedup':gap,'peer_explained_log_speedup':shared,
      'peer_fraction_of_log_speedup':float(shared/gap),'own_unexplained_log_speedup':float(gap-shared),
      'aggregate_unshrunk_ratio':float(np.exp(-best.unshrunk_peer_log_effect.mean())),
      'aggregate_unshrunk_95':np.exp(np.quantile(unshrunk_draw,[.025,.975])).tolist(),
      'aggregate_unshrunk_log_se':float(np.std(unshrunk_draw,ddof=1)),
      'aggregate_unshrunk_peer_fraction':float(-best.unshrunk_peer_log_effect.mean()/gap),
      'cohort':'All slice solvers with >=5 structurally eligible finals in the slice per season, 2019–2025; not official-2018 top100.',
      'uncertainty_scope':'2,000 draws: pre-2019 hyperparameter refit, target competition+solver resampling, seasonal-minimum reselection. Eligibility list fixed; exposure changes under ordinary cluster resampling. Does not identify latent per-extreme truth or mapping error.',
      'frozen_pre2019':frozen,'prereg_would_pass':'untestable on slice',
      'surrogate_rule_pass':bool(ratio>1.10 and np.exp(np.quantile(draw,.025))>1)}
    # Slice-only proxy cohort from pre-2019 finals, deliberately NOT official ranking.
    baseline=g.loc[pre,['person_id']].copy();baseline['logmean']=rowmean(y[pre]);baseline['nvalid']=np.isfinite(y[pre]).sum(1)
    ranking=baseline.groupby('person_id').agg(skill=('logmean','median'),nvalid=('nvalid','sum'))
    proxy=set(ranking[ranking.nvalid>=50].sort_values('skill').head(100).index)
    pb=best[best.person_id.isin(proxy)];out['slice_proxy_top100']={'n':len(pb),'ratio':float(np.exp(-pb.peer_log_effect.mean())) if len(pb) else None}
    best.to_csv(OUT/'exploratory-season-extremes.csv',index=False)
    dump('extremes.json',out);return out,best,a

def analyze(B=1000):
    g,values,y,ridx,R=load_slice();C,v,S,d=contributions(y);st=aggregate(C,v,S,d,ridx,R)
    fit,_=moment(st);ci=bootstrap(C,v,S,d,ridx,g,B)
    counts={'rounds':R,'solver_rounds':len(g),'valid_attempts':int((values>0).sum()),
      'attempt_rows':values.size,'solvers':int(g.person_id.nunique()),'informative_solver_rounds':int((d>0).sum()),
      'solver_rounds_with_any_nonpositive':int((values<=0).any(1).sum()),'extra_pool_rounds':int(g[g.extra_pool_rows>0].round_key.nunique())}
    checks=[]
    for label,mask,yy in [('complete_case',np.isfinite(y).all(1),y),
      ('log_contrast_clip_0.6',np.ones(len(g),bool),np.where(np.isfinite(y),rowmean(y)[:,None]+np.clip(y-rowmean(y)[:,None],-.6,.6),np.nan))]:
        cc,vv,ss,dd=contributions(yy);f,_=moment(aggregate(cc,vv,ss,dd,ridx,R,mask.astype(float)));checks.append({'specification':label,**f})
    dump('variance.json',{'fit':fit,'bootstrap_95':ci,'counts':counts,'sensitivity':checks})
    progress(f'Step 4: Missing-pattern moment estimator retains {counts["valid_attempts"]:,} valid solves in {R:,} finals; shared within-solver share {fit["within_solver_share"]:.2%}. Saved crossed-bootstrap uncertainty and complete-case/tail sensitivities.')
    train=aggregate(C,v,S,d,ridx,R,(g.year.to_numpy()<2019).astype(float));active=train[3]>0;train=tuple(a[active] for a in train);frozen=moment(train)[0]
    test=g.year.between(2019,2025).to_numpy()
    rel=reliability(C[test],v[test],S[test],d[test],ridx[test],g[test],frozen);progress('Step 5: Random-k peer prediction on 2019–2025 slice finals with pre-2019 hyperparameters frozen; fixed-large-panel reliability curves saved, including extrapolations and changing-panel counts.')
    inter=skill_interaction(g,y,C,v,S,d,ridx,R,B);progress(f'Step 6: Skill-tier interaction test saved on {inter["rounds"]} finals; method interaction is untestable because method is absent.')
    dnf=dnf_analysis(g,values,C,v,ridx,fit,B);progress('Step 7: Binary DNF companion saved; DNS reported separately. No whole panels removed and no arbitrary DNF times imputed.')
    ext,best,a=extreme_analysis(g,values,y,C,v,S,d,ridx,fit);progress(f'Step 8: Selection-aware exploratory seasonal extremes saved: n={ext["n"]}, geometric median-scramble ratio {ext["ratio"]:.4f}. Exact verified-cohort rule remains untestable.')
    # Replacement contamination: random mapping dilution and robust observed tails.
    tau=max(0,fit['shared_variance']);e=fit['residual_variance']
    replace=[{'replacement_fraction':p,'independent_random_replacement_corrected_variance':tau/(1-p)**2,
      'corrected_within_solver_share':(tau/(1-p)**2)/(tau+e)} for p in [0,.01,.05,.10,.20]]
    c=duckdb.connect(str(DATA/'coverage.duckdb'),read_only=True)
    noextra=c.execute('SELECT explore,year,count(DISTINCT competition_id) finals,count(*)*5 attempts FROM eligible WHERE is_final AND extra_pool_rows=0 GROUP BY ALL ORDER BY explore,year').fetchdf().to_dict('records')
    dump('mapping-sensitivity.json',{'random_replacement_sensitivity':replace,'no_extra_pool_structural_counts':noextra,
      'not_a_bound':'Assumes independent random replacement; unknown targeted replacement can bias either way. Extra-pool presence is not usage. No exact-attempt attribution is verified. Confirmation requires an assignment audit or a revised scheduled-position estimand.'})
    robustness(C,v,S,d,ridx,g,y,fit)
    make_charts(fit,ci,rel,ext,best,a)
    progress('Step 9: Three draft PNGs and replacement sensitivities saved. Next: synthesize report, power and frozen preregistration specification.')

def robustness(C,v,S,d,ridx,g,y,fit,B=500):
    rng=np.random.default_rng(SEED+50);R=ridx.max()+1;periods=[]
    for label,mask in [('pre2019',g.year.to_numpy()<2019),('2019–2022',g.year.between(2019,2022).to_numpy()),('2023–2025',g.year.between(2023,2025).to_numpy()),('2026',g.year.to_numpy()==2026)]:
        st=aggregate(C,v,S,d,ridx,R,mask.astype(float));ok=st[3]>0;st=tuple(a[ok] for a in st)
        f,_=moment(st);draw=[]
        for _ in range(B):
            w=np.bincount(rng.integers(0,ok.sum(),ok.sum()),minlength=ok.sum());draw.append(moment(st,w)[0]['within_solver_share'])
        periods.append({'period':label,'rounds':int(ok.sum()),'valid_attempts':int(np.isfinite(y[mask]).sum()),
          'shared_fraction':f['within_solver_share'],'competition_95':np.quantile(draw,[.025,.975]).tolist()})
    leave=[]
    for year in range(2019,2026):
        w=(g.year.between(2019,2025)&(g.year!=year)).to_numpy().astype(float)
        st=aggregate(C,v,S,d,ridx,R,w);leave.append({'excluded_year':year,'shared_fraction':moment(st)[0]['within_solver_share']})
    negative=[]
    for _ in range(200):
        order=np.argsort(rng.random(y.shape),axis=1);yy=np.take_along_axis(y,order,axis=1)
        cc,vv,ss,dd=contributions(yy);negative.append(moment(aggregate(cc,vv,ss,dd,ridx,R))[0]['shared_variance'])
    best=pd.read_csv(OUT/'exploratory-season-extremes.csv');ext_period=[]
    for label,mask in [('2019–2022',best.year.between(2019,2022)),('2023–2025',best.year.between(2023,2025))]:
        b=best[mask];ext_period.append({'period':label,'n':len(b),'aggregate_unshrunk_ratio':float(np.exp(-b.unshrunk_peer_log_effect.mean()))})
    out={'periods':periods,'leave_year_out':leave,'extreme_periods':ext_period,
      'independent_solver_label_negative_control':{'draws':200,'shared_variance_95':np.quantile(negative,[.025,.975]).tolist(),
       'empirical_upper_tail_p':float((1+sum(x>=fit['shared_variance'] for x in negative))/201),
       'scope':'Independent permutation of each solver complete five-slot status/time vector destroys cross-peer alignment; a signal-negative-control, not scramble causation identification.'}}
    dump('robustness.json',out);progress('Era replication, leave-year-out shared fractions, and 200 independent-solver alignment negative-controls saved.')

def make_charts(fit,ci,rel,ext,best,a):
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':150})
    fig,ax=plt.subplots(1,2,figsize=(12,5))
    # Same observed seasonal extremes: speed relative to own round baseline.
    shared=np.log(ext['aggregate_unshrunk_ratio'])
    vals=[ext['within_round_log_speedup'],shared,ext['within_round_log_speedup']-shared]
    ax[0].bar(['Extreme speedup','Peer-explained','Unexplained'],100*np.array(vals),color=['#334155','#008b8b','#c8703d'])
    elo,ehi=np.log(ext['aggregate_unshrunk_95']);ax[0].errorbar(1,100*shared,yerr=[[100*(shared-elo)],[100*(ehi-shared)]],color='black',capsize=5)
    ax[0].set_ylabel('Log-speed advantage vs solver-round baseline (%)')
    ax[0].set_title(f'Obvious answer: the best solve looks exceptional\n{ext["n"]} exploratory solver-season minima')
    ax[1].bar(['Shared position /\nscramble','Remaining variation'],[100*fit['within_solver_share'],100*(1-fit['within_solver_share'])],color=['#008b8b','#c8703d'])
    lo,hi=ci['competition_solver']['within_solver_share'];ax[1].errorbar(0,100*fit['within_solver_share'],yerr=[[100*(fit['within_solver_share']-lo)],[100*(hi-fit['within_solver_share'])]],color='black',capsize=5)
    ax[1].set_ylabel('Within solver-round log-time variance (%)');ax[1].set_ylim(0,105)
    ax[1].set_title('Fairer test: how much do peers share?\nRemaining variation cannot be called personal luck')
    fig.text(.02,.015,'Exploration only. Scheduled mapping; replacements unresolved. Shared effect may include synchronized round conditions.',fontsize=9)
    fig.tight_layout(rect=[0,.05,1,1]);fig.savefig(OUT/'01-obvious-and-fairer.png');plt.close(fig)
    fig,ax=plt.subplots(1,2,figsize=(12,5));rows=rel['all_panels'];k=np.array([x['k'] for x in rows])
    ax[0].plot(k,[x['model_latent_reliability'] for x in rows],label='Model reliability of k-peer estimate',color='#008b8b')
    extra=np.arange(int(k.max()),201)
    fp=rel['frozen_parameters'];t=fp['shared_variance'];e=fp['residual_variance']
    ax[0].plot(extra,t/(t+e/extra),':',color='#008b8b',label='Model extrapolation (up to 200 peers)')
    ax[0].plot(k,[x['empirical_latent_reliability_approx'] for x in rows],'.',label='Empirical, noise-adjusted approximation',alpha=.65)
    fx=rel['fixed_large_panels'];ax[0].plot([x['k'] for x in fx],[x['empirical_latent_reliability_approx'] for x in fx],'--',label='Same large panels (n ≥ 20)',color='#c8703d')
    ax[0].set_ylim(-.03,1.1);ax[0].set_xscale('log');ax[0].set_xlim(1.8,210)
    ax[0].set_xticks([2,5,10,20,50,100,200],labels=['2','5','10','20','50','100','200'])
    ax[0].set_ylabel('Reliability of estimated common effect');ax[0].set_xlabel('Peers used (k, logarithmic scale)');ax[0].legend(fontsize=8)
    ax[1].plot(k,[100*x['individual_prediction_R2'] for x in rows],color='#008b8b');ax[1].axhline(100*rel['frozen_parameters']['within_solver_share'],linestyle='--',color='#c8703d',label='Training-model ceiling, infinitely many peers')
    xx=rel['representative_k_uncertainty']
    ax[1].errorbar([x['k'] for x in xx],[100*x['individual_prediction_R2'] for x in xx],
      yerr=np.array([[100*(x['individual_prediction_R2']-x['individual_prediction_R2_competition_95'][0]) for x in xx],
         [100*(x['individual_prediction_R2_competition_95'][1]-x['individual_prediction_R2']) for x in xx]]),fmt='o',capsize=4,color='black',label='Competition 95% intervals')
    ax[1].set_xlabel('Peers used (k)');ax[1].set_ylabel('Held-out individual log-time R² (%)');ax[1].legend(fontsize=8)
    fig.suptitle('More peers improve measurement, but the shared signal stays small')
    fig.text(.02,.015,'Random peer splits, exploration only. Eligibility changes with k; large-k points contain few finals. Extrapolation is model-dependent.',fontsize=9)
    fig.tight_layout(rect=[0,.05,1,.94]);fig.savefig(OUT/'02-reliability-vs-peers.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(11,5));b=best.sort_values('seconds').head(20).reset_index(drop=True);x=np.arange(len(b))
    ax.plot(x,b.seconds,'o',label='Observed seasonal minimum',color='#334155')
    ax.errorbar(x,b.adjusted_seconds,yerr=np.vstack([b.adjusted_seconds-b.adjusted_seconds*np.exp(-1.96*b.peer_se),b.adjusted_seconds*np.exp(1.96*b.peer_se)-b.adjusted_seconds]),fmt='o',capsize=2,color='#008b8b',label='Median shared-effect adjustment; model 95% interval')
    ax.set_xticks(x);ax.set_xticklabels([f'{i+1}' for i in x]);ax.set_xlabel('20 fastest exploratory solver-season minima (anonymous order)');ax.set_ylabel('Seconds')
    ax.set_title(f'A spectacular solve moves little after the peer correction\nAll {len(best)} minima: aggregate unshrunk ratio {ext["aggregate_unshrunk_ratio"]:.3f}; shrunk displays {ext["ratio"]:.3f}');ax.legend(fontsize=9)
    fig.text(.02,.015,'Per-solve bands condition on frozen Gaussian hyperparameters; they omit mapping error. No historical record attribution.',fontsize=9)
    fig.tight_layout(rect=[0,.05,1,1]);fig.savefig(OUT/'03-extreme-adjustment.png');plt.close(fig)

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['sources','simulation','analyze','report','all'],default='all',nargs='?');p.add_argument('--simulation-reps',type=int,default=400);p.add_argument('--bootstrap',type=int,default=1000);args=p.parse_args()
    if args.command in ['sources','all']:sources()
    if args.command in ['simulation','all']:
        simulation(args.simulation_reps)
        from validate import validate
        validate(args.simulation_reps)
    if args.command in ['analyze','all']:analyze(args.bootstrap)
    if args.command in ['report','all']:
        from report import report
        report()

if __name__=='__main__':main()
