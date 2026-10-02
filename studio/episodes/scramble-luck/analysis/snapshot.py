#!/usr/bin/env python3
"""Verify immutable inputs and materialize sign-only confirmation structure.

No positive confirmation magnitudes are selected or stored in structural tables.
Extracted source bytes are hashed, never displayed. Run with ideation/.venv/bin/python.
"""
import json, zipfile, shutil, hashlib
import duckdb
from common import OUT, EP, DERIVED, FROZEN, sha, dump, progress, NOTICE, code_hashes

def main():
    DERIVED.mkdir(parents=True, exist_ok=True)
    m = json.loads((EP / 'data/wca-manifest.json').read_text())
    archive = EP / m['local_path']
    assert archive.stat().st_size == m['bytes']
    assert sha(archive) == m['sha256']
    lists = {}
    for label in ('exploration', 'confirmation'):
        p = EP / m['split'][label + '_ids']
        assert sha(p) == m['split'][label + '_ids_sha256']
        ids = p.read_text().splitlines()
        assert ids == sorted(set(ids)) and p.read_bytes().endswith(b'\n')
        assert all((int(hashlib.sha256(s.encode()).hexdigest(), 16) % 5 == 0)
                   == (label == 'exploration') for s in ids)
        lists[label] = ids
    assert not set(lists['exploration']) & set(lists['confirmation'])
    assert len(lists['exploration']) == 3756 and len(lists['confirmation']) == 15015
    raw = DERIVED / 'source'; raw.mkdir(exist_ok=True)
    verified = {}
    with zipfile.ZipFile(archive) as z:
        for row in FROZEN['sources']['files'][1:]:
            name = row['path'].split('/')[-1]; p = raw / name
            if not p.exists():
                with z.open(name) as src, p.open('wb') as dst: shutil.copyfileobj(src, dst)
            assert p.stat().st_size == row['bytes'] and sha(p) == row['sha256'], name
            verified[name] = row['sha256']
    progress('Step 1: ZIP and both lists verified; disjoint original-ID hash partition verified; all named source hashes verified.')
    c = duckdb.connect(str(DERIVED / 'structure.duckdb'))
    c.execute("SET threads=10; SET memory_limit='5GB'")
    # all_varchar prevents unrelated results.best/average from being decoded as outcomes.
    def source(name):
        return f"read_csv('{raw / ('WCA_export_' + name + '.tsv')}', delim='\\t', header=true, all_varchar=true, quote='', nullstr='')"
    for label, ids in lists.items():
        c.execute(f'CREATE OR REPLACE TABLE {label}_ids(id VARCHAR)')
        c.executemany(f'INSERT INTO {label}_ids VALUES (?)', [(x,) for x in ids])
    c.execute(f'''CREATE OR REPLACE TABLE competitions AS SELECT id, CAST(year AS INTEGER) AS year,
                 CAST(month AS INTEGER) AS month, CAST(day AS INTEGER) AS day FROM {source('competitions')}''')
    assert set(x[0] for x in c.execute('SELECT id FROM competitions').fetchall()) == set(lists['exploration'] + lists['confirmation'])
    c.execute(f'''CREATE OR REPLACE TABLE round_types AS SELECT id, CAST(final AS INTEGER) final FROM {source('round_types')}''')
    c.execute(f'''CREATE OR REPLACE TABLE results_structure AS SELECT r.id result_id,r.competition_id,
       r.round_type_id,r.event_id,r.format_id,r.person_id,co.year,co.month,co.day,rt.final,
       cf.id IS NOT NULL confirmation FROM {source('results')} r JOIN competitions co ON co.id=r.competition_id
       JOIN round_types rt ON rt.id=r.round_type_id LEFT JOIN confirmation_ids cf ON cf.id=r.competition_id''')
    c.execute('''CREATE OR REPLACE TABLE candidates AS SELECT * FROM results_structure
        WHERE event_id='333' AND final=1 AND format_id='a'
        AND ((confirmation AND year BETWEEN 2019 AND 2025) OR (NOT confirmation AND year<2019))''')
    c.execute(f'''CREATE OR REPLACE TABLE schedules AS SELECT s.competition_id,s.round_type_id,
       s.group_id,CAST(s.is_extra AS INTEGER) is_extra,CAST(s.scramble_num AS INTEGER) scramble_num,s.scramble
       FROM {source('scrambles')} s JOIN (SELECT DISTINCT competition_id,round_type_id FROM candidates) r
       USING(competition_id,round_type_id) WHERE s.event_id='333' ''')
    c.execute('''CREATE OR REPLACE TABLE schedule_checks AS SELECT competition_id,round_type_id,
       count(DISTINCT group_id) FILTER(WHERE is_extra=0) regular_groups,
       count(*) FILTER(WHERE is_extra=0) regular_rows,
       count(DISTINCT scramble_num) FILTER(WHERE is_extra=0 AND scramble_num BETWEEN 1 AND 5 AND length(trim(scramble))>0) valid_numbers,
       count(*) FILTER(WHERE is_extra=1) extra_pool_rows FROM schedules GROUP BY ALL''')
    c.execute('''CREATE OR REPLACE TABLE mapped AS SELECT r.*,s.extra_pool_rows FROM candidates r
       JOIN schedule_checks s USING(competition_id,round_type_id)
       WHERE regular_groups=1 AND regular_rows=5 AND valid_numbers=5''')
    # The only confirmation expression involving attempt.value is this categorical projection.
    c.execute(f'''CREATE OR REPLACE TABLE attempt_status AS SELECT a.result_id,CAST(a.attempt_number AS INTEGER) attempt_number,
       CASE WHEN CAST(a.value AS BIGINT)>0 THEN 1 WHEN a.value='-1' THEN -1
            WHEN a.value='-2' THEN -2 WHEN a.value='0' THEN 0 ELSE -99 END status
       FROM {source('result_attempts')} a JOIN mapped r ON r.result_id=a.result_id''')
    c.execute('''CREATE OR REPLACE TABLE attempt_checks AS SELECT result_id,count(*) slots,
       count(DISTINCT attempt_number) FILTER(WHERE attempt_number BETWEEN 1 AND 5) valid_numbers,
       count(*) FILTER(WHERE status IN (0,-99)) invalid_statuses FROM attempt_status GROUP BY result_id''')
    c.execute('''CREATE OR REPLACE TABLE eligible AS SELECT r.* FROM mapped r JOIN attempt_checks a USING(result_id)
       WHERE slots=5 AND valid_numbers=5 AND invalid_statuses=0''')
    cols = ','.join(f'max(status) FILTER(WHERE attempt_number={j}) status{j}' for j in range(1,6))
    c.execute(f'''CREATE OR REPLACE TABLE incidence AS SELECT r.*,{cols} FROM eligible r JOIN attempt_status a USING(result_id) GROUP BY ALL''')
    c.execute('''CREATE OR REPLACE TABLE included_scrambles AS SELECT DISTINCT s.* FROM schedules s
        JOIN (SELECT DISTINCT competition_id,round_type_id FROM eligible WHERE confirmation) r USING(competition_id,round_type_id) WHERE is_extra=0''')
    def count(sql): return c.execute(sql).fetchone()[0]
    exclusions = {
      'other_event_results':count("SELECT count(*) FROM results_structure WHERE confirmation AND year BETWEEN 2019 AND 2025 AND event_id!='333'"),
      'nonfinal_333_results':count("SELECT count(*) FROM results_structure WHERE confirmation AND year BETWEEN 2019 AND 2025 AND event_id='333' AND final!=1"),
      'invalid_format_final_results':count("SELECT count(*) FROM results_structure WHERE confirmation AND year BETWEEN 2019 AND 2025 AND event_id='333' AND final=1 AND format_id!='a'"),
      'missing_schedule_results':count('SELECT count(*) FROM candidates r LEFT JOIN schedule_checks s USING(competition_id,round_type_id) WHERE confirmation AND s.competition_id IS NULL'),
      'multigroup_results':count('SELECT count(*) FROM candidates JOIN schedule_checks USING(competition_id,round_type_id) WHERE confirmation AND regular_groups!=1'),
      'invalid_regular_schedule_results':count('SELECT count(*) FROM candidates JOIN schedule_checks USING(competition_id,round_type_id) WHERE confirmation AND regular_groups=1 AND (regular_rows!=5 OR valid_numbers!=5)'),
      'incomplete_or_duplicate_slots_results':count('SELECT count(*) FROM mapped r LEFT JOIN attempt_checks a USING(result_id) WHERE confirmation AND (slots IS NULL OR slots!=5 OR valid_numbers!=5)'),
      'invalid_status_results_after_slot_gate':count('SELECT count(*) FROM mapped JOIN attempt_checks USING(result_id) WHERE confirmation AND slots=5 AND valid_numbers=5 AND invalid_statuses>0')}
    panels = c.execute('SELECT competition_id,round_type_id,year,count(*) panel_size,max(extra_pool_rows) extra_pool_rows FROM eligible WHERE confirmation GROUP BY ALL ORDER BY competition_id,round_type_id').fetchdf()
    panels.to_parquet(DERIVED / 'panels.parquet', index=False)
    c.execute(f"COPY (SELECT * FROM incidence WHERE confirmation ORDER BY competition_id,round_type_id,person_id,result_id) TO '{DERIVED / 'structure.parquet'}' (FORMAT PARQUET)")
    c.execute(f"COPY (SELECT * FROM included_scrambles ORDER BY competition_id,round_type_id,scramble_num) TO '{DERIVED / 'scrambles.parquet'}' (FORMAT PARQUET)")
    # Exploration values ONLY, bounded by membership and pre-2019 eligibility in the join.
    wide = ','.join(f'max(CAST(a.value AS BIGINT)) FILTER(WHERE CAST(a.attempt_number AS INTEGER)={j}) v{j}' for j in range(1,6))
    c.execute(f"COPY (SELECT r.*,{wide} FROM {source('result_attempts')} a JOIN eligible r ON a.result_id=r.result_id WHERE NOT r.confirmation GROUP BY ALL ORDER BY competition_id,round_type_id,person_id,result_id) TO '{DERIVED / 'training.parquet'}' (FORMAT PARQUET)")
    patterns = c.execute('SELECT status1,status2,status3,status4,status5,count(*) n FROM incidence WHERE confirmation GROUP BY ALL ORDER BY ALL').fetchdf().to_dict('records')
    statuses = c.execute('SELECT status,count(*) FROM attempt_status JOIN eligible USING(result_id) WHERE confirmation GROUP BY status').fetchall()
    n = count('SELECT count(*) FROM eligible WHERE confirmation')
    seasons = count('SELECT count(*) FROM (SELECT person_id,year,count(DISTINCT competition_id) n FROM eligible WHERE confirmation GROUP BY ALL HAVING n>=5)')
    out = {'source_notice':NOTICE,'positive_confirmation_times_read':False,'method_sha256':sha(EP/'METHOD.md'),
      'archive_sha256':m['sha256'],'verified_file_hashes':verified,'split_counts':{k:len(v) for k,v in lists.items()},
      'eligible_finals':len(panels),'solver_final_incidence_rows':n,'included_attempt_slots':5*n,
      'structurally_eligible_person_years':seasons,'scheduled_mapped_finals_before_status_exclusions':count('SELECT count(*) FROM (SELECT DISTINCT competition_id,round_type_id FROM mapped WHERE confirmation)'),
      'successful_slots_sign_only':dict(statuses).get(1,0),'dnf_slots':dict(statuses).get(-1,0),'dns_slots':dict(statuses).get(-2,0),
      'singleton_success_panels':sum(x['n'] for x in patterns if sum(x[f'status{j}']==1 for j in range(1,6))==1),
      'no_success_panels':sum(x['n'] for x in patterns if all(x[f'status{j}']!=1 for j in range(1,6))),
      'extra_pool_finals':int((panels.extra_pool_rows>0).sum()),'panel_size_counts':{str(k):int(v) for k,v in panels.panel_size.value_counts().sort_index().items()},
      'year_coverage':panels.groupby('year').agg(finals=('panel_size','size'),solver_finals=('panel_size','sum')).reset_index().to_dict('records'),
      'status_patterns':patterns,'exclusions_mutually_exclusive_result_counts':exclusions,'code_sha256':code_hashes()}
    dump('coverage.json', out)
    c.close()
    progress(f'Step 1 complete: {len(panels):,} eligible confirmation finals, {5*n:,} sign-only slots, {seasons:,} structural person-years. coverage.json and structural bulk files saved; no positive confirmation times read.')

if __name__ == '__main__': main()
