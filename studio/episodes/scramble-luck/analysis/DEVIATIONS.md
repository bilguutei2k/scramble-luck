# Literal implementation decisions before confirmation times

METHOD.md is unchanged; no positive confirmation solve times have been read.

1. **Move metric.** “Fewest moves” does not specify quarter-turn or half-turn
   metric. Use the conventional face-turn/half-turn cross metric: all 18 U, U2,
   U′, etc. moves cost one. In the standard WCA scramble orientation, U/D are
   white/yellow. Both six-face and U/D minima are saved.
2. **Training competitions in the bootstrap.** The exact multinomial rule
   specifies confirmation competitions but also requires training-data refits.
   Draw confirmation competition multiplicities, then solver multiplicities
   over the union of training/confirmation solver IDs, then an independent
   size-Ctrain multinomial over pre-2019 exploration competitions. Solver
   multiplicities are shared between training and confirmation. This makes the
   otherwise unspecified training competition weights concrete.
3. **Simulation truth and numerical integration.** Define an oracle analogue
   of R using the same peer projection and original season-best selection with
   generated shared/tier/slot/replacement components in place of observed peer
   log times. Failure indicators and centering stay in the projection;
   execution noise is excluded from oracle peers. Sampling truth is
   exp(E[oracle log R]) across independent generated datasets on the fixed real
   structure. Except for the exact null R=1, the expectation has no supplied
   analytic formula, so integrate using 10,000 additional independent datasets
   per process (seeds disjoint from the 200 validation datasets). Report Monte
   Carlo SE, a 99.9% numerical-precision interval, and coverage's range over
   that interval. Treat this as numerical integration of a defined truth, not
   confirmation estimation. Slot shock and large-shared truth have the same
   distribution. Retain dataset-specific oracle truth and attribution error.

   **Implementation correction, before confirmation outcomes:** the initial
   run compared bootstrap intervals with each dataset's finite oracle, following
   validate.py's attribution-recovery example. During review this was corrected
   because METHOD explicitly calls these sampling intervals with changing
   exposure, rather than fixed-dataset replay intervals. At the correction,
   697 synthetic datasets were complete and early conservative null coverage
   had been seen; no confirmation times had been read. The correction changes
   the coverage target, not the estimator, bootstrap, simulations, acceptance
   bounds or fallback order. Existing point estimates, oracle values and
   intervals were retained; regenerated checks prove numerical equality. The
   finite-oracle comparison remains a diagnostic, not the primary gate target.
4. **Weighted tier support and medians.** Resampled copies weight medians, but
   cannot create distinct other finals or distinct informative peers. Require
   two different other competitions for a skill reference and three different
   informative solver IDs per tier. A solver appears once per included final;
   full focal-solver multiplicity is removed from its peers. The original
   structural seasonal roster is fixed.
5. **Tier position fit.** METHOD requires subtracting frozen β and then fitting
   pooled positions separately per tier with the frozen moment routine. Follow
   the algebraically equivalent collapsed calculation: fit positions to the raw
   centered data, since the second unconstrained zero-sum position fit absorbs
   the initial global β exactly. Independent verification checks this identity.
   Thus F is invariant to the initial nuisance change; stored tier positions
   are total fitted positions, rather than residual positions after subtracting
   frozen β. Seasonal R uses frozen β without a second position fit.
6. **Fallback rejection futility shortcut.** The initial exact pigeonhole gate
   completes all seven processes, each with 200 datasets and 500 draws. For a
   fallback, a completed 200-dataset process outside the fixed bias/coverage
   acceptance bounds is sufficient to reject that method: subsequent processes
   cannot make it pass the requirement to pass *every* process. Stop computing
   further processes for that rejected method, then try the next method in the
   unchanged fixed order. A fallback can be accepted only after completing all
   seven processes and passing all six judged processes. This saves computation
   without changing any possible acceptance decision. The shortcut was added
   after competition-only completed null and small-shared (small-shared coverage
   55.5%); some large-shared datasets were already checkpointed. Partial datasets
   are retained but do not decide acceptance. No confirmation outcomes were read.

## Step 4 implementation decisions (flagged; made before opening outcomes)

7. **Secondary logistic fixed effects.** Estimate the DNF model by exact
   conditional logistic likelihood, conditioning on each solver-round's DNF
   count. This eliminates its intercept without an incidental-parameter fit.
   Four attempt indicators and h/0.05 enter jointly; all-success/all-DNF panels
   contribute counts but no conditional likelihood. Recompute peer h and
   training beta in every product-weight draw; use percentile intervals.
8. **Cross correlation.** For every identified focal solver-round, use all five
   leave-one-out h values (including failure positions). Average h across
   focal solvers at each scheduled position, then correlate across scheduled
   scrambles. Report Pearson correlation both with raw cross length and with
   length demeaned within final, for six-face and white/yellow minima. Weight
   focal averages by solver multiplicity and scrambles by competition
   multiplicity in the bootstrap. The centered correlation is the preferred
   mechanism description because h is a within-final contrast.
9. **Subsets and deletion uncertainty.** Era and year-deletion checks use the
   full registered cluster draws with excluded competitions given zero weight;
   the original structural seasonal roster remains fixed. Reference candidates
   are limited by the same competition mask. Delete each confirmation solver
   in turn (also from training); report the entire point range with its counts.
   Report bootstrap intervals for the deletions attaining each endpoint, not
   a simultaneous interval for a data-selected range. No deletion changes the
   primary verdict. Complete-success sensitivity masks incomplete solver-rounds
   from time analysis, keeps the original seasonal roster, and reselects among
   its available complete panels. Clipping follows the frozen pilot: clip
   centered successful log times at ±0.6, then re-center through the engine.
10. **Prediction and auxiliary uncertainty.** Reuse the frozen pilot's
    whole-solver peer prediction, pre-2019 hyperparameters, other-success target
    baseline and thirty splits, at k=2,5,10,20. The fixed panel requires ≥22
    informative finalists for all k. Competition-only percentile intervals
    average splits first, as in the frozen pilot; split ranges and model
    extrapolations are labeled separately. All other estimable secondary
    statistics use the same 2,000 registered product-weight draws. Arithmetic
    and per-solver R get translated reselecting intervals as descriptive
    sensitivities; equal-tier R and its matched all-peer comparator do too.
    Negative control independently permutes all five time/status cells per
    solver-round in each of 1,000 draws, recomputing references, F and R with
    frozen primary beta. Its central 95% permutation range is not a sampling CI.

These choices resolve details METHOD does not specify. They are implementation
decisions, not new registered confirmatory endpoints; flag them in FINDINGS.
AMENDMENT-1 is a registered post-gate methodological amendment, not a silent
deviation. No primary point estimator, threshold or draw order changes here.

### Step 4 software correction after opening (flagged disclosure)

During the sensitivity block, a 2020 bootstrap draw had zero available
seasonal extrema. The wrapper incorrectly tried to average an empty array.
It now records an invalid yearly R draw and omits its zero weight from the
pooled year-specific-beta ratio. Original primary draws and completed valid
subset draws were retained unchanged; the remaining tasks resumed from their
checkpoints. No estimator, seed, primary interval, threshold or eligibility
rule changed. Sparse yearly checks are explicitly labelled diagnostic when
the registered coverage/valid-draw gates fail. Confirmation point estimates
and the primary interval had been seen at this correction.
