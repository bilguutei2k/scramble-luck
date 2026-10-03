#!/usr/bin/env python3
"""Post-review full-window era references, using the original saved draws.

Recompute references/tiers on 2019–2025, then mask outcome panels only.
No seasonal estimator or primary checkpoint is changed.
"""
import json
import numpy as np
import analyze as a
from engine import refs_tiers, accumulate, tier_fit
from common import DERIVED, OUT, EP, sha

ERAS = ('era_2019_2022', 'era_2023_2025')

def calculate(ds, st, cw, sw):
    _, tiers, _, _ = refs_tiers(
        ds.means, ds.d, st.ridx, st.cidx, st.sidx, st.years, sw, cw,
        ds.neighbors, ds.nptr, st.round_rows, st.rptr, st.R)
    fast = accumulate(ds.C, ds.z, ds.ss, ds.d, st.ridx, st.sidx, sw, st.R, tiers, 0)
    slow = accumulate(ds.C, ds.z, ds.ss, ds.d, st.ridx, st.sidx, sw, st.R, tiers, 1)
    result = {}
    for name in ERAS:
        mask = st.years <= 2022 if name == ERAS[0] else st.years >= 2023
        cm = cw * np.bincount(st.cidx, weights=mask, minlength=st.C).astype(bool)
        fit = tier_fit(fast, slow, cm[st.round_comp])
        keep = mask & (tiers >= 0) & (sw[st.sidx] > 0) & (cw[st.cidx] > 0)
        result[name] = {
            'F': fit['F'] if fit else None,
            'gamma_over_D': fit['gamma_over_D'] if fit else None,
            'tier_supported_finals': len(np.unique(st.ridx[keep])),
            'tier_successful_cells': int(np.sum(ds.d[keep] + 1)),
        }
    return a.clean(result)

def build(ds, st):
    point = calculate(ds, st, np.ones(st.C), np.ones(st.S))
    weights = [np.load(DERIVED / f'bootstrap-{name}.npy', mmap_mode='r')
               for name in ('competition', 'solver')]
    draws = []
    for b in range(a.DRAWS):
        draws.append({'draw': b, **calculate(ds, st, *[np.array(w[b], float) for w in weights])})
    path = DERIVED / 'analysis-era-full-window.jsonl'
    path.write_text(''.join(json.dumps(d, allow_nan=False) + '\n' for d in draws))
    result = {}
    for name in ERAS:
        p = point[name]
        n = {'tier_supported_finals': p['tier_supported_finals'], 'successful_cells': p['tier_successful_cells']}
        result[name] = {
            'F_tier_aware': a.metric(p['F'], [d[name]['F'] for d in draws], n),
            'tier_interaction_share_gamma_over_D': a.metric(p['gamma_over_D'], [d[name]['gamma_over_D'] for d in draws], n),
            'reference_scope': 'full 2019–2025 confirmation window, ±2 calendar years; era outcome panels only',
            'interval_scope': 'same 2,000 registered competition × solver draws; full-window references recomputed in each draw; separately refitted era tier positions',
        }
    inputs = [DERIVED / n for n in ('structure.parquet', 'confirmation-values.parquet', 'bootstrap-competition.npy', 'bootstrap-solver.npy')]
    report = {'eras': result, 'draw_file': str(path.relative_to(EP)), 'draw_sha256': sha(path),
              'input_sha256': {str(p.relative_to(EP)): sha(p) for p in inputs}, 'code_sha256': sha(__file__)}
    (OUT / 'era-reference-results.json').write_text(json.dumps(report, indent=2) + '\n')
    return result

if __name__ == '__main__':
    a.initialize()
    for name, era in build(a.DS, a.ST).items():
        print(name, json.dumps(era))
