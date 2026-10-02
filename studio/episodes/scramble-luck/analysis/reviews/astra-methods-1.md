# Scramble luck — confirmatory methods review

Reviewer: Astra (Codex). Date: 2026-10-02.

**Verdict: approve with changes.** The registered, amended primary result is
supported: **Belief fails**, R = 1.0197788256, amended 95% interval
[1.0163698055, 1.0230705471]. I found no blocking error in the primary estimator,
validation amendment, or decision. Required reporting and sensitivity changes
are listed below; this is not unconditional approval of every secondary interval.

This file was created at the start of the review and updated during inspection.
The final text replaces its interim notes. No analysis code was edited.
Numerical evidence is in [astra-methods-1-checks.json](astra-methods-1-checks.json).
References below are relative to the episode directory unless otherwise stated.

## Required changes for sign-off

1. **Cross uncertainty:** label all four displaced cross percentile ranges as
   bootstrap diagnostics with unvalidated coverage, rather than ordinary 95%
   confidence intervals/“estimable” uncertainty. Put this qualification directly
   beside each number and in `results.json` measurement status. Preserve the
   registered calculations. There is no validated full multiway cross interval
   in the supplied evidence; do not silently apply Amendment 1 to this endpoint.
   If an inferential mechanism claim is retained, validate a suitable cross
   interval in an explicitly post-confirmation investigation first. Otherwise
   report the positive point association descriptively and mark its uncertainty
   inconclusive. This secondary limitation cannot change R's verdict.
2. **Era references:** present full-2019–2025, ±2-year skill-reference era F and
   gamma/D results, counts, and corresponding same-draw intervals as the direct
   contract reading. Keep the existing within-era-reference results beside them
   as a disclosed sensitivity. The eight blind discrepancies are a definition
   difference, not numerical failure. Do not resolve contractual fidelity merely
   by harmonizing the recheck to the production code.
3. **Provenance wording:** scope 15:17:40 UTC as the main analysis pipeline's
   first magnitude SELECT. The blind recheck had already extracted magnitudes
   by 15:11:57 UTC, after amendment registration. Distinguish the reported
   pre-opening decisions 7–10 from committed registration; they first appear in
   git with the confirmation results. Correct the stronger “registered before
   opening” description in `recheck/RECHECK.md`.
4. **Simulation wording:** the informative-DNF implementation uses Gumbel
   top-k/sequential weighted sampling without replacement. Describe that process
   precisely; “conditional DNF position odds multiply by exp(12*s)” is not an
   exact description for multiple DNFs. The intended monotone difficulty stress
   is implemented, and the empirical gate results remain valid for that generator.

No additional data collection or change to the primary threshold, point
estimate, weighting, or registered R interval is required by this review.

## 1. Order, blinding and input integrity

Git author and committer timestamps agree for these commits:

| Event | Commit | UTC, 2026-10-02 |
|---|---|---|
| METHOD v2 and confirmation IDs registered | `8a474d3` | 06:49:29 |
| Original failed gate committed | `3eca079` | 07:57:04 |
| Outcome-blind amendment investigation committed | `0eb88d1` | 08:55:43 |
| Owner-approved amendment registered in METHOD | `5496074` | 15:07:31 |
| Main-pipeline first magnitude SELECT recorded | log, not a commit | 15:17:40.383923 |
| Confirmation analysis and blind recheck committed | `e8880f3` | 15:36:01 |

`PROGRESS.md:322–328` reports gate failure at 07:51:16, audit completion at
07:52:28, an unsuccessful commit attempt at 07:54:52, then the main first open.
The failed attempt is superseded by actual commit `3eca079`; it does not mean
that the gate remained uncommitted. The exact cross computation finished at
06:57:29 (`PROGRESS.md:16`), before either analysis opened magnitudes.

The gate was **run and committed**, but did not pass. Both specified fallbacks
failed. The approved amendment subsequently passed its revised empirical gate;
there is no retrospective claim that the original gate passed. Registration
`5496074` adopts the already committed amendment text even though that text
retains its historical “draft” heading. METHOD's final amendment section is
unambiguous about approval and precedence.

`analysis/snapshot.py:46–83` reads identifiers, date fields, schedules and
categorical statuses; positive confirmation values become 1. Its magnitude
extraction at lines 98–100 is confined to pre-2019 exploration. Reading/hashing
raw bytes and categorizing signs is not opening positive magnitudes for analysis
under this contract. `cross.py` accesses scramble strings only. `gate.py`
generates synthetic times; training values are used as masks. Amendment
`evaluate.py:35–59` constructs Structure from the sign-only database and supplies
training status placeholders through a restricted parquet reader.

`analyze.py:63–76` persists the timestamp immediately before its first magnitude
SELECT. However, that is not the earliest read by every concurrent analysis:
`recheck/code/derive.py:59` reads raw attempt values, and local filesystem
birth/modified timestamps put `recheck/raw_times.npy`, `raw_rows.pkl`, and
`extraction.json` at 15:11:57. The script/run files were created at 15:11:38.
These corroborate a recheck run after 15:07:31 registration and before the main
pipeline's 15:17:40 read. The seal at 15:18:34 establishes completion, not first
access. Correct the scope of the claimed timestamp, not the substantive ordering.

The available git, code, logs and local metadata support compliance; they cannot
prove the absence of all unlogged historical access. In particular, the log
phrase “approved amendment commit 5496074 verified” is hard-coded in
`analyze.py:70`, and `analysis_reports.py:80` marks registration QA true without
executing a git check. I checked actual git chronology rather than accepting
those assertions as independent evidence. Local filesystem metadata is
corroboration, not an immutable audit trail.

Independent checks in this review:

- ZIP size/hash and the recorded ZIP digest match the immutable source contract.
  All seven named extracted source hashes match.
- Exploration and confirmation lists have 3,756 and 15,015 unique sorted IDs;
  hashes match METHOD (`b5f6426b…` and `2c0d6486…`), memberships are disjoint,
  and the original-ID SHA-256 modulo-five rule is correct.
- The 2019–2025 filter is on competition start-year after the all-years split.
  Training is exploration before 2019. All observed analysis years are 2019–2025.
- All nine recorded analysis-code hashes, fifteen bulk artifact hashes, the
  bulk-manifest hash, and all thirty-four amendment artifact hashes match.
- 5,017 eligible finals/competitions; 306,155 slots; 301,668 successes;
  4,429 DNFs; 58 DNSs; 12,853 confirmation solvers. There are no duplicate
  solver/competition rows. The training/confirmation solver union has 14,289 IDs.

## 2. Primary computation and correctness

### Mapping, statuses and estimation population

`snapshot.py:61–83` enforces one regular group, five regular rows and five distinct
nonempty numbers 1–5. Together these reject duplicates, extra regular numbers,
empty regular scrambles and ambiguous groups. Extra-pool rows are retained and
flagged, never mapped to observed results. The result-ID attempt join requires
exactly five distinct positions 1–5; zero/undocumented statuses quarantine the
whole result. Missing-schedule and multigroup exclusions are counted separately.
The actual dataset has no slot/status exclusions hidden by those gates.

`analyze.py:127–145` aligns values by result ID and verifies every status against
the structural table. Positive official centiseconds become seconds by /100,
then logs. DNF/DNS are missing time cells, not imputed times. Informative
contrasts require at least two successes, while singleton/no-success panels
remain in structural counts and failure analysis. Six no-success and fourteen
singleton-success panels are disclosed; seasonal selection can use a singleton.
The DNF denominator is successes + DNF, excluding DNS; 306,097 started attempts.
There is no speed threshold, ranking filter, complete-final requirement or
unregistered six-finalist gate in the all-peer primary estimator.

### Positions, tier moments and reference eligibility

`engine.py:12–25` implements the available-slot centering matrices, centered
logs, squared residual sums and contrast degrees. The zero/singleton cases have
zero contrast. References use other-final mean successful log times, at least
two other finals, excluding the focal competition and respecting ±2 years.
Median ties enter the slow tier; both tiers require three distinct informative
reference-bearing solvers. Repeated bootstrap copies cannot manufacture
reference or tier support. No solver has multiple included finals in one
competition, so row counts and distinct-final counts coincide here.

`engine.py:74–111` implements the finite-peer correction, separate tier residual
variances, cross-tier covariance, tau, gamma and balanced-tier denominator D.
The squared-weight noise matrix is A(v²), not A(v). Competition weights are
outside the round statistics. With unit weights its subtraction reduces to
the registered sum S; under resampling it uses the frozen noise-trace formula.
Negative variance-component estimates remain signed; nonpositive estimating
or variance denominators return unavailable rather than a substitute estimate.

The tier-specific pooled position refits absorb subtraction of any global beta
exactly, as disclosed in DEVIATIONS decision 5. F's invariance to global beta is
therefore algebraic, not a missing position adjustment. R uses the frozen beta
at its point and refits pre-2019 nuisance positions in draws. I reproduced the
training beta exactly in the production engine. Full-sample F is
0.0474338766059; gamma/D is 0.00356524713818. Coverage is 4,420 tier finals and
234,525 successful cells, with exclusions and missing references reported.

### Peers, extrema and aggregation

`engine.py:128–136` removes the focal solver's entire weighted contribution
before projection, imposes the zero-sum solution, and uses eigenvalues >1e-9
for rank four. In these data one solver has one row per final, so removal is
complete. No focal-time leakage, unit error or attempt-index shift was found.
Independent literal deletion/pseudoinverse calculations for forty real rows
agree within 9.72e-17.

`engine.py:148–192,207–219` freezes the ≥5-final person-year roster, selects
positive minima with deterministic tie handling, and does not replace an
unidentified winning solve with a runner-up. Actual uniqueness makes the
result-ID tie fallback immaterial. Every original season has an available
extremum: n=3,313. R is exp(mean(-h)), equal weight per available person-year;
it is not mean(exp(-h)). Resampled solver multiplicity weights seasons;
competition multiplicity controls which opportunities remain, not an extra
weight on a winning season. The separate arithmetic, per-solver and matched
all-peer/equal-tier sensitivities are correctly constructed.

The review independently selected all raw-centisecond seasonal minima with
the literal tie tuple and independently reconstructed their peer projections;
all 3,313 selections agree, with zero selection errors and zero aggregate
log-R difference at stored precision. The saved
point and interval also reproduce by direct recomputation from all 2,000
checkpointed log-R values.

### Bootstrap and decision

`engine.py:165–173` uses independent multinomial multiplicities via
`bincount(rng.integers(...))`: confirmation competitions, union solver IDs,
then training competitions. That is the specified multinomial law. It need
not give the same finite draws as `rng.multinomial`, explaining the blind
recheck's tiny interval differences without changing the method. The first ten
saved weight draws reproduce exactly from seed 20261001; all 2,000 primary
checkpoint IDs are unique and complete. Slots remain together, references and
moments are recomputed, the season roster remains fixed, and training shares
solver weights. Exposure/absence/rank diagnostics are retained.

`analyze.py:303–315` implements precisely the amendment's mean-centered linear
quantiles on log R, followed by exponentiation. The raw percentiles, mean
bootstrap displacement, amended endpoints and valid-draw count are reported.
Procedure A fixes the original selected cell and correctly uses competition ×
solver weights. F and gamma/D retain their signed percentile intervals.

`analysis_reports.py:269–275` applies L>1.10, U≤1.10, otherwise inconclusive,
preceded by the required primary checks. All relevant gates pass; U=1.0230705
is far below 1.10. Neither F, secondary results nor alternative cohorts rescue
or reverse the result. The implementation also requires F's coverage/validity
before issuing R's verdict; that is a conservative coupling of the separate
F interpretation gate, immaterial here but worth distinguishing on future runs.

## 3. Validation gate and amendment investigation

The original seven processes are present in `gate.py:18–79`: null, small shared,
large shared, tier interaction with unequal residual variances, informative
DNF, independent 10% replacements and pure shared slot shock. Real incidence,
structural season eligibility and status patterns are used without observed
confirmation magnitudes. Slot shock is deliberately absorbed and unjudged.
There are 200 datasets/process and 500 draws/dataset for the full original
pigeonhole gate. The original biases pass, but coverage fails: among other
failures, large-shared coverage is 1%, null 100%, small-shared 99.5%.

The competition-only fallback fails small-shared at 55.5%; solver-only fails
null at 99.5%. DEVIATIONS decision 6 transparently stops rejected fallbacks
after a complete failing process. This departs from exhaustively running each
fallback, but cannot convert a failure into a pass under an all-process rule.
Partial extra checkpoint records are not counted as completed passing processes.

The change from finite-dataset oracle coverage to the process expectation
occurred after 697 synthetic datasets, before confirmation; it is explicitly
disclosed in decision 3 and PROGRESS. The amended target formally adopts that
sampling interpretation. The oracle is the success-conditioned, peer-projected
shared/tier/replacement component at selected extrema, not total individual
luck or a latent failure-time target. Integration uses disjoint 10,000-dataset
streams and reports numerical precision.

Amendment 1 diagnoses R's original interval displacement through paired
reselection/fixed-selection/frozen-beta comparisons, retains the original
point estimator, and tests four finite alternatives. It changes both the
location of R's interval and the gate: coverage ≥92%, no upper coverage ceiling,
and separately ≤2.5% false holds and false fails at the calibrated boundary.
It openly records selection after seeing synthetic gate failure. The independent
replication uses distinct replicate indices, with 200/original process and
1,000 boundary datasets, each 500 draws. Calibration, integration and replication
streams are separate. Boundary truth is a numerical calibration to the 1.10
line, not an algebraically exact proof; sensitivity to integration error is shown.

I independently recalculated B's coverage, bias and boundary errors from
`replicates.jsonl` and `replication.jsonl`. Paired judged coverage is 97–100%;
independent judged coverage is 96–100%. Boundary errors are 2%/1% (paired) and
0.6%/0.9% (independent). Maximum independent judged absolute log bias is
0.00013498, below 0.005. All records have the required draw count. The supplied
fast/full engine comparisons and 500/1000/2000 endpoint stability checks support
the R computation; I reran the frozen numerical fixtures as a cheap check.
I did not rerun millions of simulation/bootstrap fits.

One wording correction: Gumbel top-k selection gives sequential sampling
without replacement with weights exp(12*s). When there is more than one DNF,
its subset probabilities are not those of an exact conditional-logistic model
proportional to exp(12*sum(s_DNF)). This does not violate METHOD's qualitative
hard-scramble DNF stress, but the exact “conditional odds” characterization in
`GATE.md`/`gate.json` and the amendment discussion should be replaced by the
actual algorithm. Gate coverage still refers to the process actually simulated.

## 4. Optimal-cross correlation: cause and permissible uncertainty

**The 0.2658 point and [0.1975, 0.2287] percentiles are correctly computed by
this code, but the latter are not a validated 95% confidence interval for the
reported correlation. This is not the seasonal-reselection effect in Amendment 1.**

`cross.py` uses an exact half-turn-metric BFS over four labelled oriented edges,
190,080 reachable states per face, and takes the requested six-face and U/D
minima. Mapping from the 25,085 scheduled strings to five-position arrays is by
competition, round and scramble number. No string/position join error was found.

`analyze.py:185–206` projects all identified focal solver-rounds, averages their
five leave-one-out contrasts at each scheduled position, and correlates those
averages with cross length. It includes failure positions as specified in
DEVIATIONS decision 8. It does not use the selected seasonal rows for this
statistic. The centered version is the appropriate within-final geometry check.

I reproduced this calculation without invoking seasonal selection and isolated
its resampling components using the first 200 registered draws:

| Quantity / resampling | Mean r | Mean variance of averaged h | Mean covariance(h, centered cross) |
|---|---:|---:|---:|
| Original data | 0.265802 | 0.00244540 | 0.00897475 |
| Competition only, original h fixed | 0.265571 | 0.00244595 | 0.00896663 |
| Solver only, refitted peers, frozen beta | 0.213238 | 0.00380927 | 0.00898498 |
| Product weights, refitted peers, frozen beta | 0.213319 | 0.00380868 | 0.00898620 |
| Product weights, refitted peers and training beta | 0.213107 | 0.00381730 | 0.00898738 |

The reconstructed full draws agree with the saved draws within 4.45e-16.
Solver resampling drops and repeats peers, adding measurement noise to each
estimated final-position contrast. Its variance increases about 56%, while
covariance with geometry scarcely changes. The denominator of Pearson r grows,
attenuating r. Competition exposure alone and training refitting do not explain
the displacement. A percentile interval can in general exclude its point
without a coding error; here the ablation identifies a concrete statistical
calibration problem. The R gate did not test this nonlinear generated-variable
endpoint.

What interval is valid?

- **For the registered full multiway cross estimand, none is validated by the
  supplied investigation or by this review.** Keep [0.19751469, 0.22872852] only
  as the registered bootstrap percentile diagnostic and mark inferential
  uncertainty unresolved. The bootstrap mean is 0.21317016.
- Translating by point minus bootstrap mean gives [0.25014644, 0.28136028].
  This is a *candidate*, not an approved or demonstrated-valid cross CI.
  Amendment 1 explicitly validates R only. A basic reflected interval would
  instead be [0.30287530, 0.33408913]; neither transformation is justified merely
  because the original percentiles miss the point.
- Holding the observed h values and beta fixed and resampling only competitions
  gives [0.25261904, 0.27882447] in the 2,000 saved competition draws. This is a
  narrower conditional diagnostic, usable only for an explicitly conditional
  question under independent-competition assumptions. It omits regenerated
  peer/training uncertainty and repeated-solver dependence; it cannot substitute
  for the registered multiway interval.

A future full interval should be tested for this correlation and its generated
peer contrasts, with varying panel sizes/missingness and repeated solvers.
Any new calibration is post-confirmation secondary work. Existing FINDINGS
already disclose the problem at lines 121–127; the remaining correction is to
stop formatting the earlier numbers and machine-readable status as ordinary
valid 95% intervals. The point association supplies descriptive geometry evidence;
it is not a validated secondary significance claim. The same issue affects all
four cross correlations, not just the six-face centered one.

## 5. Era skill reference: which reading METHOD supports

METHOD:174–178 explicitly defines the reference as other eligible confirmation
finals within ±2 calendar years and explicitly permits future appearances within
2019–2025. METHOD:298 says to repeat F and R in the two eras, without changing
that reference definition. **The blind full-window reading is the more direct
literal implementation.** A self-contained within-era reference is scientifically
reasonable but adds an exclusion that is not stated in that definition.

DEVIATIONS decision 9 does disclose the restricted reference choice; the report
is transparent about it. Disclosure is not equivalent to an approved amendment
of the reference universe. Moreover, decisions 7–10 were first committed with
the confirmation results, despite the reported pre-opening timing. The recheck's
post-unblinding harmonization proves the two algorithms agree when definitions
agree; it cannot decide which definition the committed contract required.

I independently reproduced both interpretations:

| Era | Full-window F | Within-era F | Full-window gamma/D | Within-era gamma/D | Full-window finals / successes | Within-era finals / successes |
|---|---:|---:|---:|---:|---:|---:|
| 2019–2022 | 0.04718725046 | 0.04823810779 | 0.00328942421 | 0.00181979025 | 1,375 / 68,127 | 1,269 / 59,773 |
| 2023–2025 | 0.04731677464 | 0.04746543127 | 0.00360846067 | 0.00296930942 | 3,045 / 166,398 | 3,012 / 162,831 |

These are exactly the eight blind mismatches. The full-window tier-final counts
sum to the primary 4,420; the reference restriction loses another 139 panels.
Report both readings, with full-window reference weights recomputed in each
registered bootstrap draw while only outcome panels are restricted to the era.
Do not reuse the within-era interval on the different full-window point.
All-peer R does not use skill references, so neither era R nor the primary
verdict changes. For leave-year-out checks, deleting the year's reference
information is defensible as an actual data deletion; distinguish that aim from
estimating an era using the fixed retrospective reference definition. Yearly
sensitivity labels should likewise state whether references are restricted.

## 6. Departures, resolutions and their consequences

This inventory distinguishes genuine departures from disclosed choices where
METHOD left implementation details open. “No verdict effect” means the actual
registered primary decision in this dataset, not a universal guarantee.

| Item | Contract fidelity / disclosure | Consequence and disposition |
|---|---|---|
| Original R percentiles and 92–99% gate replaced | Approved Amendment 1, fully disclosed in METHOD/FINDINGS; not a silent departure | Material: enables a valid amended verdict after the original gate failed. Accepted under the approved contract. |
| Process-expectation oracle replaces initial finite-oracle gate target after 697 datasets | DEVIATIONS 3; formally settled by Amendment 1 | Could change gate coverage. Accepted with timing disclosure and independent replication; no confirmation-based tuning shown. |
| Fallbacks stopped after one completed failing process | DEVIATIONS 6 | Literal reduction in simulated fallback processes; logically cannot change an all-process acceptance result. Accepted. |
| Half-turn rather than quarter-turn cross metric; U/D convention | DEVIATIONS 1 | METHOD did not specify move metric. Reasonable, explicit; secondary only. |
| Solver union and independent training competition draw | DEVIATIONS 2; also recognized in blind recheck | Resolves an unspecified nuisance-resampling universe. Could affect interval widths; included in amended validation. Accepted. |
| Distinct-reference/tier support and weighted medians | DEVIATIONS 4 | Faithful to distinct finals/peers; duplicated weights do not manufacture support. Accepted. |
| Collapsed tier position fit without first explicitly subtracting beta | DEVIATIONS 5 | Algebraically identical, numerically checked. No change to F or verdict. |
| Conditional rather than dummy-intercept logistic DNF fit | DEVIATIONS 7 | Appropriate solver-round fixed-effect implementation avoiding incidental intercept estimation. Secondary; accepted. |
| Focal-average cross contrast; raw and centered variants; failure positions included | DEVIATIONS 8 | METHOD leaves aggregation details open. Reasonable point definition, but peer-resampled correlation intervals need qualification/calibration. No R effect. |
| Era references restricted to included competition mask | DEVIATIONS 9; FINDINGS and RECHECK | Adds a reference restriction; eight quantified discrepancies. Required full-window counterpart, no R effect. |
| Full-draw masks for subsets; original seasonal roster retained | DEVIATIONS 9 | Consistent fixed-roster sensitivity; pointwise intervals, not new verdicts. Accepted. |
| Complete-success masks solver-rounds, then reselects; clipping/recentering follows frozen pilot | DEVIATIONS 9 | Disclosed sensitivity choices; all primary successes retained. No primary verdict effect. |
| Leave-solver-out intervals only for observed range endpoints | DEVIATIONS 9 | METHOD requests checks with intervals but not 12,853 separate intervals. Reasonable reporting scope; explicitly not simultaneous uncertainty for the selected range. |
| Recentered arithmetic/per-solver/equal-tier intervals | DEVIATIONS 10 and FINDINGS | Amendment validates primary R, not these extensions. Descriptive only, no new guarantees or verdict. Accepted with existing qualification. |
| Prediction competition intervals, fixed ≥22 panel, 30 splits and frozen nuisance | DEVIATIONS 10 and FINDINGS | Follows frozen prediction; repeated-solver/baseline uncertainty omitted and explicitly disclosed. Secondary only. |
| Independent slot permutations with primary beta frozen | DEVIATIONS 10 | References, moments and minima are refitted; unrelated training is unchanged. Reference ranges correctly distinguished from sampling CIs. Accepted. |
| Empty yearly draw correction after opening | Dedicated DEVIATIONS section | Records invalid yearly R rather than averaging an empty array; zero-weight season cannot affect pooled yearly result. Primary checkpoints retained. Accepted bug fix. |
| Extra F coverage/validity checks coupled to R verdict | Not separately called out | Conservative beyond F-only interpretation gate; all pass here. Document if pipeline is reused where F fails but R is valid. |
| Gumbel top-k called exact conditional position odds | Algorithm disclosed; distinction not in DEVIATIONS | Wording error about multi-DNF DGP, not the intended monotone stress or calculated gate. Correct description; no current verdict effect. |
| Main FIRST OPEN described without concurrent-recheck scope | Not disclosed as a distinction | Timestamp claim too broad; recheck opened earlier but after amendment. Correct wording; chronology still supports authorization/order. |
| Decisions 7–10 called pre-open/registered | Reported pre-open, but first git evidence is `e8880f3` | Not independently established as preregistration. Treat as disclosed implementation choices, not approved contract overrides. |
| Registration QA uses literal true; checkpoints resume by ID without input/code fingerprint enforcement | Not a METHOD estimator departure; not disclosed as a QA limitation | Current chronology/hashes were checked independently and match. Harden future reruns; no observed stale-input or seed error found here. |

## 7. Interpretation and contrary checks

FINDINGS generally follows the wording contract. It names a **shared
scramble/slot component**, limits the population to eligible finals and seasonal
bests, labels success conditioning and retrospective skill references, identifies
F as a share of balanced-tier within-round log-time variance, and says the
adjustment is not a causal replay. It does not assign residual variance to
personal luck or attribute a particular world record. The required WCA notice
is present with the source's prescribed spelling. The opening “adds about 1.98%”
correctly describes adjusted/observed time, not a 1.98% reduction from adjusted time.

Contrary checks are substantially present rather than hidden: gamma's signed
interval crosses zero; DNF odds ratio 1.0348 has interval [0.9777, 1.0649]; the
success-only understatement caveat is included despite that uncertainty;
2020/2021 and parts of 2022 fail diagnostic coverage gates; solver deletion
ranges and matched equal-tier attrition are shown; peer prediction is weak and
panel-dependent; replacement scaling is explicitly neither a bound nor an R
correction; all 5,017 finals have extra pools and no actual-assignment audit is
claimed; slot shock is absorbed in simulation; cross percentile displacement
is explicitly acknowledged. The raw and fixed-selection R intervals, bootstrap
exposure loss, and original failed gate remain visible.

The remaining overstatement is presenting uncalibrated cross limits in ordinary
estimate-(interval) form before explaining their failure, while machine-readable
status says “estimable.” Secondary pointwise status does not itself establish
coverage. Move the limitation to the measurement and withhold calibrated
inferential language. Likewise, simulation recovery under the chosen DNF process
cannot bound arbitrary latent failure times; FINDINGS already states this limit.

The primary conclusion is unchanged by every issue identified here. Required
changes concern accurate secondary inference, literal reference-definition
fidelity and auditable provenance wording, not a reason to reverse the amended
“Belief fails” result.
