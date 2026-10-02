# Red-team review

All pilot findings below are exploratory. Code and saved outputs were reviewed without opening held-out outcomes. Scores judge episode potential after the stated revision, not evidential certainty. Novelty assessments are bounded by the supplied verification searches and targeted checks.

## S1 — REVISE — 4/5

**Did it test the claim?** Partly. The declared all-years 20% competition hash overrides the earlier verify slice; extraction filters before selecting outcomes. Independent check of all 148,890 exported attempts confirms membership. The balanced ANOVA estimates a shared within-round attempt component among complete successful five-solve panels, not the original official-2018 top-100 seasonal-extreme estimand or total scramble luck.

**Bugs, limitations, and checks**

- pilot.py:178–211 removes round means and decomposes solver-round, shared attempt and residual variation. Thus 1.86% is of modeled within-round log-time variation including between-finalist skill, not all population time variance. A shared attempt effect may also contain position-specific round conditions; it is not uniquely scramble causation.
- The model subtracts finite-peer residual noise from the variance estimate. Small finals make individual effects unreliable but do not by themselves explain away the small aggregate component. My check using the actual 1,656 split-final sizes predicts correlation 0.172 under this fitted model, close to observed 0.181; median half-panel sizes are 5 and 6 (scratch/redteam/S1-check.json). These are largely two expressions of the same signal-to-noise ratio, not independent evidence that luck is personal.
- Complete-case selection drops all five solves of any finalist with a nonpositive attempt; no joint DNF model, feature interactions, or skill-trend model from verify is fitted. Residual includes execution, measurement, solver-by-scramble interactions and model error; it cannot be labelled personal luck.
- Single regular group supplies scheduled mapping only. Extra pools occur in 1,992/1,996 mapped exploration finals; their presence does not prove replacements, but actual replacement use is unresolved. The verify requirement for audited mapping has not been met.
- Variance resampling correctly includes competition clusters and a separate competition/solver weighted sensitivity. Seasonal-extreme bootstrap reselects minima but freezes fitted peer effects and original eligible seasons; it omits nuisance-fit uncertainty and changes effective exposure. The nine proxy-cohort extremes are not a test of the specified >=100-extreme official cohort. Small adjusted rank shifts are shrinkage-dependent.
- Viewed 03-peer-replication.png: the low correlation is correctly displayed, but cannot carry a personal-luck conclusion. PILOT.md is an unfinished progress log; there is no pilot.json.

**Honest headline / viewer hook:** Exploratory: in 1,954 finals with 110,465 complete successful attempts, the fitted shared component was 1.86% of modeled log-time variance, or 3.85% after removing solver-round differences (two-way bootstrap interval 2.91–4.72%). Peer-adjusted seasonal bests changed by about 0.59% across 155 broadly eligible solver-seasons; that adjustment remains model-dependent.

**Episode verdict and novelty:** REVISE: a potentially distinctive episode about how little finalists agree on easy scrambles survives the supplied prior-work search; generic record luck and record reconstruction do not. The evidence points to a small average shared component plus noisy individual-scramble measurement—both. It does not establish “luck is personal, not in the scramble,” and the original record-counterfactual test is underpowered and incompletely implemented. The proxy ratio is 1.0112 (conditional interval 0.9945–1.0215; n=9), not a confirmed rejection of meaningful total luck.

**One next step:** Run one preregistered measurement-validation study with verified scramble assignments and much larger independent peer panels per scramble, reporting reliability versus peer count and out-of-sample prediction by solver method/skill. Simulate recovery of known common and interaction effects at the actual panel sizes first. Reliable prediction remaining weak with many peers would support a small shared component; method-specific prediction would identify personal scramble opportunities. Freeze that validated model before using the held-out competitions.

