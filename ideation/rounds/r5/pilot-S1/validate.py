"""Supplemental simulation: identifiable interactions and extreme selection.
Run AFTER pilot.py simulation and BEFORE pilot.py analyze.
"""
import numpy as np, pandas as pd
from pilot import OUT,SEED,dump,progress,contributions,aggregate,tier_interval

def validate(reps=400):
    sizes=pd.read_csv(OUT/'panel-sizes.csv').n.to_numpy();R=len(sizes)
    ridx=np.repeat(np.arange(R),sizes);N=len(ridx)
    tier=np.concatenate([np.where(np.arange(n)%2==0,1.,-1.) for n in sizes])
    rng=np.random.default_rng(SEED+100);rows=[]
    for label,tau,gamma in [('shared_and_tier',.0009,.0025),('tier_only',0.,.0025),('no_tier',.0009,0.)]:
        est=[];cover=[]
        for _ in range(reps):
            shared=rng.normal(0,np.sqrt(tau),(R,5));personal=rng.normal(0,np.sqrt(gamma),(R,5))
            y=shared[ridx]+tier[:,None]*personal[ridx]+rng.normal(0,np.sqrt(.0222),(N,5))
            C,v,S,d=contributions(y)
            F=aggregate(C,v,S,d,ridx,R,(tier==1).astype(float));T=aggregate(C,v,S,d,ridx,R,(tier==-1).astype(float))
            fit,ci=tier_interval(F,T);est.append([fit['shared_variance'],fit['interaction_variance']])
            cover.append([ci['shared_variance'][0]<=tau<=ci['shared_variance'][1],ci['interaction_variance'][0]<=gamma<=ci['interaction_variance'][1]])
        mean=np.mean(est,axis=0)
        rows.append({'scenario':label,'replicates':reps,'shared_truth':tau,'interaction_truth':gamma,
          'shared_mean':float(mean[0]),'shared_bias':float(mean[0]-tau),
          'interaction_mean':float(mean[1]),'interaction_bias':float(mean[1]-gamma),
          'shared_95_coverage':float(np.mean(cover,axis=0)[0]),'interaction_95_coverage':float(np.mean(cover,axis=0)[1])})
        dump('interaction-simulation.json',rows);progress(f'Interaction validation saved: {label}; shared and interaction coverage {np.mean(cover,axis=0).round(3).tolist()}.')
    # 300 synthetic solver-seasons per replicate; 5 finals x 5 attempts.
    # Actual sizes sampled from locked panels; both solver and peers centered
    # within round, exactly like the estimator. Reselect all seasonal minima.
    attribution=[]
    for tau in [.0009,.004]:
        truths=[];shrunks=[];raws=[];rawcovers=[];shrinkcovers=[]
        for _ in range(reps):
            n=rng.choice(sizes,(300,5))-1
            s=rng.normal(0,np.sqrt(tau),(300,5,5));s-=s.mean(2,keepdims=True)
            eps=rng.normal(0,np.sqrt(.0222),(300,5,5));eps-=eps.mean(2,keepdims=True)
            peer_noise=rng.normal(0,1,(300,5,5))*np.sqrt(.0222/n)[:,:,None];peer_noise-=peer_noise.mean(2,keepdims=True)
            skill_round=rng.normal(0,.04,(300,5,1))
            y=s+eps+skill_round
            best=np.argmin(y.reshape(300,25),axis=1);index=(np.arange(300),best//5,best%5)
            true=-s[index];raw=-(s+peer_noise)[index]
            shrink=raw*(tau/(tau+.0222/n))[np.arange(300),best//5]
            truths.append(true.mean());raws.append(raw.mean());shrunks.append(shrink.mean())
            rawse=np.std(raw-true,ddof=1)/np.sqrt(300)
            shrinkse=np.std(shrink-true,ddof=1)/np.sqrt(300)
            rawcovers.append(abs(raw.mean()-true.mean())<=1.96*rawse)
            shrinkcovers.append(abs(shrink.mean()-true.mean())<=1.96*shrinkse)
        attribution.append({'shared_truth':tau,'replicates':reps,'seasons_per_replicate':300,'finals_per_season':5,
          'mean_true_extreme_log_advantage':float(np.mean(truths)),
          'mean_unshrunk_estimate':float(np.mean(raws)),'unshrunk_bias':float(np.mean(raws)-np.mean(truths)),
          'unshrunk_truth_error_95_coverage':float(np.mean(rawcovers)),
          'mean_shrunk_estimate':float(np.mean(shrunks)),'shrinkage_bias':float(np.mean(shrunks)-np.mean(truths)),
          'shrunk_truth_error_95_coverage':float(np.mean(shrinkcovers)),
          'note':'Intervals use simulated estimation errors against each replicate finite-sample truth. This directly tests attribution recovery; it is not the episode bootstrap. Independent execution errors assumed.'})
        dump('selection-simulation.json',attribution);progress(f'Selection validation saved: shared variance {tau}; unshrunk bias {attribution[-1]["unshrunk_bias"]:.5f}, shrinkage bias {attribution[-1]["shrinkage_bias"]:.5f}.')

if __name__=='__main__':validate()
