"""Compare sealed blind values to Sol; no changes to either analysis's estimates.
Run with ideation/.venv/bin/python studio/episodes/scramble-luck/analysis/compare_recheck.py
"""
from pathlib import Path
import hashlib,json,math
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent; RE=HERE.parent/'recheck'
blind=json.loads((RE/'values.json').read_text());sol=json.loads((HERE/'results.json').read_text())
seal=json.loads((RE/'phase1-seal.json').read_text())
for name,expected in seal['files'].items():
 assert hashlib.sha256((RE/name).read_bytes()).hexdigest()==expected, 'Blind artifact changed: '+name
mc=json.loads((RE/'monte-carlo-tolerance.json').read_text());diagnosis=json.loads((RE/'era-reference-diagnostic.json').read_text())
def get(path):
 x=sol
 for k in path.split('.'):
  x=x[int(k)] if isinstance(x,list) else x[k]
 return x
M={}
def bind(own,path,kind='point'):
 M[own]=(get(path),path,kind)
S='coverage.structural.';O='coverage.outcome.';P='primary.';A='aggregation_and_tier_sensitivities.'
for k,path in {'finals':'eligible_finals','attempt_slots':'included_attempt_slots','dnf':'dnf_slots','dns':'dns_slots','solver_results':'solver_final_incidence_rows','eligible_solver_seasons':'structurally_eligible_person_years','extra_pool_finals':'extra_pool_finals','universe_exploration_competitions':'split_counts.exploration','universe_confirmation_competitions':'split_counts.confirmation'}.items():bind(k,S+path,'count')
for k,path in {'successes':'successful_cells','no_success_seasons':'no_success_seasons','unidentified_extrema':'unidentified_extrema','available_extrema':'available_extrema','tier_missing_reference':'missing_skill_references_informative_solver_rounds'}.items():bind(k,O+path,'count')
ex={'other_event':'other_event_results','nonfinal':'nonfinal_333_results','invalid_format':'invalid_format_final_results','multigroup_or_no_regular_group_results':'multigroup_results','missing_schedule_results':'missing_schedule_results','incomplete_duplicate_slots_results':'incomplete_or_duplicate_slots_results','invalid_status_results':'invalid_status_results_after_slot_gate','ambiguous_regular_schedule_results':'invalid_regular_schedule_results'}
for own,path in ex.items():bind('exclusion_'+own,S+'exclusions_mutually_exclusive_result_counts.'+path,'count')
M['scope_results']=(sum(get(S+'exclusions_mutually_exclusive_result_counts').values())+get(S+'solver_final_incidence_rows'),'sum(coverage.structural.exclusions_mutually_exclusive_result_counts) + coverage.structural.solver_final_incidence_rows','count')
M['under_two_success_rows']=(get(O+'no_success_solver_rounds')+get(O+'singleton_success_solver_rounds'),'coverage.outcome.no_success_solver_rounds + singleton_success_solver_rounds','count')
# Total solver count is absent from results.json: use Sol's own input table explicitly.
g=pd.read_parquet(HERE.parent/'data/derived/structure.parquet',columns=['person_id'])
M['solvers']=(int(g.person_id.nunique()),'data/derived/structure.parquet: nunique(person_id) [supplementary source]','count')
bind('R',P+'R_geometric_person_year.estimate');bind('R_arithmetic',A+'arithmetic_mean_R.estimate');bind('R_solver_weighted',A+'per_solver_weighted_R.estimate')
bind('eligible_season_solvers',A+'per_solver_weighted_R.n.solvers','count')
bind('tier_F',P+'F_tier_aware.estimate');bind('tier_gamma_share',P+'tier_interaction_share_gamma_over_D.estimate')
for k,path in {'tau':'tau','gamma':'gamma','D':'D','b_fast':'fast_shared_variance','b_slow':'slow_shared_variance','e_fast':'fast_residual_variance','e_slow':'slow_residual_variance','c':'cross_covariance'}.items():bind('tier_'+k,P+'signed_variance_components.'+path+'.estimate')
bind('tier_finals',P+'coverage.tier_supported_finals','count');bind('tier_successes',P+'coverage.tier_successful_cells','count')
for era in ['2019_2022','2023_2025']:
 p='robustness.era_'+era+'.'
 for suffix,path,kind in [('F','F_tier_aware.estimate','point'),('gamma_share','tier_interaction_share_gamma_over_D.estimate','point'),('finals','coverage.tier_supported_finals','count'),('successes','coverage.tier_successful_cells','count'),('R','R_geometric_person_year.estimate','point')]:bind(era+'_'+suffix,p+path,kind)
bind('R_ci95',P+'R_geometric_person_year.interval_95','mc_centered')
bind('R_bootstrap_raw_ci95',P+'R_geometric_person_year.raw_percentile_interval_95','mc_raw')
bind('R_fixed_ci95',P+'R_fixed_selection_A_sensitivity.interval_95','mc_fixed')
bind('R_bootstrap_mean_log',P+'R_geometric_person_year.bootstrap_mean','mc_mean')
bind('R_bootstrap_displacement',P+'R_geometric_person_year.bootstrap_mean_displacement','mc_mean')
bind('bootstrap_valid_draws',P+'R_geometric_person_year.valid_draws','count')
bind('bootstrap_absent_seasons_mean','bootstrap_exposure.absent_seasons.mean','mc_absent')
M['bootstrap_distinct_competitions_mean']=(get('bootstrap_exposure.distinct_competition_fraction.mean')*get(S+'eligible_finals'),'bootstrap_exposure.distinct_competition_fraction.mean * coverage.structural.eligible_finals','mc_competitions')
bind('verdict','verdict.outcome','verdict')
bind('dnf_started_rate','DNF_secondary.started_attempt_DNF_rate.estimate')
if get(S+'extra_pool_finals')==get(S+'eligible_finals'):
 M['extra_pool_solver_results']=(get(S+'solver_final_incidence_rows'),'all eligible finals have extra pools; coverage.structural.solver_final_incidence_rows','count')
M['complete_success_results']=(sum(p['n'] for p in get(S+'status_patterns') if all(p['status'+str(j)]==1 for j in range(1,6))),'coverage.structural.status_patterns: five success statuses','count')
records=[]
for key,(other,source,kind) in M.items():
 own=blind[key]['value'];row={'key':key,'blind':own,'sol':other,'sol_path':source,'comparison':kind}
 if kind=='count':ok=own==other;row['tolerance']='exact integer equality'
 elif kind=='verdict':ok=own.casefold()==other.casefold();row['tolerance']='case-normalized exact equality'
 elif kind=='point':ok=bool(np.all(np.isclose(own,other,rtol=1e-6,atol=0)));row['tolerance']='1e-6 relative, zero absolute tolerance'
 else:
  mckey={'mc_centered':'centered_endpoint_se','mc_raw':'raw_endpoint_se','mc_fixed':'fixed_endpoint_se','mc_mean':'mean_logR_se','mc_absent':'absent_mean_se','mc_competitions':'competition_mean_se'}[kind]
  tol=4*math.sqrt(2)*np.array(mc[mckey]);diff=np.abs(np.log(own)-np.log(other)) if kind in ['mc_centered','mc_raw','mc_fixed'] else np.abs(np.array(own)-other)
  ok=bool(np.all(diff<=tol));row['tolerance']=tol.tolist();row['difference_on_comparison_scale']=diff.tolist();row['scale']='log ratio' if kind in ['mc_centered','mc_raw','mc_fixed'] else 'native';row['mc_reason']='Equivalent multinomial algorithms consume the seeded RNG differently: blind rng.multinomial; Sol bincount(rng.integers). Tolerance is four combined Monte Carlo SEs, estimated from blind draws only.'
 row['status']='match' if ok else 'mismatch'
 if not ok:
  era=key[:9];suffix=key[10:]
  if era in diagnosis and suffix in diagnosis[era]:
   row['cause']='Blind recheck retained cross-era skill references; Sol masks reference candidates to each era (DEVIATIONS.md decision 9, analyze.py task_subsets, engine.py refs_tiers). METHOD does not explicitly specify this boundary choice. Sol documented its choice before opening outcomes.'
   row['attribution']='recheck split-reference interpretation; not a primary estimator discrepancy'
   row['resolution']=diagnosis[era][suffix]
 records.append(row)
unmapped=[]
for k in blind.keys()-M.keys():
 unmapped.append({'key':k,'blind':blind[k]['value'],'status':'not_reported_by_sol','reason':'No corresponding quantity in results.json; not counted as a match or mismatch.'})
report={'phase1_seal':seal,'sol_results_sha256':hashlib.sha256((HERE/'results.json').read_bytes()).hexdigest(),'comparison_units':'One named value per entry; a two-endpoint interval is one comparison. No duplicate counting of n fields.','monte_carlo_tolerance':mc,'summary':{'matched':sum(x['status']=='match' for x in records),'mismatched':sum(x['status']=='mismatch' for x in records),'not_reported_by_sol':len(unmapped),'total_blind_values':len(blind)},'comparisons':records,'not_reported':sorted(unmapped,key=lambda x:x['key'])}
(HERE/'recheck_report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print(json.dumps(report['summary']))
for x in records:
 if x['status']=='mismatch':print(x['key'],x['blind'],'vs',x['sol'],'harmonized matches:',x.get('resolution',{}).get('matches'))
