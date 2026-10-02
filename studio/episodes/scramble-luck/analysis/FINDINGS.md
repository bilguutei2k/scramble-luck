The shared scramble/slot adjustment adds about 1.98% to these season-best final solves on average. **Belief fails.** The data rule out an average shared scramble/slot boost as large as 10% for these season bests. R is 1.0198 (1.0164–1.0231); its entire procedure B interval is below the registered 1.10 line.

The shared scramble/slot component is detectable: tier-aware F is 4.7434% (3.9181–5.6708%) of balanced-tier within-solver-round successful log-time variance. This is not a percentage of seconds or total luck. The study answers a narrower question than whether a world record was lucky: average shared contrasts in 2019–2025 eligible finals and season bests, not a particular record or total personal luck.

This information is based on competition results owned and maintained by the World Cube Assocation, published at https://worldcubeassociation.org/results as of September 30, 2026.

## Registered primary measurements

Confirmatory under METHOD as amended by owner-approved AMENDMENT-1 (registration commit 5496074). First confirmation magnitude read: 2026-10-02T15:17:40.383923+00:00. The original gate failed. Amendment B was chosen after synthetic results were seen, before confirmation times: it removes the over-coverage ceiling and validates re-centred uncertainty. Paired B coverage was 97–100%; independent coverage was 96–100%, with 0.6% false holds and 0.9% false fails at the calibrated 1.10 boundary (n=1,000). Conservatism reduces precision; these simulations do not guarantee coverage for every process.

R: 1.0198 (1.0164–1.0231), n=3313 available person-years; 2000/2,000 valid draws. Procedure B centres by the bootstrap mean on the observed log R. Raw percentile R interval: [1.014038011976348, 1.0207233805048443]; bootstrap mean log R=0.01728889; displacement=-0.00229687. No point-estimate bias correction or clipping. Procedure A fixed-selection sensitivity: 1.0198 (1.0149–1.0246), 2000/2,000 valid draws; it cannot change the verdict.

F: 4.7434% (3.9181–5.6708%), n=4420 tier-supported finals and 234525 successful cells. Gamma/D: 0.3565% (-0.5067–0.8985%); the signed interval crosses zero. Signed variance components, tier residuals and D with their percentile intervals are in results.json. Negative moments are boundary diagnostics, not negative physical variance.

Coverage gates pass: 5017 finals, 306155 slots, 301668 successes, 3313 available extrema; zero no-success seasons and zero unidentified original extrema. The tier subset omits 597 finals and 67143 successful cells; 11557 informative solver-rounds lack skill references. Singleton-success panels=14; no-success panels=6. These remain in counts and failure analysis. Original structural eligibility remains fixed in bootstrap draws.

| Year | Eligible finals | Tier-supported finals | Tier-subset successes |
|---|---:|---:|---:|
| 2019 | 813 | 603 | 27798 |
| 2020 | 131 | 106 | 5151 |
| 2021 | 143 | 127 | 6138 |
| 2022 | 577 | 539 | 29040 |
| 2023 | 1084 | 1018 | 56432 |
| 2024 | 1133 | 1025 | 56482 |
| 2025 | 1136 | 1002 | 53484 |

Exclusions are the registered structural/status exclusions; no speed threshold, outlier deletion or complete-final requirement. Mutually exclusive result counts: {"incomplete_or_duplicate_slots_results": 0, "invalid_format_final_results": 0, "invalid_regular_schedule_results": 0, "invalid_status_results_after_slot_gate": 0, "missing_schedule_results": 26, "multigroup_results": 48911, "nonfinal_333_results": 794852, "other_event_results": 2504130}.

Bootstrap exposure diagnostics (central ranges describe draws, not extra confidence intervals):
- absent_seasons: mean 1225.1440, central 95% range [1138.0, 1311.0249999999999], min–max 1056–1368, n=2,000 draws.
- available_extrema: mean 2087.0520, central 95% range [2000.0, 2174.0], min–max 1945–2257, n=2,000 draws.
- no_success_seasons: mean 0.0010, central 95% range [0.0, 0.0], min–max 0–1, n=2,000 draws.
- unidentified_extrema: mean 0.8030, central 95% range [0.0, 3.0], min–max 0–6, n=2,000 draws.
- distinct_competition_fraction: mean 0.6322, central 95% range [0.6234801674307355, 0.6408212078931632], min–max 0.6188957544349213–0.64719952162647, n=2,000 draws.
- weighted_attempt_exposure: mean 306084.7000, central 95% range [296752.875, 316030.75], min–max 290660.0–323885.0, n=2,000 draws.
- distinct_attempt_exposure: mean 122321.2750, central 95% range [118935.0, 125685.125], min–max 116695–131070, n=2,000 draws.
- fixed_selection_n: mean 1322.3385, central 95% range [1249.0, 1397.0249999999999], min–max 1188–1457, n=2,000 draws.
- equal_tier_n: mean 969.5185, central 95% range [853.0, 1091.0249999999999], min–max 740–1185, n=2,000 draws.

## Every robustness and sensitivity check

All intervals below are pointwise. None changes the primary decision. Era and year-deletion references use the included competitions; the roster stays fixed.

| Check | F, 95% interval | R, procedure B interval | Tier finals / successes / extrema |
|---|---|---|---|
| era_2019_2022 | 4.8238% (2.7785–7.2652%) | 1.0186 (1.0125–1.0248) | 1269 / 59773 / 888 |
| era_2023_2025 | 4.7465% (3.7700–5.8016%) | 1.0202 (1.0162–1.0242) | 3012 / 162831 / 2425 |
| leave_year_2019_out | 4.7631% (3.8632–5.6939%) | 1.0198 (1.0161–1.0236) | 3783 / 204193 / 2818 |
| leave_year_2020_out | 4.7154% (3.8947–5.6510%) | 1.0197 (1.0163–1.0231) | 4289 / 227280 / 3307 |
| leave_year_2021_out | 4.7077% (3.8625–5.6561%) | 1.0199 (1.0165–1.0233) | 4270 / 226534 / 3279 |
| leave_year_2022_out | 4.7755% (3.8888–5.7673%) | 1.0200 (1.0164–1.0236) | 3845 / 201604 / 2960 |
| leave_year_2023_out | 4.6878% (3.5966–5.7644%) | 1.0191 (1.0153–1.0229) | 3304 / 168623 / 2507 |
| leave_year_2024_out | 4.8841% (3.9158–6.1362%) | 1.0200 (1.0161–1.0240) | 3303 / 169134 / 2504 |
| leave_year_2025_out | 4.7009% (3.6520–5.7689%) | 1.0199 (1.0160–1.0236) | 3343 / 174280 / 2503 |
| complete_success | 4.8514% (3.9400–5.8709%) | 1.0194 (1.0160–1.0229) | 4224 / 214820 / 3313 |
| clipped_centered_logs | 4.8220% (4.0147–5.7475%) | 1.0198 (1.0164–1.0231) | 4420 / 234525 / 3313 |

Complete-success sensitivity masks 4176 incomplete solver-rounds but keeps the original seasonal roster. Clipping affects 404 successful cells at centered log contrast ±0.6; no primary clipping occurs.

All-finalist common-only comparator (all_finalists): share 4.4145% (3.8002–5.0172%); actual within-solver denominator 0.0231 (0.0228–0.0235), n={'solver_rounds_with_contrasts': 61211, 'successful_cells': 301668}. It does not replace tier-aware F.

All-finalist common-only comparator (complete_success): share 4.4428% (3.8241–5.0631%); actual within-solver denominator 0.0231 (0.0227–0.0235), n={'solver_rounds_with_contrasts': 57055, 'successful_cells': 285275}. It does not replace tier-aware F.

All-finalist common-only comparator (clipped_centered_logs): share 4.4826% (3.8878–5.0801%); actual within-solver denominator 0.0228 (0.0224–0.0231), n={'solver_rounds_with_contrasts': 61211, 'successful_cells': 301668}. It does not replace tier-aware F.

Leave one solver out, F_tier_aware: point range [0.0472743615800455, 0.04761889258973434], n=12853 deletions. Endpoint-deletion intervals are conditional on their selected endpoints, not simultaneous range intervals.
- Delete 2019PETT01: 0.0473 (0.0390–0.0566), n={'available_person_years': 3310, 'tier_supported_finals': 4420}.
- Delete 2022CHAI02: 0.0476 (0.0394–0.0570), n={'available_person_years': 3310, 'tier_supported_finals': 4420}.

Leave one solver out, R_geometric_person_year: point range [1.0196433059759782, 1.0198988012144894], n=12853 deletions. Endpoint-deletion intervals are conditional on their selected endpoints, not simultaneous range intervals.
- Delete 2017WILL05: 1.0196 (1.0163–1.0230), n={'available_person_years': 3309, 'tier_supported_finals': 4420}.
- Delete 2018AMSB02: 1.0199 (1.0165–1.0232), n={'available_person_years': 3310, 'tier_supported_finals': 4417}.

Aggregation/tier sensitivities:
- arithmetic_mean_R: 1.0213 (1.0179–1.0246), n={'available_person_years': 3313}.
- per_solver_weighted_R: 1.0184 (1.0146–1.0222), n={'solvers': 1800, 'person_years': 3313}.
- equal_tier_R: 1.0203 (1.0155–1.0251), n={'person_years': 3043}.
- all_peer_R_on_equal_tier_subset: 1.0199 (1.0152–1.0247), n={'person_years': 3043}.

Equal-tier attrition=270 original extrema. The matched subset comparison is essential; R averages the observed peer lineup and does not establish an advantage uniform across skill tiers.

Attempt-position checks:
- confirmation_beta: R 1.0197 (1.0163–1.0230); F 4.7434% (3.9181–5.6708%); n={'available_person_years': 3313}.
  Fitted position effects and percentile intervals: -0.0004 (-0.0023–0.0014), -0.0018 (-0.0039–0.0004), -0.0016 (-0.0037–0.0004), 0.0009 (-0.0011–0.0030), 0.0029 (0.0007–0.0048).
- yearly_beta: R 1.0197 (1.0163–1.0229); F 4.7434% (3.9181–5.6708%); n={'available_person_years': 3313}.

| Year-specific beta | F, interval | R, interval | Available extrema / valid R draws |
|---|---|---|---:|
| 2019 | 4.4857% (0.4473–8.2621%) | 1.0192 (1.0111–1.0275) | 495 / 2000 |
| 2020 | 2.2008% (-34.6105–17.3792%) | 1.0449 (0.9636–1.1326) | 6 / 1994 |
| 2021 | 7.1195% (-36.9126–19.9873%) | 1.0123 (0.9834–1.0413) | 34 / 2000 |
| 2022 | 4.5769% (0.0669–8.3409%) | 1.0178 (1.0083–1.0275) | 353 / 2000 |
| 2023 | 4.9970% (2.6239–7.5061%) | 1.0220 (1.0151–1.0291) | 806 / 2000 |
| 2024 | 4.4003% (1.4507–6.2890%) | 1.0189 (1.0119–1.0261) | 809 / 2000 |
| 2025 | 4.9669% (2.4699–7.6515%) | 1.0194 (1.0127–1.0268) | 810 / 2000 |

2020 coverage warning: tier F gate=fails; available-extrema R gate=fails. Failed-gate yearly measurements and their intervals are diagnostic and cannot support general claims. Valid R draws=1994/2,000.

2021 coverage warning: tier F gate=fails; available-extrema R gate=fails. Failed-gate yearly measurements and their intervals are diagnostic and cannot support general claims. Valid R draws=2000/2,000.

2022 coverage warning: tier F gate=fails; available-extrema R gate=passes. Failed-gate yearly measurements and their intervals are diagnostic and cannot support general claims. Valid R draws=2000/2,000.

All yearly fitted beta values and intervals are in results.json. F is algebraically invariant to a global beta change because pooled tier positions are refitted. R remains sensitive to position adjustment. Scramble number and attempt number are confounded.

## Secondary checks, including contrary evidence

DNF odds ratio per 0.05 increase in leave-one-out h: 1.0348 (0.9777–1.0649), n={'identified_solver_rounds': 61231, 'discordant_solver_rounds': 4154}. Exact conditional logistic regression includes attempt effects and solver-round fixed effects. All-success/all-DNF panels contribute counts but no conditional likelihood. DNS is outside the started denominator. Binary DNF shared covariance: 0.0000 (-0.0001–0.0001). DNF rate: 1.4469% (1.3611–1.5289%); DNS rate: 0.0189% (0.0082–0.0338%). Counts: 4429 DNF; 58 DNS.

The estimated DNF association is positive, but its interval includes no association. The success-only estimate may understate shared difficulty. The frozen informative-DNF simulation bounds behavior only under its specified conditional-odds process, not a universal bound on unobserved failure times. It cannot change the verdict.

Optimal cross six_face_centered_correlation: 0.2658 (0.1975–0.2287), n={'scheduled_scrambles': 25085, 'identified_focal_solver_rounds': 61231}.

Optimal cross six_face_raw_correlation: 0.2377 (0.1764–0.2047), n={'scheduled_scrambles': 25085, 'identified_focal_solver_rounds': 61231}.

Optimal cross white_yellow_centered_correlation: 0.3429 (0.2582–0.2905), n={'scheduled_scrambles': 25085, 'identified_focal_solver_rounds': 61231}.

Optimal cross white_yellow_raw_correlation: 0.3069 (0.2312–0.2600), n={'scheduled_scrambles': 25085, 'identified_focal_solver_rounds': 61231}.

Cross lengths were solved exactly from scramble strings before any confirmation times. A positive association supports a scramble-geometry contribution, but neither this association nor the time model separates all shared slot conditions. Half-turn metric; U/D denote white/yellow in the standard orientation.

Contrary uncertainty diagnostic, six_face_centered_correlation: the observed correlation lies outside its unaltered percentile interval; bootstrap mean=0.213170, displacement=-0.052632, n=2,000 draws. Product-weight peer resampling changes measurement noise. Cross-correlation uncertainty has not been calibrated by Amendment 1 (which validates R only); do not present these endpoints as a demonstrated coverage guarantee. No unregistered recentering was applied.

Contrary uncertainty diagnostic, six_face_raw_correlation: the observed correlation lies outside its unaltered percentile interval; bootstrap mean=0.190635, displacement=-0.047086, n=2,000 draws. Product-weight peer resampling changes measurement noise. Cross-correlation uncertainty has not been calibrated by Amendment 1 (which validates R only); do not present these endpoints as a demonstrated coverage guarantee. No unregistered recentering was applied.

Contrary uncertainty diagnostic, white_yellow_centered_correlation: the observed correlation lies outside its unaltered percentile interval; bootstrap mean=0.274691, displacement=-0.068203, n=2,000 draws. Product-weight peer resampling changes measurement noise. Cross-correlation uncertainty has not been calibrated by Amendment 1 (which validates R only); do not present these endpoints as a demonstrated coverage guarantee. No unregistered recentering was applied.

Contrary uncertainty diagnostic, white_yellow_raw_correlation: the observed correlation lies outside its unaltered percentile interval; bootstrap mean=0.245869, displacement=-0.061077, n=2,000 draws. Product-weight peer resampling changes measurement noise. Cross-correlation uncertainty has not been calibrated by Amendment 1 (which validates R only); do not present these endpoints as a demonstrated coverage guarantee. No unregistered recentering was applied.

Independent within-final, per-solver time/status permutations (1,000 draws; refitted references and moments):
- F_tier_aware: reference mean -0.000031; central 95% permutation range [-0.0018556506083392138, 0.0020598288733605485]; observed 0.047434; plus-one upper-tail probability 0.000999; valid draws=1000. This reference range is not a sampling CI.
- gamma_over_D: reference mean 0.000028; central 95% permutation range [-0.0018686177540071605, 0.0019398716284379275]; observed 0.003565; plus-one upper-tail probability 0.001998; valid draws=1000. This reference range is not a sampling CI.
- R_geometric_person_year: reference mean 1.000015; central 95% permutation range [0.9985606143377274, 1.0014162890040668]; observed 1.019779; plus-one upper-tail probability 0.000999; valid draws=1000. This reference range is not a sampling CI.

| Assumed random replacement p | Scaled tau, interval | Share with original D, interval |
|---|---|---|
| p_0.00 | 0.0011 (0.0009–0.0013) | 4.7434% (3.9181–5.6708%) |
| p_0.01 | 0.0011 (0.0009–0.0014) | 4.8397% (3.9977–5.7860%) |
| p_0.05 | 0.0012 (0.0010–0.0015) | 5.2558% (4.3414–6.2835%) |
| p_0.10 | 0.0014 (0.0011–0.0016) | 5.8560% (4.8372–7.0010%) |
| p_0.20 | 0.0017 (0.0014–0.0021) | 7.4115% (6.1220–8.8607%) |

independent random replacement; neither a worst-case bound nor a correction to R; targeted replacements can bias either way; no actual-assignment audit supplied. Extra-pool presence does not reveal actual replacement usage; primary finals with pools=5017. No audited subset is available.

| Prediction panel | k | Finals / solver-rounds | Peer correlation, competition CI | Individual R², competition CI | Model reliability |
|---|---:|---|---|---|
| changing_panels | 2 | 5017 / 61211 | 0.1544 (0.1456–0.1633) | 0.0036 (0.0032–0.0039) | 0.0674 |
| changing_panels | 5 | 4828 / 60103 | 0.2019 (0.1910–0.2122) | 0.0082 (0.0075–0.0089) | 0.1529 |
| changing_panels | 10 | 3178 / 45035 | 0.1877 (0.1769–0.1988) | 0.0135 (0.0120–0.0150) | 0.2653 |
| changing_panels | 20 | 97 / 2533 | 0.3058 (0.2445–0.3657) | 0.0210 (0.0134–0.0303) | 0.4193 |
| fixed_panels | 2 | 97 / 2533 | 0.2248 (0.1767–0.2742) | 0.0039 (0.0023–0.0058) | 0.0674 |
| fixed_panels | 5 | 97 / 2533 | 0.3088 (0.2421–0.3725) | 0.0084 (0.0049–0.0125) | 0.1529 |
| fixed_panels | 10 | 97 / 2533 | 0.3852 (0.3117–0.4478) | 0.0149 (0.0094–0.0210) | 0.2653 |
| fixed_panels | 20 | 97 / 2533 | 0.3036 (0.2395–0.3640) | 0.0200 (0.0123–0.0289) | 0.4193 |

Thirty whole-solver splits exclude held-out target solvers from peers. Target baseline uses its other successes. Competition intervals average split statistics first; split-randomness ranges are separately saved in results.json. Fixed panels have ≥22 informative finalists for every k. Model reliability is extrapolation conditional on frozen training parameters, not an empirical interval. Exchangeability, stable residual variance, correct mapping and no tier interaction are assumptions. The predictive intervals omit repeated-solver and baseline uncertainty.

Frozen simulation stresses (already exposed before confirmation; procedure B independent replication):
- {"bias_MC_SE": 4.8860252551297e-05, "bias_log_R": -2.6986416003618925e-05, "boundary_error_range_truth_MC_999": null, "boundary_fails_binomial_95": null, "boundary_holds_binomial_95": null, "case": "null", "coverage": 1.0, "coverage_binomial_95": [0.9817246596448638, 1.0], "coverage_range_truth_MC_999": [1.0, 1.0], "datasets": 200, "fails_probability": 1.0, "holds_probability": 0.0, "invalid_intervals": 0, "judged": true, "mean_R_width": 0.005315518762497522, "mean_log_endpoints": [-0.0026891907847074654, 0.0026264823453186776], "mean_log_width": 0.005315673130026142, "method": "B", "passes_revised_gate": true}.
- {"bias_MC_SE": 7.20934485565446e-05, "bias_log_R": 6.74788710074252e-05, "boundary_error_range_truth_MC_999": null, "boundary_fails_binomial_95": null, "boundary_holds_binomial_95": null, "case": "small_shared", "coverage": 0.995, "coverage_binomial_95": [0.9724581015427943, 0.999873418972133], "coverage_range_truth_MC_999": [0.995, 0.995], "datasets": 200, "fails_probability": 1.0, "holds_probability": 0.0, "invalid_intervals": 0, "judged": true, "mean_R_width": 0.006245017691223006, "mean_log_endpoints": [0.012659894593021087, 0.018807373013294035], "mean_log_width": 0.006147478420272942, "method": "B", "passes_revised_gate": true}.
- {"bias_MC_SE": 6.954121358251209e-05, "bias_log_R": -2.5029150479520534e-06, "boundary_error_range_truth_MC_999": null, "boundary_fails_binomial_95": null, "boundary_holds_binomial_95": null, "case": "informative_dnf", "coverage": 1.0, "coverage_binomial_95": [0.9817246596448638, 1.0], "coverage_range_truth_MC_999": [1.0, 1.0], "datasets": 200, "fails_probability": 1.0, "holds_probability": 0.0, "invalid_intervals": 0, "judged": true, "mean_R_width": 0.0062516621487218125, "mean_log_endpoints": [0.012748307958706642, 0.018901791470877102], "mean_log_width": 0.00615348351217046, "method": "B", "passes_revised_gate": true}.
- {"bias_MC_SE": 6.557992646884692e-05, "bias_log_R": -0.0001168478086838818, "boundary_error_range_truth_MC_999": null, "boundary_fails_binomial_95": null, "boundary_holds_binomial_95": null, "case": "random_replacement_10_percent", "coverage": 1.0, "coverage_binomial_95": [0.9817246596448638, 1.0], "coverage_range_truth_MC_999": [1.0, 1.0], "datasets": 200, "fails_probability": 1.0, "holds_probability": 0.0, "invalid_intervals": 0, "judged": true, "mean_R_width": 0.006101491685575479, "mean_log_endpoints": [0.009525204279731914, 0.015550666651393869], "mean_log_width": 0.00602546237166196, "method": "B", "passes_revised_gate": true}.
- {"bias_MC_SE": 0.0001597092160597704, "bias_log_R": 3.7186321900042896e-05, "boundary_error_range_truth_MC_999": null, "boundary_fails_binomial_95": null, "boundary_holds_binomial_95": null, "case": "pure_attempt_slot_shock", "coverage": 0.97, "coverage_binomial_95": [0.935849373294973, 0.9889125443277452], "coverage_range_truth_MC_999": [0.97, 0.97], "datasets": 200, "fails_probability": 0.0, "holds_probability": 1.0, "invalid_intervals": 0, "judged": false, "mean_R_width": 0.011485689210741548, "mean_log_endpoints": [0.10995523210138475, 0.12019199126822758], "mean_log_width": 0.010236759166842883, "method": "B", "passes_revised_gate": null}.

Quantified MCAR/informative-DNF stress (n=200 independent simulated datasets each; oracle precision from 10,000 disjoint integration datasets):
- small_shared: oracle R 1.0158 (1.0158–1.0158) (95% numerical precision; 99.9% precision interval also saved), mean estimated R 1.0158 (1.0157–1.0160); mean log-R error 0.0001 (-0.0001–0.0002); central 95% dataset-error range [-0.001954693885203182, 0.0021704911688455943]. This quantifies bias/recovery under the specified stress, not the unobserved real failure-time distribution.
- informative_dnf: oracle R 1.0159 (1.0159–1.0160) (95% numerical precision; 99.9% precision interval also saved), mean estimated R 1.0159 (1.0158–1.0161); mean log-R error -0.0000 (-0.0001–0.0001); central 95% dataset-error range [-0.0018818248068807326, 0.0018612432143182722]. This quantifies bias/recovery under the specified stress, not the unobserved real failure-time distribution.

## Limitations and flagged implementation decisions

F and R are estimated from successful solves only. No failure time is imputed. The shared scramble/slot component bundles scramble geometry with conditions shared by everyone in the final’s time slot. Attempt number is confounded with scramble number. The estimated shared-scramble-adjusted time is not a causal replay on another scramble.

Residual variation includes execution, solver-specific scramble opportunities, penalties, model error, missingness and mapping error. The data cannot separate personal luck from execution. These results do not attribute a particular world record, identify the fastest record holder, or measure total personal luck. Exact-record stories require verified actual assignments and remain illustrative, not independent confirmations.

The population is structurally eligible all-finalist 2019–2025 confirmation finals and person-years with at least five such finals; it does not represent all record attempts, earlier rounds or all cubers. Skill references are retrospective and may use future appearances within ±2 years. Tier-subset coverage is disclosed above; do not generalize from it without this coverage table. Bootstrap exposure changes: the intervals are sampling intervals, not replays with original fixed attempt counts. Secondary intervals are pointwise and provide no additional confirmatory verdicts.

Flagged decisions 7–10 in DEVIATIONS.md resolve unspecified secondary details: conditional logistic likelihood; focal-averaged raw/centered cross correlations; subset/deletion weighting and endpoint-only deletion intervals; fixed ≥22-peer prediction panels and auxiliary interval scopes. They were written before opening confirmation times. Arithmetic/equal-tier/per-solver translated intervals remain descriptive and were not given new simulation coverage guarantees. The registered post-failure amendment and the original failed gate remain fully disclosed.

A flagged software correction after opening handles a yearly draw with zero available extrema: retain it as invalid, omit its zero weight from the pooled yearly-beta ratio, and resume unchanged checkpoints. Primary point estimates, primary draws and intervals, seed, eligibility and threshold were unchanged. See DEVIATIONS.md.

QA: 25/25 named checks pass; see qa.json for evidence. Independent numerical re-derivations and preconfirmation methods review are recorded. External review of the completed findings and verified actual-scramble attribution remain prerequisites for specific record stories or filming. No commit was attempted; .git is read-only.
