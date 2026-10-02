#!/usr/bin/env python3
"""Write the amendment from completed, auditable simulation summaries."""
import json, hashlib
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent

def read(name):return json.loads((HERE/name).read_text())
def pct(x):return f'{100*x:.1f}%'
def bounds(x):return '–'.join(pct(v) for v in x)

def main():
    initial=read('summary.json'); fresh=read('replication-summary.json')
    assert initial['procedure_pass']['B'] and fresh['procedure_pass']['B']
    rows=initial['results']; rr=fresh['results']
    selected=[r for r in rows if r['method']=='B' and r['judged']]
    validated=[r for r in rr if r['method']=='B' and r['judged']]
    b=next(r for r in selected if r['case']=='boundary')
    vb=next(r for r in validated if r['case']=='boundary')
    diag={d['case']:d for d in initial['diagnosis']}
    big=diag['large_shared'];small=diag['small_shared']
    calibration=read('boundary-calibration.json');truth=read('boundary-truth.json')
    stable=read('endpoint-stability.json')
    stable500=[r for r in stable if r['method']=='B' and r['draws']==500]
    max_change=max(r['max_absolute_endpoint_change'] for r in stable500)
    mean_change=np.mean([r['mean_absolute_endpoint_change'] for r in stable500])
    stability_changes=sum(r['holds_decision_changes']+r['fails_decision_changes'] for r in stable500)
    followup=read('followup-timing.json')
    seconds=truth['seconds']+read('replicates-timing.json')['wall_seconds']+sum(r['wall_seconds'] for r in followup)+read('benchmark.json')['total_seconds']
    summary_table=[]
    for method in ['A','B','C','D']:
        s=[r for r in rows if r['method']==method and r['judged']]
        v=[r for r in rr if r['method']==method and r['judged']]
        sb=next(r for r in s if r['case']=='boundary');sv=next(r for r in v if r['case']=='boundary')
        summary_table.append(f"| {method} | {bounds([min(r['coverage'] for r in s),max(r['coverage'] for r in s)])} | {pct(sb['holds_probability'])} / {pct(sb['fails_probability'])} | {bounds([min(r['coverage'] for r in v),max(r['coverage'] for r in v)])} | {pct(sv['holds_probability'])} / {pct(sv['fails_probability'])} | {'pass' if fresh['procedure_pass'][method] else 'FAIL'} |")
    coverage=bounds([min(r['coverage'] for r in selected),max(r['coverage'] for r in selected)])
    vcoverage=bounds([min(r['coverage'] for r in validated),max(r['coverage'] for r in validated)])
    doc=f'''# AMENDMENT-1 — recentered log-R uncertainty

**Draft for registration, 2026-10-02. Recommendation: B, the reselecting
pigeonhole percentile interval translated to the original log-R point estimate.**
It passes the revised empirical gate in both the paired comparison and the
independent replication below. This draft does not change the committed METHOD
or authorize opening confirmation outcomes. Register and commit an accepted
amendment and its evidence before any confirmation verdict analysis.

## Timing and disclosure

This was written **after the registered gate failed** and after its simulation
results were inspected. Candidate choice and removal of the over-coverage
ceiling are post-failure methodological changes, not original preregistration.
No confirmation solve-time magnitude was read during this consultation.
The inputs were METHOD, the failed gate and deviations/design/code, synthetic
gate records, frozen pilot parameters already used by that code, and the
time-free incidence/status table in `data/derived/structure.duckdb`.
Training success values are categorical placeholders (1), not observed times.
Neither the raw export nor outcome/training-value parquets were opened.
The originally exposed pilot and earlier design changes remain disclosed in
METHOD; this amendment does not erase them. All new work is in this directory.

The first comparison reuses the original 200 synthetic datasets/process, so it
is a paired development comparison. Before inspecting candidate results, the
evaluation plan added a disjoint replication: 200 new datasets in each original
process and 1,000 at the boundary. All candidates and thresholds were unchanged
for that replication. No confirmation result motivated candidate selection.
Amendment-developed methods remain exploratory until registered; a later
confirmation analysis using the accepted amended specification is explicitly
confirmatory under that amended, rather than original, contract.

## Diagnosis

Confirmed. In 200 large-shared datasets, mean point log R is
{big['point_mean']:.8f}; mean reselecting-bootstrap log R is
{big['reselected_bootstrap_mean']:.8f} (shift {big['reselected_shift']:.8f}).
Holding original best solves fixed and recomputing resampled peer contrasts
gives {big['fixed_bootstrap_mean']:.8f} (shift {big['fixed_shift']:.8f}).
Holding only training beta fixed gives {big['reselected_frozen_beta_mean']:.8f},
so training-position refitting does not explain the large displacement.
For small-shared, the shift falls from {small['reselected_shift']:.8f} to
{small['fixed_shift']:.8f} when selection is fixed. Draws retain
{100*big['distinct_competition_fraction']:.2f}% of distinct competitions.
Fewer distinct opportunities produce less extreme seasonal minima and less
favourable selected shared effects. The percentile distribution's location is
therefore wrong despite negligible point-estimator bias. Recentring repairs
that location; validation still has to check its width and tail behaviour.
See [DIAGNOSIS.md](DIAGNOSIS.md) and dataset-level `replicates.jsonl`.

## Exact proposed changes to METHOD

1. In **Uncertainty and pass/fail rule**, replace the log-R percentile instruction
   with the following. Keep the registered product-weight draws, competition →
   solver → training draw order, full focal exclusion, nuisance refits, original
   eligibility roster, within-draw seasonal reselection, seed 20261001 and 2,000
   draws for the eventual confirmation analysis. Let theta-hat be the original
   mean(−h) and theta-star_b the valid reselecting bootstrap values. Set

   `m_star = mean(theta_star_b)`

   `CI_logR = theta_hat + quantile(theta_star_b - m_star, [0.025, 0.975])`.

   Exponentiate both endpoints. Center by the **bootstrap mean**, not the median
   or interval midpoint. Use NumPy's linear quantile interpolation. Report the
   original bootstrap mean, its displacement from theta-hat, raw percentile
   endpoints, centered endpoints, valid draws and exposure diagnostics.
   If fewer than 1,900 of 2,000 draws are valid, the measurement is inconclusive.
   No clipping and no point-estimate bias correction are introduced.

2. Replace only the R uncertainty-validation gate and its failed fallback
   sequence by the revised gate below. The failed competition-only and
   solver-only fallbacks remain historical results, not an automatic new route
   to a verdict. If the amended method fails, keep confirmation unopened for
   a verdict pending another registered amendment.

3. Add the calibrated boundary process and the two separate boundary error
   checks. Keep the original seven processes, frozen successful-solve estimand,
   all-peer unshrunk point estimate, 1.10 decision line, equal-person-year
   weighting, and original scope/coverage checks. F and gamma/D continue to
   use their original percentile intervals. This exercise validates R only;
   it does not assert new coverage guarantees for other endpoints.

The amendment does not change the verdict inequalities: holds only if L>1.10;
fails if U≤1.10; otherwise inconclusive. It does not redefine the oracle target
as a conditional fixed-extrema quantity. The target remains the expectation of
the original selected-extrema oracle log R under the process, exponentiated.

## Candidates and rationale

A fixes the originally selected row and slot. Zero-weight selected competitions
drop their original extrema; no runner-up is selected. Available original
extrema receive competition × solver multiplicity, and peer contrasts and
training beta are recomputed. This removes the location problem but changes
the way seasonal selection enters resampling.

B preserves the registered full R resampling calculation and translates its
distribution back to the original estimate. This is the smallest change that
directly repairs the demonstrated defect while retaining resampled peer and
training uncertainty. It remains conservative; it is not claimed to provide
exact 95% coverage under every possible process.

C uses original selected x_i=−h_i, e_i=x_i−mean(x), n extrema, and
V_g = [G_g/(G_g−1)] sum_clusters(sum_i e_i)^2/n² for solver, competition and
solver×competition intersection. Set V_CGM=V_solver+V_competition−V_intersection
and use mean(x) ± 1.95996398454 sqrt(V_CGM), then exponentiate. Frozen beta is
treated as fixed; peers are not resampled. Nonpositive variance is invalid,
not clipped. This is the intercept-only
[Cameron–Gelbach–Miller sandwich](https://cameron.econ.ucdavis.edu/research/JBESpaper2009version.pdf).
Selection and shared-peer generated contrasts require the empirical checks;
the generic cluster formula alone does not guarantee validity here.

D uses the same normal interval with V_solver+V_competition. Omitting the
nonnegative overlap subtraction makes it a conservative scalar variance
alternative to C, at a cost in width. It is explicitly not labelled exact CGM.
Neither analytic candidate changes the point estimate. Full widths and all
process-specific biases/coverages are reported, including failed candidates.

## Boundary process and numerical truth

The boundary process is the original Gaussian shared-effect generator with
gamma=0 and tau defined by the equation E[oracle log R(tau)]=log(1.10), an
**exact boundary target**. Numerical calibration on 10,000 separate datasets
(seed indices 200000–209999) gives tau={calibration['tau']:.12g}; its calibration
mean is within {abs(calibration['history'][-1]['mean']-np.log(1.1)):.2g} of log(1.10).
Independent integration on seeds 300000–309999 gives R={truth['R']:.8f},
log-R Monte Carlo SE {truth['log_R_MC_standard_error']:.8f}, and a 99.9% numerical
precision interval for R of [{np.exp(truth['log_R_MC_999_interval'][0]):.8f},
{np.exp(truth['log_R_MC_999_interval'][1]):.8f}].

Thus the target is exactly 1.10, but the implemented parameter is numerically
calibrated, not an algebraic proof that its population expectation is exactly
1.10. Do not describe the independent estimate as exact truth. Gate rates use
the target log(1.10); `summary.json` and `replication-summary.json` also report
coverage and boundary-rate sensitivity over the independent truth interval.
All calibration, integration, paired-evaluation and replication seed streams
are disjoint. Existing processes retain their original integrated truths.

## Revised gate

- At least 200 independent datasets per process and at least 500 bootstrap
  draws per dataset. Retain the null, small shared, large shared, tier interaction,
  informative DNF and random replacement judged processes; add the boundary.
  Pure slot shock remains reported, not judged.
- Keep absolute bias of log R ≤0.005 in every judged process.
- Require coverage ≥92% in every judged process. **Coverage above 99% no
  longer automatically fails.** It reduces precision and the probability of a
  decisive result; it is not, by itself, evidence of excess false verdicts.
  Report it prominently with mean widths and verdict rates. The original
  over-coverage remains a failure of the original gate, not retroactively a pass.
  The fixed, finite candidate formulas and width disclosures prevent replacing
  uncertainty analysis with an arbitrary uninformative interval.
- At the boundary require each empirical error separately: P(L>1.10)≤2.5%
  and P(U≤1.10)≤2.5%. No trading one tail against the other. Report exact binomial
  95% intervals and numerical-truth sensitivity. A Monte Carlo pass is evidence
  under the specified processes, not proof of universal population guarantees.
- Count an unavailable/nonfinite interval as noncoverage; disclose it. Require
  all point/rank/valid-draw checks and input provenance checks to pass.

## Simulation results

The paired sweep uses 200 datasets in each of eight processes. Independent
replication uses 200 per original process and 1,000 at the boundary, all with
500 draws. The table's coverage ranges exclude the unjudged slot shock; the
full tables include it. Boundary entries are false holds / false fails.

| Candidate | Paired coverage | Paired boundary | Independent coverage | Independent boundary | Independent gate |
|---|---:|---:|---:|---:|---|
{chr(10).join(summary_table)}

**B passes both revised empirical gates.** Paired coverage is {coverage};
boundary errors are {pct(b['holds_probability'])} false holds and
{pct(b['fails_probability'])} false fails. Independent coverage is {vcoverage};
boundary errors are {pct(vb['holds_probability'])} and {pct(vb['fails_probability'])}
(n={vb['datasets']}). Their exact binomial 95% intervals are
[{bounds(vb['boundary_holds_binomial_95'])}] and
[{bounds(vb['boundary_fails_binomial_95'])}], respectively.
Maximum absolute independent log-R bias across judged processes is
{max(abs(r['bias_log_R']) for r in validated):.8f}.

Every candidate/process bias, coverage, mean log width, mean R width and boundary
error is in [RESULTS.md](RESULTS.md) and [replication-RESULTS.md](replication-RESULTS.md),
with CSV and JSON versions. All raw synthetic dataset records are retained.
No intervals were discarded or seeds selected based on coverage.

## Verification, endpoint stability and compute

The fast R path uses the existing engine's generator, contributions, weighted
accumulation, training moments, peer projection and seasonal selection. It
omits only unrelated F/tier/reference work. Across all eight process fixtures,
its point, oracle and bootstrap values match the full engine to machine
precision. All 1,400 original 500-draw gate intervals and points also reproduce
with maximum difference {initial['original_gate_max_numeric_difference']:.2g}.
CGM cluster sums were independently recomputed, including the intersection.

For the first 20 large-shared and 20 boundary datasets, nested 500/1000/2000
draw checks give B's mean absolute endpoint change from 500 to 2000 draws
{mean_change:.6f} log units, maximum {max_change:.6f}; there are
{stability_changes} boundary-rule classification changes across these 40 checks.
See `endpoint-stability.json` for both A/B, each process and each draw count.
The main runs retain the registered 500-draw validation minimum; production
still uses 2,000 draws. Stability checks are diagnostic, not selected reruns
used to replace inconvenient primary intervals.

Benchmarking preceded the sweep. Calibration/integration, the complete candidate
sweep, stability checks and independent replication took {seconds/60:.1f} minutes
of measured wall time in total (ten workers, one BLAS thread each), below the
approximately 75-minute compute budget. Minor verification/reporting time is
additional. `compute-budget.json`, per-run timing files, code/input hashes,
`verification.json`, and the scripts provide reproducibility and provenance.

METHOD.md, the original gate reports/code and derived gate records remain
unchanged. This is an amendment draft and simulation evidence only.
'''
    (HERE/'AMENDMENT-1.md').write_text(doc)
    budget={'measured_compute_wall_seconds':seconds,'measured_compute_wall_minutes':seconds/60,
            'wall_budget_minutes':75,'workers':10,'numerical_threads_per_worker':1,
            'components':{'calibration_and_independent_truth':truth['seconds'],
                'paired_sweep':read('replicates-timing.json')['wall_seconds'],
                'benchmark':read('benchmark.json')['total_seconds'],'followup_jobs':followup},
            'note':'Wall time, not aggregate core-minutes; minor verification/reporting excluded.'}
    (HERE/'compute-budget.json').write_text(json.dumps(budget,indent=2)+'\n')
    provenance=read('verification.json')['input_sha256']
    for name,expected in provenance.items():
        path=HERE.parent.parent/name
        assert hashlib.file_digest(path.open('rb'),'sha256').hexdigest()==expected, name
    files=[p for p in HERE.iterdir() if p.is_file() and p.name!='artifact-hashes.json']
    hashes={p.name:hashlib.file_digest(p.open('rb'),'sha256').hexdigest() for p in sorted(files)}
    (HERE/'artifact-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
    print(json.dumps({'recommended':'B','paired_coverage':coverage,'independent_coverage':vcoverage,
        'boundary_false_holds':vb['holds_probability'],'boundary_false_fails':vb['fails_probability'],
        'compute_minutes':seconds/60,'inputs_unchanged':True}))

if __name__=='__main__':main()
