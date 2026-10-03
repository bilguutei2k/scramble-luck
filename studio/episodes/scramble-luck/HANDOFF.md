# Scramble luck — handoff

Updated 2026-10-02, late evening, by Claude. Branch `next-investigations`
(local only; nothing pushed).

## State

| Layer | Status | Evidence |
|---|---|---|
| Idea search and pilot | done | `../../../ideation/` (SLATE.md, rounds r1–r6) |
| METHOD.md v2 | approved by the owner after an external review; committed before any confirmation data | `8a474d3` |
| Pre-confirmation gate | **failed** (bootstrap mis-covered; a false "fails" 96.5% of the time at R = 1.10) | `3eca079`, `analysis/GATE.md` |
| Amendment 1 (re-centred R interval) | investigated outcome-blind, owner-approved, registered before confirmation | `0eb88d1`, `5496074` |
| Confirmation analysis | **belief fails**: R = 1.0198 [1.0164, 1.0231]; F = 4.74% [3.92, 5.67]; QA 29/29 | `e8880f3`, `analysis/FINDINGS.md` |
| Blind re-derivation (Astra) | 55 values matched; 8 era-split differences explained by a reference-window reading | `recheck/RECHECK.md` |
| Methods review (Astra) | approve with changes; all required changes applied | `analysis/review.md`, `4c3fd03` |
| Claims | 148 proposed, 921 checks pass `verify_claims.py` | `CLAIMS.json`, `analysis/claims_check.json` |
| Script | v1 (Sol), 12 scenes, 9:15 narration, three shorts; v0 (local Qwen) kept | `STORY.md`, `4c3fd03` |
| Scenes | proposed, 67 cue stills, visual QA | `scenes/`, `e54116b` |
| Narrated draft | film 11:37, shorts 46 s, 41 s, 44 s; local Kokoro voice | `NARRATED_BUILD.md`, `7565ae9`; renders local |
| Companion page | pre-lock draft, 14 precomputed checks, browser QA passed | `companion/`, `6bd57ab` |

## Waiting on the owner

1. Sign-off on STORY.md v1 and the claims; then mark all claims `verified`
   (story_check then passes without warnings).
2. The video title and the on-screen verdict wording ("ABOUT 2% LONGER" today).
3. A listening review of the Kokoro narration.

## Open, not blocking

- The cross-length correlation (r = 0.266) has no validated interval; it is
  shown only as a labelled diagnostic.
- Replacement-scramble use is unaudited; results are scheduled-position.
- Historical record cards stay qualitative until bound to claims.
- Polish pass (Short A label timing, vertical 1.10 line, companion labels)
  launched 2026-10-02 23:36; check `ideation/logs/ep-s7-polish.last.md`.
- Shared tool change: `studio/tools/assemble.py` loudness retry (`f41f856`)
  affects every episode's future renders.

## Next after sign-off

Lock claims → re-run `story_check` → final narration listening fixes →
final renders → publish the companion page → push the branch for the
public repository (`studio/tools/public_repo.sh`), which needs the owner's go.
