# About 2% Longer — locked publication handoff

Updated 2026-10-03. Channel owner approved the episode, script and all claims
for publication on 2026-10-03. Working title: **About 2% Longer**.
Final locked build complete. No .git writes; Claude commits.

## State

| Layer | Final state | Evidence |
|---|---|---|
| Method / Amendment 1 | owner-approved, registered before confirmation | METHOD.md; analysis/amendment/ |
| Confirmation | belief fails; R 1.0198 [1.0164, 1.0231]; F 4.74% [3.92, 5.67] | analysis/FINDINGS.md |
| Independent claims | 148 verified, owner approval dated 2026-10-03; 921 checks pass | CLAIMS.json; analysis/claims_check.json |
| Script | locked, owner-approved 2026-10-03; narration unchanged; story_check no problems | STORY.md; renders/qa/final-probes/story-check.txt |
| Scenes | 69 rebuilt/inspected stills; zero Chromium geometry/runtime flags; no visible lock markers | scenes/VISUAL_QA.md; renders/stills/ |
| Film and Shorts | four final MP4s, captions and timing records; delivered QA passes | NARRATED_BUILD.md; renders/qa/final-assembled/checks.json |
| Companion | locked title/subtitle; 70 numeric bindings; 56/56 browser states pass | companion/index.html; renders/companion/page.html; companion/QA.md |

## Final outputs

| Deliverable | Final output | Duration | Shots | SRT cues | LUFS | dBTP | Decoded frames |
|---|---|---:|---:|---:|---:|---:|---:|
| film | `renders/final/film.mp4` (+ `.srt`, `.json`) | 696.900 s | 72 | 181 | -14.0 | -1.1 | 20,907 |
| short-a | `renders/final/short-a.mp4` (+ `.srt`, `.json`) | 46.000 s | 5 | 11 | -14.0 | -1.2 | 1,380 |
| short-b | `renders/final/short-b.mp4` (+ `.srt`, `.json`) | 40.767 s | 4 | 10 | -13.9 | -1.1 | 1,223 |
| short-c | `renders/final/short-c.mp4` (+ `.srt`, `.json`) | 43.833 s | 4 | 11 | -13.9 | -1.2 | 1,315 |

Durations/loudness are measured from final encoded files. All delivery frames
fully decode, without blank/corrupt frames. Exact timing, cue alignment, strict
captions, transitions and cached-PCM preservation pass. Narration audio is reused
unchanged. `NARRATED_BUILD.md` records the checks and reproducible commands.
Companion captures and audit are in `renders/companion/`; all widths/themes pass.

## Open, nonblocking

- Optional editorial listening for pronunciation/prosody; technical audio QA
  passes, and the authorized build preserves the approved narration audio.
- Cross-length correlation remains an expressly unvalidated diagnostic.
- Replacement assignments remain unaudited; results are scheduled-position.
- Historical record cards remain qualitative: results.json lacks historical
  Du/Park time and quote-date source-context bindings.
- Future analytical reuse needs checkpoint fingerprint hardening, as recorded
  in the methods review. These evidence limits stay visible in the final assets.

## Publication handoff

Final assets are ready. Claude owns the commit and publication steps. No branch
push, upload or companion publication was performed as part of this build.
Shared tool change: assemble.py accepts an optional `--out-dir`; current final
assembly uses `renders/final/`. No open rendering or browser-check failure remains.
