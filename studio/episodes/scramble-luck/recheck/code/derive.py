"""Independent implementation; inputs are the raw ZIP and registered constants only."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import json, hashlib, zipfile, time, sys
from pathlib import Path
import numpy as np
import pandas as pd
BASE=Path(__file__).resolve().parents[1]; EP=BASE.parent
RAW=EP/'data/raw/WCA_export_v2_273_20260930T000036Z.tsv.zip'
BETA=np.array([-.00019098085080805892,.0015330545917410243,-.00016398101357186266,-.005728817307245912,.0045507245798848085])
vals={}; counts={}
def put(k,v,n,definition):
 vals[k]={'value':v.item() if isinstance(v,np.generic) else v,'n':int(n),'definition':definition}
def read(z,name,**kw):
 return pd.read_csv(z.open('WCA_export_'+name+'.tsv'),sep='\t',keep_default_na=False,**kw)
def extract():
 t=time.time(); h=hashlib.sha256()
 with RAW.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 assert h.hexdigest()=='e6b262b2ada513228a48fa221015ddc25e9041a029340778cd253f564c23427d'
 with zipfile.ZipFile(RAW) as z:
  comp=read(z,'competitions',usecols=['id','year'])
  comp['explore']=comp.id.map(lambda x:int(hashlib.sha256(x.encode()).hexdigest(),16)%5==0)
  for label,mask in [('exploration',comp.explore),('confirmation',~comp.explore)]:
   ids=sorted(comp.loc[mask,'id']); counts[label+'_all_ids']=len(ids)
   counts[label+'_ids_sha256']=hashlib.sha256(('\n'.join(ids)+'\n').encode()).hexdigest()
  cf=set(comp.loc[~comp.explore & comp.year.between(2019,2025),'id'])
  tr=set(comp.loc[comp.explore & (comp.year<2019),'id']); wanted=cf|tr
  years=dict(zip(comp.id,comp.year))
  finals=set(read(z,'round_types').query('final == 1').id.astype(str))
  chunks=[]
  for d in read(z,'results',chunksize=400000,usecols=['id','competition_id','round_type_id','event_id','person_id','format_id'],dtype={'round_type_id':str,'event_id':str}):
   scope=d.competition_id.isin(cf)
   counts['scope_results']=counts.get('scope_results',0)+int(scope.sum())
   for name,test in [('other_event',d.event_id!='333'),('nonfinal',~d.round_type_id.isin(finals)),('invalid_format',d.format_id!='a')]:
    counts[name]=counts.get(name,0)+int((scope&test).sum());scope &= ~test
   d=d[d.competition_id.isin(wanted)&(d.event_id=='333')&d.round_type_id.isin(finals)&(d.format_id=='a')]
   chunks.append(d)
  results=pd.concat(chunks,ignore_index=True)
  schedules=[]
  for d in read(z,'scrambles',chunksize=400000,dtype={'round_type_id':str,'event_id':str}):
   schedules.append(d[d.competition_id.isin(wanted)&(d.event_id=='333')&d.round_type_id.isin(finals)])
  sched=pd.concat(schedules,ignore_index=True)
  valid=set(); reasons={}; pools=set()
  for key,d in sched.groupby(['competition_id','round_type_id']):
   if (d.is_extra==1).any():pools.add(key)
   r=d[d.is_extra==0]
   if r.group_id.nunique()!=1:reason='multigroup_or_no_regular_group'
   elif len(r)!=5 or sorted(r.scramble_num)!=[1,2,3,4,5] or (r.scramble.str.strip()=='').any():reason='ambiguous_regular_schedule'
   else: valid.add(key);continue
   reasons[key]=reason
  results['panelkey']=list(zip(results.competition_id,results.round_type_id))
  bad=results[~results.panelkey.isin(valid)&results.competition_id.isin(cf)]
  for key,d in bad.groupby('panelkey'):
   r=reasons.get(key,'missing_schedule'); counts[r+'_results']=counts.get(r+'_results',0)+len(d);counts[r+'_finals']=counts.get(r+'_finals',0)+1
  results=results[results.panelkey.isin(valid)].copy()
  ids=set(results.id);ats=[]
  for d in read(z,'result_attempts',chunksize=1000000):ats.append(d[d.result_id.isin(ids)])
  att=pd.concat(ats,ignore_index=True)
  shape=att.groupby('result_id').attempt_number.agg(['size','nunique','min','max'])
  good=set(shape.index[(shape['size']==5)&(shape['nunique']==5)&(shape['min']==1)&(shape['max']==5)])
  for label,mask in [('incomplete_duplicate_slots',~results.id.isin(good))]:counts[label+'_results']=int((mask&results.competition_id.isin(cf)).sum())
  results=results[results.id.isin(good)]
  badstatus=set(att.loc[~((att.value>0)|att.value.isin([-1,-2])),'result_id'])
  counts['invalid_status_results']=int((results.id.isin(badstatus)&results.competition_id.isin(cf)).sum())
  results=results[~results.id.isin(badstatus)].copy()
  results=results.sort_values(['competition_id','round_type_id','person_id','id']).reset_index(drop=True)
  wide=att[att.result_id.isin(results.id)].pivot(index='result_id',columns='attempt_number',values='value').loc[results.id].to_numpy()
  results['year']=results.competition_id.map(years);results['training']=results.competition_id.isin(tr);results['extra_pool']=results.panelkey.isin(pools)
  results.drop(columns='panelkey').to_pickle(BASE/'raw_rows.pkl');np.save(BASE/'raw_times.npy',wide)
  (BASE/'extraction.json').write_text(json.dumps(counts,indent=2))
 print('raw extraction seconds',round(time.time()-t),flush=True)

def arrays(rows,times):
 q=(times>0).astype(float); m=q.sum(1); yy=np.log(np.where(times>0,times/100,1))
 C=np.einsum('ni,ij->nij',q,np.eye(5))-np.einsum('ni,nj->nij',q,q)/np.maximum(m,1)[:,None,None]
 C[m<2]=0
 y=np.einsum('nij,nj->ni',C,yy)
 keys=list(zip(rows.competition_id,rows.round_type_id)); panel,_=pd.factorize(pd.Series(keys),sort=True)
 return dict(C=C,y=y,m=m,d=np.maximum(m-1,0),panel=panel,P=panel.max()+1,yy=yy)
def fit_beta(a,weights):
 return np.linalg.pinv(np.einsum('n,nij->ij',weights,a['C']),rcond=1e-12)@np.einsum('n,ni->i',weights,a['y'])
def reference(rows,a):
 means=np.divide(a['yy'].sum(1),a['m'],out=np.full(len(rows),np.nan),where=a['m']>0)
 ref=np.full(len(rows),np.nan); year_array=rows.year.to_numpy(); comp_array=rows.competition_id.to_numpy()
 for _,ix in rows.groupby('person_id').indices.items():
  for i in ix:
   js=ix[(np.abs(year_array[ix]-year_array[i])<=2)&(comp_array[ix]!=comp_array[i])&np.isfinite(means[ix])]
   if len(js)>=2:ref[i]=np.median(means[js])
 return ref

def tier_stats(rows,a,ref,subset=None):
 if subset is None:subset=np.ones(len(rows),bool)
 eligible=np.isfinite(ref)&(a['m']>=2)&subset
 fast=np.zeros(len(rows),bool);slow=fast.copy();supported=[]
 for p in range(a['P']):
  ix=np.flatnonzero((a['panel']==p)&eligible)
  if not len(ix):continue
  f=ix[ref[ix]<np.median(ref[ix])];s=ix[ref[ix]>=np.median(ref[ix])]
  if len(f)>=3 and len(s)>=3:fast[f]=True;slow[s]=True;supported.append(p)
 out=[]
 for mask in [fast,slow]:
  beta=fit_beta(a,mask.astype(float))
  x=a['y']-np.einsum('nij,j->ni',a['C'],beta)
  A=np.zeros((a['P'],5,5));V=np.zeros((a['P'],5));S=np.zeros(a['P']);d=np.zeros(a['P'])
  np.add.at(A,a['panel'][mask],a['C'][mask]);np.add.at(V,a['panel'][mask],x[mask]);np.add.at(S,a['panel'][mask],(x[mask]**2).sum(1));np.add.at(d,a['panel'][mask],a['d'][mask])
  b=((V**2).sum()-S.sum())/((A**2).sum()-d.sum());e=S.sum()/d.sum()-b
  out.append((A,V,b,e))
 A,V,bf,ef=out[0];B,W,bs,es=out[1]
 c=(V*W).sum()/(A*B).sum();tau=(bf+bs+2*c)/4;gamma=(bf+bs-2*c)/4;D=(bf+ef+bs+es)/2
 return dict(F=tau/D,gamma_share=gamma/D,tau=tau,gamma=gamma,D=D,b_fast=bf,b_slow=bs,e_fast=ef,e_slow=es,c=c,finals=len(supported),successes=int(a['m'][fast|slow].sum()),rows=int((fast|slow).sum()),missing_reference=int((~np.isfinite(ref)&(a['m']>=2)&subset).sum()))

def peer_selected(a,solverweights,beta,selected,slots):
 C=a['C'];x=a['y']-np.einsum('nij,j->ni',C,beta);p=a['panel'];P=a['P']
 A=np.zeros((P,5,5));V=np.zeros((P,5));np.add.at(A,p,C*solverweights[:,None,None]);np.add.at(V,p,x*solverweights[:,None])
 # One result per solver-panel verified below: removing the row removes all focal copies.
 mat=A[p[selected]]-C[selected]*solverweights[selected,None,None]
 rhs=V[p[selected]]-x[selected]*solverweights[selected,None]
 eig,U=np.linalg.eigh(mat);rank=(eig>1e-9).sum(1)==4
 inv=np.divide(1,eig,out=np.zeros_like(eig),where=eig>1e-9)
 h=np.einsum('nik,nk,njk,nj->ni',U,inv,U,rhs)
 return -h[np.arange(len(selected)),slots],rank

def main(draws=2000):
 if not (BASE/'raw_rows.pkl').exists():extract()
 rows=pd.read_pickle(BASE/'raw_rows.pkl');times=np.load(BASE/'raw_times.npy');ct=json.loads((BASE/'extraction.json').read_text())
 train=rows.training.to_numpy();tr=rows[train].reset_index(drop=True);tt=times[train];r=rows[~train].reset_index(drop=True);t=times[~train]
 a=arrays(r,t);ta=arrays(tr,tt)
 assert not r.duplicated(['competition_id','round_type_id','person_id']).any()
 for k,v in ct.items():
  if isinstance(v,int):put('exclusion_'+k if k not in ['scope_results'] else k,v,ct['scope_results'],'Sequential raw-result exclusion/count: '+k)
 for k,v,definition in [('finals',a['P'],'Distinct included competition/final-round panels'),('attempt_slots',t.size,'Five included scheduled slots per solver result'),('successes',int((t>0).sum()),'Positive official attempt values'),('dnf',int((t==-1).sum()),'Official -1 attempt values'),('dns',int((t==-2).sum()),'Official -2 attempt values'),('solvers',r.person_id.nunique(),'Distinct included WCA person IDs'),('solver_results',len(r),'Included solver-final rows'),('under_two_success_rows',int((a['m']<2).sum()),'Rows retained in counts but uninformative for time contrasts')]:put(k,v,len(r),definition)
 roster=r.groupby(['person_id','year']).competition_id.nunique();roster=roster[roster>=5]
 seasons=list(roster.index);season_index={k:i for i,k in enumerate(seasons)}
 season=np.array([season_index.get(k,-1) for k in zip(r.person_id,r.year)])
 mint=np.where(t>0,t,np.inf).min(1);slot=np.where(t>0,t,np.inf).argmin(1)
 # Stable sort implements competition, round, attempt, result tie breaking.
 candidates=pd.DataFrame({'row':np.arange(len(r)),'value':mint,'comp':r.competition_id,'round':r.round_type_id,'slot':slot,'id':r.id}).sort_values(['value','comp','round','slot','id'])['row'].to_numpy()
 candidates=candidates[(season[candidates]>=0)&np.isfinite(mint[candidates])]
 def select(cw,rowc):
  cand=candidates[cw[rowc[candidates]]>0];ss=season[cand];_,ix=np.unique(ss,return_index=True);return cand[ix]
 comps=sorted(r.competition_id.unique());rowc=pd.Categorical(r.competition_id,categories=comps).codes
 solvers=sorted(set(r.person_id)|set(tr.person_id));rowsol=pd.Categorical(r.person_id,categories=solvers).codes;trsol=pd.Categorical(tr.person_id,categories=solvers).codes
 trcomps=sorted(tr.competition_id.unique());trc=pd.Categorical(tr.competition_id,categories=trcomps).codes
 selected=select(np.ones(len(comps)),rowc);x,ok=peer_selected(a,np.ones(len(r)),BETA,selected,slot[selected]);theta=x[ok].mean()
 put('eligible_solver_seasons',len(seasons),len(roster),'Person-years with at least five distinct included confirmation competitions')
 put('no_success_seasons',len(seasons)-len(selected),len(seasons),'Eligible seasons with no successful solve')
 put('unidentified_extrema',int((~ok).sum()),len(selected),'Selected extrema whose leave-focal-out peer matrix has rank below four')
 put('available_extrema',int(ok.sum()),len(seasons),'Eligible seasons with successful and identified selected extrema')
 put('R',float(np.exp(theta)),ok.sum(),'Geometric mean exp(-peer shared contrast) across available person-years')
 put('R_arithmetic',float(np.exp(x[ok]).mean()),ok.sum(),'Arithmetic mean of estimated adjusted/observed ratios')
 xx=pd.Series(x[ok]).groupby(r.person_id.iloc[selected[ok]].to_numpy()).mean()
 put('R_solver_weighted',float(np.exp(xx.mean())),len(xx),'Average log ratio within solver, then equally across solvers, exponentiated')
 print('points: R computed',flush=True);ref=reference(r,a);stats=tier_stats(r,a,ref);print('points: F computed',flush=True)
 for k,v in stats.items():put('tier_'+k,v,stats['finals'],'Balanced-tier moment quantity: '+k)
 put('training_beta',fit_beta(ta,np.ones(len(tr))).tolist(),len(tr),'Pooled pre-2019 exploration solver-demeaned position coefficients')
 for lo,hi in [(2019,2022),(2023,2025)]:
  mask=r.year.between(lo,hi).to_numpy();st=tier_stats(r,a,ref,mask);eraok=ok&mask[selected]
  for k in ['F','gamma_share','finals','successes']:put(f'{lo}_{hi}_{k}',st[k],st['finals'],'Era-restricted tier measure with full-window skill references: '+k)
  put(f'{lo}_{hi}_R',float(np.exp(x[eraok].mean())),eraok.sum(),'Geometric seasonal ratio in the named calendar-year era')
 rng=np.random.default_rng(20261001);stars=[];fixed=[];absent=[];nvalid=[];exposures=[];betas=[];start=time.time()
 for b in range(0 if '--reuse-bootstrap' in sys.argv else draws):
  cw=rng.multinomial(len(comps),np.full(len(comps),1/len(comps)))
  sw=rng.multinomial(len(solvers),np.full(len(solvers),1/len(solvers)))
  tw=rng.multinomial(len(trcomps),np.full(len(trcomps),1/len(trcomps)))
  beta=fit_beta(ta,tw[trc]*sw[trsol]);sel=select(cw,rowc);sel=sel[sw[rowsol[sel]]>0]
  xb,valid=peer_selected(a,sw[rowsol],beta,sel,slot[sel]);weight=sw[rowsol[sel]]
  stars.append(np.average(xb[valid],weights=weight[valid]) if valid.any() else np.nan)
  fs=selected[(cw[rowc[selected]]>0)&(sw[rowsol[selected]]>0)]
  xf,vf=peer_selected(a,sw[rowsol],beta,fs,slot[fs]);fw=cw[rowc[fs]]*sw[rowsol[fs]]
  fixed.append(np.average(xf[vf],weights=fw[vf]) if vf.any() else np.nan)
  absent.append(len(seasons)-len(sel));nvalid.append(int(valid.sum()));exposures.append(int(np.count_nonzero(cw)));betas.append(beta)
  if (b+1)%100==0:print('bootstrap',b+1,'seconds',round(time.time()-start),flush=True)
 if '--reuse-bootstrap' in sys.argv:
  saved=np.load(BASE/'bootstrap.npz');stars=saved['logR'];fixed=saved['fixed_logR'];absent=saved['absent'];nvalid=saved['valid_seasons'];exposures=saved['distinct_competitions'];betas=saved['beta']
 stars=np.array(stars);fixed=np.array(fixed);np.savez(BASE/'bootstrap.npz',logR=stars,fixed_logR=fixed,absent=absent,valid_seasons=nvalid,distinct_competitions=exposures,beta=betas)
 finite=stars[np.isfinite(stars)];ci=np.exp(theta+np.quantile(finite-finite.mean(),[.025,.975]));rawci=np.exp(np.quantile(finite,[.025,.975]))
 put('R_ci95',ci.tolist(),len(finite),'Amendment B: exponentiated mean-recentered linear log-R percentile endpoints')
 put('R_bootstrap_raw_ci95',rawci.tolist(),len(finite),'Uncentered reselecting percentile interval, diagnostic only')
 put('R_bootstrap_mean_log',float(finite.mean()),len(finite),'Mean reselecting bootstrap log R')
 put('R_bootstrap_displacement',float(finite.mean()-theta),len(finite),'Bootstrap mean log R minus original log R')
 put('R_fixed_ci95',np.exp(np.quantile(fixed[np.isfinite(fixed)],[.025,.975])).tolist(),int(np.isfinite(fixed).sum()),'Amendment A: fixed original extrema with competition times solver weights')
 put('bootstrap_valid_draws',len(finite),draws,'Finite reselecting pigeonhole bootstrap draws')
 put('bootstrap_absent_seasons_mean',float(np.mean(absent)),draws,'Mean roster seasons absent after competition and solver resampling')
 put('bootstrap_distinct_competitions_mean',float(np.mean(exposures)),draws,'Mean distinct included confirmation competitions in a draw')
 verdict='belief fails' if ci[1]<=1.1 else ('belief holds' if ci[0]>1.1 else 'inconclusive')
 if len(finite)<1900:verdict='inconclusive: fewer than 1900 valid draws (recheck compute limit)'
 put('verdict',verdict,len(finite),'Registered interval decision, conditional on accepted validation gate and coverage checks')
 (BASE/'values.json').write_text(json.dumps(vals,indent=2,allow_nan=False)+'\n')
 print(json.dumps({k:vals[k]['value'] for k in ['finals','attempt_slots','successes','dnf','dns','eligible_solver_seasons','tier_F','tier_gamma_share','R','R_ci95','verdict']}),flush=True)
if __name__=='__main__':main()
