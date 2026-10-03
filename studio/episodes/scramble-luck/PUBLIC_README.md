# About 2% Longer: how much of a record-speed Rubik's Cube solve is the shared scramble?

The data, code and checks behind the video. Every number in it comes from
`analysis/results.json` through a verified claim, and every step that produced
those numbers is here, including the parts that went wrong.

**Companion page:** https://bilguutei2k.github.io/scramble-luck/

## The short version

Record solves are often called "lucky scrambles". In a WCA final every
finalist solves the same five scrambles, so the other finalists' times show how
much a scramble helped everyone. Across 3,313 solver-seasons of 3×3
average-of-five finals (2019–2025; 5,017 finals, 301,668 successful solves), the
part of scramble luck that finalists share makes season-best solves about **2%**
faster on average: the season best would take an estimated 1.98% longer with
that shared component removed (95% interval 1.64% to 2.31%). The data rule out a
shared boost as large as 10%, the line fixed before any data was read.

What this cannot tell you: luck that belongs to one solver's own solution (a
skip on their path), execution, and conditions shared by everyone solving in the
same time slot are not separated here. It says nothing about the total luck of
any particular record.

## Where things are

All paths are under `studio/episodes/scramble-luck/`.

| What | File |
|---|---|
| The question, measures and pass/fail rule, written before the confirmation data, with Amendment 1 | `METHOD.md` |
| The failed pre-confirmation gate | `analysis/GATE.md`, `analysis/gate.json` |
| Amendment 1: diagnosis, candidates, simulations, independent replication | `analysis/amendment/` |
| The confirmatory analysis and its outputs | `analysis/analyze.py`, `analysis/results.json`, `analysis/qa.json`, `analysis/FINDINGS.md` |
| The 148 claims the video may make, each tied to result keys | `CLAIMS.json` |
| Independent recomputation of every claim value | `analysis/verify_claims.py`, `analysis/claims_check.json` |
| A blind re-derivation by a second model, and the comparison | `recheck/`, `analysis/compare_recheck.py`, `analysis/recheck_report.json` |
| The methods review and what changed because of it | `analysis/review.md`, `analysis/reviews/` |
| Implementation decisions and their timing | `analysis/DEVIATIONS.md`, `analysis/PROGRESS.md` |
| The script, every numbered line citing a claim | `STORY.md` |
| The animated scenes (numbers only from `scenes/data.js`, built from the results) | `scenes/` |
| The edit and the narrated build | `EDIT.json`, `NARRATED_BUILD.md` |
| The companion page | `companion/` |
| How the idea was found and piloted on a held-out 20% of competitions | `../../../ideation/` (`SLATE.md`, `rounds/r3/pilot-S1/`, `rounds/r5/pilot-S1/`) |

The renderer is in `studio/render/`, and the narration, assembly and script
checks are in `studio/tools/`.

## Written down before the data

1. The idea was piloted on a 20% hashed sample of competitions
   (`data/exploration-competition-ids.txt`); the other 80% were held out.
2. `METHOD.md` was revised after an external methods review, approved by the
   channel owner and committed with the frozen confirmation ID list before any
   confirmation solve time was read. Its 10% line predates the pilot's first
   solve time.
3. Its pre-confirmation simulation gate **failed**: the registered bootstrap
   interval would have produced a false "belief fails" 96.5% of the time at a
   true 10% effect. The failure was committed before any confirmation data.
4. Amendment 1 (a re-centred interval) was investigated without confirmation
   data, passed a revised gate on the original simulations and an independent
   replication, was approved by the owner and committed. Only then was the
   confirmation data opened.

The commits for each step are listed in "About this history" below.

## Data

Results come from the [World Cube Association results export](https://www.worldcubeassociation.org/export/results)
dated 2026-09-30. The export (379 MB) is not committed because of its size;
`data/wca-manifest.json` gives its address and SHA-256, and the analysis
refuses to run on a file that does not match. The WCA's terms require this
notice:

> This information is based on competition results owned and maintained by
> the World Cube Assocation, published at https://worldcubeassociation.org/results
> as of September 30, 2026.

(The notice's spelling is the WCA's own.)

The quotes, dates and regulations the script cites were checked against saved
copies of their web pages. Those pages belong to their publishers (WIRED,
Ruwix, the WCA and others) and are **not redistributed** here;
`analysis/claim_sources/manifest.json` lists each page's address, retrieval
date and SHA-256. To rerun the quote checks, save the listed pages to the
paths in the manifest; `analysis/verify_claims.py` checks every file against
its hash and reports a mismatch.

## Running the checks

```sh
python3 -m venv .venv && .venv/bin/pip install duckdb polars pandas pyarrow numpy scipy statsmodels numba
# save the export to studio/episodes/scramble-luck/data/raw/ and check its hash, then:
.venv/bin/python studio/episodes/scramble-luck/analysis/verify_claims.py
python3 studio/tools/story_check.py studio/episodes/scramble-luck
```

The full analysis (`analysis/snapshot.py`, `cross.py`, `gate.py`, `analyze.py`)
takes a few hours on a 10-core laptop. Rendering needs Node and a headless
Chromium; narration needs Apple Silicon and `studio/tools/requirements-voice.txt`.

## How it was made

The research was run by Claude (Anthropic) orchestrating two Codex models:
Sol 6.1 built the analysis, scenes and page; Astra did the blind re-derivation,
the red-team reviews and the amendment investigation. A first script draft
came from a local Qwen model and was rewritten and fact-checked. Every
decision that changed the method was approved by the channel owner.

## About this history

This repository's history was filtered from the working repository to keep
only this episode and what it depends on; commit order and dates are
unchanged, so hashes differ from those quoted inside `METHOD.md` and
`HANDOFF.md`. The table below maps them.

Code is under the MIT license (`LICENSE`). Statistics are facts from the WCA's
results, published with the notice above.
