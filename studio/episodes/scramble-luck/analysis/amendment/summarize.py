#!/usr/bin/env python3
"""Deterministic tables from synthetic replicate records, no outcomes."""
import evaluate as e
import numpy as np
import json, csv, argparse
from scipy.stats import beta

def load(name):return [json.loads(s) for s in (e.HERE/name).read_text().splitlines()]

def binomial(k,n):
    return [float(beta.ppf(.025,k,n-k+1)) if k else 0.,
            float(beta.ppf(.975,k+1,n-k)) if k<n else 1.]

def coverage_range(ci,low,high):
    endpoints=ci.ravel(); inside=endpoints[(endpoints>=low)&(endpoints<=high)]
    knots=np.unique(np.r_[low,inside,high]); grid=np.r_[knots,(knots[:-1]+knots[1:])/2]
    rates=[np.mean((ci[:,0]<=t)&(ci[:,1]>=t)) for t in grid]
    return [float(min(rates)),float(max(rates))]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',default='replicates.jsonl');parser.add_argument('--prefix',default='')
    args=parser.parse_args();prefix=args.prefix
    rows=load(args.input); truths=json.loads((e.HERE.parent/'population-truth.json').read_text())
    truths['boundary']=json.loads((e.HERE/'boundary-truth.json').read_text())
    original=[json.loads(s) for s in (e.DERIVED/'gate-pigeonhole.jsonl').read_text().splitlines()]
    old={(r['case'],r['replicate']):r for r in original}
    comparisons=[]
    for r in rows:
        if (r['case'],r['replicate']) in old:
            o=old[r['case'],r['replicate']]
            comparisons.append(max(abs(r['point']-o['estimated_log_R']),
                float(np.max(np.abs(np.array(r['intervals']['original'])-o['log_R_interval_95'])))))
    if comparisons:assert max(comparisons)<1e-12
    table=[];diagnostic=[]
    for case in e.gate.CASES:
        rr=sorted([r for r in rows if r['case']==case],key=lambda x:x['replicate'])
        assert len(rr)>=200 and len(set(r['replicate'] for r in rr))==len(rr)
        theta=truths[case]['log_R']
        # Boundary gate is evaluated at the exact decision-line target. Also
        # report coverage over independent integration uncertainty separately.
        if case=='boundary':theta=float(np.log(1.1))
        p=np.array([r['point'] for r in rr]);n=len(rr)
        boot=np.array([r['bootstrap_mean'] for r in rr])
        diagnostic.append({'case':case,'point_mean':float(p.mean()),
            'reselected_bootstrap_mean':float(boot[:,0].mean()),'fixed_bootstrap_mean':float(boot[:,1].mean()),
            'reselected_frozen_beta_mean':float(boot[:,2].mean()),
            'reselected_shift':float((boot[:,0]-p).mean()),'fixed_shift':float((boot[:,1]-p).mean()),
            'shift_reselected_sd':float((boot[:,0]-p).std(ddof=1)),
            'distinct_competition_fraction':float(np.mean([r['distinct_competition_fraction'] for r in rr]))})
        for method in ['original','A','B','C','D']:
            ci=np.array([r['intervals'][method] if r['intervals'][method] is not None else [np.nan,np.nan] for r in rr])
            covered=(ci[:,0]<=theta)&(theta<=ci[:,1]); holds=ci[:,0]>np.log(1.1); fails=ci[:,1]<=np.log(1.1)
            coverage=float(covered.mean());bias=float(p.mean()-theta)
            low,high=truths[case]['log_R_MC_999_interval']
            item={'method':method,'case':case,'datasets':n,'bias_log_R':bias,
                'bias_MC_SE':float(p.std(ddof=1)/np.sqrt(n)),'coverage':coverage,
                'coverage_binomial_95':binomial(int(covered.sum()),n),
                'coverage_range_truth_MC_999':coverage_range(ci,low,high),
                'mean_log_width':float(np.nanmean(ci[:,1]-ci[:,0])),
                'mean_R_width':float(np.nanmean(np.exp(ci[:,1])-np.exp(ci[:,0]))),
                'mean_log_endpoints':np.nanmean(ci,axis=0).tolist(),
                'invalid_intervals':int(np.sum(~np.isfinite(ci).all(axis=1))),
                'holds_probability':float(holds.mean()),'fails_probability':float(fails.mean()),
                'boundary_holds_binomial_95':binomial(int(holds.sum()),n) if case=='boundary' else None,
                'boundary_fails_binomial_95':binomial(int(fails.sum()),n) if case=='boundary' else None,
                'boundary_error_range_truth_MC_999':{
                    'holds':[float(np.mean(ci[:,0]>high)),float(np.mean(ci[:,0]>low))],
                    'fails':[float(np.mean(ci[:,1]<=low)),float(np.mean(ci[:,1]<=high))]
                } if case=='boundary' else None,
                'judged':case!='pure_attempt_slot_shock'}
            item['passes_revised_gate']=bool(abs(bias)<=.005 and coverage>=.92 and item['invalid_intervals']==0
                and (case!='boundary' or (holds.mean()<=.025 and fails.mean()<=.025))) if item['judged'] else None
            table.append(item)
    e.save(prefix+'summary.json',{'results':table,'diagnosis':diagnostic,
           'original_gate_max_numeric_difference':max(comparisons) if comparisons else None,
           'procedure_pass':{m:all(r['passes_revised_gate'] for r in table if r['method']==m and r['judged']) for m in ['A','B','C','D']}})
    with (e.HERE/(prefix+'results.csv')).open('w') as f:
        keys=['method','case','datasets','bias_log_R','coverage','mean_log_width','mean_R_width','holds_probability','fails_probability','passes_revised_gate']
        writer=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');writer.writeheader();writer.writerows(table)
    lines=['# Candidate simulation results','',
           '500 draws/dataset; dataset counts are in the machine-readable results; widths use log R and R scales.',
           'Boundary errors are probabilities at R=1.10; elsewhere verdict rates are not false-error rates.','',
           '| Method | Process | Datasets | Bias log R | Coverage | Mean log width | Mean R width | Boundary false holds | Boundary false fails |',
           '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in table:
        boundary=r['case']=='boundary'
        lines.append(f"| {r['method']} | {r['case']} | {r['datasets']} | {r['bias_log_R']:.6f} | {100*r['coverage']:.1f}% | {r['mean_log_width']:.6f} | {r['mean_R_width']:.6f} | "+
          (f"{100*r['holds_probability']:.1f}% | {100*r['fails_probability']:.1f}% |" if boundary else '— | — |'))
    (e.HERE/(prefix+'RESULTS.md')).write_text('\n'.join(lines)+'\n')
    lines=['# Selection diagnosis','',
           'All quantities below are on the log R scale. Bootstrap means are computed within each dataset, then averaged.',
           'The frozen-beta column changes only the nuisance refit within the reselecting draws.','',
           '| Process | Point mean | Reselect mean | Fixed-selection mean | Reselect, frozen beta | Reselect shift | Fixed shift |',
           '|---|---:|---:|---:|---:|---:|---:|']
    for d in diagnostic:
        lines.append(f"| {d['case']} | {d['point_mean']:.8f} | {d['reselected_bootstrap_mean']:.8f} | {d['fixed_bootstrap_mean']:.8f} | {d['reselected_frozen_beta_mean']:.8f} | {d['reselected_shift']:.8f} | {d['fixed_shift']:.8f} |")
    lines+=['','Independent multinomial competition draws retain about 63.2% of distinct competitions.',
            'The large shared-effect downward shift disappears when original extrema are held fixed;',
            'holding only training beta fixed does not remove it. This directly supports the proposed',
            'exposure/reselection mechanism. Point-estimator bias and bootstrap-distribution bias are',
            'different: an unbiased point estimator does not make the percentile interval centered correctly.']
    (e.HERE/(prefix+'DIAGNOSIS.md')).write_text('\n'.join(lines)+'\n')
    stability=e.HERE/'stability.jsonl'
    if stability.exists() and not prefix:
        records=load('stability.jsonl'); output=[]
        for case in sorted(set(r['case'] for r in records)):
            rr=[r for r in records if r['case']==case]
            for method in ['A','B']:
                final=np.array([r['intervals'][method] for r in rr])
                for count in ['250','500','1000']:
                    short=np.array([r['prefix_intervals'][count][method] for r in rr]);delta=np.abs(short-final)
                    output.append({'case':case,'method':method,'datasets':len(rr),'draws':int(count),'reference_draws':2000,
                      'mean_absolute_endpoint_change':float(delta.mean()),'max_absolute_endpoint_change':float(delta.max()),
                      'relative_to_mean_width':float(delta.mean()/np.mean(final[:,1]-final[:,0])),
                      'holds_decision_changes':int(np.sum((short[:,0]>np.log(1.1))!=(final[:,0]>np.log(1.1)))),
                      'fails_decision_changes':int(np.sum((short[:,1]<=np.log(1.1))!=(final[:,1]<=np.log(1.1))))})
        e.save('endpoint-stability.json',output)
    print(json.dumps({'procedure_pass':{m:all(r['passes_revised_gate'] for r in table if r['method']==m and r['judged']) for m in ['A','B','C','D']},
                      'original_gate_max_numeric_difference':max(comparisons) if comparisons else None}))

if __name__=='__main__':main()
