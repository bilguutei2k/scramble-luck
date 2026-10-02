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
