#!/usr/bin/env python3
"""Independent small synthetic re-derivations; no confirmation magnitudes.

Tests literal replicated peers against product weights; verifies nuisance fits,
minimum reselection, weighted medians and rank diagnostics independently of the
optimized routines. Run before accepting any gate or opening confirmation.
"""
import numpy as np
from common import dump, progress, SEED
from engine import contributions, accumulate, moment, project, weighted_median, refs_tiers, select_best

def main():
    rng=np.random.default_rng(SEED+9000);checks=[]
    n=14;y=rng.normal(size=(n,5));y[0,2:]=np.nan;y[1,:]=np.nan;y[2,1:]=np.nan
    C,z,S,d,means=contributions(y);ridx=np.zeros(n,dtype=int);sidx=np.arange(n)
    weights=rng.integers(0,4,n).astype(float);weights[0]=2
    st=accumulate(C,z,S,d,ridx,sidx,weights,1,np.zeros(n,dtype=np.int8),-1)
    rows=np.arange(n)
    h,rank,Ap=project(st[0],st[1],C,z,ridx,sidx,weights,rows,np.zeros(5))
    maximum_error=0
    for target in rows:
        # Construct the actual repeated table and remove ALL copies of target.
        repeated=np.repeat(np.arange(n),weights.astype(int));repeated=repeated[repeated!=target]
        A=C[repeated].sum(0);V=z[repeated].sum(0)
        independent=np.linalg.pinv(A)@V
        maximum_error=max(maximum_error,float(np.max(np.abs(independent-h[target]))))
    checks.append({'name':'explicit_copies_exclude_every_focal_solver_copy','pass':maximum_error<1e-10,'max_error':maximum_error})
    checks.append({'name':'squared_weights_not_independent_copies_noise_operator','pass':bool(np.allclose(st[4][0],np.sum(C*weights[:,None,None]**2,axis=0)) and not np.allclose(st[4],st[0]))})
    h,rank,_=project(np.zeros((1,5,5)),np.zeros((1,5)),C*0,z*0,ridx,sidx,np.ones(n),np.arange(n),np.zeros(5))
    checks.append({'name':'empty_peer_graph_is_unidentified','pass':bool(np.all(rank==0))})
    for trial in range(100):
        values=rng.normal(size=10);w=rng.integers(0,4,10).astype(float)
        assert np.allclose(weighted_median(values,w),np.median(np.repeat(values,w.astype(int))))
    checks.append({'name':'weighted_median_matches_literal_repeated_sample','pass':True,'cases':100})
    # Two apparent copies of ONE other final cannot supply a skill reference.
    nr=4;nc=4;ns=1
    ref,tiers,supported,cells=refs_tiers(np.arange(4,dtype=float),np.full(4,4.),
        np.arange(4),np.arange(4),np.zeros(4,dtype=int),np.full(4,2020),np.ones(1),np.array([1.,20.,0.,0.]),
        np.array([1,2,3,0,2,3,0,1,3,0,1,2]),np.array([0,3,6,9,12]),np.arange(4),np.arange(5),4)
    checks.append({'name':'reference_requires_two_distinct_other_finals','pass':bool(np.isnan(ref[0]))})
    # Ability/intercepts cancel exactly with any missing pattern.
    intercept=rng.normal(size=(n,1));_,z2,S2,d2,_=contributions(y+intercept)
    checks.append({'name':'solver_round_intercepts_cancel_with_missingness','pass':bool(np.allclose(z,z2) and np.allclose(S,S2) and np.allclose(d,d2))})
    # Position re-fit after frozen subtraction is algebraically invariant.
    ridx=np.repeat(np.arange(20),n);sidx=np.tile(np.arange(n),20)
    yy=rng.normal(size=(len(ridx),5));cc,vv,ss,dd,_=contributions(yy)
    shift=np.array([.1,-.2,.03,.04,.03]);cc2,vv2,ss2,dd2,_=contributions(yy-shift)
    original=moment(accumulate(cc,vv,ss,dd,ridx,sidx,np.ones(n),20,np.zeros(len(ridx),dtype=np.int8),-1),np.ones(20))
    shifted=moment(accumulate(cc2,vv2,ss2,dd2,ridx,sidx,np.ones(n),20,np.zeros(len(ridx),dtype=np.int8),-1),np.ones(20))
    checks.append({'name':'tier_position_refit_absorbs_initial_global_beta','pass':bool(np.allclose(original['b'],shifted['b']) and np.allclose(original['e'],shifted['e']))})
    dump('verification.json',{'all_checks_passed':all(x['pass'] for x in checks),'checks':checks,'positive_confirmation_times_read':False})
    assert all(x['pass'] for x in checks)
    progress(f'Independent verification: all {len(checks)} literal-copy, median, rank, missingness and nuisance-invariance checks pass; confirmation magnitudes unopened.')

if __name__=='__main__':main()
