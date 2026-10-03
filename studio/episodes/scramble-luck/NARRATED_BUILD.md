# About 2% Longer — final locked narrated build

2026-10-03 · locked · channel owner approved the script and all claims for publication.
All 148 claims use `verified`, with dated owner approval; 921/921 independent
value checks pass. `story_check` reports `Lint: passed`, with no problems or warnings.
No .git writes; Claude owns the commit.

## Delivered files and measurements

| Deliverable | Final output | Duration | Shots | SRT cues | LUFS | dBTP | Decoded frames |
|---|---|---:|---:|---:|---:|---:|---:|
| film | `renders/final/film.mp4` (+ `.srt`, `.json`) | 696.900 s | 72 | 181 | -14.0 | -1.1 | 20,907 |
| short-a | `renders/final/short-a.mp4` (+ `.srt`, `.json`) | 46.000 s | 5 | 11 | -14.0 | -1.2 | 1,380 |
| short-b | `renders/final/short-b.mp4` (+ `.srt`, `.json`) | 40.767 s | 4 | 10 | -13.9 | -1.1 | 1,223 |
| short-c | `renders/final/short-c.mp4` (+ `.srt`, `.json`) | 43.833 s | 4 | 11 | -13.9 | -1.2 | 1,315 |

Film: 1920×1080. Shorts: 1080×1920. All H.264/AAC, 30 fps, strict separate SRT
captions and timing/provenance JSON. `EDIT.json` and final timing records are locked.

## Narration preservation

Reused all 67 cached WAVs from `renders/audio/`; no synthesis, voice, speed,
spoken form, word timing or narration line changed. Voice remains local Kokoro
`af_heart`, speed 1.0. Parsed narration before/after the title/status edit is
identical. Only the narration manifest's STORY hash was rebound after that proof.
Audio hashes and that invariant are recorded in
`renders/qa/final-probes/audio-preservation.json` and `lock-review.json`.

## Final QA

- `analysis/verify_claims.py`: 148/148 claims, 921/921 values pass. Analytical
  claim content and frozen results unchanged; only status and approval were added.
- Scenes: 69 cue states, 41 precision checks pass; native Chromium has zero
  geometry flags and runtime errors. Rebuilt and inspected all 69 stills in eight
  contact sheets, with both verdicts reopened at native size. No visible lock-state
  marker remains; illustrative, schematic and unvalidated-diagnostic labels remain.
- Actual-timing preflight: 802 samples, zero missing headings,
  unsafe bounds or runtime errors, with lock-marker assertions on visible text.
- `check_narrated.py` with the final render and QA directories
  passes all four delivered MP4s: measured AAC loudness within −14 ±0.2 LUFS,
  true peak ≤−1 dBTP; exact durations, ordered caption words/endpoints and cached
  PCM slices/bridges match; zero clipped PCM samples or early/late state failures.
- All 24,825 delivery frames decode;
  zero corrupt or blank frames. Extracted 771
  decoded samples at shot starts/ends, word-cue anchors and reveal gates, including
  the frame before/at/after boundaries. Contact sheets inspected for all four outputs:
  complete headings, persistent sources, clean hard cuts, no early reveals or markers.
- Short A keeps the complete endpoint phrases on their number cues; registered
  line/label and verdict reveal together at 28.4667 s on “rule”.
- Companion: 56/56 browser states pass at 390×844 and 1440×1000, both themes;
  exact title/h1/subtitle, no lock-state labels, overflow, missing fonts, network
  requests or browser errors. `companion/QA.md` records bindings and captures.

Evidence: `renders/qa/final-assembled/checks.json`, `final-probes/samples.json`,
`final-decoded/manifest.json`, `locked-stills/`, `scenes/browser_qa.json`,
`scenes/visual_qa.json`, `renders/stills/manifest.json`, companion browser audit.
Source grep finds no static labels in scene HTML, CUES/data or the generated
companion page; remaining source strings are conditional unlocked-state fallbacks
or marker-leak assertions. No label is emitted by the locked build.

## Rebuild

Reuse `renders/audio/narration.json`; run `scenes/build_data.py`, scene checks,
`scenes/render_stills.py`, `build_narrated_edit.py`, then
`python3 studio/tools/assemble.py studio/episodes/scramble-luck --jobs 4 --out-dir studio/episodes/scramble-luck/renders/final`
inside `render_stills.py`'s disposable `offline_chrome()` environment. The assembler
now accepts `--out-dir`; existing invocations retain their default output directory.
Run `python3 studio/episodes/scramble-luck/check_narrated.py --render-dir studio/episodes/scramble-luck/renders/final --qa-dir studio/episodes/scramble-luck/renders/qa/final-assembled`.
Claim verification uses `ideation/.venv/bin/python studio/episodes/scramble-luck/analysis/verify_claims.py`.
Rebuild the companion with `companion/build.py` and run its browser sweep.

No open render, caption, cue, measured-audio or browser QA issue remains.
Optional editorial listening for pronunciation/prosody is not claimed by automated
QA. Historical Du/Park times and quote dates remain qualitative because their
results.json bindings are absent; unvalidated cross inference and unaudited
replacement assignments remain disclosed. Publication/commit are handed to Claude.
