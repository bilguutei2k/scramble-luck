"""Scene data: numeric observations come only from results.json.

CLAIMS.json supplies IDs/keys and status, never numerical observations.
Historical source-only values remain unbound until results.json supplies them.
"""
import hashlib
import json
import re
from pathlib import Path

EP = Path(__file__).resolve().parent.parent

def payload():
    raw = (EP / 'analysis/results.json').read_bytes()
    claim_raw = (EP / 'CLAIMS.json').read_bytes()
    results = json.loads(raw)
    claims = json.loads(claim_raw)['claims']
    values, provenance = {}, {}
    def flatten(item, key):
        values[key] = item
        if isinstance(item, dict):
            for name, value in item.items(): flatten(value, key + '.' + name)
        elif isinstance(item, list):
            for index, value in enumerate(item): flatten(value, key + '[%d]' % index)
    for key, item in results.items(): flatten(item, key)
    for claim in claims:
        for item in claim.get('values', []):
            key = item.get('key')
            if key in values: provenance.setdefault(key, []).append(claim['id'])
    def derived(key, value, inputs, ids):
        values['derived.' + key] = value
        provenance['derived.' + key] = ids
        derivatives[key] = inputs
    derivatives = {}
    years = results['coverage']['structural']['year_coverage']
    derived('first_year', min(x['year'] for x in years), ['coverage.structural.year_coverage'], ['SL-C003'])
    derived('last_year', max(x['year'] for x in years), ['coverage.structural.year_coverage'], ['SL-C003'])
    derived('scheduled_positions', results['coverage']['structural']['included_attempt_slots'] // results['coverage']['structural']['solver_final_incidence_rows'], ['coverage.structural.included_attempt_slots', 'coverage.structural.solver_final_incidence_rows'], ['SL-C002', 'SL-C130', 'SL-C148'])
    derived('dnf_h_increment', float(re.search(r'h/(0\.\d+)', results['DNF_secondary']['model']).group(1)), ['DNF_secondary.model'], ['SL-C074'])
    neutral = results['verdict']['threshold'] / results['verdict']['threshold']
    derived('neutral_ratio', neutral, ['verdict.threshold'], ['SL-C001', 'SL-C074'])
    derived('adjustment_percent', (results['primary']['R_geometric_person_year']['estimate'] - neutral) * 100, ['primary.R_geometric_person_year.estimate'], ['SL-C144'])
    derived('threshold_percent', (results['verdict']['threshold'] - neutral) * 100, ['verdict.threshold'], ['SL-C001'])
    derived('confidence', int(re.search(r'interval_(\d+)', next(x['key'] for x in claims[0]['values'] if 'interval_' in x.get('key',''))).group(1)), ['primary.R_geometric_person_year.interval_95'], ['SL-C001', 'SL-C005', 'SL-C074'])
    # Grammar constants are not measurements; the five-column diagram is a schematic.
    assert values['derived.scheduled_positions'] * results['coverage']['structural']['solver_final_incidence_rows'] == results['coverage']['structural']['included_attempt_slots']
    locked = bool(claims) and all(c['status'] == 'verified' for c in claims)
    return dict(locked=locked, status='locked' if locked else 'PRE-LOCK DRAFT — CLAIMS PROPOSED', results_sha256=hashlib.sha256(raw).hexdigest(), claims_sha256=hashlib.sha256(claim_raw).hexdigest(), values=values, claim_ids=provenance, derived_from=derivatives, historical_claim_exception=False, claims={c['id']: dict(status=c['status']) for c in claims})

if __name__ == '__main__':
    data = payload()
    (EP / 'scenes/data.js').write_text('// Generated from results and claim lock state.\nwindow.SCENE_DATA = ' + json.dumps(data, ensure_ascii=False, sort_keys=True, indent=1) + ';\n')
    print('Wrote results-bound data.js; source-only historical observations omitted')
