# Pre-confirmation validation gate

**FAIL: inconclusive: uncertainty not validated**

No positive confirmation solve time has been read. The gate uses real solver-final incidence and sign-only status masks with synthetic log times.

Each process: 200 independent datasets; 500 exact cluster-bootstrap draws per dataset. Seed 20261001. Ten worker processes; numerical libraries limited to one thread each.

Every draw recomputes training positions/moments, weighted skill references, tier moments with squared-weight noise traces, focal-solver-excluded peer contrasts, fixed-roster seasonal minimum selection and geometric R.

Sampling truth is the process expectation of oracle log R at originally selected extrema. It is integrated using 10,000 independent synthetic datasets/process with disjoint seeds; null truth is exactly zero. Integration SE and the coverage range over its 99.9% Monte Carlo interval are reported. Finite-dataset oracle coverage is retained as an attribution diagnostic. See DEVIATIONS.md for underspecified contract details and the implementation correction.

Measured warm pipeline time: 0.0117 seconds. Planned pigeonhole CPU time: 2.28 hours; ideal ten-core wall time: 13.7 minutes.

| Bootstrap | Process | Bias log R | Coverage | Mean true R | Mean estimated R | Decision |
|---|---|---:|---:|---:|---:|---|
| pigeonhole | null | 0.000058 | 100.0% | 1.00000 | 1.00006 | FAIL |
| pigeonhole | small_shared | -0.000030 | 99.5% | 1.01578 | 1.01575 | FAIL |
| pigeonhole | large_shared | 0.000057 | 1.0% | 1.12190 | 1.12197 | FAIL |
| pigeonhole | shared_plus_tier_interaction | -0.000078 | 99.5% | 1.01269 | 1.01262 | FAIL |
| pigeonhole | informative_dnf | -0.000003 | 98.0% | 1.01595 | 1.01595 | pass |
| pigeonhole | random_replacement_10_percent | 0.000074 | 100.0% | 1.01274 | 1.01281 | FAIL |
| pigeonhole | pure_attempt_slot_shock | 0.000191 | 2.0% | 1.12190 | 1.12212 | reported only: slot shock absorbed |
| competition_only | null | 0.000058 | 95.5% | 1.00000 | 1.00006 | pass |
| competition_only | small_shared | -0.000030 | 55.5% | 1.01578 | 1.01575 | FAIL |
| solver_only | null | 0.000058 | 99.5% | 1.00000 | 1.00006 | FAIL |

Selected method: none.

Acceptance requires absolute log-R bias ≤0.005 and 95% coverage between 92% and 99% in each judged process. A bias failure prevents fallback rescue; coverage fallback order is competition-only then solver-only.

Initial pigeonhole validation completes all seven processes. A fallback is rejected as soon as one full 200-dataset process fails: remaining processes cannot rescue its requirement to pass every process. Acceptance of a fallback still requires all seven complete processes. Partial cancelled fallback datasets remain in the bulk checkpoints but never decide acceptance. See DEVIATIONS.md.

All frozen-code fixture, focal exclusion, missing-pattern and squared-noise-trace checks pass.

Generated raw replicate records and timing/exposure diagnostics: data/derived/gate-*.jsonl. No simulated positive values are confused with confirmation observations.

If this gate fails, confirmation remains unopened and step 4 is not run. A registered and committed amendment would be required to proceed.

### Simulation wording correction — 2026-10-02

Each real solver-final DNF count and DNS locations retained; Gumbel top-k implements sequential weighted sampling without replacement among started slots, with weights exp(12*shared_slot), renormalized over remaining slots at each selection. Multi-DNF subset probabilities are not exact conditional-logistic subset odds. The monotone difficulty stress and empirical gate results are unchanged.
