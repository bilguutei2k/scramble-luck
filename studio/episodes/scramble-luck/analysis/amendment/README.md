# Outcome-blind amendment investigation

All commands run from the repository root using `ideation/.venv/bin/python`.
All new artifacts are in this directory. No original method, engine or gate is
edited. No confirmation solve times are opened. The only observational data
queried are the `incidence` identifiers/statuses in read-only `structure.duckdb`;
training successes become the integer 1, never a time. Original synthetic gate
records and integrated truths are reused for paired comparisons. Frozen pilot
hyperparameters are imported by the existing `common.py`.

```sh
ideation/.venv/bin/python studio/episodes/scramble-luck/analysis/amendment/evaluate.py benchmark
ideation/.venv/bin/python studio/episodes/scramble-luck/analysis/amendment/verify.py
ideation/.venv/bin/python studio/episodes/scramble-luck/analysis/amendment/evaluate.py calibrate --reps 10000
ideation/.venv/bin/python studio/episodes/scramble-luck/analysis/amendment/evaluate.py run
ideation/.venv/bin/python studio/episodes/scramble-luck/analysis/amendment/evaluate.py run --case large_shared --reps 20 --draws 2000 --output stability.jsonl
ideation/.venv/bin/python studio/episodes/scramble-luck/analysis/amendment/evaluate.py run --case boundary --reps 20 --draws 2000 --output stability.jsonl
ideation/.venv/bin/python studio/episodes/scramble-luck/analysis/amendment/summarize.py
```

`run` checkpoints each completed dataset and resumes without duplicating its
case/replicate/draw-count key. Calibration rewrites its own integration output.
Ten worker processes use one numerical-library thread each. Do not run multiple
ten-worker commands concurrently. `benchmark.json` gives measured single-worker
time and initial projection; completed `*-timing.json` files give actual wall time.

Read `EVALUATION-PLAN.md` for candidate definitions, `RESULTS.md` / `results.csv`
for comparisons, `summary.json` for binomial and truth-integration uncertainty,
`replicates.jsonl` for dataset-level diagnostics, and `endpoint-stability.json`
for nested draw-count checks. `AMENDMENT-1.md` is a draft for registration, not
an automatic change to the committed contract or permission to open outcomes.

CGM reference: Cameron, Gelbach and Miller, *Robust Inference With Multiway
Clustering*, JBES 29(2), 2011, 238–249,
https://cameron.econ.ucdavis.edu/research/JBESpaper2009version.pdf.
The scalar intercept-only sandwich adds solver and competition cluster-score
meats and subtracts their intersection. Applied here to generated, selected
peer contrasts, that formula is a candidate assessed by simulation, not a
general theorem covering the selection and shared-peer dependence. The D
alternative omits the nonnegative overlap subtraction and is wider by design.
