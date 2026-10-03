# About 2% Longer

Status: locked, owner-approved 2026-10-03; script v1. Revised from preserved `STORY.v0.md`.
All claims verified; numerical verification is in `analysis/claims_check.json`.

## Argument: “A shortcut isn't a shared advantage”

| Beat | What the viewer learns | Evidence |
|---|---|---|
| Belief | WIRED and Ruwix use luck language, with qualifications. | S01 source links; SL-C104 |
| Obvious answer | Park's then-record reconstruction shows a PLL skip. | SL-C105, SL-C138; S03 source |
| Flaw | One chosen solution cannot measure an advantage common to the field. | METHOD, belief → flaw; S04 schematic |
| Fairer test | Exclude the focal solver, compare peers within their own final, then adjust the observed seasonal best. | METHOD, measures; SL-C002–004 |
| Honest uncertainty | The original gate failed; an owner-approved amendment preceded confirmation. | METHOD Amendment 1; analysis/review.md |
| Verdict | Belief fails under the amended contract; the average adjustment is about 2%, below the registered 10% line. | SL-C001, SL-C144 |
| Limits | Slot conditions, replacements, success conditioning and personal luck limit interpretation. | SL-C074, SL-C075, SL-C134; METHOD |

Wording rules: use **shared scramble/slot component** throughout. The question
is average adjustment of eligible season-best final solves, not a particular
record's total luck. Say **estimated shared-scramble-adjusted time**; R is an
equal-person-year geometric ratio of adjusted to observed time. A longer
adjusted time is not the same percentage reduction in observed time. Use
METHOD's permitted verdict sentence verbatim, with R and its amended interval.
F is successful log-time variance, not seconds or a partition of total luck.
Never assign the residual to personal luck or rank skill against luck.
Cross-length evidence is an **unvalidated diagnostic**, with no calibrated
interval claim. Quotes are exact, publication-attributed and linked beside
the scene. Historical records are **then-records**. First-person narration;
schematics carry no invented results. Claim tags and source labels aren't spoken.

## Scene table

| Scene | Viewer question | Evidence | Visual | Why next? |
|---|---|---|---|---|
| S01 Lucky scramble? | What does that phrase mean? | SL-C104; WIRED/Ruwix | Big-number reveal: Du's historical mark; publication quote cards, dates and source/scope caption. Night. | Define the shortcut. |
| S02 The basics | What is being skipped? | SL-C130, SL-C135; CubeSkills | Q · Measure cards: CROSS / F2L / OLL / PLL; edge-only cross schematic, then average-of-five discard diagram. Paper. | Inspect a real example. |
| S03 The obvious answer | Does a reconstruction settle it? | SL-C105, SL-C138 | Q cards highlight Park's PLL skip and remaining top alignment; no stage durations or “easy” stamp. Source strip. | Whose advantage? |
| S04 The flaw | Shared luck or one solution? | METHOD | Two-part split: THIS SOLUTION / SHARED BY THE FIELD?; schematic contrasting paths, no fabricated times. | Specify the population. |
| S05 The scope | Which solves count? | SL-C002–004, SL-C133 | Big-number reveal: 5,017 finals, then 3,313 solver-seasons; scope strip with years and five-final eligibility. | Show the comparison. |
| S06 Listen to the peers | How is the shared contrast estimated? | METHOD, measures | **New: Finalist × scheduled-scramble matrix**; remove focal row, center each peer row, reveal column summaries. Label SCHEMATIC. | Apply it to the selected best. |
| S07 The seasonal best | What does the adjustment mean? | SL-C002; METHOD | Before → after: OBSERVED BEST → SHARED-COMPONENT-ADJUSTED TIME; symbolic arrow, then Q cards for variance F versus seasonal ratio R. | Validate the uncertainty. |
| S08 The failed gate | Was the test fixed in advance? | SL-C024, SL-C025; Amendment 1 | Q cards: ORIGINAL GATE FAILED / AMENDMENT REGISTERED / CONFIRMATION; separate fixed-selection sensitivity card. No misleading first-open timestamp. | Read the decision scale. |
| S09 The verdict | Does the shared boost reach the line? | SL-C001, SL-C144 | N · Resampling range bars adapted to ratio R: dot 1.0198, amended interval 1.0164–1.0231, rule 1.10. Mint: BELIEF FAILS. | Does it survive checks? |
| S10 The checks | Detectable, and stable? | SL-C005, SL-C145, SL-C015, SL-C035, SL-C036, SL-C050–053, SL-C077 | Q cards with counts and qualifications; N-style matched-subset ratio rows; separate cross card stamped UNVALIDATED DIAGNOSTIC. | State remaining limits. |
| S11 What remains unknown | Could this still miss luck? | SL-C074, SL-C075, SL-C134; METHOD | Q cards: SLOT CONDITIONS / REPLACEMENTS / DNF / PERSONAL LUCK; N range for DNF odds, no invented failure time. | Return to the opening. |
| S12 The takeaway | What can I say about a lucky solve? | SL-C001, SL-C144; METHOD | Night verdict card, then source/scope strip and evidence link. | End. |

Visual implementation: retain Paper/Night surfaces, Ink rules, Plex Mono
numbers, field peers and one highlighted focal row. The new matrix extends
the dot/slope grammar to five scheduled columns; the small-table component's
four-column cap cannot hold it. A hollow, separately tagged cell illustrates
a replacement, not an audited observation. Record this adaptation in
`studio/DIRECTION.md` before renderer use. N's reference line and captions
are adapted to this episode's ratio and amended interval. All numerical
graphics bind claim keys, not the design reference's placeholder values.

## Script (v1)

### S01 Lucky scramble?

> A timer stops. A record falls. And there's an appealing explanation waiting: a lucky scramble.
> WIRED put the intuition plainly: “The fact is, sometimes you just get a lucky scramble.” [SL-C146]
> Ruwix asked, “Lucky scramble? Maybe.” That was its coverage of Yusheng Du's then-record 3.47-second solve in 2018. The article also credited skill. [SL-C104] [SL-C146]
> I want to test a narrower question. When a solver sets their fastest final-round time of a season, how much help came from something that helped the other finalists too?
> That distinction matters. A shortcut in one person's solution and an advantage shared by the field are different things to measure.

Source cards: [WIRED video and transcript, released 2019-05-23](https://www.wired.com/video/watch/almost-impossible-why-solving-a-rubik-s-cube-in-under-3-seconds-is-almost-impossible),
[Ruwix, published 2018-11-25](https://ruwix.com/blog/yusheng-du-record-347/).
Publication date is not asserted as the solve day. Both quotations checked
against the linked originals for this revision.

### S02 The basics

> A scramble is the move sequence used to set up the cube's starting state. Official random generation does not promise equal human difficulty. [SL-C135] [SL-C147]
> Here's a common solving method: CFOP. Make a cross, fill the first two layers, orient the last layer, then permute its pieces into place. [SL-C147]
> The cross solves the edge pieces around a face's center, with side colors matching the neighboring centers. It doesn't solve the whole face. [SL-C147]
> A PLL skip means that, after orientation, the last-layer pieces already have the right relative positions. The permutation algorithm is unnecessary; a final top-face alignment may remain. [SL-C147]
> An average of five drops the fastest and slowest of 5 attempts and averages the middle 3. This study examines singles inside those finals, rather than the official average. [SL-C130]

Definitions: [CubeSkills glossary](https://www.cubeskills.com/tools/glossary),
[PLL guide](https://ruwix.com/the-rubiks-cube/advanced-cfop-fridrich/permutate-the-last-layer-pll/).
Format: [2025 WCA regulation 9f8](https://www.worldcubeassociation.org/regulations/history/official/2025-07-17/#9f8).

### S03 The obvious answer

> The obvious way to investigate luck is a reconstruction: replay the moves and look for shortcuts.
> Take Max Park's then-world-record 3.13-second single, set in 2023. Ruwix's published solution includes a double extended cross and a PLL skip. [SL-C105, SL-C138]
> A double extended cross solves the cross alongside additional corner-edge pairs. Don't mistake that opening for a bare-cross count. [SL-C147]
> The reconstruction still includes last-layer orientation and a final top-face adjustment. It isn't a whole-last-layer skip. [SL-C138]
> That's useful evidence about the route Park took. But to estimate a shared advantage, I need a comparison the reconstruction doesn't provide: what happened to the other finalists?

Source: [Ruwix, published 2023-06-12; record set 2023-06-11](https://ruwix.com/blog/max-park-rubik-single-record-313/),
cross-checked against [the published reconstruction](https://reco.nz/solve/9155).
No precise record day is spoken; no claim of today's record is made.

### S04 The flaw

> Imagine the diagram shows different paths through the same starting state. It's a teaching example, not competition data. [SL-C148]
> One solver's choices lead to a skip. Another solver takes a different route. The first solution alone cannot tell me how much easier the starting state was for everyone. [SL-C148]
> And even the same solver can execute a promising route differently. Recognizing an opportunity and turning without a pause aren't measured separately here. [SL-C148]
> So I can't label every unusually fast attempt shared luck. I need to ask whether peers also ran faster than their own usual pace within that final. That is the fairer test. [SL-C148]

Methodological inference: METHOD, “Belief → obvious answer → flaw → fairer
test” and “Measures”; no illustrative result is claimed.

### S05 The scope

> I used official WCA results for eligible one-group, average-of-five finals from 2019 through 2025. In the finals included here, competitors are assigned the same scheduled scrambles. That isn't a universal rule for every final. [SL-C003, SL-C133]
> The confirmation sample was held out from the idea-stage pilot by a locked competition split. Its 80% label describes that split rule, not the fraction of solves surviving every filter. [SL-C004]
> The included sample has 5,017 finals and 306,155 scheduled attempt slots. The seasonal comparison has 3,313 solver-seasons, each requiring at least 5 eligible finals. [SL-C002]
> That population answers the seasonal question. It doesn't represent every cuber, every record attempt or every round.

Scope: EPISODE and METHOD; group recommendations:
[historical WCA regulation 1h and guidelines](https://www.worldcubeassociation.org/regulations/history/official/2025-07-17/#1h).

### S06 Listen to the peers

> Each row here is a finalist. Each column is a scheduled scramble position. The picture is schematic. [SL-C148]
> First, compare each peer with their own pace in that final. Otherwise, a fast finalist could make every column look easy merely by being fast. [SL-C148]
> Then look down a column. If peers tended to beat their own pace there, the model estimates a favorable shared contrast. If they tended to slow down, it estimates an unfavorable one. [SL-C148]
> Crucially, I remove the focal solver's entire row before estimating their shared contrast. Their spectacular time cannot serve as its own evidence that the scramble helped everyone. [SL-C148]
> For the variance calculation, I correct for noise from having a finite set of peers. This estimates a shared scramble/slot component, with uncertainty. It doesn't turn each peer's stopwatch into a perfect difficulty meter. [SL-C148]

Method: within-solver-round centering, finite-peer correction and whole-focal
exclusion in METHOD, “Measures”. No schematic values are spoken or displayed.

### S07 The seasonal best

> Next, select each eligible solver's fastest successful final solve of the season. Keep that observed best selected; don't swap in whichever adjusted attempt now looks fastest. [SL-C148]
> At its scheduled position, remove the estimated shared contrast under the model. A favorable shared contrast makes the estimated adjusted time longer than the observed time. [SL-C148]
> This is an estimated shared-scramble-adjusted time. It isn't a replay of the solver on a different cube. [SL-C148]
> I combine the adjusted-to-observed ratios geometrically, giving each available solver-season equal weight. That measure is R. A solver with more eligible seasons contributes more seasons. [SL-C002] [SL-C148]
> A separate measure asks how much successful log-time variation is shared. That's F. Variance share and seasonal time adjustment answer different questions; neither is a complete luck score. [SL-C148]

Method: “Seasonal-best correction”, aggregation and shared variance share.

### S08 The failed gate

> Before using the confirmation results for a verdict, the uncertainty procedure had to recover known truths in simulations. [SL-C148]
> The original gate failed. I can't leave that out of the story. [SL-C148]
> After investigating the synthetic results, an owner-approved amendment changed how the interval was centered and revised the validation gate. It was registered before any confirmation solve times were read. The amended procedure passed its specified simulation checks. [SL-C148]
> It reselects seasonal bests as competitions and solvers are resampled, then centers the bootstrap differences on the observed estimate. [SL-C024] [SL-C148]
> A fixed-selection interval is reported separately as a sensitivity. It cannot change the verdict. These simulations validate the amended procedure under their specified processes, not every possible real-world process. [SL-C025] [SL-C148]

Disclosure: METHOD Amendment 1, `analysis/amendment/AMENDMENT-1.md` and
`analysis/review.md`. No claim that all secondary intervals were validated.

### S09 The verdict

> The line on this chart was fixed before solve times were read: an adjusted ratio of 1.10, meaning an estimated adjusted time 10% longer than observed. [SL-C001]
> The measured R is 1.0198, with an amended 95% interval from 1.0164 to 1.0231. In plain language, the estimated adjustment is about 2%. [SL-C001, SL-C144]
> The entire interval is below the decision line. Belief fails. [SL-C001]
> The data rule out an average shared scramble/slot boost as large as 10% for these season bests. [SL-C001]
> That's the permitted conclusion. It doesn't say that an individual spectacular solve received only that much help, or that a skip was unimportant to its solver.

### S10 The checks

> There is a detectable shared component: F is 4.7% of balanced-tier, within-solver-round successful log-time variance. Its interval is on screen. That is not a percentage of seconds. [SL-C005, SL-C145]
> This tier comparison excludes 597 finals lacking the required support; its coverage matters. [SL-C015]
> The seasonal result stays below the decision line with complete-success panels, clipped contrasts and individual solvers removed. None supplies a new verdict. [SL-C035, SL-C036, SL-C050]
> Equal weighting of the skill tiers gives a similar ratio on its matched subset, but omits 270 seasonal bests. It doesn't establish a uniform advantage across skill levels. [SL-C051, SL-C053]
> A geometry check links optimal cross length positively with the shared contrast. Its bootstrap uncertainty is unvalidated: treat it as a diagnostic, not calibrated inference. It cannot remove the slot confound. [SL-C077]

On-screen supporting values: F 4.7434%, interval 3.9181–5.6708%; tier sample
4,420 finals / 234,525 successes. Matched-subset R: all-peer 1.0199
(1.0152–1.0247), equal-tier 1.0203 (1.0155–1.0251), n=3,043; translated
sensitivity intervals are descriptive. Cross card shows the qualitative
association and **UNVALIDATED DIAGNOSTIC**, with no numerical endpoints.
The independent per-solver alignment permutation check (SL-C081) belongs in
the companion evidence, not a second decision rule. Era F comparisons are omitted from narration. The review’s applied fixes
now disclose full-window references and retain within-era estimates separately.

### S11 What remains unknown

> The biggest naming limitation is the slot. Scramble number and attempt number travel together. Warm-up, nerves or changing conditions could track the position. The model controls average position effects, but cannot isolate scramble geometry from conditions shared within a final's slot. [SL-C148]
> Nor do assigned scrambles prove actual assignments. An extra attempt uses a different scramble and replaces the numbered result. There is no actual-assignment audit here. [SL-C134] [SL-C148]
> Then there are failures. F and R use successful solves only; I don't invent a completion time for a DNF. The separate failure endpoint asks whether higher peer-measured difficulty goes with higher DNF odds. [SL-C148]
> Its estimated association is positive, but the interval includes no association. Success conditioning may understate shared difficulty. Simulation stresses don't give a universal bound on missing failure times. [SL-C074, SL-C075] [SL-C148]
> Finally, the remaining variation includes execution, solver-specific opportunities, penalties and model or mapping errors. These data cannot separate personal luck from execution. A PLL skip illustrates an opportunity in a chosen solution; it doesn't reveal the whole field's advantage. [SL-C148]

Rules: [2025 WCA 11e1–11e2](https://www.worldcubeassociation.org/regulations/history/official/2025-07-17/#11e1).
DNF card: odds ratio 1.0348 (0.9777–1.0649) per 0.05 higher h; 61,231
identified solver-rounds, 4,154 discordant rows. Limits: METHOD and FINDINGS.

### S12 The takeaway

> So, was the record a lucky scramble? This aggregate study can't settle that particular solve.
> It can say that, across these eligible seasonal bests, removing the estimated shared scramble/slot component makes the time about 2% longer on average. [SL-C144]
> The data rule out an average shared scramble/slot boost as large as 10% for these season bests. [SL-C001]
> The next time a reconstruction reveals a wonderful shortcut, I want to ask whose shortcut it was, and what comparison would measure it. The method, sources and all the checks are linked with this video.

## Short-form adaptations

Each portrait short has its own hook and payoff. Its scope strip remains
visible throughout; qualifications stay in narration. Compose separately
within the system's portrait safe area.

### Short A: What the shared scramble adds

Visual: N ratio range → big-number reveal; scope: eligible one-group
average-of-five finals, 2019–2025; seasonal eligibility ≥5 finals; successful
times, shared scramble/slot estimate; confirmatory under Amendment 1.

> A lucky scramble sounds like an explanation for a record. I tested a narrower question: how much did the shared scramble/slot component help eligible season-best final solves?
> The estimated adjustment is about 2%. The ratio is 1.0198, with an amended 95% interval of 1.0164 to 1.0231. [SL-C001, SL-C144]
> The data rule out an average shared scramble/slot boost as large as 10% for these season bests. [SL-C001]
> That doesn't measure a particular record's luck. It bundles shared slot conditions with the scramble, and cannot separate personal luck from execution.

### Short B: A skip isn't a shared advantage

Visual: Q stages → two-part split → focal-row exclusion matrix.
Scope: published historical reconstruction; illustrative distinction;
one-group seasonal-final study, not a record attribution.

> Max Park's then-record 3.13-second solve included a PLL skip in Ruwix's reconstruction. A final top-face alignment still remained. [SL-C105, SL-C138]
> That's a shortcut in the solution he chose. It doesn't tell me how much the starting state helped everyone else.
> To estimate the shared scramble/slot component, I compare peers with their own pace in the final, excluding the focal solver entirely. [SL-C148]
> A reconstruction explains a route. The peer comparison measures a shared pattern. Neither can separate personal luck from execution in these data. [SL-C148]

Source: [Ruwix reconstruction](https://ruwix.com/blog/max-park-rubik-single-record-313/).

### Short C: Why “scramble luck” includes the slot

Visual: Q limitation cards → separate replacement tag in schematic matrix.
Scope: scheduled-position analysis of eligible one-group finals, 2019–2025;
no actual-assignment audit, successful times only.

> If finalists are assigned the same scheduled scramble, their times offer a useful comparison. But scramble number and attempt number travel together. [SL-C148]
> Conditions shared at that position can enter the estimate too. That's why I call it the shared scramble/slot component. [SL-C148]
> An extra attempt also uses a different scramble while replacing the original numbered result. Scheduled position isn't proof of the actual cube used. [SL-C134] [SL-C148]
> The primary estimate uses successful solves; failures are a separate endpoint. This comparison has limits, and it cannot tell us a particular record holder's total luck. [SL-C148]

## Timing and evidence

Long-form: **1,388 words, approximately 9:15 at 150 words per minute**, across
12 scenes. Shorts: approximately 0:34, 0:32 and 0:36 respectively.

Timing is a word-count estimate at 150 words per minute, excluding claim tags,
source notes and visual instructions; final voice and chart holds will be
timed after script lock. Long-form and shorts are counted separately.

Required WCA notice for video/source strip and companion page, preserving
the source's spelling:

This information is based on competition results owned and maintained by the
World Cube Assocation, published at https://worldcubeassociation.org/results
as of September 30, 2026.

Evidence: `METHOD.md` including Amendment 1, `analysis/FINDINGS.md`,
`analysis/review.md`, `analysis/CONTEXT.md`, `CLAIMS.json` and
`analysis/claims_check.json`. Context links are publication evidence, not
independent confirmations of the seasonal estimate.

## Review integration

Re-read `analysis/review.md`, including “Fixes applied — 2026-10-02”, and
the live `CLAIMS.json` after verification. Applied cross labels, era reference
scopes, timestamp qualifications and corrected informative-DNF simulation
wording leave the primary result unchanged. This script presents no cross
interval endpoints, no disputed era F reading, no exact first-access timestamp
and no conditional-logistic claim about the simulation sampling mechanism.
Final verification covers all 148 proposed claims; `story_check` has only
“not verified” warnings pending owner lock.

## Changes from v0

- Replaced named WIRED-presenter attribution with WIRED publication attribution;
  removed “the same article” joining separate Ruwix posts and the Geng opening.
- Removed unsupported assertions about what the first comment usually says,
  how often reconstructions look easy, skill mattering more than luck, luck
  being nondominant and “only about 2% of the story”.
- Corrected the scramble, cross and PLL definitions; removed “most common”
  as unnecessary and stopped labeling extended-cross tokens as a bare cross.
- Rebuilt the peer comparison and seasonal adjustment as separate measures;
  added amended-gate disclosure, precise scope, coverage and DNF uncertainty.
- Removed the specific Wang-record comparison and era statistics; retained
  sourced historical Du/Park illustrations without extrapolating to them.
- Replaced unsupported numerical teaching examples and generic cube-spinning
  directions with labeled schematics and named design-system components.
