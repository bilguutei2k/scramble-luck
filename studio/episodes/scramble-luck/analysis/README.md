# Scramble luck confirmatory analysis

Contract: ../METHOD.md, commit 8a474d3. Frozen components:
S1-r5-measurement-v1. METHOD's newer interval decision rule takes precedence
over the older pilot's decision rule.

Run from the repository root, in this order:

```sh
ideation/.venv/bin/python studio/episodes/scramble-luck/analysis/snapshot.py
ideation/.venv/bin/python studio/episodes/scramble-luck/analysis/cross.py
ideation/.venv/bin/python studio/episodes/scramble-luck/analysis/verify.py
ideation/.venv/bin/python studio/episodes/scramble-luck/analysis/gate.py --benchmark
ideation/.venv/bin/python studio/episodes/scramble-luck/analysis/gate.py --workers 10
```

Dependencies: duckdb, numpy, pandas, pyarrow, scipy, matplotlib (frozen pilot
comparison), numba. Numerical libraries use one thread per simulation worker.
The raw dated ZIP is verified locally; these scripts fetch no WCA data.

Bulk extracted sources, sign-only incidence, exploration-only training,
scrambles, exact BFS pruning tables and gate checkpoints are in the gitignored
../data/derived/. gate.py resumes completed datasets from checkpoints. The
simulation design and all literal implementation decisions are documented in
SIMULATION_DESIGN.md and DEVIATIONS.md.

Coverage/cross outputs contain structural counts and scramble metrics. Gate
ratios and shares describe **synthetic datasets only**. They are not episode
confirmation estimates. Positive confirmation solve magnitudes stay unopened
until a passing gate report has been committed. If all permitted bootstrap
methods fail, the required endpoint is “inconclusive: uncertainty not
validated” and step 4 is not run.

## Completed run

The validation gate failed. Pigeonhole large-shared coverage was 1%;
competition-only small-shared coverage was 55.5%; solver-only null coverage
was 99.5%, above the fixed 99% ceiling. See GATE.md and gate.json for all
completed processes, diagnostics, numerical truth precision and fallback
rejection stopping. No positive confirmation times were read; step 4 outputs
are intentionally absent under METHOD's stop rule.

The requested `git add` was attempted but the workspace policy prevents
writing `.git/index.lock` (Operation not permitted). No gate commit was created.
The exact requested commit message, including its co-author trailer, is in
COMMIT_MESSAGE.txt. All code and gate reports are ready for a repository writer
with Git filesystem access. CONTEXT.md is concurrent story research, outside
this analysis/gate change, and should be excluded from this commit.

The source's required notice applies to redistributed source-derived tables:

> This information is based on competition results owned and maintained by the
> World Cube Assocation, published at https://worldcubeassociation.org/results
> as of September 30, 2026.
