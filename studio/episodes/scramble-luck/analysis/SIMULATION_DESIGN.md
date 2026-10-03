# Outcome-blind simulation design

This document describes the generator used by gate.py, not measured confirmation
effects. Real solver IDs, competition IDs, years, final incidence, panel sizes,
the structural ≥5-final person-year roster, and categorical attempt statuses
are retained. No confirmation time magnitude enters the simulations.

- Each solver receives baseline log skill Normal(log(12), 0.30²), shared across
  that solver's appearances and training data. Independent solver-final
  intercept fluctuations have SD 0.04. The actual frozen five-position β is
  added to generated times.
- Within each final the true interaction tier is determined by baseline skill
  below the panel median. Independent execution variance is 0.018 in the fast
  tier and 0.026 in the slow tier. This tests unequal residual variances.
- Five common effects are independent zero-mean normal draws, then centered
  across the five positions. Null variance is zero. Small shared variance is
  0.0014; large shared variance is 0.0121. These scales were set using time-free
  synthetic calibration outside the gate's replicate seeds to approximate
  oracle seasonal R=1.016 and R=1.12 on the real incidence structure.
- The interaction process adds a centered five-position interaction with
  variance 0.0025, with opposite signs in the two true tiers. Skill references
  and estimated tiers are nevertheless recomputed from other generated finals,
  exactly as they will be for measurement.
- All processes except informative DNF keep the actual success/DNF/DNS masks,
  independently of synthetic effects and execution; this is the empirical-mask
  MCAR stress. Single-success and all-failure solver panels remain present.
- Informative DNF preserves each solver-final's real DNF count and DNS
  positions. It selects DNF positions among started slots by sequential weighted sampling
  without replacement, with weights exp(12 × generated shared effect)
  renormalized over remaining slots at each selection. Independent Gumbel scores
  plus log weights implement the equivalent top-k ranking. For multiple DNFs,
  subset probabilities are not exact conditional-logistic subset odds. Thus harder scheduled slots raise DNF probability. Execution
  errors do not enter this missingness mechanism. This is one specified
  informative mechanism, not a worst-case bound on all informative failures.
- Random replacements independently replace 10% of solver-attempt common
  components by independent Normal(0, 0.0014) draws. Actual generated replacement
  components enter oracle peers. Replacement flags are independent of times,
  solver skill, statuses and which attempts later become extrema.
- Pure slot shock has shared variance 0.0121 and zero scramble effect. The same
  estimator necessarily absorbs a synchronized slot shock; this is reported
  rather than judged, exactly as METHOD requests.
- Synthetic pre-2019 exploration training follows the frozen common/residual
  variances 0.0007830105490928417 and 0.021684974210191423. Its real exploration
  status masks are retained. Solver skills are shared with confirmation where
  the IDs overlap. Training position/moment refits use the resampled training
  competitions and the same solver multiplicities as confirmation.

Every process has 200 independent datasets. Every dataset receives 500
bootstrap draws, with the exact competition→solver draw order and seed
20261001. Common datasets and common random draws are reused across the fixed
fallback methods; only the retained cluster dimensions change. This aids
comparisons without selecting methods using confirmation outcomes.

The finite oracle is the original selected-extremum, peer-projected latent
shared component, with the same success mask and leave-one-solver-out operator.
It includes the observed peer mix's tier interaction or scheduled-position
replacement dilution, just as the frozen all-peer endpoint does. Sampling
truth is exp(E[finite oracle log R]) over the specified process. Integrate that
expectation with 10,000 additional independent datasets for each non-null,
distinct process, using replicate seeds ≥100000, disjoint from validation and
calibration. The null has exactly R=1. Pure slot shock has the same distribution
as large shared, so they share integrated truth.

Report integration SE, its 99.9% Monte Carlo precision interval, and the range
of interval coverage over that precision interval. The original finite-oracle
attribution check is retained separately. See DEVIATIONS.md for the initial
coverage-target implementation correction and its timing. No gate threshold,
simulation dataset, estimator or fallback order changed.
