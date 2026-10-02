Does the part of a scramble's difficulty that all finalists share materially speed up season-best solves?
Test 2019–2025 single-group 3×3 finals in the untouched 80% of WCA competitions.
Measure, from successful solves, the shared scramble/slot component and the shared-scramble-adjusted ratio R for each solver's season best.
Belief holds if R's 95% lower bound >1.10; it fails if R's 95% upper bound ≤1.10; anything else is inconclusive.
The 10% line was fixed before any solve time was read; the simulations that validate the whole R pipeline and its bootstrap must pass first.
The data cannot separate personal luck from execution, nor isolate a scramble from conditions shared by its time slot, nor explain a particular record.

# How much of a record-speed Rubik’s Cube solve is the shared scramble? — methods

Motivating question for the video: “Was the world record a lucky scramble?” The
study answers a narrower one, and the video must say so early: on average, how
much does the scramble difficulty shared by every finalist speed up season-best
final solves? It does not measure a record holder’s total luck.

Status: draft pre-registration, 2026-10-01, written after the locked 20% pilot
and before reading confirmation outcomes. Review and commit this method and
the confirmation ID list before opening those outcomes. This file records a
revised all-finalist test, not the original official-2018 top-100 test.
Later changes belong under Amendments, with their timing and reason.

## Question

How much successful solve-time variation is shared among finalists assigned
the same scheduled scramble, and how much does that peer-measured component
help their fastest final-round solves of a season? A world record motivates
the question; the confirmatory population is seasonal bests in eligible finals.
It does not represent all record attempts, earlier rounds, or all cubers.

## Belief → obvious answer → flaw → fairer test

Starting belief: record-speed singles benefit materially from an unusually
favourable scramble. Operationally, “materially” means an aggregate estimated
shared-scramble-adjusted time more than 10% longer than the observed seasonal best.
On a 3–5 second elite solve, 10% is roughly 0.3–0.5 seconds, a very large margin
at that level. Timing disclosure: the 10% line was fixed in
`../r2/verify-S1.json` at 07:17 on 2026-10-01, before the exploration slice was
locked (07:38) and before any solve time was read (07:43). It is unchanged.
The familiar competing intuition is that the lowest official time identifies
the fastest cuber. Neither intuition is settled by one spectacular solve.

The obvious answer is to inspect a record reconstruction for easy pairs or a
skipped last step, or rank solvers by their best single. Published examples:
[Ruwix, 12 June 2023](https://ruwix.com/blog/max-park-rubik-single-record-313/)
describes Max Park’s then-record 3.13-second solve as including a “lucky PLL skip”;
[Ruwix, 25 November 2018](https://ruwix.com/blog/yusheng-du-record-347/)
asks whether Yusheng Du’s then-record 3.47 was a lucky scramble and stresses
both skill and luck. These are historical claims, not statements of today’s record.
Two web searches on 2026-10-01 located these sources. Their reconstructions
motivate the belief; they do not certify the export’s per-attempt assignments.

Flaw: a solution can suit one solver’s method, orientation, or choices;
execution and attempt exposure also affect a minimum. A lucky-looking solution
does not measure an advantage common to finalists. The fairer test estimates
shared contrasts from peers in the same final, excluding the focal solver,
and repeats seasonal-best selection in resampling. Within-round centering
removes solver-round ability and common round conditions, not every confounder.
Random scheduled scrambles supply a natural comparison; synchronized conditions
at an attempt position and replacement errors remain alternative explanations.

## Scope and sources

- Confirmation: competitions with `int(sha256(id.encode('utf-8')).hexdigest(),16) % 5 != 0`;
  eligible finals dated by competition start year, 2019–2025 inclusive.
  Hash original IDs without normalization, across every year before period filtering.
- All 18,771 export IDs, including cancelled/no-results competitions, define the split:
  3,756 exploration and 15,015 confirmation. “80%” denotes the locked hash rule,
  not a requirement that exactly 80% of competitions or attempts remain eligible.
- Exploration list SHA-256:
  `b5f6426bffbbf01c4d742cbe65f083cb4cbb5a134a5b60c3fe9fa312d028b7a4`.
  Confirmation list: [confirmation-competition-ids.txt](confirmation-competition-ids.txt),
  sorted lexicographically, UTF-8, one ID per line, LF terminated; SHA-256:
  `2c0d64860c762e8214ec78123326b62ddd262feabadb45a3515728cbef1b4ed8`.
- Population: every structurally eligible finalist; no ranking or reputation filter.
  Seasonal population: every person-year with ≥5 eligible confirmation finals.
  This explicitly replaces the unavailable official-2018 top-100 roster and
  ≥50 pre-2019 attempts requirement; no slice-derived top-100 proxy substitutes.
- Outcome-blind pilot counts: 5,017 scheduled-mapped confirmation finals,
  306,155 attempt slots and 3,313 structurally eligible person-years in 2019–2025.
  These are potential coverage, not valid-time or identifiable-effect counts.
- Source: [WCA results export](https://www.worldcubeassociation.org/export/results),
  v2.0.2, immutable [dated ZIP](https://exports.worldcubeassociation.org/results/WCA_export_v2_273_20260930T000036Z.tsv.zip),
  exported 2026-09-30 00:00:36 UTC; 378,739,520 bytes; ZIP SHA-256:
  `e6b262b2ada513228a48fa221015ddc25e9041a029340778cd253f564c23427d`.
  Use results, result_attempts, scrambles, competitions, round_types and metadata.
  Individual file hashes and source checks are in
  `../r5/pilot-S1/source-manifest.json` and `source-verification.json`.
  Recheck hashes before analysis; no daily-export refresh or network fetch in analysis.
- Licence: bundled README’s custom Allowed Use grants whole/partial republication
  with the prescribed notice. README SHA-256:
  `ec4a096b29b937e4d4f4e395227d703bbb773d711ff4b6c4ca569ee03e904a8d`.
  Carry this notice prominently in video, companion page and redistributed tables
  (retain the source’s spelling): “This information is based on competition results
  owned and maintained by the World Cube Assocation, published at
  https://worldcubeassociation.org/results as of September 30, 2026.”

## Attempt-to-scramble mapping and statuses

Use event `333`, `round_types.final=1`, format `a` (average of five).
Join results to attempts on result ID, and to schedules on competition/event/round.
Require exactly one distinct non-extra group and exactly one nonempty regular
scramble for each number 1–5, with no duplicates or additional regular numbers.
Each included result must have exactly five attempt slots numbered 1–5.
The scheduled link is `attempt_number = scramble_num` within that unique group;
never join a multi-group round merely by competition/round/attempt.

Extra-pool rows are never assigned by their order, scramble number, or time.
Keep finals with pools in the primary scheduled-position analysis and flag them.
Neither pool presence nor absence reveals whether an extra was used.
[WCA Regulation 11e1](https://www.worldcubeassociation.org/regulations/#11e1)
requires a different scramble for an extra attempt: the official exported result
may therefore occupy a scheduled slot whose actual scramble was different.
Do not infer replacement use from an unusually fast/slow result.

Actual-scramble attribution requires an independent solver/round/attempt audit,
including replacement usage and the scramble actually used, especially for extrema.
Use official assignment/incident records or independently corroborated footage;
log the evidence and unresolved cases. Audited analyses are separate sensitivity
or case-study outputs: they cannot silently replace the scheduled primary sample.
No audit is supplied here; the primary claim is explicitly scheduled-position.

Positive values are official centiseconds (penalties included); use seconds = value/100.
`-1` is DNF, `-2` DNS, `0` absent. Keep every successful cell in DNF/DNS panels;
never impute a failure time, treat zero as a fast solve, or drop a whole final for DNF.
Zero or an undocumented status violates the five-attempt policy: quarantine that
solver-result with a reason. With <2 successes a solver-round supplies no time
contrast, but stays in counts and failure analysis; it can still supply a seasonal best.
Started-attempt DNF denominator is successes + DNF; DNS is reported separately.

**F and R are estimated from successful solves only.** They condition on
success: a log-time model cannot contain a DNF, and no failure time is imputed.
Because a hard scramble may raise DNFs as well as times, failures are analysed
separately as a preregistered secondary endpoint: a logistic model of started-attempt
DNF on the leave-one-out peer-measured shared contrast h (defined below), with
attempt-number and solver-round fixed effects, reported as an odds ratio per
0.05 of h with its multiway-bootstrap interval. If that association is positive,
the video must say the success-only estimate may understate shared difficulty, and
the informative-DNF simulation (below) bounds by how much. It cannot change the
verdict.

## Measures: frozen validated components

Use `S1-r5-measurement-v1` in `../r5/pilot-S1/FROZEN_MODEL.md` and
`frozen-model.json`; algorithms `pilot.py:moment`, `tier_moment`, `peer_effects`
and `extreme_analysis`, with validation in `validate.py`. Finite-peer bias
correction, unequal residual variances by tier, and unshrunk aggregation stay fixed.
Tier-aware variance is promoted from the frozen secondary analysis to a primary
descriptive measure here; the frozen all-peer seasonal ratio remains the verdict
endpoint. Equal-tier seasonal estimates are mandatory sensitivity, not a newly
validated primary algorithm. No common-only estimate replaces the tier-aware share.

**Shared variance share.** Let y be log successful seconds; demean within each
solver-round’s available successful slots. Model y = solver-round intercept +
global attempt-position effect + shared round-position effect + tier interaction + residual.

**Attempt number is confounded with scramble number** (scramble k is always
attempt k), so warm-up, fatigue, nerves or venue drift could pose as scramble
difficulty. Two controls, both fixed now: (1) attempt-number fixed effects β
(the global position effect), frozen from pre-2019 exploration finals and
subtracted before any shared contrast is estimated; as a sensitivity, β is
re-estimated within the confirmation data and within each year, and F and R are
reported again. (2) A mechanism check that does not use times at all: for every
included scheduled scramble, compute the optimal cross length (fewest moves to
solve the four edges of one face, minimum over all six faces and, separately,
over white/yellow only) with an exact solver from the scramble string, before
joining any times. Report the correlation between the peer-measured shared
contrast and optimal cross length, with its multiway-bootstrap interval. A
positive association is evidence the component reflects scramble geometry; none
means it may largely be slot conditions. It is a secondary check and cannot
change the verdict. Conditions shared by everyone in one final's time slot
remain bundled with scramble difficulty; this component is therefore named the
**shared scramble/slot component** throughout, and the video must not call it
pure scramble difficulty.

Skill reference = median of other-final mean log times from ≥2 eligible confirmation
finals within ±2 calendar years, excluding the focal competition. Future appearances
within 2019–2025 are allowed; this is retrospective adjustment, not a forecast.
Among reference-bearing informative finalists, fast = reference below the panel
median; slow = the remainder. Require ≥3 informative solvers per tier. Report
coverage lost to this requirement, and the all-finalist common-only comparator.

For valid-slot indicator q and m successes, C_i = diag(q) − qqᵀ/m;
C_i = 0 when m <2. In each tier and final r, A_r = ΣC_i,
V_r = ΣC_i(y_i−β), S_r = Σ||C_i(y_i−β)||², d_r = Σ(m_i−1).
Fit pooled position β by the frozen pseudoinverse moment routine separately per
tier; b_t = [Σ||V_r||²−ΣS_r]/[Σtr(A_r²)−Σd_r],
e_t = ΣS_r/Σd_r−b_t. This subtracts finite-peer noise with exact missing-pattern traces.
Cross-tier c = ΣV_fastᵀV_slow / Σtr(A_fast A_slow).
Common variance τ = (b_fast+b_slow+2c)/4;
tier-interaction variance γ = (b_fast+b_slow−2c)/4.
Primary share F = τ / D, D = (b_fast+e_fast+b_slow+e_slow)/2.
This is balanced-tier, within-solver-round successful log-time variance, not total
population variance or percent of seconds caused by luck. Also report γ/D and
tier residuals. Signed estimates/intervals remain signed; constrain only display
SDs and label boundary diagnostics. A negative moment is not negative physical variance.

**Seasonal-best correction (verdict endpoint).** Freeze global β from pre-2019
exploration finals at [-0.00019098085080805892, 0.0015330545917410243,
−0.00016398101357186266, −0.005728817307245912, 0.0045507245798848085].
For each focal solver-final, exclude all five of that solver’s cells; estimate
h = A_peer⁺V_peer from other finalists, with zero-sum five-position constraint.
Require rank(A_peer)=4 (eigenvalues >1e−9); otherwise the full contrast is not identified.
Select the fastest positive time in each structurally eligible person-year;
ties break by competition ID, round ID, attempt number, result ID. If its peer
contrast is unidentified, mark that season unavailable; never choose a runner-up.
Report no-success seasons and unavailable extrema before applying coverage gates.
At selected position j, the **estimated shared-scramble-adjusted time** =
observed time × exp(−h_j): the solve with the estimated shared scramble/slot
component removed under the model. It is not a causal replay of the solve on a
different scramble; solver-specific compatibility, inspection choices,
orientation, execution and skips are unobserved and stay in the observed time.
**Aggregation, frozen:** R = exp(mean over person-years of −h_j), the geometric
mean of the adjusted/observed ratios, with equal weight per eligible, available
person-year (a solver with six eligible seasons contributes six terms). R is not
mean(exp(−h_j)); that arithmetic-mean ratio, which extreme corrections pull
harder, and a per-solver-weighted R (average −h_j within solver first, then
across solvers) are reported as sensitivities and cannot change the verdict.
The reference point is zero shared contrast, the median under the frozen symmetric
model, not a newly selected fastest corrected solve or an empirically chosen percentile.
R=1.10 means a 10% longer estimated adjusted time, not a 10% reduction in time.
This all-peer estimate averages the observed peer lineup; tier imbalance can load
interaction into it. F separates the identified skill-tier component; R does not
identify an individual’s total scramble luck. Report the equal-tier sensitivity beside R.
Use unshrunk contrasts for R: selecting extrema makes peer-only posterior shrinkage
biased toward zero. Shrunk individual displays use frozen τ=0.0007830105490928417,
e=0.021684974210191423; label their selection/mapping limits and never average them as R.

## Uncertainty and pass/fail rule

Use 2,000 crossed competition/solver-ID bootstrap draws, seed 20261001;
sample each cluster dimension independently with replacement, keeping all slots
and appearances of a cluster together. Recompute weighted moments and peer effects;
exclude every weighted copy of the focal solver. Squared solver weights enter the
residual-noise traces A(w²), rather than pretending copies are independent peers.
Refit pre-2019 exploration nuisance positions/training moments in the same draw,
with solver weights shared across training/confirmation, and reselect each seasonal
minimum among resampled competitions. Recompute skill references for variance
estimation; a repeated copy of one other final does not meet the two-final gate.
Keep the original seasonal eligibility roster (do not reapply the five-final gate);
report seasons absent from each draw, changes in exposure and valid-draw counts.
Resampling changes the race’s exposure: these are sampling intervals, not a replay
with the original fixed attempt counts. Report 95% percentile intervals for F,
γ/D and log R, exponentiating the last. No clipping before interval calculation.

**Bootstrap algorithm, exactly** (the two-way “pigeonhole” product-weight
bootstrap for cross-classified data): in each draw, give every confirmation
competition c a multiplicity w_c from a multinomial draw of size C over the C
competitions, and independently every solver s a multiplicity v_s from a
multinomial draw of size S over the S solvers. Each solver-result in competition
c by solver s gets weight w_c·v_s; a weight of zero drops it. All five slots of
a solver-result share its weight. Moments, peer effects, skill references,
season-best selection and R are recomputed from the weighted data as above.
Seed 20261001; draw order competitions then solvers.

**Pre-confirmation validation gate (must pass before any confirmation time is
read).** Using the confirmation set's real structure only (which solvers sat in
which finals, panel sizes, DNF/DNS pattern counts; no times), simulate log times
with known truth under at least seven data-generating processes: null; small
shared (pilot-sized, R≈1.016); large shared (R≈1.12); shared plus fast/slow
tier interaction; informative DNF (hard scrambles raise DNF); 10% random
replacement scrambles; and a pure attempt-slot shock shared within a final with
no scramble effect. Run the entire pipeline end to end on each (leave-one-out
peer estimation, season-best selection, aggregation, the bootstrap above), with
at least 200 simulated datasets per process and 500 bootstrap draws each.
Acceptance: absolute bias of log R ≤ 0.005 and 95%-interval coverage of the
true R between 92% and 99% in every process except the slot-shock one, where
the expected result (the component absorbs the shock) is reported, not judged.
If the pigeonhole bootstrap fails coverage, the fallback order is fixed now:
(1) competition-only cluster bootstrap, (2) solver-only cluster bootstrap; use
the first that passes. If none passes, or bias fails, the verdict is
“inconclusive: uncertainty not validated”, and the confirmation is not opened
for a verdict until an amendment is registered and committed.

Before a verdict require ≥500 eligible confirmation finals, ≥20,000 included
attempt slots and ≥100 available seasonal extrema. For interpreting F require
≥500 tier-supported finals and ≥20,000 successful cells in that subset.
Nonpositive variance denominators, unavailable intervals, or <1,900 valid bootstrap
draws trigger an inconclusive measurement, not a substitute estimator.
After gates pass, apply these mutually exclusive rules to R and its interval [L,U]:

| Outcome | Numerical rule | Permitted video claim |
|---|---|---|
| Belief holds | L >1.10 | The shared scramble/slot component speeds these season-best solves by more than 10% on average. |
| Belief fails | U ≤1.10 | The data rule out an average shared scramble/slot boost as large as 10% for these season bests; report R and its interval (for example “around 2%”). |
| Inconclusive | All other cases, or a gate fails | The fairer test cannot decide whether the average shared boost reaches 10%. |

The rule compares the whole interval with the 10% line, symmetrically: an
interval that contains 1.10 is inconclusive, whatever the point estimate.
Exactly L = 1.10 is not a pass. F quantifies scale separately;
an interval above zero can show a detectable shared component even if the belief fails.
No F significance test, secondary endpoint, or alternative cohort rescues R’s verdict.
Intervals are pointwise; secondary checks carry no additional confirmatory verdicts.

## Robustness, exclusions and wording

Report all checks, including contrary results, with counts and intervals:
- Complete-success solver panels; clip centered log contrasts at ±0.6; show the
  all-finalist common-only share with its actual within-solver denominator.
- Repeat F and R in 2019–2022 and 2023–2025; leave one year and one solver out.
  Divergence limits general wording; it never changes the primary verdict rule.
- For extrema with ≥3 identified peers in each skill tier after focal-solver removal,
  compute h_equal=(A_fast⁺V_fast+A_slow⁺V_slow)/2. Compare equal-tier and frozen
  all-peer R on the same available extrema, and disclose subset attrition.
  Disagreement forbids describing R as an advantage uniform across skill tiers.
- Separate binary DNF covariance and peer-difficulty/DNF association, DNS counts,
  and the frozen MCAR/informative-DNF simulation stresses; no joint latent-time claim.
- Independent within-final per-solver permutations of all five time/status slots,
  1,000 draws, refitting the pipeline: a shared-alignment negative control.
  A common permutation for every finalist is invariant and is not a placebo.
- Replacement sensitivity p=0, .01, .05, .10, .20: τ/(1−p)² assumes independent
  random replacement. This is neither a worst-case bound nor a correction to R;
  targeted replacements can bias either way. Show audited subset results if available.
- Peer prediction at k=2,5,10,20 with 30 whole-solver splits, ≥k+2 informative
  finalists, target excluded from baseline; report fixed-panel sensitivity and counts.
  Distinguish split randomness, competition intervals and model extrapolation.

Exclude other events, nonfinal/multigroup/invalid-format rounds, ambiguous regular
schedules, incomplete/duplicate attempt slots and invalid statuses, with reason counts.
No speed threshold, outlier deletion, six-finalist gate or complete-final requirement.
Report singleton/failure panels, missing skill references and peer-rank failures.
Do not generalize from the tier-supported subset without its coverage table.
For every outcome, residual variation includes execution, solver-specific scramble
opportunities, penalties, model error, missingness and mapping error. The data
cannot separate personal luck from execution. Never say “the rest is personal luck,”
“the record was only luck,” “the record holder is not the fastest,” or attribute a
particular world record from the aggregate result. Exact-record stories require
verified actual assignments and remain illustrative, not independent confirmations.

## Exploration, verification and amendments

Everything learned from the locked 20% is exploratory: the 3.81% common-only
share (95% 2.94%–4.70%), broad seasonal R=1.0163 (1.0049–1.0225, n=180),
weak peer prediction, tier diagnostics, era patterns, mapping/DNF findings and
cohort/model choices. Known-truth simulations validate recovery under their
specified models, not real-world attribution; aggregate unshrunk recovery was
tested under independent execution noise, not every interaction/missingness process.
Pilot-based power extrapolations are assumptions, not promised confirmation power.
Record-arrival simulation, optimal-move features, method/orientation effects,
alternative cohorts/counterfactual percentiles and individual rankings are exploratory.
None is a preregistered partition of skill, execution and total luck.

Before confirmation analysis: verify source/list hashes, disjoint membership,
join uniqueness, statuses, centisecond conversion, peer exclusion and trace identities;
check code reproduces the frozen synthetic moment/selection results; pass the
pre-confirmation validation gate above and commit its report; compute the
optimal-cross metric for every included scramble. Save code hashes,
exclusion/coverage tables, executable analysis and result keys for every script number.
Use independent verification, blind re-derivation and methods review before filming.
Only identifiers were read to materialize the confirmation list for this draft.

Amendments at registration: adopt the locked all-years competition split rather
than r2’s obsolete slice; restrict confirmation to 2019–2025; replace the unavailable
top-100 cohort explicitly; accept scheduled-position attribution; retain DNF successes;
promote the validated tier-aware variance share; use unshrunk seasonal aggregation;
preregister the upper-bound failure rule separately from failure to pass. These
changes follow the exposed pilot/design limitations, not held-out results.

Changes after an external methods review of draft v1 (2026-10-01, afternoon;
the 20% pilot results were known, no confirmation outcome was): (1) the
decision rule now compares the interval with 1.10 on both sides. Draft v1 and
`../r2/verify-S1.json` (07:17, before any data) passed the belief on R >1.10 with
a lower bound above 1.00, which does not establish a boost above 10%. The
stricter “holds” rule makes the belief harder to confirm. The “fails if the upper
bound ≤1.10” rule was first written after the pilot; it is disclosed as such.
Its justification is symmetry with the “holds” rule, not the pilot's estimate.
(2) The 10% line is unchanged, and its pre-data timing is recorded above.
(3) R is described as an estimated shared-scramble-adjusted ratio, not a causal
counterfactual. (4) Attempt-number fixed effects and the slot confound are made
explicit, with a time-free optimal-cross mechanism check. (5) F and R are
explicitly success-only, with a DNF secondary endpoint. (6) The bootstrap
algorithm is specified exactly, and (7) a whole-pipeline validation gate with
acceptance criteria and a fixed fallback must pass before confirmation.
(8) R's aggregation and weighting are frozen with sensitivities. Draft v1 is kept
as `scramble-luck-METHOD.v1.md`.
No post-registration amendments yet. Log date, rationale, outcomes already seen,
and whether each later amendment makes an analysis exploratory; never overwrite
this specification because a result looks more or less attractive.
