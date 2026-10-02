# S1 exploration slice — locked before outcome analysis

Exact user rule: **Competitions whose int(sha256(competition_id).hexdigest(),16) % 5 == 0 (a 20% hashed sample of all WCA competitions, every year). The other 80% are confirmatory and must not be used for outcome analysis. Within the slice, use 3x3 rounds where attempts can be mapped to scrambles (single scramble group, five attempts); also report how much of the confirmatory data meets that condition (outcome-blind count).**

```python
def in_slice(competition_id: str) -> bool:
    return int(hashlib.sha256(competition_id.encode('utf-8')).hexdigest(), 16) % 5 == 0
```

Implemented in `pilot.py:in_slice` and `prepare`. All original IDs in the frozen competitions table are eligible for hashing, including cancelled / no-results competitions. No year limit. UTF-8, no normalization. Manifest: `exploration-competition-ids.txt`, sorted lexicographically, one ID per line, LF terminated.

- All competition IDs: 18,771; exploration: 3,756; confirmation: 15,015.
- SHA-256 of exploration ID list: `b5f6426bffbbf01c4d742cbe65f083cb4cbb5a134a5b60c3fe9fa312d028b7a4`.
- Source: https://exports.worldcubeassociation.org/results/WCA_export_v2_273_20260930T000036Z.tsv.zip; metadata date: 2026-09-30 00:00:36 UTC. Raw hashes: `source-manifest.json`.

## Outcome-blind row counts

All 3x3 results / attempt-row presence:
```json
[
  {
    "explore": false,
    "result_rows": 1501727,
    "attempt_rows": 7495038.0,
    "rounds": 34992,
    "final_result_rows": 182684,
    "final_rounds": 12357
  },
  {
    "explore": true,
    "result_rows": 369569,
    "attempt_rows": 1845196.0,
    "rounds": 8702,
    "final_result_rows": 45341,
    "final_rounds": 3077
  }
]
```
Single-group, exactly five regular scramble numbers 1–5, average-of-five result, exactly five attempt rows numbered 1–5:
```json
[
  {
    "explore": false,
    "is_final": false,
    "result_rows": 24826,
    "attempt_rows": 124130,
    "competitions": 459,
    "rounds": 556,
    "solvers": 11299,
    "rounds_with_extra_pool": 552
  },
  {
    "explore": false,
    "is_final": true,
    "result_rows": 95877,
    "attempt_rows": 479385,
    "competitions": 8014,
    "rounds": 8014,
    "solvers": 17981,
    "rounds_with_extra_pool": 8006
  },
  {
    "explore": true,
    "is_final": false,
    "result_rows": 5871,
    "attempt_rows": 29355,
    "competitions": 102,
    "rounds": 134,
    "solvers": 3660,
    "rounds_with_extra_pool": 132
  },
  {
    "explore": true,
    "is_final": true,
    "result_rows": 23907,
    "attempt_rows": 119535,
    "competitions": 1996,
    "rounds": 1996,
    "solvers": 9139,
    "rounds_with_extra_pool": 1992
  }
]
```

The membership, schema and these counts were written before selecting any attempt value. Confirmation queries select no value, best, average, rank or record field. Detailed year balance is in `coverage.json`. All time analysis uses only `exploration-attempts.parquet`, created with `WHERE e.explore` inside the SQL scan. No confirmation outcome table is created.

## Mapping limitation

There is no group_id / scramble_id in the results or attempts tables. A unique regular scramble group gives a defensible **scheduled** mapping through attempt_number = scramble_num; it does not verify replacement attempts. Extra scramble rows describe a pool, not usage. `rounds_with_extra_pool` is reported separately. No exact-record attribution will be claimed without external per-attempt audit. Analysis eligibility and successful-time model counts are reported in PILOT.md, separately from this pre-outcome lock.

## Round 5 implementation
Exact round-3 locked membership reused. The extraction function is `rounds/r3/pilot-S1/pilot.py:prepare`, imported by `rounds/r5/pilot-S1/pilot.py:sources` with its output directory redirected here. Round-5 `in_slice` and `load_slice` independently assert membership before any outcome fit. Simulation reads only structural `panel-sizes.csv` first. The held-out 80% remains unused for outcome analysis; only structural counts are read.
