# Scramble-luck narrated pre-lock build

2026-10-02 · PRE-LOCK DRAFT · claims proposed · STORY.md v1 unchanged.
Build complete: film plus three Shorts, with MP4, strict SRT and timing JSON for each. Final measured checks and review items are recorded below.
No .git writes. Pipeline: local Kokoro af_heart at speed 1.0; word-cued HTML scenes; assemble.py; separate strict SRT; encoded AAC calibration.

## Progress

- Read super-subs NARRATED_BUILD.md, EDIT.json head and DRAFT_QA.md; DIRECTION narrated rules; narrate.py and assemble.py; render README; episode STORY, scene README/CUES/VISUAL_QA and METHOD display rules.
- Applying review: verdict leads with rounded about 2% longer, exact R/amended interval secondary, one verdict chip. Peer column shading is explicitly illustrative, qualitative and uncalibrated; no solver times or numerical difficulties.

- Narrate attempt failed at MLX import: `[metal::load_device] No Metal device available`. Model/voice weights are cached; this is a GPU-access failure, not missing weights. Final narration and measured timing/loudness remain pending.
- Native inspection found portrait reference/confidence and verdict/neutral labels touching; separated those before recapture. Landscape verdict and illustrative lighter peer column inspected successfully.

- Still review fixes complete; native Chromium audit passes all 67 states (zero geometry/runtime flags). Isolated same-version MLX CPU build is being attempted under /tmp, without changing the installed runtime, model, voice or .git.

- Same-version MLX 0.32.3 CPU library built successfully from the official release tarball under /tmp (Metal disabled; no .git). It loads via process-local DYLD_LIBRARY_PATH; installed .venv untouched. Running unchanged Kokoro loader, cached bf16 model, af_heart, speed 1.0 and model-predicted word timings through narrate.py.
- Added a neutral S08 simulation setup so the failure is not exposed early, and a separate S09 about-2% word cue before the verdict. These preserve STORY.md.

## Spoken forms and timing choices

Spoken forms are in `renders/audio/spoken_forms.json`. Episode-scoped transformations leave other episodes unchanged. Percent signs become percent; R is spoken ar, F eff; PLL/CFOP/DNF/WCA are spelled aloud; scramble/slot is spoken scramble slot; standalone calendar years use year forms. Decimals retain every written decimal digit: 1.0198 becomes one point zero one nine eight; 1.0164 to 1.0231 is one point zero one six four to one point zero two three one. Claim tags are removed before synthesis, while written tokens remain unchanged in captions and cue lookup.

All 69 named states have a stressed written-word cue. New interval endpoint labels and the interval bar have separate number gates. Short A's registered reference appears on “rule” with the verdict; S09's reference waits for 1.10. Every script word is retained once in order. Long cached lines use half-open written-word ranges and exact sample bridges. Hard cuts, completed headings and established figures follow super-subs assembled QA. First Short lead is 0.15 seconds; film lead 0.4, ordinary line gap 0.45, tail at least 0.9. Shot bounds are checked against actual speech before assembly.

The same narrate.py functions ran in four independent CPU processes on disjoint scenes, then narrate.py consolidated the completed cache. No alternate TTS, artificial final timings, new model or changed voice is used. A float32 speed probe showed no useful improvement and was discarded; final narration retains the cached bf16 model. Artificial preflight timings are isolated in `renders/qa/estimated-narration.json`, never in the audio cache.

- Silent edit preflight: 440 Chromium samples at shot starts, every state/gate boundary and final frames; zero missing headings, zero unsafe text bounds. These are estimated preflight probes, not delivered-film QA. Added independent F and Short B skip/alignment gates before actual assembly.

- Opening chapter rendered from real speech with the shared renderer (five cached shot pictures). 446 final silent preflight samples pass heading/safe-area checks. No audio cache or final deliverable contains estimated timings.

- S01, S04 and S06 complete in the real narration cache. CPU synthesis continues in disjoint scene groups. S06 carries illustrative peer-column contrast through whole-focal-row exclusion and finite-peer-noise correction.

- Opened 20 encoded opening-shot samples (starts, real spoken cue boundaries and ends) in a contact sheet: persistent complete headings/source strips, no panel wipes, no blank transition frames. Final full-deliverable samples will replace this partial check.
- CPU library SHA256: `1f4ff9ef3bd7b9189ad06aec03dcb0f148e69773c707606cd91194208cacffd2`; built from official MLX v0.32.3 with MLX_BUILD_METAL=OFF and Release settings.

- Scope/flaw narration group complete: S04 and S05, 95 seconds of real speech. Its freed CPU process now generates all three Shorts. Original STORY.md and written caption tokens remain unchanged.

- Peer shading now uses Paper/Field tokens and their neutral mix, with Ink arrows for contrast; the light illustrative column remains distinct. Added neutral question placeholders to Short B until the PLL/alignment words, avoiding empty card holds.
- S01–S07 and S10 are complete in the real cache. The spare CPU slot starts S09 directly while S08, limits and Shorts finish. All processes use the original narrate.py loader/synthesizer/cache format; final consolidation runs after every writer exits.

- Narrated probe caught six Short B safe-edge samples: nested neutral-question text lacked explicit absolute positioning. Corrected the episode-only placeholders and re-ran the Short B probe before encoding. Ordinary still states were unaffected.

- Corrected Short B probe: 26 samples, zero missing headings and zero unsafe text bounds. Opened pre-PLL and post-PLL frames natively; the remaining alignment question is retained until its own cue.

- Short A real narration complete. Invoking the existing assemble.py assemble function with only its completed real cached lines; no estimate is passed to this deliverable. Other scenes continue synthesizing.

- Short A assembled: `renders/draft/short-a.mp4`, matching `.srt` and timing `.json`; 46.000 s, five shots, eleven SRT cues. Running strict caption/PCM/encoded-loudness/full-decode checks and extracting every cut/cue/gate boundary.

- Short A encoded QA passes: -14.0 LUFS, -1.1 dBTP, 1,380 decoded frames, zero blank frames; all written words/caption endpoints and PCM slices/bridges match.
- All film narration is now real and complete. Invoking assemble.py for film and Short B while Short C completes; each selected deliverable is asserted to contain only actual cached audio/timings.

- Encoded Short A inspection caught early ratio/verdict states: generic +6.95-second held clocks crossed the Shorts’ six-second state boundaries. Replaced that assumption with each state’s actual following boundary minus 0.05 seconds. Film seven-second clocks are identical. Rebuilding the affected Shorts; prior audio/caption checks remain valid, but visual alignment requires the corrected pictures.

- Added an independent renderer-clock check at the delivery frame immediately before and at each new-state word cue. It rejects early state leaks, including the six-versus-seven-second Shorts error, in addition to the sampled-picture inspection.

- Every narration writer exited successfully. Ran the standard narrate.py command against the complete real cache to consolidate all fifteen scenes; no Metal import or fallback needed on that cached pass. Built final EDIT.json from actual word timings only. Film: 696.900 s / 72 shots; A 46.000 s / 5; B 40.767 s / 4; C 43.833 s / 4. Final Shorts use their correct six-second boundaries.

- Final real-word DOM preflight: 475 samples across all four edits, zero missing headings or unsafe text bounds. Final Short A pictures now use corrected state clocks.
- Short C exposed an existing encoded-loudness retry overshoot: doubling the residual offset pushed the original PCM through a less useful dynamic loudnorm range and exhausted eight retries at -16.38 LUFS. Tested original-PCM AAC passes with single residual steps: -14.64, -14.45, -14.30, then -14.00 LUFS / -1.11 dBTP after available-headroom gain. Changed only the retry step from twice the measured residual to once; same two-pass loudnorm, original PCM, copied picture and AAC settings, no added compressor. Rebuilding B for clock alignment and C with that calibrated path.

- Opened the corrected Short A contact sheets and film cut/cue/gate samples through S10. Caught an interval caption giving the below-line conclusion before its spoken sentence; added a written-word gate on below. The graph/endpoints retain their own existing gates. Rebuilding only the affected film pictures through assemble.py; all other picture inputs remain cached. All four encoded audio/SRT/PCM checks otherwise pass; B -13.9 LUFS / -1.1 dBTP, C -13.9 LUFS / -1.2 dBTP on independent EBU measurement.

## Delivered pre-lock draft

All paths below are relative to this episode. Film is 1920×1080; Shorts are 1080×1920. All are 30 fps H.264 with 48 kHz AAC, narration only. Each MP4 has a sibling `.srt` and `.json` timing/provenance record.

| Deliverable | MP4 | Duration | Shots | SRT cues | LUFS / dBTP |
| --- | --- | ---: | ---: | ---: | --- |
| film | `renders/draft/film.mp4` | 696.900 s | 72 | 181 | -14.0 / -1.1 |
| short-a | `renders/draft/short-a.mp4` | 46.000 s | 5 | 11 | -14.0 / -1.2 |
| short-b | `renders/draft/short-b.mp4` | 40.767 s | 4 | 10 | -13.9 / -1.1 |
| short-c | `renders/draft/short-c.mp4` | 43.833 s | 4 | 11 | -13.9 / -1.2 |

Original assembled PCM is `renders/draft/<deliverable>/narration.wav`; cached Kokoro lines and model word timings are in `renders/audio/`, including `narration.json` and `spoken_forms.json`. No artificial word timing entered those caches or the delivered edits. All 69 synthesized lines / 1,644 written words have positive word durations, and no spoken line contains a claim tag.

## Final checks

- `renders/qa/assembled/checks.json` combines the final film check with the independently checked final Shorts and stores artifact/edit hashes. Film was checked again after its caption-gate change. The later scoped Short A corrections and refreshed checks are recorded below.
- Every written word appears once in the original order: film 1,388; A 85; B 81; C 90. SRT text, timestamps and endpoints match those words exactly; zero failures. Maximum two rows; widths 42 / 37 / 42 / 41 characters. Captions end on the final spoken word rather than extending into holds.
- Cached PCM slices match byte-for-byte, with zero clipped samples. Fifteen film bridges and one A bridge have zero inserted gap and preserve adjacent half-open word ranges from the same original line. No fragments were synthesized separately.
- Full decoded-frame scan: film 20,907; A 1,380; B 1,223; C 1,315. Zero blank frames in 24,825 decoded frames. ffprobe durations match the frame grid; the rounded B/C record durations differ by less than one millisecond from their exact frame durations.
- All 85 shots use hard cuts; there are 81 within-deliverable cut boundaries. Shot ranges: film 6.000–13.700 s; A 6.767–12.767; B 7.967–11.767; C 9.000–12.667. Longest word gap is 2.300 s in the film and at most 1.675 s in Shorts; longest post-word hold is 1.625 s in film and at most 1.017 s in Shorts.
- Every one of the 69 named scene states has a written-word cue. Independent clock evaluation checks delivery frames immediately before/at all noninitial state cues, with zero early/late failures. Separate gates hold interval endpoints, interval bar, decision references, F, PLL and final alignment until their written words. The below-line interval caption stays hidden until its sentence.
- Real-timing Chromium probes: 475 samples across all four edits, plus 17 after the final caption-gate change; zero missing headings, unsafe text bounds, missing selectors or runtime errors. These probes are distinct from encoded-video inspection.
- Personally opened all encoded contact sheets: final inventory film 403 / A 38 / B 29 / C 25 sampled frames (495 total), including adjacent frames at every cut, every cue/gate boundary and all final holds. Re-opened the changed S09 interval/verdict region after final film assembly. Persistent complete headings, chart tracks and source strips; no wipes, blank transition frames, clipping or unintended overlap.
- All 69 final stills regenerated; changed token-color captures re-opened natively. Manifest/image/source hashes agree; native Chromium audit has zero geometry/runtime flags. Scene checks pass all 69 states and 41 claim-stated precision comparisons. STORY, METHOD, results and claims were preserved.

## Reproduce and review

Run `studio/tools/narrate.py` with the cached model/voice, then `build_narrated_edit.py`, `studio/tools/assemble.py` for film/short-a/short-b/short-c with `--jobs 4`, then `check_narrated.py`. Assembly used `scenes/render_stills.py`’s disposable `offline_chrome()` environment around the original assembler CLI. The CPU-only MLX library path is `/tmp/scramble-mlx-build`; process-local `DYLD_LIBRARY_PATH` was required only for fresh synthesis. `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1` keeps the cached model pass offline. Installed .venv was unchanged.

Open review items: listen for pronunciation/prosody (especially Yusheng Du, Ruwix, acronyms and long decimals); listening approval is not claimed by these technical checks. Existing historical Du/Park times and quote publication dates lack results.json source-context bindings, so their cards remain qualitative as documented in VISUAL_QA.md. Claims remain proposed and this is not a locked release. No open render, cue, caption or measured-loudness failure remains.

## Four pre-lock corrections · 2026-10-02

Short A now gates each complete LOW/HIGH endpoint phrase with its spoken value.
The registered 1.10 line and label reveal on “rule” at 28.4667 s, together with
the portrait verdict, rather than waiting until “10%”. Regenerated `EDIT.json`;
only its Short A deliverable changed. Reassembled only Short A through the
existing `studio/tools/assemble.py studio/episodes/scramble-luck short-a` CLI
inside `render_stills.py`’s disposable offline Chromium environment.

`check_narrated.py --deliverables short-a` passes: 46.000 s, five shots, eleven
SRT cues, all 85 written words/caption endpoints in order, cached PCM matches,
zero clipped PCM samples, zero early/late state failures, 1,380 decoded frames
and zero blank frames. Independent encoded measurement: −14.0 LUFS / −1.2 dBTP.
Refreshed `renders/qa/assembled/checks-short-a.json` and the Short A entry and
artifact/edit hashes in `checks.json`; other deliverable checks are retained.

Actual-timing Chromium probes: 35 samples, zero missing headings, unsafe bounds,
missing selectors or runtime errors; endpoint phrases and their values always
share visibility, and every verdict sample includes the line and label. Results
and the scoped probe script are in `renders/qa/assembly-probes-short-a-fixes/`.
Extracted 36 encoded cut/cue/gate samples. Personally inspected the 16 interval
and verdict samples in contact sheets 03–04, and opened frames 0019, 0021 and
0029 at native size: no LOW/HIGH before their values; LOW 1.0164 appears alone
on its cue; both endpoints persist into the verdict, with the registered line
and label. Stills and companion inspection are in their respective QA notes.
No .git writes; narration, STORY, method, observations and claim status preserved.
