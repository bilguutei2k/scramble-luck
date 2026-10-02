# Frozen specification ready for METHOD.md

This is a revised measurement-validation design. The original official-2018 top-100 test is not replicated. Commit a reviewed METHOD.md before opening confirmation outcomes. Source hashes and exact coefficients are in `frozen-model.json`.

## Id

S1-r5-measurement-v1

## Status

ready for preregistration; not yet committed METHOD.md

## Confirmation

All competitions with sha256 UTF-8 ID integer modulo 5 != 0; 2019–2025; no outcomes inspected in this study.

## Slice Id Sha256

b5f6426bffbbf01c4d742cbe65f083cb4cbb5a134a5b60c3fe9fa312d028b7a4

## Training

Pre-2019 mapped finals only in the locked exploration slice; no confirmation outcomes used.

## Skill Training

Within-final solver intercepts cancel; skill-tier reference is median log mean of >=2 other eligible finals within +/-2 years, excluding focal competition.

## Eligibility

333, round_types.final=1, format a; one non-extra group; exactly five nonmissing regular scramble rows numbered 1–5; five recorded attempt slots 1–5; retain all statuses. For outcome contrasts need >=2 successful cells per solver; singleton/all-failure panels remain in counts and binary failure analysis.

## Time Model

log(value/100)=solver-round intercept + frozen global position + shared round-position contrast + independent residual. Demean within available successful cells. Shared Gaussian prior is used only for displayed individual predictions; moments allow non-Gaussian residuals with finite variance.

## Moment Equations

C_i=diag(valid)-valid valid^T/m_i; A_r=sum_i C_i; V_r=sum_i C_i(y_i-beta). S_r=sum_i ||C_i(y_i-beta)||²; d_r=sum_i(m_i-1). tau=(sum ||V_r||²-sum S_r)/(sum tr(A_r²)-sum d_r); e=sum S_r/sum d_r-tau. Weighted solver bootstraps replace residual noise trace by A(w²).

## Predictive Validation

Predetermine k=2,5,10,20; 30 random whole-solver splits per final, >=k+2 informative solvers. Peer posterior solve (A_peer+e/tau I)^-1 V_peer. Predict target scramble time relative to mean of target solver OTHER successful attempts; target solve is never used in its baseline. Report R² and competition CI. k=2..max and extrapolations descriptive.

## Primary Endpoint

Geometric mean estimated median-shared-effect / observed fastest valid time ratio for all eligible solver-seasons with >=5 eligible finals in confirmation, 2019–2025; leave out focal solver; unshrunk pseudoinverse peer contrasts; fixed zero/median symmetric shared-effect counterfactual.

## Primary Rule

Material shared scheduled-position advantage passes iff ratio >1.10 and two-way competition/solver bootstrap 95% lower bound >1.00. Otherwise fails; inconclusive if interval spans both 1.00 and 1.10. >=500 eligible finals, >=20,000 attempt rows, >=100 eligible extrema. This is a revised all-finalist estimand, not the verified official-top100 test.

## Uncertainty

2,000 competition+solver draws; refit position/training moments on resampled pre-2019 exploration training finals; recompute leave-one-out effects and reselect minima in target competition resamples. Original eligible-season list fixed; report changing exposure separately. Individual Gaussian intervals omit mapping error and selection conditioning.

## Dnf

Separate started-attempt binary covariance/risk endpoint, DNS separately. Successful-time estimand conditional on success. Report informative-DNF simulation and complete-case/clipped-log sensitivity; no unidentified latent DNF times.

## Tier Secondary

Faster/slower half by other-final skill reference; >=3 informative peers per tier. Separate tier shared variances/residual variances and cross covariance; interaction=(bFast+bSlow-2cov)/4. Signed moments and crossed bootstrap CI; constrain display only. No method claim. Tier test secondary, not proof of personal luck.

## Mapping Gate

Actual scramble claim requires independent per-attempt assignment/replacement audit, including extrema. Without audit, preregister a scheduled-position claim only, explicitly including synchronized round conditions and unknown replacement dilution. Do not treat absent extra pool as verified no replacement.

## Robustness

Repeat full DNF-retaining model, complete-case sensitivity, log-contrast clipping +/-0.6, periods 2019–2022 and 2023–2025 and leave-year-out. Report all results regardless of sign; no alternate specification rescue. Independent per-solver within-round label permutation is a signal-negative-control; common permutation of whole scramble labels is invariant and is not a valid placebo.

## Personal Luck

Unexplained remainder includes execution, solver-by-scramble opportunities, missing skill, penalties and assignment errors. It is not identified personal luck.

## Selection Caution

Shrinkage posterior means conditional only on peers are biased for aggregate extrema selected using focal times. Unshrunk aggregates validated under independent-noise simulations; individual displays remain shrunk and labelled.

## Frozen numerical parameters

```json
{
  "shared_variance": 0.0007830105490928417,
  "residual_variance": 0.021684974210191423,
  "within_solver_share": 0.03485005698026765,
  "shared_log_sd": 0.027982325655542675,
  "position": [
    -0.00019098085080805892,
    0.0015330545917410243,
    -0.00016398101357186266,
    -0.005728817307245912,
    0.0045507245798848085
  ]
}
```
