"""Synthesize existing result keys, freeze model and write pilot.json."""
from pathlib import Path
import json,hashlib,math
import numpy as np
from scipy.stats import norm
from pilot import OUT,ROOT,dump,progress,sha

def pct(x):return f'{100*x:.2f}%'
def ci_pct(ci):return f'{pct(ci[0])}–{pct(ci[1])}'
def read(name):return json.loads((OUT/name).read_text())

def report():
    var=read('variance.json');fit=var['fit'];vc=var['bootstrap_95']['competition_solver'];counts=var['counts']
    sim=read('simulation.json');tsim=read('interaction-simulation.json');sel=read('selection-simulation.json')
    rel=read('reliability.json');inter=read('interaction.json');dnf=read('dnf.json');ext=read('extremes.json')
    cov=read('confirmation-structural-coverage.json') if (OUT/'confirmation-structural-coverage.json').exists() else structural_coverage()
    mapping=read('mapping-sensitivity.json')
    robust=read('robustness.json')
    r10=next(r for r in rel['representative_k_uncertainty'] if r['k']==10)
    structural=next(r for r in cov['season_coverage'] if not r['explore'])
    rci=ext['aggregate_unshrunk_95'];estimate=ext['aggregate_unshrunk_ratio']
    changes=[
      'Use within-solver-round log-time variation as the denominator; do not label between-finalist variation or total population variation as scramble luck.',
      'Retain every successful cell of DNF/DNS panels using exact missing-pattern trace corrections. Analyze DNF as a separate binary component; do not impute a DNF time or claim joint latent-time identification.',
      'Validate finite-peer correction in simulation and show reliability and out-of-sample predictive R² separately. Freeze pre-2019 hyperparameters before 2019–2025 prediction.',
      'For aggregate selected-extreme attribution use unshrunk leave-one-solver-out peer estimates. Retain shrinkage only for individual displays; label its conditional uncertainty and selection bias.',
      'Measure skill-tier interactions using skill estimates from other finals; allow tier-specific residual variance and use competition+solver uncertainty. Method interaction remains untestable without method labels.',
      'Treat attempt-number joins as scheduled mappings. Audit actual replacement use before claiming actual scramble attribution; retain unresolved rows only for a renamed shared scheduled-position estimand. Extra-pool presence cannot certify replacement use or non-use.',
      'Replace the unavailable official-2018 top100 pilot cohort with an explicitly exploratory all-finalist cohort; any confirmatory cohort change must be preregistered and cannot be described as the original test.',
      'Refit training nuisance parameters and reselect minima in uncertainty calculations; keep and disclose the original eligible-season population. Do not present cluster-resampled exposure as the original fixed-exposure race.',
      'Write pilot.json, a complete report, frozen specification, result-key ledger and artifact hashes. The held-out outcomes remain untouched.'
    ]
    se=ext['aggregate_unshrunk_log_se'];threshold=math.log(1.10)
    scenarios=[]
    for label,mult in [('4x competition precision heuristic',4),('18.4x extreme count, independence heuristic',structural['seasons_ge5']/ext['n'])]:
        confirm_se=se/math.sqrt(mult)
        def power(truth):return float(norm.sf((max(threshold,1.96*confirm_se)-math.log(truth))/confirm_se))
        scenarios.append({'scenario':label,'assumed_log_SE':confirm_se,'pass_probability_at_pilot_ratio':power(estimate),
          'power_if_ratio_1_10':power(1.10),'power_if_ratio_1_12':power(1.12)})
    power_note=('Original official-cohort power is not identifiable here: ranking and verified assignment coverage are absent. '
      f'The structural 2019–2025 holdout has 5,017 scheduled-mapped finals, 306,155 attempt rows and {structural["seasons_ge5"]:,} broadly eligible solver-seasons. '
      'Conditional normal approximations using the unshrunk pilot SE and 4x competition precision give a confirmatory log-SE of '
      f'{scenarios[0]["assumed_log_SE"]:.4f}: essentially zero chance to exceed 1.10 at the pilot effect, 50% power exactly at 1.10, and >99.9% at 1.12. '
      'These are sensitivity calculations, not promised power: cohort exposure, dependence, replacement audit and selection change. Structural season eligibility grows about 18x, not 4x.')
    dump('power.json',{'note':power_note,'scenarios':scenarios,'original_cohort':'unavailable','heldout_outcomes_read':False,'structural':cov})
    headline=[
      {'claim':'Shared scheduled-position component of within-solver-round successful log-time variance (exploratory)',
       'value':fit['within_solver_share'],'ci':vc['within_solver_share'],'n':counts['valid_attempts']},
      {'claim':'Unshrunk aggregate median-shared-effect / observed seasonal-minimum time ratio, exploratory broad cohort',
       'value':estimate,'ci':rci,'n':ext['n']},
      {'claim':'Held-out peer log-time R² with 10 peers, pre-2019 model frozen (exploratory)',
       'value':r10['individual_prediction_R2'],'ci':r10['individual_prediction_R2_competition_95'],'n':r10['rounds']},
      {'claim':'Skill-tier interaction variance, unconstrained moment diagnostic (exploratory; negative estimate is sampling noise)',
       'value':inter['model']['interaction_variance'],'ci':inter['competition_solver_bootstrap_95']['interaction_variance'],'n':inter['rounds']}
    ]
    pj={'id':'S1','slice':{'rule':'int(sha256(competition_id.encode("utf-8")).hexdigest(),16) % 5 == 0; all years; identical to rounds/r3/pilot-S1/SLICE.md',
        'competition_ids':3756,'id_list_sha256':'b5f6426bffbbf01c4d742cbe65f083cb4cbb5a134a5b60c3fe9fa312d028b7a4',
        'outcome_final_rounds':counts['rounds'],'attempt_rows':counts['attempt_rows'],'heldout_outcomes_opened':False},
        'headline':headline,'prereg_would_pass':'untestable on slice','power_note':power_note,
        'design_changes':changes,'recommendation':'revise',
        'why':'The small shared component survives DNF retention, tail sensitivity, finite-peer simulation and held-out-peer prediction. The broad seasonal-extreme adjustment is far below 10%, but the original official-cohort claim cannot be tested. Actual replacement assignments and method labels are missing; low split-peer correlation does not establish personal luck. Revise the episode to shared versus unexplained variation and audit mapping before any exact scramble claim.'}
    dump('pilot.json',pj)
    frozen={'id':'S1-r5-measurement-v1','status':'ready for preregistration; not yet committed METHOD.md',
      'confirmation':'All competitions with sha256 UTF-8 ID integer modulo 5 != 0; 2019–2025; no outcomes inspected in this study.',
      'sources':read('source-manifest.json'),'slice_id_sha256':pj['slice']['id_list_sha256'],
      'training':'Pre-2019 mapped finals only in the locked exploration slice; no confirmation outcomes used.',
      'hyperparameters':ext['frozen_pre2019'],'skill_training':'Within-final solver intercepts cancel; skill-tier reference is median log mean of >=2 other eligible finals within +/-2 years, excluding focal competition.',
      'eligibility':'333, round_types.final=1, format a; one non-extra group; exactly five nonmissing regular scramble rows numbered 1–5; five recorded attempt slots 1–5; retain all statuses. For outcome contrasts need >=2 successful cells per solver; singleton/all-failure panels remain in counts and binary failure analysis.',
      'time_model':'log(value/100)=solver-round intercept + frozen global position + shared round-position contrast + independent residual. Demean within available successful cells. Shared Gaussian prior is used only for displayed individual predictions; moments allow non-Gaussian residuals with finite variance.',
      'moment_equations':'C_i=diag(valid)-valid valid^T/m_i; A_r=sum_i C_i; V_r=sum_i C_i(y_i-beta). S_r=sum_i ||C_i(y_i-beta)||²; d_r=sum_i(m_i-1). tau=(sum ||V_r||²-sum S_r)/(sum tr(A_r²)-sum d_r); e=sum S_r/sum d_r-tau. Weighted solver bootstraps replace residual noise trace by A(w²).',
      'predictive_validation':'Predetermine k=2,5,10,20; 30 random whole-solver splits per final, >=k+2 informative solvers. Peer posterior solve (A_peer+e/tau I)^-1 V_peer. Predict target scramble time relative to mean of target solver OTHER successful attempts; target solve is never used in its baseline. Report R² and competition CI. k=2..max and extrapolations descriptive.',
      'primary_endpoint':'Geometric mean estimated median-shared-effect / observed fastest valid time ratio for all eligible solver-seasons with >=5 eligible finals in confirmation, 2019–2025; leave out focal solver; unshrunk pseudoinverse peer contrasts; fixed zero/median symmetric shared-effect counterfactual.',
      'primary_rule':'Material shared scheduled-position advantage passes iff ratio >1.10 and two-way competition/solver bootstrap 95% lower bound >1.00. Otherwise fails; inconclusive if interval spans both 1.00 and 1.10. >=500 eligible finals, >=20,000 attempt rows, >=100 eligible extrema. This is a revised all-finalist estimand, not the verified official-top100 test.',
      'uncertainty':'2,000 competition+solver draws; refit position/training moments on resampled pre-2019 exploration training finals; recompute leave-one-out effects and reselect minima in target competition resamples. Original eligible-season list fixed; report changing exposure separately. Individual Gaussian intervals omit mapping error and selection conditioning.',
      'DNF':'Separate started-attempt binary covariance/risk endpoint, DNS separately. Successful-time estimand conditional on success. Report informative-DNF simulation and complete-case/clipped-log sensitivity; no unidentified latent DNF times.',
      'tier_secondary':'Faster/slower half by other-final skill reference; >=3 informative peers per tier. Separate tier shared variances/residual variances and cross covariance; interaction=(bFast+bSlow-2cov)/4. Signed moments and crossed bootstrap CI; constrain display only. No method claim. Tier test secondary, not proof of personal luck.',
      'mapping_gate':'Actual scramble claim requires independent per-attempt assignment/replacement audit, including extrema. Without audit, preregister a scheduled-position claim only, explicitly including synchronized round conditions and unknown replacement dilution. Do not treat absent extra pool as verified no replacement.',
      'robustness':'Repeat full DNF-retaining model, complete-case sensitivity, log-contrast clipping +/-0.6, periods 2019–2022 and 2023–2025 and leave-year-out. Report all results regardless of sign; no alternate specification rescue. Independent per-solver within-round label permutation is a signal-negative-control; common permutation of whole scramble labels is invariant and is not a valid placebo.',
      'personal_luck':'Unexplained remainder includes execution, solver-by-scramble opportunities, missing skill, penalties and assignment errors. It is not identified personal luck.',
      'selection_caution':'Shrinkage posterior means conditional only on peers are biased for aggregate extrema selected using focal times. Unshrunk aggregates validated under independent-noise simulations; individual displays remain shrunk and labelled.',
      'algorithm_hashes':{f:sha(OUT/f) for f in ['pilot.py','validate.py','report.py']}}
    dump('frozen-model.json',frozen)
    (OUT/'FROZEN_MODEL.md').write_text('# Frozen specification ready for METHOD.md\n\nThis is a revised measurement-validation design. The original official-2018 top-100 test is not replicated. Commit a reviewed METHOD.md before opening confirmation outcomes. Source hashes and exact coefficients are in `frozen-model.json`.\n\n'+
       '\n\n'.join(f'## {k.replace("_"," ").title()}\n\n{v}' for k,v in frozen.items() if k not in ['sources','algorithm_hashes','hyperparameters'])+
       '\n\n## Frozen numerical parameters\n\n```json\n'+json.dumps(frozen['hyperparameters'],indent=2)+'\n```\n')
    rows='\n'.join(f'| {x["scenario"]} | {x["shared_truth"]:.6f} | {x["revised_common_bias"]:+.6f} | {x["competition_sandwich_95_coverage"]:.1%} | {x["split_peer_correlation_mean"]:.3f} |' for x in sim['results'])
    tierrows='\n'.join(f'| {x["scenario"]} | {x["shared_bias"]:+.6f} | {x["interaction_bias"]:+.6f} | {x["shared_95_coverage"]:.1%} | {x["interaction_95_coverage"]:.1%} |' for x in tsim)
    relrows='\n'.join(f'| {x["k"]} | {x["rounds"]:,} | {x["peer_correlation"]:.3f} | {pct(x["individual_prediction_R2"])} | {ci_pct(x["individual_prediction_R2_competition_95"])} |' for x in rel['representative_k_uncertainty'])
    sensitivity='; '.join(f'{x["specification"]}: {pct(x["within_solver_share"])}' for x in var['sensitivity'])
    tci=inter['competition_solver_bootstrap_95']['interaction_variance'];tupper=math.sqrt(max(0,tci[1]))
    if not (OUT/'PROGRESS.md').exists():(OUT/'PROGRESS.md').write_text((OUT/'PILOT.md').read_text())
    md=f'''# S1 measurement-validation pilot — REVISE

Exploration only, locked before the new analysis. The shared scheduled-position component is **{pct(fit['within_solver_share'])} of within-solver-round successful log-time variance** (competition+solver bootstrap 95%: **{ci_pct(vc['within_solver_share'])}**). It is detectable but small. The aggregate unshrunk seasonal-extreme correction is **{estimate:.4f}×** (95% **{rci[0]:.4f}–{rci[1]:.4f}**, n={ext['n']} exploratory solver-seasons). This does not support a 10% average shared boost. It does not establish that the remaining variation is personal luck.

**Recommendation: revise.** An episode about the difference between common scramble opportunity and an individual's spectacular solve survives. A record-attribution episode with verified actual scramble links does not yet have the required data. Method labels and replacement assignments are absent. Do not open the 80% until a reviewed, committed METHOD.md freezes the revised estimand and mapping policy.

## Slice, sources and scope

Same exact rule as `rounds/r3/pilot-S1/SLICE.md`: UTF-8 competition ID SHA-256 integer modulo 5 equals zero, all years. {3756:,}/{18771:,} IDs. ID-list SHA-256: `b5f6426bffbbf01c4d742cbe65f083cb4cbb5a134a5b60c3fe9fa312d028b7a4`. `SLICE.md` was written first. Independently checked all eight frozen source hashes against the round-3 manifest, including the immutable 2026-09-30 ZIP. The manifest, extraction rule, row counts and executable are included. No confirmatory outcome query or outcome table was created; confirmation counts use only identifiers, dates, formats, group counts and attempt presence. All outcome SQL reads only the exploration parquet, whose membership is asserted again before analysis.

The exact final slice contains {counts['rounds']:,} scheduled-mapped finals, {counts['solver_rounds']:,} solver-rounds, {counts['attempt_rows']:,} attempt slots, {counts['valid_attempts']:,} valid times, {dnf['DNF']:,} DNF and {dnf['DNS']} DNS, {counts['solvers']:,} solvers. Real structural panels range 4–48 finalists; median 12. {counts['informative_solver_rounds']:,} solver-rounds have at least two valid times. One/all-successless solver-rounds provide no time contrast but remain in failure analysis. This recovers 7,314 valid attempts absent from the previous min-six complete-panel analysis, through DNF retention and removal of the min-six gate.

Source attribution: WCA owns and maintains the results, [WCA results export](https://www.worldcubeassociation.org/export/results), export date 2026-09-30 00:00:36 UTC. Dated bundled README terms and hashes are in the raw manifest. Published work must carry the bundled notice.

## 1. Simulation first: known truth at the real panel sizes

Before any new real-outcome computation, simulated all {sim['panel_rounds']:,} finals / {sim['solver_rounds']:,} solver-rounds at the structural sizes. Each scenario has 400 independent simulations (seed 20261001). Generated log-times with known round-position common variance, independent residual variance 0.0222, and, where specified, an observable faster/slower-tier × scramble interaction variance 0.0025. Solver-round intercepts cancel through centering. Coverage is of a competition-sandwich 95% interval, not a posterior interval; at 95% coverage its Monte Carlo SE is about 1.1 percentage points. Boundary scenarios use signed variance estimates to avoid artificial clipping coverage.

| Synthetic truth | Common variance | Common-only estimator bias | 95% coverage | Split-peer correlation |
|---|---:|---:|---:|---:|
{rows}

The small-common truth implies split-peer r≈0.18, close to the prior 0.181 observation. A much larger common component implies r≈0.50. At a typical 12-person panel, the analytic value is tau / sqrt((tau+e/6)(tau+e/6)); the full simulation uses each actual panel size. Therefore low split-peer correlation alone does not show that luck is personal. The original balanced estimator also recovers independent-noise common truth; small panels do not explain away the aggregate signal.

The common-only estimator is **wrong when a strong structured interaction exists**: in the shared+tier truth it underestimates common variance by about 23%, with only 1.8% interval coverage. Tier-specific peer covariance fixes this under the generated model:

| Tier-aware estimator | Shared bias | Interaction bias | Shared coverage | Interaction coverage |
|---|---:|---:|---:|---:|
{tierrows}

These simulations identify a structured interaction because tier labels are observed. Independent unobserved solver-by-scramble opportunities are observationally indistinguishable from execution residuals here; no estimator can partition those without extra measurements. MCAR DNF at 1.5% preserves recovery. One prespecified informative-DNF stress model causes about 1.6% relative downward common-variance bias. That is a narrow sensitivity check, not a proof against every missingness process.

**Selection revealed an additional design flaw.** In 400 simulations of 300 solver-seasons × five finals, with real panel sizes sampled and minima reselected, the small-common truth gives mean true shared extreme advantage {sel[0]['mean_true_extreme_log_advantage']:.5f} log units. Unshrunk leave-one-out peers recover {sel[0]['mean_unshrunk_estimate']:.5f} (bias {sel[0]['unshrunk_bias']:+.5f}; finite-sample truth-error 95% coverage {sel[0]['unshrunk_truth_error_95_coverage']:.1%}). Shrinkage gives only {sel[0]['mean_shrunk_estimate']:.5f}, with zero truth-error interval coverage in this setup. At the larger common truth, unshrunk coverage is {sel[1]['unshrunk_truth_error_95_coverage']:.1%}. Shrinkage is useful for displaying individual effects, but peer-only posterior means shrink away part of an aggregate effect selected using the focal solve. The frozen primary aggregate now uses unshrunk contrasts; do not recycle the old shrunk headline.

## 2. DNF-retaining common component and reliability versus peers

Model: log successful time = solver-round intercept + pooled attempt position + common round-position contrast + residual. The intercept absorbs finalist ability and round-wide conditions. This is a **within-solver-round** variance decomposition; it does not measure all population variation. Common position effects can also contain synchronized round conditions. Scramble causation is not separately identified.

For each solver's observed successful slots use C = diag(valid) − valid validᵀ/m. With A=sum C, V=sum C(y−position), S=sum ||C(y−position)||² and d=sum(m−1), E(S)=d(tau+e), E(||V||²)=tau tr(A²)+e d. These equations subtract finite-peer noise without requiring five successes. Fit pooled positions; resample competitions and solver IDs with corrected squared-weight noise traces. Main intervals use 1,000 crossed-bootstrap draws; no confidence intervals are obtained by clipping negative moments.

Result: common variance {fit['shared_variance']:.6f}; residual {fit['residual_variance']:.6f}; common log-SD {pct(fit['shared_log_sd'])} (crossed 95% {ci_pct(vc['shared_log_sd'])}). Shared fraction {pct(fit['within_solver_share'])}. Sensitivities: {sensitivity}. The old removal of whole DNF panels did not drive the headline, but it was unnecessary and biased the study population.

Era replication (competition intervals, conditional on each period's solvers): { '; '.join(x['period']+': '+pct(x['shared_fraction'])+' ('+ci_pct(x['competition_95'])+')' for x in robust['periods']) }. Leave-one-year-out across the modern slice gives shared fractions {pct(min(x['shared_fraction'] for x in robust['leave_year_out']))}–{pct(max(x['shared_fraction'] for x in robust['leave_year_out']))}. In 200 independent-per-solver within-round label permutations, the null common-variance interval is {robust['independent_solver_label_negative_control']['shared_variance_95'][0]:+.6f} to {robust['independent_solver_label_negative_control']['shared_variance_95'][1]:+.6f}; empirical upper-tail p={robust['independent_solver_label_negative_control']['empirical_upper_tail_p']:.4f}. Alignment matters, but this is a signal-negative-control and does not distinguish scrambles from other synchronized conditions. Exploratory seasonal unshrunk adjustments by era: { '; '.join(x['period']+': '+f"{x['aggregate_unshrunk_ratio']:.4f}× (n={x['n']})" for x in robust['extreme_periods']) }.

Predictive model hyperparameters and position effects were **frozen using pre-2019 exploration finals**, then applied to 2019–2025 exploration finals. For each k, randomly choose entire peer solvers; estimate their common contrast; predict the held-out solver's same-scramble time relative to its other valid solves. The target solve is excluded from its baseline. Predictions are of log-time contrasts conditional on those other attempts, not an unconditional forecast of raw seconds or intrinsic ability. Thirty random splits are averaged before competition resampling at the headline k values.

| Peers k | Eligible finals | Correlation with remaining-peer estimate | Held-out individual R² | Competition 95% R² |
|---:|---:|---:|---:|---:|
{relrows}

The full curve covers k=2..{rel['all_panels'][-1]['k']} (requires ≥2 held-out peers). Only 16 modern finals support k=20; the maximum-k endpoint has very few panels. The fixed-large-panel curve uses the same {rel['fixed_large_panels'][0]['rounds']} finals with ≥20 informative peers for k=2..18, avoiding changing-population comparisons. Random-split ranges in JSON are Monte Carlo variability, **not** sampling confidence intervals; separate competition intervals are given above. Those predictive intervals condition on frozen training parameters and do not fully capture repeated solvers.

Extrapolation under the training model: latent common-effect reliability R(k)=tau/(tau+e/k). About **{rel['peers_for_50pct_reliability']:.0f} peers** yield 50% reliability and **{rel['peers_for_80pct_reliability']:.0f} peers** yield 80%. At 50 / 100 / 200 peers the model predicts {', '.join(pct(x['latent_reliability']) for x in rel['extrapolation'] if x['k'] in [50,100,200])}. These are extrapolations, not observed large-panel evidence. Even perfectly measuring the common effect would explain only {pct(rel['frozen_parameters']['within_solver_share'])} of individual contrast variation under this training model. Large panels solve the measurement problem, not the small-signal problem. Assignment error and unseen interactions could alter this ceiling.

## 3. Is the luck personal? What is and is not testable

Method is absent from the export. No Roux/CFOP/orientation claim is tested or inferred from skill. For skill, use each solver's median log mean in at least two **other** exploration finals within ±2 years; split each eligible panel into faster/slower halves. Both halves need ≥3 informative peers. This yields {inter['rounds']:,} finals / {inter['solver_rounds']:,} solver-rounds. References may use future exploration appearances and the focal round is excluded; this is labelled exploratory.

Allow separate independent residual variances in each tier. Estimate the two within-tier shared variances and cross-tier covariance, then interaction variance = (b_fast+b_slow−2cov)/4. Raw interaction moment {inter['model']['interaction_variance']:+.6f}; competition+solver 95% interval **{tci[0]:+.6f} to {tci[1]:+.6f}**. The admissible point estimate is zero; the negative raw moment and raw correlation >1 are sampling diagnostics, not physical variance or a claim of super-perfect agreement. Repeated-solver uncertainty is materially wider than competition-only uncertainty. The crossed upper interaction log-SD is about **{pct(tupper)}** (twice that for the fast-minus-slow contrast). There is no detected tier interaction, but meaningful tier differences and method-specific opportunities are not ruled out. In particular, this does **not** establish personal luck.

The {ext['n']} broad-cohort seasonal minima are on average {ext['within_round_log_speedup']:.3f} log units faster than their own successful-round mean. The unshrunk peer component explains {math.log(estimate):.4f} log units, about {pct(ext['aggregate_unshrunk_peer_fraction'])} of that observed extreme deviation. The remainder is unexplained by this peer model: execution, solver-specific opportunities, penalties, model error, missingness and replacement/misscramble error can all contribute. This descriptive decomposition holds the observed within-round baseline fixed; it is not a causal allocation of skill and luck.

## 4. Honest episode numbers, original pass rule and power

- Shared component: **{pct(fit['within_solver_share'])}**, 95% **{ci_pct(vc['within_solver_share'])}**, n={counts['valid_attempts']:,} valid solves in {counts['rounds']:,} finals.
- Aggregate broad-cohort median-shared-effect correction: **{estimate:.4f}×**, 95% **{rci[0]:.4f}–{rci[1]:.4f}**, n={ext['n']} solver-season minima, {ext['solvers']} solvers. At the point estimate this is **{(estimate-1)*100:.2f}%** more time on the median shared contrast. Shrunk individual-display average: {ext['ratio']:.4f}×, conditional refit/reselection CI {ext['competition_solver_refit_reselection_95'][0]:.4f}–{ext['competition_solver_refit_reselection_95'][1]:.4f}.
- Ten peers predict **{pct(r10['individual_prediction_R2'])}** of a held-out solver's log-time contrast variation, competition 95% **{ci_pct(r10['individual_prediction_R2_competition_95'])}**, n={r10['rounds']} modern finals.

**Original verified prereg rule: untestable on slice.** The official-2018 top100 roster is not supplied; reconstructing it from the 80% would violate the pilot boundary. Actual replacement assignments are unverified. The slice-only top100 proxy has {ext['slice_proxy_top100']['n']} extremes, below the 100-extreme gate, and is not the official cohort. The broader exploratory cohort has 180 extrema and meets simple count gates, but cannot replace the official cohort silently. Its shrunk and unshrunk adjustments both fail the >1.10 point-estimate rule, and the unshrunk interval is wholly below 1.10; this is a surrogate exploratory result, not a preregistered rejection. Strong statistical evidence of a small common component is compatible with failing a materially-large-effect rule.

{power_note}

The 1.10 rule imposes a point-estimate threshold as well as significance. At a true ratio exactly 1.10, nominal pass probability tends to 50%, however precise the data are. For a future equivalence claim such as “shared advantage is under 10%,” preregister the upper-confidence-bound criterion separately; do not reinterpret a failed large-effect test as equivalence without that rule.

## 5. DNF and replacement handling

Started-attempt DNF rate **{pct(dnf['DNF_rate_among_started'])}**. Binary DNF shared covariance {dnf['binary_shared_variance']:.6f}, competition interval {dnf['binary_shared_variance_competition_95'][0]:+.6f} to {dnf['binary_shared_variance_competition_95'][1]:+.6f}. Peer time difficulty versus target DNF slope {dnf['peer_log_difficulty_DNF_risk_slope']:+.4f} risk/log-unit, CI {dnf['slope_competition_95'][0]:+.4f} to {dnf['slope_competition_95'][1]:+.4f}: no detected association. This is a binary companion, **not** a fitted joint latent-time likelihood. The estimand is successful-time variation plus separately reported failure; latent completion times for DNF are not observed. Simulation and complete-case sensitivity are limited probes of informative missingness.

**Extra scrambles cannot be resolved from these tables.** {counts['extra_pool_rounds']:,}/{counts['rounds']:,} exploration finals have extra pools. A pool is not a usage log. [WCA Regulation 11e1](https://www.worldcubeassociation.org/regulations/#11e1) specifies that extra attempts use a different scramble, so a replacement may invalidate the scheduled attempt-number link. Only four exploration finals and eight confirmation finals lack an extra pool, all before 2019; absence of a pool is itself not proof that no replacement occurred. Strictly excluding every extra-pool final leaves zero 2019–2025 finals, so it kills the original record study rather than repairing it.

Under an **assumed independent random replacement** rate of 5%, 10%, 20%, common covariance attenuates approximately (1−p)². Corrected shared fractions would be {', '.join(pct(x['corrected_within_solver_share']) for x in mapping['random_replacement_sensitivity'] if x['replacement_fraction'] in [.05,.10,.20])}. This is a model sensitivity, **not a worst-case bound**; targeted replacement can bias either way. Fix: independently audit actual solver-attempt assignments and replacement use for the confirmatory measurement sample and extrema, or explicitly rename the estimand “shared scheduled-position variation” and abandon exact-record scramble causation. No individual historical record is attributed here. The provided export cannot supply the red-team's verified-assignment study by itself.

## 6. Candidate claims — all exploratory

1. **“Ten other finalists explain little of your speed on the same scramble.”** With the pre-2019 peer model frozen, ten peers explain about {pct(r10['individual_prediction_R2'])} of held-out log-time contrast variation; a small common signal persists.
2. **“A small shared advantage survives the fairer test, but the 10% story does not.”** The broad seasonal-extreme correction is {estimate:.4f}×, while roughly {pct(1-fit['within_solver_share'])} of within-solver variance remains unexplained by common effects. This concerns scheduled finals and successful attempts, not all scramble luck or world records.
3. **“The statistical correction can hide the effect it is trying to measure.”** Peer-only shrinkage reduces the exploratory aggregate seasonal adjustment from {(estimate-1)*100:.2f}% to {(ext['ratio']-1)*100:.2f}%. Known-truth simulation shows why selecting extremes makes that attenuation systematic. Use unshrunk aggregation, shrink individual displays, and show their different purposes.

## 7. Every exposed design issue and frozen fixes

'''+ '\n'.join(f'{j+1}. {x}' for j,x in enumerate(changes))+f'''

Further fixes: do not interpret an unconstrained negative interaction moment or correlation above one as physical truth; show boundary diagnostics and broad crossed uncertainty. Distinguish variation across random peer splits from sampling uncertainty. Large-k curves change eligible finals, so show a fixed-panel sensitivity and its counts. The five-finals gate is nonlinear: 20% competition hashing produces far fewer eligible solver-seasons than one-quarter of the 80%; preserve exposure and avoid naive power scaling. A common permutation of all scramble labels in a final is invariant for the variance estimator; use independent per-solver permutations only as a signal-negative-control, not a causal scramble placebo. Actual fixed-exposure record-arrival null and official-cohort confirmation remain outside this exploratory study.

Frozen numerical model and algorithm are in `FROZEN_MODEL.md` / `frozen-model.json`. They are ready to adapt into a reviewed and committed METHOD.md; they are not a claim that preregistration has happened. The mapping gate must be resolved or the scheduled-position endpoint accepted before opening held-out outcomes.

## Reproduce, results and visuals

From workspace root:

```sh
.venv/bin/python rounds/r5/pilot-S1/pilot.py all
```

Stages can be rerun individually: `sources`, `simulation` (includes `validate.py`), `analyze`, `report`. Raw files and exploration-derived parquet caches are in gitignored `data/S1/`. The only minimal wide outcome table loaded into pandas contains the locked slice finals; large-export extraction and coverage use DuckDB SQL. Default: 400 simulations/scenario, 1,000 variance/predictive/interaction bootstrap draws, 2,000 extreme refit/reselection draws. Runtime is minutes on this laptop; no confirmation outcomes are selected. The pipeline reuses `rounds/r3/pilot-S1/pilot.py` extraction and its frozen manifest; these are repository dependencies, not undocumented downloaded code.

Charts: `01-obvious-and-fairer.png` (observed extreme deviation and fairer within-solver decomposition); `02-reliability-vs-peers.png` (measurement reliability versus predictive usefulness, with extrapolation); `03-extreme-adjustment.png` (observed extremes and conditional shrunk individual adjustments, separately labelled from aggregate correction).

Claim/result keys: shared fraction → `variance.json.fit.within_solver_share` / `bootstrap_95.competition_solver`; ten-peer R² → `reliability.json.representative_k_uncertainty[k=10]`; seasonal ratio → `extremes.json.aggregate_unshrunk_ratio` / `aggregate_unshrunk_95`; skill interaction → `interaction.json.model.interaction_variance` / `competition_solver_bootstrap_95`; DNF → `dnf.json`; simulation recovery → `simulation.json`, `interaction-simulation.json`, `selection-simulation.json`; mapping sensitivity → `mapping-sensitivity.json`; structural power coverage → `confirmation-structural-coverage.json`; power assumptions → `power.json`. `pilot.json` is the machine-readable recommendation. `PROGRESS.md` preserves stage-by-stage checkpoints.
'''
    (OUT/'PILOT.md').write_text(md)
    dump('artifact-manifest.json',{'files':[{'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='artifact-manifest.json']})
    print(f'Report and pilot.json saved: shared {pct(fit["within_solver_share"])}, seasonal ratio {estimate:.4f}, recommendation revise.',flush=True)

def structural_coverage():
    import duckdb
    c=duckdb.connect(str(ROOT/'data/S1/coverage.duckdb'),read_only=True)
    q='''WITH s AS (SELECT explore,person_id,year,count(*) nf FROM eligible WHERE is_final AND year BETWEEN 2019 AND 2025 GROUP BY ALL) SELECT explore,count(*) solver_seasons,count(*) FILTER(WHERE nf>=5) seasons_ge5,count(DISTINCT person_id) FILTER(WHERE nf>=5) solvers_ge5 FROM s GROUP BY explore ORDER BY explore'''
    a=c.execute(q).fetchdf().to_dict('records')
    b=c.execute('SELECT explore,year,count(DISTINCT competition_id) finals,count(*)*5 attempts FROM eligible WHERE is_final AND extra_pool_rows=0 GROUP BY ALL ORDER BY explore,year').fetchdf().to_dict('records')
    obj={'season_coverage':a,'no_extra_pool':b,'outcome_blind':True};dump('confirmation-structural-coverage.json',obj);return obj

if __name__=='__main__':report()
