# Selection diagnosis

All quantities below are on the log R scale. Bootstrap means are computed within each dataset, then averaged.
The frozen-beta column changes only the nuisance refit within the reselecting draws.

| Process | Point mean | Reselect mean | Fixed-selection mean | Reselect, frozen beta | Reselect shift | Fixed shift |
|---|---:|---:|---:|---:|---:|---:|
| null | 0.00005773 | 0.00006655 | 0.00005895 | 0.00006782 | 0.00000882 | 0.00000121 |
| small_shared | 0.01562636 | 0.01437518 | 0.01561856 | 0.01437712 | -0.00125117 | -0.00000780 |
| large_shared | 0.11508463 | 0.10530041 | 0.11507048 | 0.10530329 | -0.00978421 | -0.00001415 |
| shared_plus_tier_interaction | 0.01253664 | 0.01153081 | 0.01254092 | 0.01153089 | -0.00100583 | 0.00000427 |
| informative_dnf | 0.01581936 | 0.01457091 | 0.01581268 | 0.01457091 | -0.00124845 | -0.00000667 |
| random_replacement_10_percent | 0.01273217 | 0.01169254 | 0.01272414 | 0.01169862 | -0.00103963 | -0.00000803 |
| pure_attempt_slot_shock | 0.11521871 | 0.10545720 | 0.11521082 | 0.10545642 | -0.00976151 | -0.00000789 |
| boundary | 0.09526363 | 0.08730270 | 0.09524567 | 0.08730283 | -0.00796093 | -0.00001795 |

Independent multinomial competition draws retain about 63.2% of distinct competitions.
The large shared-effect downward shift disappears when original extrema are held fixed;
holding only training beta fixed does not remove it. This directly supports the proposed
exposure/reselection mechanism. Point-estimator bias and bootstrap-distribution bias are
different: an unbiased point estimator does not make the percentile interval centered correctly.
