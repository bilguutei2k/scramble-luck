# How much of a record-speed Rubik’s Cube solve is the shared scramble? — reviews

## Review 1 — 2026-10-02, Astra (Codex): confirmatory methods review

Full review: [reviews/astra-methods-1.md](reviews/astra-methods-1.md).
Numerical evidence: [reviews/astra-methods-1-checks.json](reviews/astra-methods-1-checks.json).
Verdict: **approve with changes**. No blocking issue was found in the amended
primary result: **Belief fails**, R=1.0197788256, 95% amended interval
[1.0163698055, 1.0230705471]. All 3,313 raw-centisecond seasonal selections and
their independently reconstructed aggregate R agree exactly. Astra did not edit analysis code during the review. The required changes below
were applied in the dated fixes note under this section; the primary result is unchanged.

| # | Point | Disposition |
|---|---|---|
| 1 | The original failed gate, amendment investigation and owner-approved registration precede the recorded confirmation analysis. Source, split, code and artifact hashes match; the filter is competition start-year 2019–2025. | Verified. Retain the original gate failure and amended-contract qualification. |
| 2 | Mapping, success-only estimation, tier moments, focal-copy exclusion, seasonal selection, equal-person-year R, product weights and mean-centered amended interval match the contract. | Verified. No primary-verdict blocker. |
| 3 | Cross r=0.265802 has raw percentiles [0.197515, 0.228729] because peer resampling inflates contrast noise, not because seasonal minima are reselected. No full multiway cross CI has been validated. | Done. All four ranges are labelled unvalidated bootstrap diagnostics beside the numbers in FINDINGS and claims, with machine-readable coverage flags; calibrated cross inference is inconclusive. Points and n are retained. |
| 4 | METHOD's explicit 2019–2025 ±2-year reference definition supports the blind full-window era reading more directly. Restricting references to each era produces the eight disclosed discrepancies. | Done. Full-window era F and γ/D, counts and their own same-draw intervals reproduce the blind points and counts, beside the retained within-era sensitivity. METHOD supports the full-window reading more directly; all-peer R is unchanged. |
| 5 | The main pipeline's 15:17:40 “FIRST OPEN” is later than the blind recheck's extraction by 15:11:57; both follow amendment registration at 15:07:31. Decisions 7–10 first appear in git with confirmation results, despite reported pre-opening timing. | Done. Main-pipeline and blind-recheck timestamps are scoped separately, with the local-metadata qualification. Decisions 7–10 are disclosed as reported pre-opening but first committed with confirmation results, including in RECHECK.md. |
| 6 | Gumbel top-k informative-DNF sampling is sequential weighted sampling without replacement, not exact conditional-logistic subset odds when multiple DNFs occur. | Done. Simulation descriptions now specify Gumbel top-k/sequential weighted sampling without replacement, preserving DNF counts and DNS positions; numerical gate results are unchanged. |
| 7 | Failed-gate fallbacks stop after a completed failing process; training solver-union draws, nuisance-fit collapse and secondary implementation choices are disclosed. Empty yearly draws were repaired after opening. | Accepted with the qualifications in the full review. None changes the observed primary verdict; the original gate and amendment history must remain visible. |
| 8 | FINDINGS reports success conditioning, slot confounding, tier attrition, uncertain DNF association, sparse-year gates, weak prediction, replacement limitations and contrary cross diagnostics. | Done. Item-3 labels are applied beside every cross range; all contrary checks and limitations are retained. |
| 9 | Registration QA is partly hard-coded, and checkpoint reuse does not enforce input/code fingerprints. | Nonblocking for this run: chronology, hashes and primary calculations were independently checked. Harden before future reuse. |

### Fixes applied — 2026-10-02

- **Item 3 — done:** all four cross points and n are retained; each range is an unvalidated bootstrap diagnostic in FINDINGS, results.json and SL-C077–080, with coverage-validation flags false and inferential uncertainty inconclusive. No interval recentering or calibrated geometry claim was introduced.
- **Item 4 — done:** full-window ±2-year reference era F and γ/D reproduce the blind values and counts (1,375/68,127 and 3,045/166,398). Their own percentile intervals use all 2,000 original registered draws, with full-window references recomputed before masking era outcome panels. Within-era F and γ/D remain beside them as a separate sensitivity; SL-C037–038 include both readings. Year-deletion/yearly reference scopes are explicit.
- **Item 5 — done:** 15:17:40.383923 UTC denotes the main pipeline first magnitude SELECT; the blind recheck had extracted magnitudes by 15:11:57 UTC, corroborated by local cache metadata rather than an exact first-access audit. Both follow amendment registration at 15:07:31 UTC. Decisions 7–10 were reported pre-opening but first committed together with confirmation results in e8880f3 at 15:36:01 UTC; FINDINGS, DEVIATIONS, PROGRESS, results/QA and RECHECK now disclose the distinction.
- **Item 6 — done:** informative-DNF descriptions specify sequential weighted sampling without replacement via Gumbel top-k, weights exp(12 × shared effect) renormalized over remaining started slots, preserving each solver-final DNF count and DNS positions. Multi-DNF subsets are not exact conditional-logistic subset odds. Gate outcomes are unchanged; SL-C098 is updated.
- **Item 8 follow-up — done:** diagnostic cross uncertainty is qualified beside the numbers and all contrary evidence is retained.

`analysis/verify_claims.py` passed **148/148 proposed claims**, with **921 value/reporting checks** and **zero failures**; `qa.json` now records this evidence and all **29/29 named checks pass**. All claim statuses remain `proposed`. METHOD.md, the primary estimand, primary point/intervals and **Belief fails** verdict are unchanged. No .git writes were attempted.
