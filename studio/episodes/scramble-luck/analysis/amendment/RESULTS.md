# Candidate simulation results

500 draws/dataset; dataset counts are in the machine-readable results; widths use log R and R scales.
Boundary errors are probabilities at R=1.10; elsewhere verdict rates are not false-error rates.

| Method | Process | Datasets | Bias log R | Coverage | Mean log width | Mean R width | Boundary false holds | Boundary false fails |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| original | null | 200 | 0.000058 | 100.0% | 0.005319 | 0.005320 | — | — |
| A | null | 200 | 0.000058 | 100.0% | 0.007390 | 0.007391 | — | — |
| B | null | 200 | 0.000058 | 100.0% | 0.005319 | 0.005320 | — | — |
| C | null | 200 | 0.000058 | 96.0% | 0.002802 | 0.002802 | — | — |
| D | null | 200 | 0.000058 | 99.5% | 0.003908 | 0.003908 | — | — |
| original | small_shared | 200 | -0.000030 | 99.5% | 0.006150 | 0.006239 | — | — |
| A | small_shared | 200 | -0.000030 | 100.0% | 0.008536 | 0.008670 | — | — |
| B | small_shared | 200 | -0.000030 | 99.5% | 0.006150 | 0.006247 | — | — |
| C | small_shared | 200 | -0.000030 | 94.0% | 0.003791 | 0.003850 | — | — |
| D | small_shared | 200 | -0.000030 | 97.5% | 0.005176 | 0.005257 | — | — |
| original | large_shared | 200 | 0.000057 | 1.0% | 0.010339 | 0.011487 | — | — |
| A | large_shared | 200 | 0.000057 | 99.5% | 0.014299 | 0.016045 | — | — |
| B | large_shared | 200 | 0.000057 | 98.5% | 0.010339 | 0.011600 | — | — |
| C | large_shared | 200 | 0.000057 | 95.5% | 0.008813 | 0.009889 | — | — |
| D | large_shared | 200 | 0.000057 | 99.5% | 0.010944 | 0.012280 | — | — |
| original | shared_plus_tier_interaction | 200 | -0.000078 | 99.5% | 0.006390 | 0.006465 | — | — |
| A | shared_plus_tier_interaction | 200 | -0.000078 | 100.0% | 0.008914 | 0.009027 | — | — |
| B | shared_plus_tier_interaction | 200 | -0.000078 | 99.5% | 0.006390 | 0.006471 | — | — |
| C | shared_plus_tier_interaction | 200 | -0.000078 | 95.5% | 0.003791 | 0.003839 | — | — |
| D | shared_plus_tier_interaction | 200 | -0.000078 | 99.5% | 0.005192 | 0.005258 | — | — |
| original | informative_dnf | 200 | -0.000003 | 98.0% | 0.006161 | 0.006251 | — | — |
| A | informative_dnf | 200 | -0.000003 | 100.0% | 0.008499 | 0.008635 | — | — |
| B | informative_dnf | 200 | -0.000003 | 100.0% | 0.006161 | 0.006259 | — | — |
| C | informative_dnf | 200 | -0.000003 | 93.5% | 0.003781 | 0.003841 | — | — |
| D | informative_dnf | 200 | -0.000003 | 98.0% | 0.005165 | 0.005248 | — | — |
| original | random_replacement_10_percent | 200 | 0.000074 | 100.0% | 0.006009 | 0.006079 | — | — |
| A | random_replacement_10_percent | 200 | 0.000074 | 100.0% | 0.008398 | 0.008506 | — | — |
| B | random_replacement_10_percent | 200 | 0.000074 | 100.0% | 0.006009 | 0.006086 | — | — |
| C | random_replacement_10_percent | 200 | 0.000074 | 95.0% | 0.003640 | 0.003686 | — | — |
| D | random_replacement_10_percent | 200 | 0.000074 | 99.0% | 0.004988 | 0.005052 | — | — |
| original | pure_attempt_slot_shock | 200 | 0.000191 | 2.0% | 0.010348 | 0.011499 | — | — |
| A | pure_attempt_slot_shock | 200 | 0.000191 | 99.0% | 0.014354 | 0.016108 | — | — |
| B | pure_attempt_slot_shock | 200 | 0.000191 | 96.5% | 0.010348 | 0.011612 | — | — |
| C | pure_attempt_slot_shock | 200 | 0.000191 | 94.0% | 0.008788 | 0.009861 | — | — |
| D | pure_attempt_slot_shock | 200 | 0.000191 | 98.0% | 0.010917 | 0.012250 | — | — |
| original | boundary | 200 | -0.000047 | 3.5% | 0.009591 | 0.010467 | 0.0% | 96.5% |
| A | boundary | 200 | -0.000047 | 99.5% | 0.013221 | 0.014543 | 0.5% | 0.0% |
| B | boundary | 200 | -0.000047 | 97.0% | 0.009591 | 0.010550 | 2.0% | 1.0% |
| C | boundary | 200 | -0.000047 | 94.5% | 0.007827 | 0.008609 | 3.0% | 2.5% |
| D | boundary | 200 | -0.000047 | 97.5% | 0.009876 | 0.010864 | 1.5% | 1.0% |
