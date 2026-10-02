#!/usr/bin/env python3
"""Targeted engine equivalence and analytic formula checks; no real times."""
import evaluate as e
import numpy as np
from engine import Dataset
import hashlib, json

def main():
    e.initialize()
    checks=[]
    for case in e.gate.CASES:
        arrays=e.gate.generate(e.ST,case,17,arrays_only=True)
        fast=e.FastR(*arrays); full=Dataset(e.ST,*arrays)
        point=full.run(details=True)
        assert np.isclose(fast.point,point['logR'],atol=1e-14,rtol=0)
        assert np.array_equal(fast.rows,point['rows'])
        assert abs(fast.oracle()-full.run(oracle=True)['logR'])<1e-14
        one=fast.draw(np.ones(e.ST.C),np.ones(e.ST.S),np.ones(e.ST.TC))
        # Both agree with refitted beta; frozen beta returns original point.
        assert abs(one[0]-one[1])<1e-14
        assert abs(one[2]-fast.point)<1e-14
        rng=np.random.default_rng(e.SEED); errors=[]
        for _ in range(5):
            weights=e.ST.weights(rng)
            errors.append(abs(fast.draw(*weights)[0]-full.run(*weights)['logR']))
        assert max(errors)<1e-14
        # Independent group-score sum, including full solver × competition
        # intersection (not just HC0 if repeated pairs ever occur).
        residual=fast.x-fast.point; n=len(residual)
        terms=[]
        s=e.ST.sidx[fast.rows];c=e.ST.cidx[fast.rows]
        for labels in (s,c,list(zip(s.tolist(),c.tolist()))):
            buckets={}
            for label,r in zip(labels,residual):buckets[label]=buckets.get(label,0.)+r
            g=len(buckets);terms.append(g/(g-1)*sum(x*x for x in buckets.values())/n**2)
        v=fast.analytic()['variance_terms']
        assert np.allclose(terms,[v['solver'],v['competition'],v['intersection']],atol=1e-18,rtol=1e-12)
        assert abs(v['CGM']-(terms[0]+terms[1]-terms[2]))<1e-18
        checks.append({'case':case,'max_full_engine_draw_difference':max(errors),'pass':True})
    paths=[e.HERE.parent.parent/'METHOD.md']+[e.HERE.parent/n for n in
          ('GATE.md','DEVIATIONS.md','SIMULATION_DESIGN.md','engine.py','gate.py','common.py')]
    paths += [e.DERIVED/'structure.duckdb',e.DERIVED/'panels.parquet',e.HERE.parent/'population-truth.json']
    hashes={str(p.relative_to(e.HERE.parent.parent)):hashlib.file_digest(p.open('rb'),'sha256').hexdigest() for p in paths}
    e.save('verification.json',{'checks':checks,'input_sha256':hashes,
        'structure_only_reads':'incidence table from read-only structure.duckdb; training v columns are statuses',
        'confirmation_outcome_magnitudes_read':False})
    print(json.dumps(checks))

if __name__=='__main__':main()
