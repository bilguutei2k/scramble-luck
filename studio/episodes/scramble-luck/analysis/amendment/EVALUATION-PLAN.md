# Post-failure evaluation plan

Written 2026-10-02, after reading the failed gate and before the candidate sweep.
No confirmation solve-time magnitude is read. This is an amendment investigation,
not an original preregistration. METHOD and the original gate remain unchanged.

Evaluate 200 datasets per original process and a boundary process. Reuse original
replicates 0–199 for paired comparisons, explicitly not fresh validation of a
procedure selected after the failed gate. Use 500 bootstrap draws, plus paired
500/1000/2000 endpoint checks on 20 datasets each of large_shared and boundary.
Use ten workers with BLAS thread counts one; benchmark before the main sweep.

Candidate definitions fixed before the sweep:

- A: hold original identified season-best row/slot fixed. Independently resample
  competitions and solvers, recompute peer projection, exclude the full focal
  solver multiplicity, refit training positions. Aggregate retained original
  extrema with competition × solver product multiplicity. No runner-up.
- B: original reselecting bootstrap, translate every draw by point estimate
  minus its bootstrap mean; take 2.5% and 97.5% quantiles on log R.
- C: intercept-only two-way CGM sandwich of original selected −h values;
  solver and selected-competition meats minus their intersection meat, each
  multiplied by G/(G−1). Divide squared cluster-score sums by n². Normal 95%
  log interval. Nonpositive variance is invalid, not clipped. Frozen beta.
- D: same analytic interval but use solver + competition meats without overlap
  subtraction. Conservative scalar alternative, not claimed to be exact CGM.
  It double-counts the intersection and therefore loses precision; it is
  included as an explicit variance upper bound relative to C, not a tuned factor.

All retain the point estimator and oracle expectation target. The original
bootstrap is also retained as a diagnostic. The R-only fast path must match
the full engine; unrelated F, tier fitting and skill-reference calculations
cannot affect all-peer R and are omitted only from these simulations.

Boundary uses the identical generator with shared variance tau solving
E[oracle log R(tau)] = log(1.10). Numerical calibration uses separate seeds,
followed by 10,000 independent integration draws; report numerical uncertainty,
not a claim that floating-point calibration proves an expectation exactly.

Report bias, coverage, mean log/R width, bootstrap mean shifts, and each boundary
false-verdict probability. Retain bias ≤0.005, require coverage ≥92% in judged
processes, and each empirical boundary error ≤2.5%. Slot shock remains reported.
Propose dropping the 99% ceiling: excess coverage costs decision power, while
one-sided boundary error directly measures invalid verdicts. Do not conceal
overcoverage; widths and rates must accompany the revised gate. A finite Monte
Carlo pass is not proof of population error control; report binomial intervals.
Recommend a passing candidate using correctness, simplicity and efficiency;
do not tune a variance multiplier or select individual seeds to force a pass.

Budget extension recorded while the first sweep was running, before reading its
candidate results: reserve an independent replication at seeds 1000–1199 in
each process, plus boundary seeds 1200–1999 (1,000 independent boundary datasets
total). Apply the same candidate definitions and thresholds; do not tune them
on these results. Report this replication separately from the original paired
200-dataset sweep. The observed throughput projects the complete work, including
this replication and stability checks, below the requested 75-minute wall budget.
