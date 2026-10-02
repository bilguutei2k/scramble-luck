# S1 measurement-validation pilot — progress

Step 1: Read BRIEF, verified design and red-team review. Wrote SLICE.md first, reusing the exact round-3 competition hash rule and recorded structural counts. Next: independently validate source hashes and ID membership, then run simulation before real outcomes.

Step 2: Independently matched all eight source SHA-256 hashes to round 3 and recomputed the slice ID seal. Extracted real panel sizes using only structural fields, before new outcome analysis. Simulation is next.

Simulation saved: null; common bias -0.000004; coverage 0.927; split-peer r -0.001.

Simulation saved: small_shared; common bias -0.000001; coverage 0.953; split-peer r 0.183.

Simulation saved: large_shared; common bias 0.000004; coverage 0.950; split-peer r 0.497.

Simulation saved: shared_and_tier; common bias -0.000208; coverage 0.018; split-peer r 0.125.

Simulation saved: tier_only; common bias -0.000208; coverage 0.000; split-peer r -0.059.

Simulation saved: MCAR_DNF; common bias -0.000004; coverage 0.943; split-peer r 0.170.

Simulation saved: informative_DNF; common bias -0.000014; coverage 0.932; split-peer r 0.170.

Interaction validation saved: shared_and_tier; shared and interaction coverage [0.96, 0.95].

Interaction validation saved: tier_only; shared and interaction coverage [0.935, 0.968].

Interaction validation saved: no_tier; shared and interaction coverage [0.96, 0.925].

Selection validation saved: shared variance 0.0009; unshrunk bias -0.00011, shrinkage bias -0.00716.

Selection validation saved: shared variance 0.004; unshrunk bias 0.00019, shrinkage bias -0.01484.

Step 4: Missing-pattern moment estimator retains 117,779 valid solves in 1,996 finals; shared within-solver share 3.81%. Saved crossed-bootstrap uncertainty and complete-case/tail sensitivities.

Step 5: Random-k peer prediction and fixed-large-panel reliability curves saved, including extrapolations and changing-panel counts.

Step 6: Skill-tier interaction test saved on 1260 finals; method interaction is untestable because method is absent.

Step 7: Binary DNF companion saved; DNS reported separately. No whole panels removed and no arbitrary DNF times imputed.

Step 8: Selection-aware exploratory seasonal extremes saved: n=180, geometric median-scramble ratio 1.0049. Exact verified-cohort rule remains untestable.

Step 9: Three draft PNGs and replacement sensitivities saved. Next: synthesize report, power and frozen preregistration specification.

Predictive refinement: hyperparameters now frozen from pre-2019; 2019–2025 target peer times predicted with baselines excluding each target solve. Competition intervals at k=2,5,10,20 saved.

Interaction refinement: added competition+solver bootstrap sensitivity. Negative raw variance and correlations above one explicitly labelled as unconstrained sampling diagnostics.

Central visuals updated to distinguish aggregate unshrunk attribution from shrunken individual displays.

Era replication, leave-year-out shared fractions, and 200 independent-solver alignment negative-controls saved.

Sources and slice independently verified. All confirmation queries were structural; outcome extraction is restricted inside SQL to explore=true.

Simulation saved: null; common bias -0.000004; coverage 0.927; split-peer r -0.001.

Simulation saved: small_shared; common bias -0.000001; coverage 0.953; split-peer r 0.183.

Simulation saved: large_shared; common bias 0.000004; coverage 0.950; split-peer r 0.497.

Simulation saved: shared_and_tier; common bias -0.000208; coverage 0.018; split-peer r 0.125.

Simulation saved: tier_only; common bias -0.000208; coverage 0.000; split-peer r -0.059.

Simulation saved: MCAR_DNF; common bias -0.000004; coverage 0.943; split-peer r 0.178.

Simulation saved: informative_DNF; common bias -0.000014; coverage 0.932; split-peer r 0.177.

Interaction validation saved: shared_and_tier; shared and interaction coverage [0.96, 0.95].

Interaction validation saved: tier_only; shared and interaction coverage [0.935, 0.968].

Interaction validation saved: no_tier; shared and interaction coverage [0.96, 0.925].

Selection validation saved: shared variance 0.0009; unshrunk bias -0.00011, shrinkage bias -0.00716.

Selection validation saved: shared variance 0.004; unshrunk bias 0.00019, shrinkage bias -0.01484.

Step 4: Missing-pattern moment estimator retains 117,779 valid solves in 1,996 finals; shared within-solver share 3.81%. Saved crossed-bootstrap uncertainty and complete-case/tail sensitivities.

Step 5: Random-k peer prediction on 2019–2025 slice finals with pre-2019 hyperparameters frozen; fixed-large-panel reliability curves saved, including extrapolations and changing-panel counts.

Step 6: Skill-tier interaction test saved on 1260 finals; method interaction is untestable because method is absent.

Step 7: Binary DNF companion saved; DNS reported separately. No whole panels removed and no arbitrary DNF times imputed.

Step 8: Selection-aware exploratory seasonal extremes saved: n=180, geometric median-scramble ratio 1.0049. Exact verified-cohort rule remains untestable.

Era replication, leave-year-out shared fractions, and 200 independent-solver alignment negative-controls saved.

Step 9: Three draft PNGs and replacement sensitivities saved. Next: synthesize report, power and frozen preregistration specification.
