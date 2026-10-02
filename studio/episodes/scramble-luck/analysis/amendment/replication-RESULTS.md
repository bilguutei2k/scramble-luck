# Candidate simulation results

500 draws/dataset; dataset counts are in the machine-readable results; widths use log R and R scales.
Boundary errors are probabilities at R=1.10; elsewhere verdict rates are not false-error rates.

| Method | Process | Datasets | Bias log R | Coverage | Mean log width | Mean R width | Boundary false holds | Boundary false fails |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| original | null | 200 | -0.000027 | 100.0% | 0.005316 | 0.005316 | — | — |
| A | null | 200 | -0.000027 | 100.0% | 0.007432 | 0.007432 | — | — |
| B | null | 200 | -0.000027 | 100.0% | 0.005316 | 0.005316 | — | — |
| C | null | 200 | -0.000027 | 96.5% | 0.002813 | 0.002813 | — | — |
| D | null | 200 | -0.000027 | 98.0% | 0.003918 | 0.003918 | — | — |
| original | small_shared | 200 | 0.000067 | 99.0% | 0.006147 | 0.006237 | — | — |
| A | small_shared | 200 | 0.000067 | 100.0% | 0.008506 | 0.008641 | — | — |
| B | small_shared | 200 | 0.000067 | 99.5% | 0.006147 | 0.006245 | — | — |
| C | small_shared | 200 | 0.000067 | 94.0% | 0.003775 | 0.003835 | — | — |
| D | small_shared | 200 | 0.000067 | 98.0% | 0.005162 | 0.005243 | — | — |
| original | large_shared | 200 | 0.000001 | 2.0% | 0.010315 | 0.011460 | — | — |
| A | large_shared | 200 | 0.000001 | 100.0% | 0.014256 | 0.015996 | — | — |
| B | large_shared | 200 | 0.000001 | 96.0% | 0.010315 | 0.011572 | — | — |
| C | large_shared | 200 | 0.000001 | 93.5% | 0.008781 | 0.009851 | — | — |
| D | large_shared | 200 | 0.000001 | 96.5% | 0.010911 | 0.012242 | — | — |
| original | shared_plus_tier_interaction | 200 | 0.000135 | 100.0% | 0.006388 | 0.006463 | — | — |
| A | shared_plus_tier_interaction | 200 | 0.000135 | 100.0% | 0.008900 | 0.009014 | — | — |
| B | shared_plus_tier_interaction | 200 | 0.000135 | 100.0% | 0.006388 | 0.006470 | — | — |
| C | shared_plus_tier_interaction | 200 | 0.000135 | 95.5% | 0.003806 | 0.003855 | — | — |
| D | shared_plus_tier_interaction | 200 | 0.000135 | 100.0% | 0.005208 | 0.005275 | — | — |
| original | informative_dnf | 200 | -0.000003 | 99.5% | 0.006153 | 0.006244 | — | — |
| A | informative_dnf | 200 | -0.000003 | 100.0% | 0.008521 | 0.008657 | — | — |
| B | informative_dnf | 200 | -0.000003 | 100.0% | 0.006153 | 0.006252 | — | — |
| C | informative_dnf | 200 | -0.000003 | 94.5% | 0.003782 | 0.003842 | — | — |
| D | informative_dnf | 200 | -0.000003 | 99.5% | 0.005164 | 0.005247 | — | — |
| original | random_replacement_10_percent | 200 | -0.000117 | 100.0% | 0.006025 | 0.006096 | — | — |
| A | random_replacement_10_percent | 200 | -0.000117 | 100.0% | 0.008356 | 0.008462 | — | — |
| B | random_replacement_10_percent | 200 | -0.000117 | 100.0% | 0.006025 | 0.006101 | — | — |
| C | random_replacement_10_percent | 200 | -0.000117 | 93.5% | 0.003621 | 0.003667 | — | — |
| D | random_replacement_10_percent | 200 | -0.000117 | 99.5% | 0.004974 | 0.005037 | — | — |
| original | pure_attempt_slot_shock | 200 | 0.000037 | 1.0% | 0.010237 | 0.011375 | — | — |
| A | pure_attempt_slot_shock | 200 | 0.000037 | 100.0% | 0.014196 | 0.015928 | — | — |
| B | pure_attempt_slot_shock | 200 | 0.000037 | 97.0% | 0.010237 | 0.011486 | — | — |
| C | pure_attempt_slot_shock | 200 | 0.000037 | 95.0% | 0.008753 | 0.009821 | — | — |
| D | pure_attempt_slot_shock | 200 | 0.000037 | 97.0% | 0.010886 | 0.012214 | — | — |
| original | boundary | 1000 | -0.000012 | 2.0% | 0.009577 | 0.010451 | 0.0% | 98.0% |
| A | boundary | 1000 | -0.000012 | 99.9% | 0.013220 | 0.014543 | 0.1% | 0.0% |
| B | boundary | 1000 | -0.000012 | 98.5% | 0.009577 | 0.010535 | 0.6% | 0.9% |
| C | boundary | 1000 | -0.000012 | 96.0% | 0.007850 | 0.008636 | 1.5% | 2.5% |
| D | boundary | 1000 | -0.000012 | 98.7% | 0.009897 | 0.010887 | 0.4% | 0.9% |
