# Scramble-luck visual QA — proposed pre-lock draft

Inspected all 69 final cue PNGs at their native delivery sizes: twelve
1920×1080 scenes and three 1080×1920 compositions. This is visual draft QA;
claims remain proposed and no observations have been locked.

## Inspection result

No open clipping, unintended overlap, unsafe-edge or native-size legibility
issues. Landscape labels stay at or above 24 px; portrait labels are at least
32 px. Sources persist throughout. Portraits have their own stacked layouts
inside x=72–920 and y=220–1500, leaving platform overlay space. Four dense
samples (peer exclusion, R interval, DNF interval, portrait R) were also
inspected at half size; the important labels and qualifiers remain readable.

The first inspection covered all 65 initial cue states. Added and changed
captures were opened at native size as the review fixes were made. On the
final refresh, 65 captures match the preceding inspection and four changed
color-token captures were re-opened at native size. `visual_qa.json` records every final
PNG hash and its inspection result. `../renders/stills/manifest.json` and the
individual `.png.json` sidecars record clocks, page/data hashes and dimensions.
All sidecars and image hashes agree with the delivered source files.

## Fixes verified in the final PNGs

- Opening question no longer exposes the later field comparison.
- Cross schematic leaves corners unsolved and separately pairs each side
  sticker with its matching center. CFOP cards have no empty stamp artifacts.
- Peer column cue includes the shared contrast; the whole focal row remains
  removed through the finite-peer-noise cue.
- R point estimate and amended interval now have separate narration cues.
  Endpoint labels and the decision-reference label clear the chart rules.
- Coverage cards, success/failure cards and the concluding permitted sentence
  clear their frames and source strips. Evidence links inherit Night colours.
- Portrait A follows narration order and keeps the complete seasonal scope.
  Portrait B names Max Park and retains PLL skip plus final alignment.

## Automated checks

`node scenes/check_scenes.mjs` passes all 69 states: fresh results/claims hashes,
exact builder regeneration, claim provenance, 41 claim-stated precision
comparisons, narration cue substrings, format dimensions, prohibited wording,
source-strip presence, missing-key refusal and forward/backward seek purity.
The tests also check full-row exclusion, failed-gate reveal order, R against
the registered line, and the DNF interval against its own neutral reference.

`node scenes/check_scenes.mjs --browser` was run through disposable offline
Chromium. `browser_qa.json` contains 69 cue checks, zero runtime errors and zero
geometry flags: text bounds, card bounds, safe edges, overlaps and minimum
font sizes. Graphical marks were assessed in the PNGs in addition to these
text checks. Shared render.mjs, system.css and system.js are unchanged; their
capture hashes are retained in the manifest. No .git writes were performed.

## Number and wording audit

Numerical observations are emitted through `SL.num()` with their results key
and claim IDs. Derived percentages, neutral reference, study-year range,
confidence level, scheduled-position count and DNF increment retain their
input keys and claim IDs in data.js. No analytical values are hand-typed.
Qualitative diagrams are explicitly schematic and contain no invented times,
numerical peer difficulties, replacement frequencies or stage durations. Claim tags,
lexical F2L, layout/timing constants and the required verbatim WCA notice are
not observations; the notice is copied from `results.source_notice` and marked
with its source key rather than assigned a fabricated claim.

“Shared scramble/slot component” is retained. The adjustment is described as
estimated adjusted time longer, with the successful seasonal population; it
is never equated with all luck. F remains a variance share, R a seasonal-best
ratio, and DNF a separate association. Failed original gate, registered
amendment, specified simulation pass and sensitivity keep separate roles.

## Open visual binding issue

Du’s historical time (SL-C104), Park’s historical time (SL-C105), and the quote
publication dates requested in STORY lack analysis/results.json bindings.
The historical cards therefore stay qualitative, and quote labels refer to
publication context in the linked originals. This is a visible departure from
the requested numeric historical cards/date labels, not a clipping issue.
Restoring those labels requires source-context bindings in results.json and
matching claim keys; no numbers were copied from claim-stated values. Results,
claims and narration were not edited. Still clocks remain design holds; the assembled edit now uses real narration-word cues, documented in NARRATED_BUILD.md.

## Capture inventory

| Page | Cue PNGs | Native size |
| --- | ---: | --- |
| s01-lucky-scramble.html | 5 | 1920×1080 |
| s02-the-basics.html | 5 | 1920×1080 |
| s03-the-obvious-answer.html | 4 | 1920×1080 |
| s04-the-flaw.html | 3 | 1920×1080 |
| s05-the-scope.html | 5 | 1920×1080 |
| s06-listen-to-the-peers.html | 5 | 1920×1080 |
| s07-the-seasonal-best.html | 4 | 1920×1080 |
| s08-the-failed-gate.html | 5 | 1920×1080 |
| s09-the-verdict.html | 5 | 1920×1080 |
| s10-the-checks.html | 5 | 1920×1080 |
| s11-what-remains-unknown.html | 5 | 1920×1080 |
| s12-the-takeaway.html | 4 | 1920×1080 |
| short-a.html | 6 | 1080×1920 |
| short-b.html | 4 | 1080×1920 |
| short-c.html | 4 | 1080×1920 |

## Narrated review fixes · 2026-10-02

Re-rendered S09, S06 and Short A cue PNGs. Opened the landscape and portrait verdicts and peer-column capture at native size. Both verdicts lead with claim-bound rounded ABOUT 2% LONGER; exact R = 1.0198 and amended 95% interval remain secondary, with one mint BELIEF FAILS chip. Fixed portrait legend and neutral-reference spacing during inspection. The later matrix cues shade the five peer columns qualitatively: B is visibly lighter, D darker. Labelled ILLUSTRATIVE · PEER-MEASURED CONTRAST; no solver times, calibrated difficulties or analytical observations are invented. Focal-row removal persists through noise correction. Native Chromium audit: all 69 states, zero geometry flags and zero runtime errors.

Narrated-film timing/transition QA is recorded in ../NARRATED_BUILD.md separately from this still review.

Added and inspected neutral simulation setup and separate about-2% state; latest native Chromium audit covers 69 states with zero geometry/runtime flags. Peer exclusion and finite-noise captures were opened individually; illustrative column shading persists while the focal row is removed.

Final refresh: regenerated all 69 cue PNGs from the final source. The four color-token changes (S06 columns/exclude/noise and Short B peers) were re-opened at native size; all remaining PNG hashes match the previous inspections. Updated visual_qa.json and the full still manifest. Final native Chromium audit again reports 69 states, zero geometry flags and zero runtime errors.

## Four pre-lock corrections · 2026-10-02

Re-rendered only the six Short A stills with `render_stills.py --pages short-a.html`.
Opened the interval and verdict PNGs at 1080×1920. Portrait LOW/HIGH labels
now share their numeric reveal gates; no empty endpoint labels remain. The
registered 1.10 rule and its label appear together on “rule”, coincident with
the portrait verdict cue, and remain visible throughout that state. The
landscape S09 composition and its edit remain unchanged.

The existing native Chromium audit was restricted to Short A: six states,
zero geometry flags and zero runtime errors (`browser_qa_short_a_fixes.json`).
Actual-timing probes checked 35 Short A samples, including adjacent delivery
frames at endpoint/reference gates: zero missing headings, unsafe bounds,
missing selectors, runtime errors, orphan endpoint labels or verdict states
without the registered reference. `visual_qa.json` records the refreshed Short A
hashes and this scoped inspection; previous other-scene inspections are retained.
Encoded-frame inspection is recorded in `../NARRATED_BUILD.md`.
