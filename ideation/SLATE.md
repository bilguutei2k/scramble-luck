# The next investigations: idea slate

Status: 2026-10-01, 12:10. Made by Claude with Sol 6.1 and Astra across four
Codex usage windows. Codex then hit its **weekly** limit ("try again at Oct 6th,
2026 11:21 PM"). Every finding below is exploratory: pilots touched only the
hashed exploration slices recorded in each `SLICE.md`, so confirmatory tests
can still be pre-registered on data nobody has looked at.

## How the search ran

| Round | Who | What | Output |
|---|---|---|---|
| 1 | 4 Sol + 2 Astra scouts | 288 raw candidates across sports, society and Mongolia, finance, culture and science, games, method-first designs, myths | `rounds/r1/*.raw.md`, 7 write-ups in `rounds/r1/partial/` |
| 1b | Claude | Screened all 288 against `BRIEF.md`; 12 to verify | `rounds/r1/SHORTLIST.md` |
| 2 | 4 Sol | Data, licence, prior-work and design gates for the 12 | `rounds/r2/verify-S*.json`: 7 go-if, 5 killed |
| 3 | 4 Sol pilots, Astra + Sol scouts | Real-data pilots for S1, S2, S4, S6; novelty-first scouting (hidden natural experiments; 2024–26 territory) | `rounds/r3/pilot-*`, `rounds/r3/new-*.json` (8), raw lists |
| 4 | Astra, Sol | Red-team (S1 finished), earthquake pilot (slice locked only), label-boundary scout (raw list) | `rounds/r4/` |

The lesson of round 2: **novelty is the binding constraint, not data.** Popular
myths are mostly tested already: Wales's 20 mph, Ulaanbaatar's coal ban,
science "disruption" and buybacks all died on close published answers. The
ideas that survived all exploit something structural in the data that others
have not used: a shared random stimulus, a rounded public label, or a fresh
rule change.

## Update, 13:40: the tier-1 trials (round 5, after a banked reset)

| Idea | Result | Decision |
|---|---|---|
| Earthquake 4.0 label | The label shown at the time is not recoverable for most events, there are too few US events near 4, and even the full data would give about 14% power for a true 20% jump. Slice ratio 2.32 (0.70–11.53). Aside: 25% of archived early labels near 4 crossed 4.0 on revision. | Killed (`rounds/r4/pilot-Q1/PILOT.md`) |
| Chess first-game lottery | Colour is not random: Lichess balances colour by history, and players can choose it in some rated games; newcomers got White 47.1% (46.4–47.8%) of the time. | Killed (`rounds/r5/pilot-C1/PILOT.md`) |
| Mongolia warming | Redesign fails its gates: 11 eligible Mongolian stations, 2 supported, none in the west. "Three times" compares 2.46 °C over 1940–2022 with an unspecified global figure. | Killed as a national test; possible short (`rounds/r5/mongolia-redteam.md`) |
| Rubik's Cube scrambles | Validation study passed: the estimator recovers known truths in simulation; shared component 3.81% (2.94–4.70%); seasonal-best correction 1.6% (0.5–2.3%). | Taken forward (`rounds/r5/pilot-S1/PILOT.md`) |

Taken forward today: the Rubik's Cube scrambles and, as the second
episode, the airline table (pilot done). Their METHOD drafts are in
`rounds/r6/`.

## Tier 1: pursue (as of the morning)

### 1. Does a 4.0 earthquake get more witnesses than a 3.9?
`rounds/r3/new-shared-01.json`; pilot slice locked in `rounds/r4/pilot-Q1/`.
USGS ComCat and Did You Feel It (public domain; millions of felt reports).
Magnitudes are continuous, but the public sees a rounded label, and news
and alerts often start at 4.0. A regression discontinuity at the label
boundary, with final magnitude, depth, nearby population and time of day
changing smoothly, and placebo cutoffs at every other tenth. Novelty gate
passed (three searches; no integer-label study found). Either verdict works:
a jump means the headline number changes what people report feeling; no jump
means felt reports track the shaking, not the label. **First gate:** whether the
magnitude shown at the time (often revised later) is recoverable.
A possible format: *does the label matter more than the number?* The
label scout (`rounds/r4/scout-labels.raw.md`) found more of the same shape:
air-quality colour bands, the 14,000-foot peaks, hurricane categories, and
top-ten lists.

### 2. How much of a record-speed Rubik's Cube solve is the scramble?
`rounds/r2/verify-S1.json` (go-if, 30/35), `rounds/r3/pilot-S1/`, red-team in
`rounds/r4/REDTEAM.md`. WCA export (republication allowed with attribution).
Every finalist solves the same random scrambles, a natural experiment nobody
had used. Pilot on a 20% hashed slice (1,954 finals, 110,465 solves): the
shared component is 3.85% of within-round log-time variance (bootstrap
2.9–4.7%), and peer-adjusted season bests move about 0.6%. Astra's red-team:
the result is real, but it does **not** yet show that "luck is personal". Small
finals make single-scramble difficulty noisy, and the next step is a
measurement-validation study (reliability against number of peers, simulated
recovery of known effects) before opening the held-out 80%. Spin-offs with
the same data: does barely making a final make you better (`new-shared-02`,
a regression discontinuity, 28/35); do easy scrambles help the favourite or
the underdog (`new-shared-05`, 29/35).

### 3. Is Mongolia really warming three times faster than the world?
`rounds/r2/verify-S4.json` (go-if, 29/35), `rounds/r3/pilot-S4/`. NOAA GHCN
(public domain). The famous ratio compares a continental interior with a
global mean that includes oceans; the fairer test compares matched continental
stations. Pilot: the national 1940–2022 design fails coverage (14.6% of matched
cells), but an exploratory pre-1980 diagnostic shows Mongolia running
+0.33 °C/decade above matched peers (95% CI 0.11–0.56; 6 Mongolian stations,
17 controls). Revise to a supported-population question (long-record stations)
before confirmation. The strongest Mongolia-audience idea; either verdict works.

### 4. Does losing your first game make you quit? (unverified lead)
Built by Claude from Astra's raw idea 44 (`rounds/r3/scout-shared.raw.md`)
and Sol's chess list. In Lichess (CC0), a new player's first rated games
come with a random colour (and in Chess960, a random starting position), which
shifts the chance of winning without saying anything about the player. That
randomness separates "losing makes people quit" from "people who would quit
anyway also lose". The question is universal; the data runs to millions of
newcomers. **Gates, not yet run:** whether colour was chosen by the player
(lobby seeks allow it; the PGN may not say), the strength of the first stage,
and prior work on newcomer retention (Wikipedia, online games).

## Tier 2: worth doing with a redesign or a lower bar for novelty

| Idea | Status | Note |
|---|---|---|
| Powerlifting weigh-ins follow the 2011 class change (S2) | revise | Pile-ups visibly move with the rule; unchanged-rule comparison federations are too thin for a causal claim. Strong visual, descriptive story. |
| Which airline wins on your route (S6) | pilot done | 2015 slice (5.8M flights): the league table mostly survives the same-route, cancellation-inclusive test; Southwest falls 4th → 6th. A good "belief survives" episode; novelty 3/5. |
| Your city's wet-weekend streak (S7) | go-if, 30/35 | Generic weekend-rain debunks exist; the new angle is how unusual the *worst* streak is once you count every city and year searched. |
| Chess tilt: how much hidden quitting would overturn "no tilt"? (S8) | go-if, novelty 2 | Audit of a published null. |
| The chess clock versus hard positions (S9) | go-if, novelty 2 | Engine-heavy; earlier work is close. |
| Did goats survive the 2024 dzud better, or live in luckier places? (`new-fresh-01`) | go-if, 27/35 | Mongolia-specific; soum-level data, not large. |
| Can a database update move a biodiversity hotspot? (`new-fresh-02`) | go-if, 29/35 | GBIF taxonomy switch; rigorous but a niche hook. |
| Distant earthquake crowds out local reports (`new-shared-04`) | go-if, 28/35 | Pairs with tier-1 #1. |
| New Jersey bike-share price rise (`new-fresh-03`) | go-if, 25/35 | Narrow. |

## Killed, and why

| Idea | Reason |
|---|---|
| Wales 20 mph (S3) | Synthetic-control and reclassification analyses already published. |
| Ulaanbaatar raw-coal ban (S5) | 2025 peer-reviewed interrupted time series with weather and COVID handling. |
| Science "less disruptive" (S10) | The original used a network null; the critiques and the 2026 Nature exchange cover the fixes; the snapshot is 707 GB. |
| Buybacks and share counts (S11) | Same question and stock-pay explanation already published. |
| Speedrun records (S12) | speedrun.com data is CC BY-NC; fails the monetised-use gate. |

## Raw leads not yet gated (second wave)

From `rounds/r4/scout-labels.raw.md`, `rounds/r3/scout-shared.raw.md` and
`rounds/r3/scout-fresh.raw.md`: the 2024 US air-quality breakpoint change (the
same pollution got a worse colour; did cycling respond to the colour?);
14,000-foot peaks and attention; hurricane categories against inland flood
risk; a rainy diary day and the parents' childcare gap (ATUS); an
unexpectedly hard first problem in programming contests; Mongolia's 2025
minimum-wage bunching; New York's congestion toll and inside-zone taxi trips;
Paris's 50 km/h ring road at its ramps.

## Next, when Codex is back (or with a banked reset)

1. Earthquake label pilot (`prompts/r4-pilot-Q1.md`; slice already locked).
2. Gates for the chess first-game lottery (colour assignment, first stage, prior work).
3. Astra's red-team of S2, S4, S6 and the new ideas (`prompts/r4-redteam.md`; S1 done).
4. Label-boundary scout write-ups (`prompts/r4-scout-labels.md`; raw list saved).

Budget note: one 5-hour Codex window held roughly 80–150 agent-minutes at
`high` effort. Plan about one round per window.
