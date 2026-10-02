# AMENDMENT-1 — recentered log-R uncertainty

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
0.11508463; mean reselecting-bootstrap log R is
0.10530041 (shift -0.00978421).
Holding original best solves fixed and recomputing resampled peer contrasts
gives 0.11507048 (shift -0.00001415).
Holding only training beta fixed gives 0.10530329,
so training-position refitting does not explain the large displacement.
For small-shared, the shift falls from -0.00125117 to
-0.00000780 when selection is fixed. Draws retain
63.24% of distinct competitions.
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
(seed indices 200000–209999) gives tau=0.00971440821107; its calibration
mean is within 1e-09 of log(1.10).
Independent integration on seeds 300000–309999 gives R=1.10004144,
log-R Monte Carlo SE 0.00001778, and a 99.9% numerical
precision interval for R of [1.09997707,
1.10010581].

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
| A | 99.5%–100.0% | 0.5% / 0.0% | 99.9%–100.0% | 0.1% / 0.0% | pass |
| B | 97.0%–100.0% | 2.0% / 1.0% | 96.0%–100.0% | 0.6% / 0.9% | pass |
| C | 93.5%–96.0% | 3.0% / 2.5% | 93.5%–96.5% | 1.5% / 2.5% | pass |
| D | 97.5%–99.5% | 1.5% / 1.0% | 96.5%–100.0% | 0.4% / 0.9% | pass |

**B passes both revised empirical gates.** Paired coverage is 97.0%–100.0%;
boundary errors are 2.0% false holds and
1.0% false fails. Independent coverage is 96.0%–100.0%;
boundary errors are 0.6% and 0.9%
(n=1000). Their exact binomial 95% intervals are
[0.2%–1.3%] and
[0.4%–1.7%], respectively.
Maximum absolute independent log-R bias across judged processes is
0.00013498.

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
with maximum difference 0.
CGM cluster sums were independently recomputed, including the intersection.

For the first 20 large-shared and 20 boundary datasets, nested 500/1000/2000
draw checks give B's mean absolute endpoint change from 500 to 2000 draws
0.000194 log units, maximum 0.000726; there are
0 boundary-rule classification changes across these 40 checks.
See `endpoint-stability.json` for both A/B, each process and each draw count.
The main runs retain the registered 500-draw validation minimum; production
still uses 2,000 draws. Stability checks are diagnostic, not selected reruns
used to replace inconvenient primary intervals.

Benchmarking preceded the sweep. Calibration/integration, the complete candidate
sweep, stability checks and independent replication took 15.0 minutes
of measured wall time in total (ten workers, one BLAS thread each), below the
approximately 75-minute compute budget. Minor verification/reporting time is
additional. `compute-budget.json`, per-run timing files, code/input hashes,
`verification.json`, and the scripts provide reproducibility and provenance.

METHOD.md, the original gate reports/code and derived gate records remain
unchanged. This is an amendment draft and simulation evidence only.
