# Selection diagnosis

All quantities below are on the log R scale. Bootstrap means are computed within each dataset, then averaged.
The frozen-beta column changes only the nuisance refit within the reselecting draws.

| Process | Point mean | Reselect mean | Fixed-selection mean | Reselect, frozen beta | Reselect shift | Fixed shift |
|---|---:|---:|---:|---:|---:|---:|
| null | -0.00002699 | -0.00000471 | -0.00002215 | -0.00000279 | 0.00002227 | 0.00000484 |
| small_shared | 0.01572425 | 0.01444165 | 0.01571571 | 0.01444753 | -0.00128260 | -0.00000855 |
| large_shared | 0.11502799 | 0.10528162 | 0.11503352 | 0.10528154 | -0.00974637 | 0.00000553 |
| shared_plus_tier_interaction | 0.01274958 | 0.01166263 | 0.01276077 | 0.01166323 | -0.00108695 | 0.00001119 |
| informative_dnf | 0.01581939 | 0.01459404 | 0.01581023 | 0.01459597 | -0.00122535 | -0.00000915 |
| random_replacement_10_percent | 0.01254114 | 0.01159286 | 0.01254382 | 0.01159169 | -0.00094828 | 0.00000269 |
| pure_attempt_slot_shock | 0.11506448 | 0.10535181 | 0.11505855 | 0.10535149 | -0.00971267 | -0.00000594 |
| boundary | 0.09529842 | 0.08731873 | 0.09528400 | 0.08731936 | -0.00797969 | -0.00001442 |

Independent multinomial competition draws retain about 63.2% of distinct competitions.
The large shared-effect downward shift disappears when original extrema are held fixed;
holding only training beta fixed does not remove it. This directly supports the proposed
exposure/reselection mechanism. Point-estimator bias and bootstrap-distribution bias are
different: an unbiased point estimator does not make the percentile interval centered correctly.
