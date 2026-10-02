# Round 1 shortlist (Claude's screen of 288 raw candidates)

2026-10-01, 02:20. Round 1 was cut off twice by the Codex usage limit
(00:02 and 02:09), so the six scouts left raw lists (`*.raw.md`), search logs
in `scratch/`, and seven finished write-ups recovered into
`partial/myths.json`. This shortlist screens all 288 raw candidates against
`BRIEF.md`. It favours ideas where the data is large and openly licensed, the
fairer test is a real design and not just a ratio, and our search memory does
not already hold a well-known published answer.

Already well covered elsewhere, so screened out (they come back only with a
twist that changes the published answer): NFL fourth downs, icing and
overtime tosses; baseball make-up calls and the shift ban; teams "vulnerable
after scoring"; nervous nineties; the cricket toss in general; marathon
round-number finishes; birthweight heaping; weekend births; stamp-duty
bunching; earnings beaten by a penny; the January effect and overnight
returns; female-named hurricanes; ChatGPT and Stack Overflow; Ngram pronouns.

## The twelve to verify

| # | Working title | Data (licence to confirm) | Design |
|---|---|---|---|
| S1 | Was the Rubik's Cube world record skill, or a lucky scramble? | WCA results export, including scrambles and every attempt | Every competitor in a round solves the same scrambles, so scramble difficulty and solver skill separate in a crossed random-effects model; extreme-value expectation of the record given attempt counts; a solver-computed scramble difficulty as a check |
| S2 | How much do powerlifters cut weight, and does it pay? | OpenPowerlifting (public domain) | Bunching of bodyweights just under class limits; the 2011 IPF class change as a natural experiment (does the pile move with the limit?); within-lifter strength when cutting versus not |
| S3 | Did Wales's 20 mph limit actually save lives? | STATS19 road collisions (OGL) | Synthetic control and DiD against English authorities; handle the CRASH severity-recording change and the pandemic; placebo dates |
| S4 | Is Mongolia really warming three times faster than the world? | NOAA GHCN-Daily / GHCNm | The claim compares a continental interior with a global mean that includes oceans; fairer test against matched stations of similar latitude, elevation and continentality, fixed-station cohorts |
| S5 | Did the raw-coal ban clean Ulaanbaatar's air? | OpenAQ and US Embassy PM2.5; ERA5 or GHCN weather | Weather-normalised (deweathered) interrupted time series, synthetic comparison cities, pandemic handling, placebo winters |
| S6 | Which airline is really most on time on your route? (and are timetables just padded?) | BTS On-Time Performance (public domain) | Route-hour-matched hierarchical model counting cancellations and diversions as outcomes; scheduled block time trends for padding; see `partial/myths.json` myths-04/05/06 |
| S7 | Does it really rain more on weekends? | NOAA GHCN-Daily | Global station panel, the weekly cycle against a null from shifted 7-day "weeks", false discovery control, pollution-cycle sub-hypothesis; see myths-07 |
| S8 | Does losing at chess make you lose again? | Lichess open database (CC0) | Within-player performance against rating expectation after losses, with session self-selection and matchmaking handled; see myths-01 |
| S9 | Does the chess clock cause blunders, or do hard positions do both? | Lichess games with clock and engine evaluations (CC0) | Error rates by remaining clock in positions matched on engine-measured difficulty; increment as a natural experiment; see myths-02 |
| S10 | Is science really becoming less disruptive? | OpenAlex (CC0) | Re-test Park, Leahey and Funk (Nature 2023) against a degree-preserving null and citation inflation; the critiques already published must be found and beaten |
| S11 | Do stock buybacks actually shrink the share count? | SEC XBRL company facts (public domain) | Repurchase dollars against split-adjusted share-count change; how much goes to offset stock-based pay; by firm size and era |
| S12 | Are speedrun records slowing because games are solved, or because runners leave? | speedrun.com API (terms to check) | Record progression against the number of active runners and attempts; extreme-value null for a fixed field |

Reserves: chess rating milestones and quitting (check Anderson and Green,
PNAS 2018); the "100-year rule" for baby names (SSA, public domain); the
cricket toss when rain arrives after the decision (Cricsheet licence); New
York's congestion toll and drivers' tips (TLC).
