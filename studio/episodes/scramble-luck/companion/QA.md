# Companion QA — 2026-10-02

Status: **pre-lock draft: claims proposed**. No claim status was changed.

## Deliverables and build

- `build.py` and `template.html` generate `index.html` and
  `../renders/companion/page.html` (identical head/body content, without the
  document wrapper). Run from the repository root:
  `python3 studio/episodes/scramble-luck/companion/build.py`.
- One analytical select offers 14 precomputed selections: registered R,
  arithmetic R, per-solver R, equal-tier R, its matched all-peer comparator,
  both eras, the leave-one-year-out range, fixed-selection A, and all five
  available replacement assumptions. Every choice names its change and says
  it cannot change the verdict. The theme button is separate.
- Replacement assumptions change shared variance, **not R**: results.json
  contains no replacement-adjusted R. The registered point/interval stay put.
- Year deletion shows seven individual points and pointwise intervals; the
  span of points is not presented as a simultaneous confidence interval.
- The permitted answer, amended interval, scope, original failed gate,
  amendment timing, both era-reference readings, blind comparison explanation,
  methods review/fixes and full commit hashes remain visible.
- Cross ranges are expressly unvalidated diagnostics; points outside their
  ranges and the inconclusive inferential uncertainty are disclosed beside them.

## Evidence binding

- Results SHA-256:
  `4cb552244944cc0194bd750c7ea088030129285491996de91a48869ba5deb334`.
- Verified claims SHA-256:
  `a2eb17f7cbbd27e0916b065b43106f4053cb931744e5ca6eb67bbf9abc7f933e`.
- The independent verifier intentionally did not open results.json and does
  not store its hash. The companion explicitly freezes the current results,
  verified claims and verification report together, and additionally checks
  70 displayed numeric bindings against independently recomputed evidence.
  Confidence level and scope wording come from CLAIMS.json. Mathematical axis
  coordinates and percentage transformations derive from those bound values.
- Temporary-copy tests changed each of results.json, CLAIMS.json and
  claims_check.json separately: all builds refused before writing outputs.
  Existing outputs stayed unchanged. Pins must not be automatically refreshed.
- Ten embedded source downloads decode byte-for-byte to their original files.
  An actual Chromium METHOD.md download also matched the original exactly.
- WCA notice matches METHOD verbatim, including “World Cube Assocation”.

## Chromium and layout checks

`check_browser.py` records the reproducible sweep. Headless Chromium was run
via agent-browser 0.38.2, using the existing local headless-shell executable,
a disposable socket directory, and `--single-process,--no-sandbox,
--in-process-gpu,--disable-gpu` for this restricted local environment.

- **56/56 states pass:** every selection at 390×844 and 1440×1000, in Paper
  and Night, including the expanded provenance disclosure.
- At 390px, document scroll width is exactly 390px and both gutters are 16px.
  At 1440px the centered column has 160px gutters. No element spills beyond
  either viewport. The long native-select label has a wrapping visible copy.
- Point/interval readouts match bound values; SVG coordinates use unrounded
  measurements, a stable linear domain and the fixed registered reference.
- Replacement variance readouts and unchanged R pass; every year deletion
  receives its own point and interval. Verdict stays the primary verdict.
- Embedded display 900, serif 500 and mono 600 faces load; zero network
  resource requests, zero console messages and zero runtime errors.
- Visual inspection passed for desktop control, phone headline/control,
  year deletion, replacement, stacked diagram and cross diagnostic table.
  No radius except circular dots; no shadows; channel colour roles preserved.
- The wrapper-free fragment was placed inside a minimal host wrapper:
  arithmetic selection works at 390px with no overflow and loaded fonts.
  The initial registered readout and SVG also exist in the static markup.
- `git diff --check` passes. Only read-only Git commands were used; no .git
  writes or deployment were attempted.

Machine-readable results: `../renders/companion/browser-audit.json`.
Captures: `390-paper.png`, `390-night.png`, `1440-paper.png`, `1440-night.png`
and viewport crops for controls, year deletion, replacement, diagram and
diagnostic, all under `../renders/companion/`.

## Open issues

Owner lock remains pending. Locking/changing claims requires current independent
verification and a reviewed update of the frozen binding before regeneration.
Cross inference remains unvalidated and actual replacement assignments remain
unaudited. These are disclosed evidence limits; no known layout/runtime issue
remains. Future analytical reuse still needs checkpoint fingerprint hardening
and less hard-coded registration QA, as recorded in the methods review.
