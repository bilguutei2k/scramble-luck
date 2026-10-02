# How much of a record-speed Rubik’s Cube solve is the shared scramble? — reviews

## Review 1 — 2026-10-02, Astra (Codex): confirmatory methods review

Full review: [reviews/astra-methods-1.md](reviews/astra-methods-1.md).
Numerical evidence: [reviews/astra-methods-1-checks.json](reviews/astra-methods-1-checks.json).
Verdict: **approve with changes**. No blocking issue was found in the amended
primary result: **Belief fails**, R=1.0197788256, 95% amended interval
[1.0163698055, 1.0230705471]. All 3,313 raw-centisecond seasonal selections and
their independently reconstructed aggregate R agree exactly. Analysis code was
not edited. Required changes below remain pending; this review does not imply
that the owner has accepted or implemented them.

| # | Point | Disposition |
|---|---|---|
| 1 | The original failed gate, amendment investigation and owner-approved registration precede the recorded confirmation analysis. Source, split, code and artifact hashes match; the filter is competition start-year 2019–2025. | Verified. Retain the original gate failure and amended-contract qualification. |
| 2 | Mapping, success-only estimation, tier moments, focal-copy exclusion, seasonal selection, equal-person-year R, product weights and mean-centered amended interval match the contract. | Verified. No primary-verdict blocker. |
| 3 | Cross r=0.265802 has raw percentiles [0.197515, 0.228729] because peer resampling inflates contrast noise, not because seasonal minima are reselected. No full multiway cross CI has been validated. | Required; pending. Label all four ranges as unvalidated bootstrap diagnostics directly beside the numbers and in machine-readable status. Withhold calibrated inference, or validate a new interval as post-confirmation secondary work. Recentered [0.250146, 0.281360] is only an unvalidated candidate. |
| 4 | METHOD's explicit 2019–2025 ±2-year reference definition supports the blind full-window era reading more directly. Restricting references to each era produces the eight disclosed discrepancies. | Required; pending. Add full-window era F/gamma results, counts and same-draw intervals; retain the existing restricted-reference results as a separate sensitivity. Neither reading affects all-peer R. |
| 5 | The main pipeline's 15:17:40 “FIRST OPEN” is later than the blind recheck's extraction by 15:11:57; both follow amendment registration at 15:07:31. Decisions 7–10 first appear in git with confirmation results, despite reported pre-opening timing. | Required; pending. Scope the timestamp to the main pipeline and distinguish reported pre-open decisions from committed registration, including in RECHECK.md. Actual ordering remains supported. |
| 6 | Gumbel top-k informative-DNF sampling is sequential weighted sampling without replacement, not exact conditional-logistic subset odds when multiple DNFs occur. | Required; pending. Correct the simulation description. The monotone difficulty stress and its empirical gate results remain intact. |
| 7 | Failed-gate fallbacks stop after a completed failing process; training solver-union draws, nuisance-fit collapse and secondary implementation choices are disclosed. Empty yearly draws were repaired after opening. | Accepted with the qualifications in the full review. None changes the observed primary verdict; the original gate and amendment history must remain visible. |
| 8 | FINDINGS reports success conditioning, slot confounding, tier attrition, uncertain DNF association, sparse-year gates, weak prediction, replacement limitations and contrary cross diagnostics. | Substantially compliant. Apply item 3 so diagnostic cross ranges cannot be mistaken for established 95% limits; retain all contrary checks. |
| 9 | Registration QA is partly hard-coded, and checkpoint reuse does not enforce input/code fingerprints. | Nonblocking for this run: chronology, hashes and primary calculations were independently checked. Harden before future reuse. |
