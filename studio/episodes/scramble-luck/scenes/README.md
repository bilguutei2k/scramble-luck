# Scramble-luck proposed visual draft

Twelve landscape STORY scenes and three separately composed portrait shorts,
with 67 cue states and matching PNGs in `../renders/stills/`.
All claims remain proposed. Cue clocks are designed reveals and holds, not
locked narration timing. No analytical numbers are typed into scene HTML/JS.
`build_data.py` reads results.json for observations and CLAIMS.json for IDs/keys;
`SL.num()` records claim IDs and full input keys on each numeric label. The
results and claims hashes accompany data and captures. No .git writes.

The historical Du/Park times and quote publication dates are absent from
results.json. Those cards remain qualitative; their requested numeric labels
are an open binding gap. The builder never reads stated values from claims.
Quotes retain exact publication wording and adjacent clickable source labels.
S12 carries the complete required WCA notice from results.json.

New episode components, recorded before renderer use (also in DIRECTION.md):

- **Finalist × scheduled-position matrix.** Five columns extend the dot/slope
  grammar beyond the small-table cap. Orange focal row, grey peers, Ink rules,
  Plex labels. Cells show qualitative up/down/level marks, never invented
  times or calibrated difficulty. Row-centering, column-reading and full-row
  exclusion are distinct cue states. Hollow replacement cell is separately
  tagged as illustrative, without an audited assignment claim.
- **Seasonal-best adjustment strip.** Observed-best selection remains fixed;
  a symbolic arrow removes the shared contrast. No invented before/after
  time. R and F get separate Q cards; geometric equal-person-year weighting
  is stated beside the strip.
- **Ratio interval with decision reference.** Extends N's observed-dot/range
  grammar to R. Actual unrounded coordinates; full linear domain includes
  neutral ratio and registered line. Endpoint labels use separate lanes to
  avoid crowding. Mint is reserved for the permitted verdict; amended
  interval and successful seasonal population are named explicitly.
- **Failed-gate disclosure cards.** Q cards in causal order: failed original
  gate, owner-approved registered amendment, passed specified simulations.
  Fixed-selection sensitivity is a separate card with no decision authority.
  No exact first-open timestamp or universal validation claim.
- **Matched-subset ratio rows / DNF association row.** N-style ranges retain
  actual endpoints and descriptive-sensitivity captions. DNF uses its own
  neutral reference and never receives the seasonal decision rule or mint.
- **Cross-edge and average-of-five schematics.** Paper/Ink cube net highlights
  edges and center while leaving corners unsolved; side centers match.
  Ordered attempt tiles strike only the fastest/slowest and outline the
  middle set. No solution times or stage durations are invented.

Q's episode cards use shorter heights to clear scope strips. Portraits stack
cards and matrices inside x=72–920, y=220–1500. Sources remain visible for
all cue states. Paper/Night, local fonts, system grain and settle easing are
preserved. Shared renderer files are untouched.

Run from repository root:

```sh
python3 -B studio/episodes/scramble-luck/scenes/build_data.py
node studio/episodes/scramble-luck/scenes/check_scenes.mjs
python3 -B studio/episodes/scramble-luck/scenes/render_stills.py
```

CUES.json names exact narration substrings, claim IDs, page/state/clock and PNG.
PROGRESS.md is updated after each scene. VISUAL_QA.md records actual capture
and delivery-size inspection, including unresolved source-only bindings.
