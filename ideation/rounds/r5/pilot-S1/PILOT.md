# S1 measurement-validation pilot — REVISE

Exploration only, locked before the new analysis. The shared scheduled-position component is **3.81% of within-solver-round successful log-time variance** (competition+solver bootstrap 95%: **2.94%–4.70%**). It is detectable but small. The aggregate unshrunk seasonal-extreme correction is **1.0163×** (95% **1.0049–1.0225**, n=180 exploratory solver-seasons). This does not support a 10% average shared boost. It does not establish that the remaining variation is personal luck.

**Recommendation: revise.** An episode about the difference between common scramble opportunity and an individual's spectacular solve survives. A record-attribution episode with verified actual scramble links does not yet have the required data. Method labels and replacement assignments are absent. Do not open the 80% until a reviewed, committed METHOD.md freezes the revised estimand and mapping policy.

## Slice, sources and scope

Same exact rule as `rounds/r3/pilot-S1/SLICE.md`: UTF-8 competition ID SHA-256 integer modulo 5 equals zero, all years. 3,756/18,771 IDs. ID-list SHA-256: `b5f6426bffbbf01c4d742cbe65f083cb4cbb5a134a5b60c3fe9fa312d028b7a4`. `SLICE.md` was written first. Independently checked all eight frozen source hashes against the round-3 manifest, including the immutable 2026-09-30 ZIP. The manifest, extraction rule, row counts and executable are included. No confirmatory outcome query or outcome table was created; confirmation counts use only identifiers, dates, formats, group counts and attempt presence. All outcome SQL reads only the exploration parquet, whose membership is asserted again before analysis.

The exact final slice contains 1,996 scheduled-mapped finals, 23,907 solver-rounds, 119,535 attempt slots, 117,779 valid times, 1,723 DNF and 33 DNS, 9,139 solvers. Real structural panels range 4–48 finalists; median 12. 23,900 solver-rounds have at least two valid times. One/all-successless solver-rounds provide no time contrast but remain in failure analysis. This recovers 7,314 valid attempts absent from the previous min-six complete-panel analysis, through DNF retention and removal of the min-six gate.

Source attribution: WCA owns and maintains the results, [WCA results export](https://www.worldcubeassociation.org/export/results), export date 2026-09-30 00:00:36 UTC. Dated bundled README terms and hashes are in the raw manifest. Published work must carry the bundled notice.

## 1. Simulation first: known truth at the real panel sizes

Before any new real-outcome computation, simulated all 1,996 finals / 23,907 solver-rounds at the structural sizes. Each scenario has 400 independent simulations (seed 20261001). Generated log-times with known round-position common variance, independent residual variance 0.0222, and, where specified, an observable faster/slower-tier × scramble interaction variance 0.0025. Solver-round intercepts cancel through centering. Coverage is of a competition-sandwich 95% interval, not a posterior interval; at 95% coverage its Monte Carlo SE is about 1.1 percentage points. Boundary scenarios use signed variance estimates to avoid artificial clipping coverage.

| Synthetic truth | Common variance | Common-only estimator bias | 95% coverage | Split-peer correlation |
|---|---:|---:|---:|---:|
| null | 0.000000 | -0.000004 | 92.8% | -0.001 |
| small_shared | 0.000900 | -0.000001 | 95.2% | 0.183 |
| large_shared | 0.004000 | +0.000004 | 95.0% | 0.497 |
| shared_and_tier | 0.000900 | -0.000208 | 1.8% | 0.125 |
| tier_only | 0.000000 | -0.000208 | 0.0% | -0.059 |
| MCAR_DNF | 0.000900 | -0.000004 | 94.2% | 0.178 |
| informative_DNF | 0.000900 | -0.000014 | 93.2% | 0.177 |

The small-common truth implies split-peer r≈0.18, close to the prior 0.181 observation. A much larger common component implies r≈0.50. At a typical 12-person panel, the analytic value is tau / sqrt((tau+e/6)(tau+e/6)); the full simulation uses each actual panel size. Therefore low split-peer correlation alone does not show that luck is personal. The original balanced estimator also recovers independent-noise common truth; small panels do not explain away the aggregate signal.

The common-only estimator is **wrong when a strong structured interaction exists**: in the shared+tier truth it underestimates common variance by about 23%, with only 1.8% interval coverage. Tier-specific peer covariance fixes this under the generated model:

| Tier-aware estimator | Shared bias | Interaction bias | Shared coverage | Interaction coverage |
|---|---:|---:|---:|---:|
| shared_and_tier | -0.000003 | -0.000007 | 96.0% | 95.0% |
| tier_only | -0.000000 | +0.000003 | 93.5% | 96.8% |
| no_tier | -0.000003 | -0.000001 | 96.0% | 92.5% |

These simulations identify a structured interaction because tier labels are observed. Independent unobserved solver-by-scramble opportunities are observationally indistinguishable from execution residuals here; no estimator can partition those without extra measurements. MCAR DNF at 1.5% preserves recovery. One prespecified informative-DNF stress model causes about 1.6% relative downward common-variance bias. That is a narrow sensitivity check, not a proof against every missingness process.

**Selection revealed an additional design flaw.** In 400 simulations of 300 solver-seasons × five finals, with real panel sizes sampled and minima reselected, the small-common truth gives mean true shared extreme advantage 0.01020 log units. Unshrunk leave-one-out peers recover 0.01009 (bias -0.00011; finite-sample truth-error 95% coverage 95.0%). Shrinkage gives only 0.00304, with zero truth-error interval coverage in this setup. At the larger common truth, unshrunk coverage is 95.5%. Shrinkage is useful for displaying individual effects, but peer-only posterior means shrink away part of an aggregate effect selected using the focal solve. The frozen primary aggregate now uses unshrunk contrasts; do not recycle the old shrunk headline.

## 2. DNF-retaining common component and reliability versus peers

Model: log successful time = solver-round intercept + pooled attempt position + common round-position contrast + residual. The intercept absorbs finalist ability and round-wide conditions. This is a **within-solver-round** variance decomposition; it does not measure all population variation. Common position effects can also contain synchronized round conditions. Scramble causation is not separately identified.

For each solver's observed successful slots use C = diag(valid) − valid validᵀ/m. With A=sum C, V=sum C(y−position), S=sum ||C(y−position)||² and d=sum(m−1), E(S)=d(tau+e), E(||V||²)=tau tr(A²)+e d. These equations subtract finite-peer noise without requiring five successes. Fit pooled positions; resample competitions and solver IDs with corrected squared-weight noise traces. Main intervals use 1,000 crossed-bootstrap draws; no confidence intervals are obtained by clipping negative moments.

Result: common variance 0.000881; residual 0.022231; common log-SD 2.97% (crossed 95% 2.60%–3.31%). Shared fraction 3.81%. Sensitivities: complete_case: 3.90%; log_contrast_clip_0.6: 3.89%. The old removal of whole DNF panels did not drive the headline, but it was unnecessary and biased the study population.

Era replication (competition intervals, conditional on each period's solvers): pre2019: 3.49% (2.76%–4.17%); 2019–2022: 4.37% (3.56%–5.26%); 2023–2025: 3.69% (3.14%–4.27%); 2026: 3.88% (2.52%–5.29%). Leave-one-year-out across the modern slice gives shared fractions 3.75%–4.02%. In 200 independent-per-solver within-round label permutations, the null common-variance interval is -0.000061 to +0.000055; empirical upper-tail p=0.0050. Alignment matters, but this is a signal-negative-control and does not distinguish scrambles from other synchronized conditions. Exploratory seasonal unshrunk adjustments by era: 2019–2022: 1.0225× (n=41); 2023–2025: 1.0145× (n=139).

Predictive model hyperparameters and position effects were **frozen using pre-2019 exploration finals**, then applied to 2019–2025 exploration finals. For each k, randomly choose entire peer solvers; estimate their common contrast; predict the held-out solver's same-scramble time relative to its other valid solves. The target solve is excluded from its baseline. Predictions are of log-time contrasts conditional on those other attempts, not an unconditional forecast of raw seconds or intrinsic ability. Thirty random splits are averaged before competition resampling at the headline k values.

| Peers k | Eligible finals | Correlation with remaining-peer estimate | Held-out individual R² | Competition 95% R² |
|---:|---:|---:|---:|---:|
| 2 | 1,248 | 0.133 | 0.28% | 0.22%–0.34% |
| 5 | 1,201 | 0.179 | 0.65% | 0.51%–0.79% |
| 10 | 809 | 0.173 | 1.11% | 0.84%–1.38% |
| 20 | 16 | 0.203 | 1.46% | 0.55%–2.06% |

The full curve covers k=2..39 (requires ≥2 held-out peers). Only 16 modern finals support k=20; the maximum-k endpoint has very few panels. The fixed-large-panel curve uses the same 61 finals with ≥20 informative peers for k=2..18, avoiding changing-population comparisons. Random-split ranges in JSON are Monte Carlo variability, **not** sampling confidence intervals; separate competition intervals are given above. Those predictive intervals condition on frozen training parameters and do not fully capture repeated solvers.

Extrapolation under the training model: latent common-effect reliability R(k)=tau/(tau+e/k). About **28 peers** yield 50% reliability and **111 peers** yield 80%. At 50 / 100 / 200 peers the model predicts 64.35%, 78.31%, 87.84%. These are extrapolations, not observed large-panel evidence. Even perfectly measuring the common effect would explain only 3.49% of individual contrast variation under this training model. Large panels solve the measurement problem, not the small-signal problem. Assignment error and unseen interactions could alter this ceiling.

## 3. Is the luck personal? What is and is not testable

Method is absent from the export. No Roux/CFOP/orientation claim is tested or inferred from skill. For skill, use each solver's median log mean in at least two **other** exploration finals within ±2 years; split each eligible panel into faster/slower halves. Both halves need ≥3 informative peers. This yields 1,260 finals / 11,545 solver-rounds. References may use future exploration appearances and the focal round is excluded; this is labelled exploratory.

Allow separate independent residual variances in each tier. Estimate the two within-tier shared variances and cross-tier covariance, then interaction variance = (b_fast+b_slow−2cov)/4. Raw interaction moment -0.000036; competition+solver 95% interval **-0.000348 to +0.000301**. The admissible point estimate is zero; the negative raw moment and raw correlation >1 are sampling diagnostics, not physical variance or a claim of super-perfect agreement. Repeated-solver uncertainty is materially wider than competition-only uncertainty. The crossed upper interaction log-SD is about **1.73%** (twice that for the fast-minus-slow contrast). There is no detected tier interaction, but meaningful tier differences and method-specific opportunities are not ruled out. In particular, this does **not** establish personal luck.

The 180 broad-cohort seasonal minima are on average 0.232 log units faster than their own successful-round mean. The unshrunk peer component explains 0.0162 log units, about 6.99% of that observed extreme deviation. The remainder is unexplained by this peer model: execution, solver-specific opportunities, penalties, model error, missingness and replacement/misscramble error can all contribute. This descriptive decomposition holds the observed within-round baseline fixed; it is not a causal allocation of skill and luck.

## 4. Honest episode numbers, original pass rule and power

- Shared component: **3.81%**, 95% **2.94%–4.70%**, n=117,779 valid solves in 1,996 finals.
- Aggregate broad-cohort median-shared-effect correction: **1.0163×**, 95% **1.0049–1.0225**, n=180 solver-season minima, 133 solvers. At the point estimate this is **1.63%** more time on the median shared contrast. Shrunk individual-display average: 1.0049×, conditional refit/reselection CI 1.0015–1.0069.
- Ten peers predict **1.11%** of a held-out solver's log-time contrast variation, competition 95% **0.84%–1.38%**, n=809 modern finals.

**Original verified prereg rule: untestable on slice.** The official-2018 top100 roster is not supplied; reconstructing it from the 80% would violate the pilot boundary. Actual replacement assignments are unverified. The slice-only top100 proxy has 14 extremes, below the 100-extreme gate, and is not the official cohort. The broader exploratory cohort has 180 extrema and meets simple count gates, but cannot replace the official cohort silently. Its shrunk and unshrunk adjustments both fail the >1.10 point-estimate rule, and the unshrunk interval is wholly below 1.10; this is a surrogate exploratory result, not a preregistered rejection. Strong statistical evidence of a small common component is compatible with failing a materially-large-effect rule.

Original official-cohort power is not identifiable here: ranking and verified assignment coverage are absent. The structural 2019–2025 holdout has 5,017 scheduled-mapped finals, 306,155 attempt rows and 3,313 broadly eligible solver-seasons. Conditional normal approximations using the unshrunk pilot SE and 4x competition precision give a confirmatory log-SE of 0.0022: essentially zero chance to exceed 1.10 at the pilot effect, 50% power exactly at 1.10, and >99.9% at 1.12. These are sensitivity calculations, not promised power: cohort exposure, dependence, replacement audit and selection change. Structural season eligibility grows about 18x, not 4x.

The 1.10 rule imposes a point-estimate threshold as well as significance. At a true ratio exactly 1.10, nominal pass probability tends to 50%, however precise the data are. For a future equivalence claim such as “shared advantage is under 10%,” preregister the upper-confidence-bound criterion separately; do not reinterpret a failed large-effect test as equivalence without that rule.

## 5. DNF and replacement handling

Started-attempt DNF rate **1.44%**. Binary DNF shared covariance 0.000022, competition interval -0.000014 to +0.000062. Peer time difficulty versus target DNF slope -0.0032 risk/log-unit, CI -0.0533 to +0.0427: no detected association. This is a binary companion, **not** a fitted joint latent-time likelihood. The estimand is successful-time variation plus separately reported failure; latent completion times for DNF are not observed. Simulation and complete-case sensitivity are limited probes of informative missingness.

**Extra scrambles cannot be resolved from these tables.** 1,992/1,996 exploration finals have extra pools. A pool is not a usage log. [WCA Regulation 11e1](https://www.worldcubeassociation.org/regulations/#11e1) specifies that extra attempts use a different scramble, so a replacement may invalidate the scheduled attempt-number link. Only four exploration finals and eight confirmation finals lack an extra pool, all before 2019; absence of a pool is itself not proof that no replacement occurred. Strictly excluding every extra-pool final leaves zero 2019–2025 finals, so it kills the original record study rather than repairing it.

Under an **assumed independent random replacement** rate of 5%, 10%, 20%, common covariance attenuates approximately (1−p)². Corrected shared fractions would be 4.23%, 4.71%, 5.96%. This is a model sensitivity, **not a worst-case bound**; targeted replacement can bias either way. Fix: independently audit actual solver-attempt assignments and replacement use for the confirmatory measurement sample and extrema, or explicitly rename the estimand “shared scheduled-position variation” and abandon exact-record scramble causation. No individual historical record is attributed here. The provided export cannot supply the red-team's verified-assignment study by itself.

## 6. Candidate claims — all exploratory

1. **“Ten other finalists explain little of your speed on the same scramble.”** With the pre-2019 peer model frozen, ten peers explain about 1.11% of held-out log-time contrast variation; a small common signal persists.
2. **“A small shared advantage survives the fairer test, but the 10% story does not.”** The broad seasonal-extreme correction is 1.0163×, while roughly 96.19% of within-solver variance remains unexplained by common effects. This concerns scheduled finals and successful attempts, not all scramble luck or world records.
3. **“The statistical correction can hide the effect it is trying to measure.”** Peer-only shrinkage reduces the exploratory aggregate seasonal adjustment from 1.63% to 0.49%. Known-truth simulation shows why selecting extremes makes that attenuation systematic. Use unshrunk aggregation, shrink individual displays, and show their different purposes.

## 7. Every exposed design issue and frozen fixes

1. Use within-solver-round log-time variation as the denominator; do not label between-finalist variation or total population variation as scramble luck.
2. Retain every successful cell of DNF/DNS panels using exact missing-pattern trace corrections. Analyze DNF as a separate binary component; do not impute a DNF time or claim joint latent-time identification.
3. Validate finite-peer correction in simulation and show reliability and out-of-sample predictive R² separately. Freeze pre-2019 hyperparameters before 2019–2025 prediction.
4. For aggregate selected-extreme attribution use unshrunk leave-one-solver-out peer estimates. Retain shrinkage only for individual displays; label its conditional uncertainty and selection bias.
5. Measure skill-tier interactions using skill estimates from other finals; allow tier-specific residual variance and use competition+solver uncertainty. Method interaction remains untestable without method labels.
6. Treat attempt-number joins as scheduled mappings. Audit actual replacement use before claiming actual scramble attribution; retain unresolved rows only for a renamed shared scheduled-position estimand. Extra-pool presence cannot certify replacement use or non-use.
7. Replace the unavailable official-2018 top100 pilot cohort with an explicitly exploratory all-finalist cohort; any confirmatory cohort change must be preregistered and cannot be described as the original test.
8. Refit training nuisance parameters and reselect minima in uncertainty calculations; keep and disclose the original eligible-season population. Do not present cluster-resampled exposure as the original fixed-exposure race.
9. Write pilot.json, a complete report, frozen specification, result-key ledger and artifact hashes. The held-out outcomes remain untouched.

Further fixes: do not interpret an unconstrained negative interaction moment or correlation above one as physical truth; show boundary diagnostics and broad crossed uncertainty. Distinguish variation across random peer splits from sampling uncertainty. Large-k curves change eligible finals, so show a fixed-panel sensitivity and its counts. The five-finals gate is nonlinear: 20% competition hashing produces far fewer eligible solver-seasons than one-quarter of the 80%; preserve exposure and avoid naive power scaling. A common permutation of all scramble labels in a final is invariant for the variance estimator; use independent per-solver permutations only as a signal-negative-control, not a causal scramble placebo. Actual fixed-exposure record-arrival null and official-cohort confirmation remain outside this exploratory study.

Frozen numerical model and algorithm are in `FROZEN_MODEL.md` / `frozen-model.json`. They are ready to adapt into a reviewed and committed METHOD.md; they are not a claim that preregistration has happened. The mapping gate must be resolved or the scheduled-position endpoint accepted before opening held-out outcomes.

## Reproduce, results and visuals

From workspace root:

```sh
.venv/bin/python rounds/r5/pilot-S1/pilot.py all
```

Stages can be rerun individually: `sources`, `simulation` (includes `validate.py`), `analyze`, `report`. Raw files and exploration-derived parquet caches are in gitignored `data/S1/`. The only minimal wide outcome table loaded into pandas contains the locked slice finals; large-export extraction and coverage use DuckDB SQL. Default: 400 simulations/scenario, 1,000 variance/predictive/interaction bootstrap draws, 2,000 extreme refit/reselection draws. Runtime is minutes on this laptop; no confirmation outcomes are selected. The pipeline reuses `rounds/r3/pilot-S1/pilot.py` extraction and its frozen manifest; these are repository dependencies, not undocumented downloaded code.

Charts: `01-obvious-and-fairer.png` (observed extreme deviation and fairer within-solver decomposition); `02-reliability-vs-peers.png` (measurement reliability versus predictive usefulness, with extrapolation); `03-extreme-adjustment.png` (observed extremes and conditional shrunk individual adjustments, separately labelled from aggregate correction).

Claim/result keys: shared fraction → `variance.json.fit.within_solver_share` / `bootstrap_95.competition_solver`; ten-peer R² → `reliability.json.representative_k_uncertainty[k=10]`; seasonal ratio → `extremes.json.aggregate_unshrunk_ratio` / `aggregate_unshrunk_95`; skill interaction → `interaction.json.model.interaction_variance` / `competition_solver_bootstrap_95`; DNF → `dnf.json`; simulation recovery → `simulation.json`, `interaction-simulation.json`, `selection-simulation.json`; mapping sensitivity → `mapping-sensitivity.json`; structural power coverage → `confirmation-structural-coverage.json`; power assumptions → `power.json`. `pilot.json` is the machine-readable recommendation. `PROGRESS.md` preserves stage-by-stage checkpoints.
