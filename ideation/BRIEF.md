# Idea search: the next investigations

Status: brief for a multi-round idea search run by Claude with Sol 6.1
(`gpt-6.1-sol`) and Astra (`gpt-6-astra`), 2026-09-30.

## The channel so far

"The Fairer Test" makes narrated statistical investigations: one 16:9 video
(8–10 min), 2–4 vertical shorts, and a companion web page that reuses the same
charts and lets a visitor test one meaningful assumption. Every episode runs
the same spine: **belief → obvious answer → flaw → fairer test → verdict**. A
belief that survives the fairer test is as good an ending as one that falls.

Five episodes exist, all sports, all built from small hand-collected tables
(tens to a few thousand rows):

- Is Playoff Jimmy real? (Butler's playoff scoring rise is all minutes; per 36
  he holds steady while most players slip.)
- Is 10 Premier League goals actually average for a forward?
- Defoe has the super-sub record. Who was the better super-sub?
- Did Ronaldo really own the Champions League knockouts?
- Could anyone beat Wilt's 50-point season?

The production contract (see `../docs/project-brief.md`, `../studio/WORKFLOW.md`):
the question, measures and pass/fail rule are written in `METHOD.md` and
committed **before** any data is saved; immutable source snapshots with
SHA-256 manifests; executable analysis; a claim ledger where every number in
the script cites a result key; an independent verifier; a blind re-derivation;
a methods review. Look at one finished episode
(`../studio/episodes/playoff-jimmy/`) to see the standard.

## What the user wants now

The user likes the direction, the design language and the companion pages, and
wants more investigations like them, but with:

1. **More rigorous statistical analysis.** Not just a fairer ratio. Think an
   explicit estimand; an identification strategy that answers the obvious
   confounder; honest uncertainty (bootstrap, permutation, hierarchical
   shrinkage, simulation from a null); control of forking paths (a
   pre-registered confirmatory test, an exploration/confirmation split,
   multiple-comparison control); robustness (specification curves, placebo
   and falsification tests, out-of-sample or out-of-era replication).
2. **Novel findings.** Something a careful search of the literature, the
   press and the data-journalism world (FiveThirtyEight, The Pudding, The
   Economist, NYT Upshot, Our World in Data, academic papers, popular
   blogs/YouTube) does not already show — or a well-known claim whose
   published answer changes under a fairer test or at a new scale. "Big
   dataset, nice charts" is not novel.
3. **Large datasets.** Ideally millions of rows or more (event logs,
   microdata, every game/transaction/record), so the analysis can do things
   small tables can't: condition finely, find natural experiments, replicate
   across eras or populations.
4. **Variety.** Any domain: sports of every kind, games (chess, esports,
   speedrunning), economics and finance, cities and transport, health and
   demography, science and academia, the internet, culture and media,
   language, politics, climate and weather, Mongolia-specific subjects. Any
   kind of analysis: causal designs, forensic statistics, survival models,
   network analysis, changepoints, Bayesian hierarchical models, simulation,
   text analysis, geospatial.

## Hard constraints

- **Data is free and legal** to download and analyse, and its terms allow
  publishing derived statistics in a monetised video. Prefer licences that
  allow redistribution (public domain, CC0, CC-BY, ODbL, ODC-BY, government
  open data) so the companion repository can ship the data; name the licence.
  No scraping that breaks a site's terms; no private or personal data beyond
  what is already published openly; nothing that singles out private people.
- **Feasible on one laptop**: Apple M1 Max, 64 GB RAM, ~500 GB free disk,
  Python (duckdb/polars/pandas/statsmodels/PyMC are installable). A full
  pipeline should run in hours, not weeks.
- **Pre-registrable**: the question and the pass/fail rule can be written
  before the confirmatory data is touched. Pilots in this idea search may only
  touch a declared exploration slice (for example one season, one month, a 5%
  random sample by hashed ID) and must say which slice they used, so a later
  `METHOD.md` can pre-register the confirmatory test on the rest.
- **Video-shaped**: a question a curious non-specialist understands in ten
  seconds; a believable "obvious answer" with a real flaw; a fairer test that
  can be shown in one or two central visuals; a verdict that is interesting
  whichever way it falls; 2–4 standalone sub-claims for shorts; one assumption
  a companion-page visitor could change and watch the answer move.
- **Honest**: no correlation fishing dressed up as a finding; no claims that
  could cause harm if wrong (medical advice, defamation of named people
  without strong evidence). Named public figures and teams are fine when the
  claim is about their public record.

## Scoring rubric (used in every round)

Score 1–5 on each; justify each score in one line.

| Criterion | 5 means |
|---|---|
| Novelty | No published answer found after a real search, or the fairer test plausibly overturns the published one. |
| Rigour | A clear estimand and identification strategy; the main confounder has a convincing answer; uncertainty is quantifiable. |
| Data | ≥ 1M rows (or the full population), free, licence allows redistribution, verified reachable. |
| Hook | A ten-second question many people already have an opinion about. |
| Verdict either way | Both outcomes make a good episode; no outcome depends on a lucky result. |
| Visual | One central chart that carries the turn from obvious answer to fairer test. |
| Feasibility | One laptop, days not weeks, low legal and data-cleaning risk. |
