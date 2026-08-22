# Experiment Evidence Synthesis

Status: 2026-08-11. This is a map of every experiment program in this
repository, what it observed, and the strongest conclusion it can support.
It intentionally distinguishes completed evidence from protocols and
infrastructure. It is not a count of independent models or a claim that the
listed studies establish a universal result.

## Bottom Line

Across conventional metric tests, large exploratory grids, controlled
known-truth simulations, a public 10,000-model ledger, and corrected causal-LM
artifacts, the evidence suggests the following research direction:

> Raw metric-performance correlation is not enough to justify a general metric
> claim. Reliability is conditional on task, architecture, intervention
> geometry, baseline information, and the estimand. Metric evaluation should
> therefore report grouped out-of-sample incremental value, uncertainty,
> nuisance-model sensitivity, and abstention alongside raw association.

The experiments justify moving MBE to a higher scale. They do **not** yet
verify a universal metric ranking, establish that any metric family is broadly
invalid, establish cross-task transport, or validate an automatic
metric-selection service. Corrected image and multi-environment artifacts now
exist, but their binding calibration gate abstained. The next scale gate is a
new rule confirmed on disjoint known-truth data, followed by a genuinely
external holdout and independent execution.

## Evidence At A Glance

| Evidence family | What the evidence suggests | Appropriate claim now |
|---|---|---|
| FIM_norm case study | FIM effective rank can pass ordinary correlation and transfer checks, but its useful signal is largely gradient-energy/loss related and does not show reliable value beyond loss in the controlled follow-ups. | An honest self-falsification case study, not a new generalization metric claim. |
| Legacy image/text metric audits | Metric labels vary with task, architecture, pooling, and controls; some metrics survive while others wash out or reverse. | Motivation and regression evidence only: repeated configurations and invalid legacy text masking prevent confirmatory claims. |
| MBE calibration and comparator studies | Full-refit MBE can be conservative in named designs, but the 24/48-configuration benchmark exposed a sharp calibration-power frontier across MBE, GCM, WGCM, KCI, and rank references. | Conditional methodological evidence with explicit sample-size, nuisance, and estimand boundaries. |
| Dziugaite et al. public ledger | Many established measures retain incremental predictive information; a few wash out or reverse, and source robustness ranking measures something different. | MBE is not a blanket metric killer; it is a complementary audit. |
| Corrected causal text | A valid random control and strict refit rule abstained even for strong raw associations in one 36-configuration environment. | MBE can avoid promoting association to support here; real-environment power remains unresolved. |

## Experiment-by-Experiment Record

| Program | Completed work and observation | Scope boundary | Reproduction entry point |
|---|---|---|---|
| 01: MLP acid tests | Varying label noise and training-set size gave FIM effective-rank correlations in the expected direction under ordinary evaluation. | Small digits study; no baseline-controlled increment claim. | [`fim_acid_test.py`](../experiments/01_acid_tests/fim_acid_test.py), [`fim_stability.py`](../experiments/01_acid_tests/fim_stability.py) |
| 02: architecture probes | CNN + BatchNorm transferred the ordinary FIM pattern; Transformer capacity transfer held but its noise probe was not significant; the small ResNet/CIFAR result was directionally mixed. | Architecture plumbing and conventional checks, not a broad transfer study. | [`fim_cnn_test.py`](../experiments/02_architectures/fim_cnn_test.py), [`fim_transformer_test.py`](../experiments/02_architectures/fim_transformer_test.py), [`fim_cifar_test.py`](../experiments/02_architectures/fim_cifar_test.py) |
| 03: metric comparisons and utility | FIM, trace, stable-rank, and gradient magnitude all looked plausible in raw tests; bootstrap uncertainty was often wide. FIM early-stopping rules failed and loss later dominated the prediction task. | Ordinary metric tests cannot establish incremental usefulness. | [`fim_baselines.py`](../experiments/03_comparisons/fim_baselines.py), [`fim_bootstrap_ci.py`](../experiments/03_comparisons/fim_bootstrap_ci.py), [`fim_early_stop.py`](../experiments/03_comparisons/fim_early_stop.py) |
| 04: falsification grids | Two heterogeneous 1,000-row MLP grids moved FIM_norm from raw correlations near `-0.8` to near zero after controls; weight norm also washed out and some sharpness/gradient quantities changed sign. | Strong exploratory confounding demonstration, not independent real-world validation. | [`fim_unified_grid.py`](../experiments/04_falsification/fim_unified_grid.py), [artifact audit](../experiments/06_independent_audit/artifact_audit_report.md) |
| 05: early Kaggle CIFAR | The 50-run local CNN smoke test showed apparent survival; the 250-row result had weak raw signal for most measures. | Engineering and scale discovery; insufficient design control for paper claims. | [`kaggle_cifar10_grid.py`](../experiments/05_kaggle/kaggle_cifar10_grid.py), [`print_results.py`](../experiments/05_kaggle/print_results.py) |
| 06: artifact audit and ResNet smoke tests | Direct recomputation confirmed the large-MLP washouts. Eight- and 18-run ResNet probes were unstable, showing why larger image designs were needed. | An internal audit, not independent external replication; small ResNet samples are non-inferential. | [`artifact_audit.py`](../experiments/06_independent_audit/artifact_audit.py), [`resnet_fim_mbe_smoke.py`](../experiments/06_independent_audit/resnet_fim_mbe_smoke.py) |
| 07: legacy JMLR-scale and CEI studies | The 680-row exploratory pool contained selective survival, washout, and reversals. FIM varied by slice; a derived CEI composite did not generalize, though feature-dispersion residuals were suggestive. | Repeated configurations; legacy text has causal leakage. Preserve as exploratory only. | [`jmlr_scale_experiment.py`](../experiments/07_jmlr_scale/jmlr_scale_experiment.py), [`analyze_jmlr_scale.py`](../experiments/07_jmlr_scale/analyze_jmlr_scale.py), [`ARTIFACTS.md`](../experiments/07_jmlr_scale/ARTIFACTS.md) |
| 08: synthetic and semi-synthetic calibration | Degree-6 interaction-capable nuisance models controlled the named proxy/null cases while recovering injected signal. Degree-2 and tested Extra Trees variants were anti-conservative. | Known-truth calibration, not proof about real metric populations. | [`run_calibration.py`](../experiments/08_protocol_calibration/run_calibration.py), [`run_monte_carlo.py`](../experiments/08_protocol_calibration/run_monte_carlo.py), [calibration report](../experiments/08_protocol_calibration/out/CREDIBILITY_SUMMARY.md) |
| 09: published-study reaudit and PGDL intake | The Dziugaite source statistic reproduced exactly; on its public 10,000-model ledger, most of 32 measures retained B1 incremental evidence, while some washed out or reversed. PGDL metadata/pilot extraction is complete but full metric inference is not. | Retrospective complementary analysis; PGDL is infrastructure until full checkpoint metrics and frozen holdouts run. | [`reproduce_source.py`](../experiments/09_published_metric_reaudit/studies/dziugaite2020/reproduce_source.py), [`run_reaudit.py`](../experiments/09_published_metric_reaudit/run_reaudit.py), [Dziugaite results](../experiments/09_published_metric_reaudit/studies/dziugaite2020/RESULTS.md) |
| 10: method comparison and inference stress | Raw/partial/CMI scores can remain high for known proxies. Interaction MBE largely avoided those false supports and recovered the injected increment. Refit inference was safer than residual permutation, whose clustered-null rate was mildly high. | A finite stress matrix, not a universal coverage guarantee. | [`run_factorial_benchmark.py`](../experiments/10_method_comparison/run_factorial_benchmark.py), [`run_inference_stress.py`](../experiments/10_method_comparison/run_inference_stress.py), [stress report](../experiments/10_method_comparison/out/INFERENCE_STRESS_TEST.md) |
| 11: credibility freeze | The estimand, decision rule, baseline ladder, abstention conditions, and protected PGDL task policy were frozen. | This is a protocol, not empirical evidence. | [`PREREGISTRATION.md`](../experiments/11_credibility_freeze/PREREGISTRATION.md) |
| 12: independent replication workflow | A signed, conflict-declared external audit workflow validates hashes, claim gates, tests, and discrepancies. | No independent executor has completed it yet. | [`run_replication_audit.py`](../experiments/12_independent_replication/run_replication_audit.py) |
| 13: causal-text pilot | 24/24 WikiText-2 runs completed. A future-token perturbation changed causal prefix logits by `0.0`; the intentionally unmasked control changed them. | Implementation gate only, not metric evidence. | [`mbe2_causal_text_pilot.py`](../experiments/13_causal_text_pilot/mbe2_causal_text_pilot.py), [completion report](../experiments/13_causal_text_pilot/PILOT_COMPLETION_REPORT.md) |
| 14: first corrected causal factorial | 100/100 valid causal-LM rows and metric-batch repeats completed. Inference abstained because there were only 20 configuration units and the random control was constant after aggregation. | A preserved implementation failure and corrected raw artifact, not a metric verdict. | [`mbe2_causal_text_factorial.py`](../experiments/14_corrected_causal_text_factorial/mbe2_causal_text_factorial.py), [`analyze_factorial.py`](../experiments/14_corrected_causal_text_factorial/analyze_factorial.py), [artifact record](../experiments/14_corrected_causal_text_factorial/ARTIFACTS.md) |
| 15: sequential causal-text replication | 180/180 valid rows, 36 configuration units, causal test passed, and the random control was valid. Strong raw metric associations, including confidence and margin, produced no joint full-refit support at B1/B2/B3; random control also did not pass. | One text environment. The result can mean no stable increment or inadequate real-environment power; it cannot label all metrics useless. | [`mbe2_causal_text_factorial_replication.py`](../experiments/15_causal_text_factorial_replication/mbe2_causal_text_factorial_replication.py), [`analyze_replication.py`](../experiments/15_causal_text_factorial_replication/analyze_replication.py), [artifact record](../experiments/15_causal_text_factorial_replication/ARTIFACTS.md) |
| 16-18: observed-design CPU calibration | Mapped nuisance degree, inference stress, and refit-draw convergence; full-refit false support was low while residual permutation and small-design power remained problematic. | Known-truth and implementation evidence, not real-metric validity. | [`experiments/17_cpu_credibility_campaign`](../experiments/17_cpu_credibility_campaign), [`experiments/18_refit_draw_convergence`](../experiments/18_refit_draw_convergence) |
| 19-20: protected GPU artifacts | Completed 96 image and 144 multi-corpus text rows with structural, causal, balance, and hash gates passing. | Associations remain sealed because the calibration opening gate has not passed. | [`experiments/19_corrected_image_factorial`](../experiments/19_corrected_image_factorial), [`experiments/20_multicorpus_text_atlas`](../experiments/20_multicorpus_text_atlas) |
| 21: design-matched calibration | Corrected 48,000-cell screen completed with zero eligible finalists. | Binding abstention; protected image/text outcomes stayed locked. | [`experiments/21_design_matched_calibration`](../experiments/21_design_matched_calibration) |
| 22, 25-28: orthogonal development and PGDL transfer | A 192-group rule passed synthetic confirmation, failed pooled-PGDL null control, and was revised. The revision controlled all null cells but narrowly missed one frozen power criterion. | Useful estimator development and honest near miss; no PGDL association was authorized. | [`experiments/22_orthogonal_score_development`](../experiments/22_orthogonal_score_development), [`experiments/28_pgdl_transfer_confirmation_v2`](../experiments/28_pgdl_transfer_confirmation_v2) |
| 23: conditional comparator benchmark | 9,600 paired datasets and 153,600 method rows showed no uniformly calibrated, adequately powered method at 24/48 configurations. | A calibration-power frontier across distinct estimands, not a global method ranking. | [`COMPARATOR_RESULTS.md`](../experiments/23_conditional_comparator_benchmark/COMPARATOR_RESULTS.md) |
| 29: repeated-split stability development | A 10,080-row fresh known-truth screen rejected all six split-stability candidates: tighter stability reduced support but did not retain the required low-sample power. | A retained negative result; no candidate advances to confirmation and no protected association is opened. | [`DEVELOPMENT_RESULTS.md`](../experiments/29_repeated_split_stability_development/DEVELOPMENT_RESULTS.md) |

## What This Body Of Work Supports

1. **Metric evaluation needs stronger evidence than raw correlation.** The
   controlled proxy cases, exploratory MLP grids, Dziugaite reversals, and
   causal-text abstention all show that raw association can be misleading about
   out-of-sample incremental usefulness.
2. **MBE should be an abstaining conditional audit, not a universal score.**
   It needs frozen controls, grouped splits, flexible nuisance sensitivity,
   refit-aware uncertainty, and an explicit declaration of the estimand.
3. **Established metrics are heterogeneous, not uniformly flawed.** The
   Dziugaite reaudit and legacy image slices retain many measures. A washout or
   sign change is evidence about a named environment and baseline, not a global
   death certificate.
4. **FIM_norm is a valuable self-falsification case.** It motivated the work by
   passing conventional tests, then lost its independent case against cheap
   loss baselines in decisive follow-ups. It should be reported as an honest
   case study rather than a central metric claim.
5. **CEI-style residual composites are exploratory.** Feature-dispersion
   residuals merit a preregistered follow-up, but neither the general composite
   nor a cross-domain mechanism is validated.

## What Must Be Verified At Higher Scale

- corrected image factorials with enough independently varied configurations;
- multiple public checkpoint environments, starting with a frozen PGDL
  development/validation/transfer sequence;
- a locked external holdout evaluated once from frozen code and thresholds;
- power calibration in real intervention geometry, especially where strong raw
  metrics are expected to have a true increment;
- prospective metric selection and an independent signed reproduction.

Until then, the responsible public framing is: **the accumulated experiments
justify scaling the research program, not claiming that it has finished the
scientific question.**
