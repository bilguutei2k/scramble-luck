"""Vectorized/compiled entire measurement pipeline, synthetic or real.

This module never opens confirmation magnitudes. Weighted operators use v_s
inside each round and w_c outside round moments. Residual noise uses v_s².
"""
import numpy as np
import pandas as pd
from numba import njit
from common import DERIVED, BETA

@njit(cache=True)
def contributions(y):
    n=len(y); C=np.zeros((n,5,5));z=np.zeros((n,5));ss=np.zeros(n);d=np.zeros(n);means=np.full(n,np.nan)
    for i in range(n):
        m=0;total=0.
        for j in range(5):
            if np.isfinite(y[i,j]):m+=1;total+=y[i,j]
        if m==0:continue
        means[i]=total/m;d[i]=max(0,m-1)
        for j in range(5):
            if not np.isfinite(y[i,j]):continue
            z[i,j]=y[i,j]-means[i];ss[i]+=z[i,j]**2
            for k in range(5):
                if np.isfinite(y[i,k]):C[i,j,k]=(1. if j==k else 0.)-1./m
    return C,z,ss,d,means

@njit(cache=True)
def weighted_median(values, weights):
    order=np.argsort(values);total=weights.sum()
    if total==0:return np.nan
    left=(total-1)//2;right=total//2;c=0.;a=np.nan;b=np.nan
    for k in order:
        c+=weights[k]
        if np.isnan(a) and c>left:a=values[k]
        if c>right:b=values[k];break
    return (a+b)/2

@njit(cache=True)
def refs_tiers(means,d,ridx,cidx,sidx,years,sw,cw,neighbors,ptr,round_rows,rptr,R):
    n=len(means);ref=np.full(n,np.nan);tiers=np.full(n,-1,dtype=np.int8)
    for i in range(n):
        if sw[sidx[i]]==0 or cw[cidx[i]]==0:continue
        total=0;distinct=0
        for p in range(ptr[i],ptr[i+1]):
            k=neighbors[p]
            if cw[cidx[k]]>0:total+=cw[cidx[k]];distinct+=1
        if distinct<2:continue
        left=(total-1)//2;right=total//2;c=0;a=np.nan
        for p in range(ptr[i],ptr[i+1]):
            k=neighbors[p];c+=cw[cidx[k]]
            if np.isnan(a) and c>left:a=means[k]
            if c>right:ref[i]=(a+means[k])/2;break
    supported=0;cells=0
    for r in range(R):
        ix=round_rows[rptr[r]:rptr[r+1]]
        vals=np.empty(len(ix));w=np.zeros(len(ix));nf=0;ns=0
        for p in range(len(ix)):
            i=ix[p];vals[p]=ref[i] if np.isfinite(ref[i]) else np.inf
            if np.isfinite(ref[i]) and d[i]>0 and sw[sidx[i]]>0 and cw[cidx[i]]>0:w[p]=sw[sidx[i]]
        if np.count_nonzero(w)<6:continue
        median=weighted_median(vals,w)
        for p in range(len(ix)):
            if w[p]>0:
                if vals[p]<median:nf+=1
                else:ns+=1
        if nf<3 or ns<3:continue
        supported+=1
        for p in range(len(ix)):
            if w[p]>0:
                i=ix[p];tiers[i]=0 if vals[p]<median else 1;cells+=int(d[i]+1)
    return ref,tiers,supported,cells

@njit(cache=True)
def accumulate(C,z,ss,d,ridx,sidx,sw,R,tiers,which):
    A=np.zeros((R,5,5));A2=np.zeros((R,5,5));V=np.zeros((R,5));S=np.zeros(R);D=np.zeros(R)
    for i in range(len(d)):
        w=sw[sidx[i]]
        if w==0 or (which>=0 and tiers[i]!=which):continue
        r=ridx[i];S[r]+=w*ss[i];D[r]+=w*d[i]
        for j in range(5):
            V[r,j]+=w*z[i,j]
            for k in range(5):A[r,j,k]+=w*C[i,j,k];A2[r,j,k]+=w*w*C[i,j,k]
    return A,V,S,D,A2

def moment(st,cw):
    A,V,S,d,A2=st
    den_d=cw@d
    if den_d<=0:return None
    beta=np.linalg.pinv(np.einsum('r,rij->ij',cw,A),rcond=1e-12)@(cw@V)
    centered=V-np.einsum('rij,j->ri',A,beta)
    Sc=S-2*(V@beta)+np.einsum('j,rjk,k->r',beta,A,beta)
    total=(cw@Sc)/den_d
    noise=np.trace(A2,axis1=1,axis2=2)
    denom=cw@(np.sum(A*A,axis=(1,2))-noise)
    if denom<=0:return None
    b=float((cw@(np.sum(centered*centered,axis=1)-total*noise))/denom)
    return {'b':b,'e':float(total-b),'total':float(total),'beta':beta,'A':A,'V':centered,
            'moment_denominator':float(denom),'contrast_degrees':float(den_d)}

def tier_fit(fast,slow,cw):
    f=moment(fast,cw);s=moment(slow,cw)
    if f is None or s is None:return None
    crossden=cw@np.sum(f['A']*s['A'],axis=(1,2))
    if crossden<=0:return None
    c=float((cw@np.sum(f['V']*s['V'],axis=1))/crossden)
    tau=(f['b']+s['b']+2*c)/4;gamma=(f['b']+s['b']-2*c)/4;D=(f['total']+s['total'])/2
    if D<=0:return None
    return {'F':tau/D,'gamma_over_D':gamma/D,'tau':tau,'gamma':gamma,'D':D,
            'fast_shared_variance':f['b'],'slow_shared_variance':s['b'],'cross_covariance':c,
            'fast_residual_variance':f['e'],'slow_residual_variance':s['e'],
            'fast_position':f['beta'],'slow_position':s['beta']}

@njit(cache=True)
def select_best(order,ptr,row_min,cidx,sidx,sw,cw):
    rows=np.full(len(ptr)-1,-1,dtype=np.int64)
    absent=0;no_success=0
    for g in range(len(rows)):
        exists=False
        for k in range(ptr[g],ptr[g+1]):
            i=order[k]
            if sw[sidx[i]]==0 or cw[cidx[i]]==0:continue
            exists=True
            if np.isfinite(row_min[i]):rows[g]=i;break
        if not exists:absent+=1
        elif rows[g]<0:no_success+=1
    return rows,absent,no_success

def project(A,V,C,z,ridx,sidx,sw,rows,beta):
    w=sw[sidx[rows]]
    Ap=A[ridx[rows]]-C[rows]*w[:,None,None]
    vp=V[ridx[rows]]-z[rows]*w[:,None]-np.einsum('nij,j->ni',Ap,beta)
    eig,U=np.linalg.eigh(Ap)
    rank=np.sum(eig>1e-9,axis=1)
    denom=np.where(eig>1e-9,eig,np.inf)
    h=np.einsum('nij,nj->ni',U,np.einsum('nji,nj->ni',U,vp)/denom)
    return h,rank,Ap

class Structure:
    def __init__(self):
        self.g=pd.read_parquet(DERIVED/'structure.parquet')
        self.tg=pd.read_parquet(DERIVED/'training.parquet')
        self.solvers=np.union1d(self.g.person_id.unique(),self.tg.person_id.unique())
        self.sidx=np.searchsorted(self.solvers,self.g.person_id)
        self.tsidx=np.searchsorted(self.solvers,self.tg.person_id)
        self.comps,self.cidx=np.unique(self.g.competition_id,return_inverse=True)
        self.tcomps,self.tcidx=np.unique(self.tg.competition_id,return_inverse=True)
        self.ridx=pd.factorize(self.g.competition_id+'|'+self.g.round_type_id,sort=True)[0]
        self.tridx=pd.factorize(self.tg.competition_id+'|'+self.tg.round_type_id,sort=True)[0]
        self.R=self.ridx.max()+1;self.TR=self.tridx.max()+1
        self.round_comp=np.zeros(self.R,dtype=int);self.round_comp[self.ridx]=self.cidx
        self.train_comp=np.zeros(self.TR,dtype=int);self.train_comp[self.tridx]=self.tcidx
        self.status=self.g[[f'status{j}' for j in range(1,6)]].to_numpy()
        self.years=self.g.year.to_numpy()
        self.round_rows=np.argsort(self.ridx,kind='stable')
        self.rptr=np.r_[0,np.cumsum(np.bincount(self.ridx,minlength=self.R))]
        self.solver_rows=np.argsort(self.sidx,kind='stable')
        self.sptr=np.r_[0,np.cumsum(np.bincount(self.sidx,minlength=len(self.solvers)))]
        groups=self.g.groupby(['person_id','year'],sort=True).indices
        self.season_keys=[key for key,ix in groups.items() if len(np.unique(self.cidx[ix]))>=5]
        self.season_rows=[groups[k] for k in self.season_keys]
        self.N=len(self.g);self.S=len(self.solvers);self.C=len(self.comps);self.TC=len(self.tcomps)
        self.tie_order=np.lexsort((self.g.result_id.astype(str),self.g.round_type_id,self.g.competition_id))
        self.tie_rank=np.empty(self.N,dtype=int);self.tie_rank[self.tie_order]=np.arange(self.N)

    def weights(self,rng,method='pigeonhole'):
        # Exact documented draw order: confirmation competitions, solver union, training competitions.
        cw=np.bincount(rng.integers(self.C,size=self.C),minlength=self.C).astype(float)
        sw=np.bincount(rng.integers(self.S,size=self.S),minlength=self.S).astype(float)
        tw=np.bincount(rng.integers(self.TC,size=self.TC),minlength=self.TC).astype(float)
        if method=='competition_only':sw[:]=1
        if method=='solver_only':cw[:]=1;tw[:]=1
        return cw,sw,tw

class Dataset:
    def __init__(self,structure,y,ty,latent=None):
        self.st=structure;self.y=y;self.ty=ty;self.latent=latent
        self.C,self.z,self.ss,self.d,self.means=contributions(y)
        self.TC,self.tz,self.tss,self.td,self.tmeans=contributions(ty)
        self.row_min=np.min(np.where(np.isfinite(y),y,np.inf),axis=1)
        self.row_min[~np.isfinite(self.row_min)]=np.nan
        self.js=np.argmin(np.where(np.isfinite(y),y,np.inf),axis=1)
        order=[];ptr=[0]
        for ix in structure.season_rows:
            order.extend(ix[np.lexsort((structure.tie_rank[ix],self.row_min[ix]))]);ptr.append(len(order))
        self.order=np.array(order,dtype=np.int64);self.ptr=np.array(ptr,dtype=np.int64)
        # Candidate other-finals sorted once by their mean; resampling changes weights, not values.
        neighbors=[];nptr=[0]
        for i in range(structure.N):
            s=structure.sidx[i];ix=structure.solver_rows[structure.sptr[s]:structure.sptr[s+1]]
            ix=ix[(np.abs(structure.years[ix]-structure.years[i])<=2)&(structure.cidx[ix]!=structure.cidx[i])&np.isfinite(self.means[ix])]
            neighbors.extend(ix[np.argsort(self.means[ix],kind='stable')]);nptr.append(len(neighbors))
        self.neighbors=np.array(neighbors,dtype=np.int64);self.nptr=np.array(nptr,dtype=np.int64)
        if latent is not None:
            _,self.lz,self.lss,_,_=contributions(np.where(np.isfinite(y),latent,np.nan))

    def run(self,cw=None,sw=None,tw=None,details=False,oracle=False):
        st=self.st;original=cw is None
        if cw is None:cw=np.ones(st.C);sw=np.ones(st.S);tw=np.ones(st.TC)
        train=accumulate(self.TC,self.tz,self.tss,self.td,st.tridx,st.tsidx,sw,st.TR,np.zeros(len(st.tg),dtype=np.int8),-1)
        training=moment(train,tw[st.train_comp])
        beta=BETA if original else (training['beta'] if training is not None else np.full(5,np.nan))
        ref,tiers,supported,cells=refs_tiers(self.means,self.d,st.ridx,st.cidx,st.sidx,st.years,sw,cw,self.neighbors,self.nptr,st.round_rows,st.rptr,st.R)
        fast=accumulate(self.C,self.z,self.ss,self.d,st.ridx,st.sidx,sw,st.R,tiers,0)
        slow=accumulate(self.C,self.z,self.ss,self.d,st.ridx,st.sidx,sw,st.R,tiers,1)
        fit=tier_fit(fast,slow,cw[st.round_comp])
        allst=accumulate(self.C,self.z,self.ss,self.d,st.ridx,st.sidx,sw,st.R,tiers,-1)
        rows,absent,nosuccess=select_best(self.order,self.ptr,self.row_min,st.cidx,st.sidx,sw,cw)
        rows=rows[rows>=0]
        if oracle:
            lst=accumulate(self.C,self.lz,self.lss,self.d,st.ridx,st.sidx,sw,st.R,tiers,-1)
            h,rank,_=project(lst[0],lst[1],self.C,self.lz,st.ridx,st.sidx,sw,rows,np.zeros(5))
        else:h,rank,_=project(allst[0],allst[1],self.C,self.z,st.ridx,st.sidx,sw,rows,beta)
        identified=rank==4
        weights=sw[st.sidx[rows]][identified];selected=rows[identified]
        effects=h[identified,self.js[selected]]
        logR=float(-np.average(effects,weights=weights)) if len(effects) and np.all(np.isfinite(effects)) else np.nan
        out={'logR':logR,'F':fit['F'] if fit is not None else np.nan,
             'gamma_over_D':fit['gamma_over_D'] if fit is not None else np.nan,
             'available_extrema':len(selected),'absent_seasons':absent,'no_success_seasons':nosuccess,
             'unidentified_extrema':int((~identified).sum()),'tier_supported_finals':supported,'tier_successful_cells':cells}
        if details:
            out.update(fit=fit,beta=beta,training_fit=training,rows=selected,h=h[identified],effects=effects,
                       skill_reference=ref,tiers=tiers,allst=allst,weights=weights)
        return out
