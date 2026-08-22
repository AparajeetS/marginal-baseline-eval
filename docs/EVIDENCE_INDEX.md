# MBE Evidence Index

Status: 2026-08-11. This is the public map from evidence to claims. It is
designed to make it easy to distinguish a validated component, a completed
pipeline, an informative failure, and an unresolved scientific question.

## Read This First

MBE is open research infrastructure, not a completed benchmark claim. The
software, protocols, raw ledgers, failures, and reproduction commands are
public so that an outside reader can see both what the project has established
and what it has not.

| Evidence tier | Status | What it supports | What it does not support |
|---|---|---|---|
| Synthetic and semi-synthetic calibration | Conditional evidence with retained failures | Full-refit inference controls false support and recovers injected signal in named designs; the degrees 1-6 map and a 10,080-row repeated-split screen expose the tradeoff between proxy control and target-design power. | Universal error control, one universally valid nuisance learner, or causal identification. |
| Repeated-split stability development | Completed rejection | Across six candidates on fresh 24/48-configuration geometries, repeated agreement across cross-fit partitions did not meet both the frozen raw null and power floors. | A valid small-design opening rule or authorization to inspect protected associations. |
| Conditional comparator benchmark | Completed mixed result | Across 153,600 method rows at 24/48 configurations, apparent power traded sharply against worst-cell false support; no tested method was uniformly reliable. | Superiority of MBE or any conditional-independence test. |
| Corrected causal-LM pipeline pilot | Passed as implementation evidence | Attention masking, data splits, IDs, metric extraction, resume behavior, and failure handling work on WikiText-2. | Metric-family, selector, or transport claims. |
| Corrected causal-text factorial v1 | Completed; inference abstained | A 100-run, causally valid text ledger with batch-repeatability measurements and a preserved failure record. | Metric survivor/washout labels: it has 20 independent configurations and an invalid configuration-level random control. |
| Causal-text factorial sequential replication | Completed; frozen rule abstained | A preregistered 180-run, causally valid, 36-configuration text ledger with a valid random control and full refit analysis. | A substantive metric null: later known-truth calibration found the mandatory consensus severely underpowered at this design size. |
| Corrected CIFAR-10 image factorial | Completed; protected analysis locked | A preregistered 96-run, 48-configuration artifact with two seeds per configuration, three architectures, repeated metric batches, a protected test split, and a valid run-level random control. | Metric reliability verdicts: the design-matched calibration screen selected no eligible rule, so opening remains unauthorized. |
| Multi-corpus causal-LM atlas | Completed; protected analysis locked | A preregistered 144-run, 72-configuration artifact balanced across WikiText-2, Penn Treebank, and Tiny Shakespeare; all causal and structural gates passed. | Within-corpus or transport verdicts: the outcome-blind calibration screen selected no eligible rule, so opening remains unauthorized. |
| Legacy 680-row image/text pool | Exploratory and quarantined | Historical motivation, software regression cases, and examples of why pooled correlation can mislead. | Confirmatory language-model, transport, or independent-sample claims. |
| PGDL pooled transfer calibration | Completed abstention | The first rule failed null control; a lower-shrinkage revision controlled all null cells but missed one frozen power gate by Wilson lower bound 0.492 versus 0.500. | Protected PGDL target-metric associations; they remain sealed. |
| External holdout, prospective selector, independent replication | Prepared but incomplete | The 240-model PGDL intake and replication packet v2 are structurally validated and hash-sealed; protected opening is denied and the replication run to date is internal only. | Holdout results, prospective selection utility, or independent confirmation. Main paper claims remain blocked. |

The adversarial gate-by-gate record is maintained in
[MBE_CREDIBILITY_LEDGER.md](MBE_CREDIBILITY_LEDGER.md). The historical v1
ledger is retained separately in [SUPPORTING_EVIDENCE.md](../SUPPORTING_EVIDENCE.md).
For a complete experiment-by-experiment account, including reproduction entry
points and the claim boundary of each program, see
[EXPERIMENT_EVIDENCE_SYNTHESIS.md](EXPERIMENT_EVIDENCE_SYNTHESIS.md).
The completed CPU campaign and its frozen transition gates are recorded in
[CPU_CAMPAIGN_NEXT_48_HOURS.md](CPU_CAMPAIGN_NEXT_48_HOURS.md).
The frozen observed-design power calibration and its 16-vCPU execution record
are in
[`experiments/16_causal_text_observed_design_power/`](../experiments/16_causal_text_observed_design_power/).
The frozen follow-on known-truth and reproduction campaign is in
[`experiments/17_cpu_credibility_campaign/`](../experiments/17_cpu_credibility_campaign/).
The paired full-refit draw convergence study is in
[`experiments/18_refit_draw_convergence/`](../experiments/18_refit_draw_convergence/).
The completed, analysis-locked GPU artifacts are in
[`experiments/19_corrected_image_factorial/`](../experiments/19_corrected_image_factorial/)
and
[`experiments/20_multicorpus_text_atlas/`](../experiments/20_multicorpus_text_atlas/).

## CPU Credibility Campaign

The 16-vCPU campaign completed:

- 8,000 full-refit stress rows and 8,000 block-null rows;
- 45,000 observed-design rows across degrees 1, 2, 3, 4, and 6;
- 19,200 new generic degree 1/3/4 calibration rows, combined with the existing
  degree 2/6 grid;
- 4,000 paired 99/199/499/999-draw convergence rows;
- a 9,700-run public Dziugaite ledger reconstruction and reaudit.

The full-refit predictive path had 0.25% false support across 6,400 named
null/proxy rows and recovered all 1,600 injected-signal rows. Residual
permutation remained anti-conservative at 5.30%-7.25% and is diagnostic only.
The nuisance-complexity ablation found no universal two-family operating point:
degrees 1-3 failed generic proxies, while the interaction family had only
1.0%-4.6% large-effect power in the 36-configuration observed design. The
current consensus rule is therefore an informative methodological failure,
not evidence that real metrics lack information.

See
[`NUISANCE_COMPLEXITY_ABLATION.md`](../experiments/17_cpu_credibility_campaign/NUISANCE_COMPLEXITY_ABLATION.md),
[`INFERENCE_STRESS_RESULTS.md`](../experiments/17_cpu_credibility_campaign/INFERENCE_STRESS_RESULTS.md),
and
[`RESULTS.md`](../experiments/18_refit_draw_convergence/RESULTS.md).

## Current Corrected Causal Evidence

### Pipeline pilot

The corrected WikiText-2 causal-LM pilot completed 24 of 24 planned rows. A
future-token perturbation changed causal prefix logits by exactly `0.0`, while
the intentionally unmasked negative control changed them by `3.1989`. The
pilot sources and compact completion record are in
[`experiments/13_causal_text_pilot/`](../experiments/13_causal_text_pilot/).

This result matters because the legacy character-LM experiment lacked causal
masking and is excluded from current language-model evidence. It is still only
a pipeline gate, not a result about metric validity.

### First corrected factorial

The first corrected factorial completed all 100 planned WikiText-2 runs:
two model sizes, ten training configurations, five seeds each, and three
deterministic metric batches per model. The raw CSV, Kaggle manifest, source,
analysis script, hashes, and report are in
[`experiments/14_corrected_causal_text_factorial/`](../experiments/14_corrected_causal_text_factorial/).

The integrity review found two limitations that are intentionally retained:

1. five repeated seeds do not create 100 independent interventions; the
   factorial contains 20 configuration units and falls below the frozen 30-unit
   inference floor;
2. the original `random_metric` was seeded by repeated seed ID only, making it
   constant after configuration aggregation and invalid as a configuration-level
   negative control.

The run therefore contributes a corrected pipeline, a transparent raw ledger,
and metric batch-stability measurements. It does not receive MBE
increment-supported, survivor, or washout labels.

### Sequential replication

The preregistered replacement replication completed at
[`experiments/15_causal_text_factorial_replication/`](../experiments/15_causal_text_factorial_replication/):
180 / 180 valid WikiText-2 causal-LM rows, two model sizes, a balanced `3 x 3 x
2` intervention grid, and five seeds per configuration. It has 36 independent
configuration units, a valid full-`run_id` random control, a passing causal
behavior test, and 9.185 P100-hours of recorded execution.

Several metrics have strong raw configuration-level associations with test
NLL, but no metric passed the frozen joint full-refit increment rule under B1
(design), B2 (training-state), or B3 (validation) baselines. The repaired
random control also passed no baseline. Later known-truth calibration in this
exact geometry found that the mandatory interaction-family veto has only
1.0%-4.6% power even for the largest injected effect. The completed
real-metric result is therefore a valid frozen abstention but cannot support a
substantive claim that the metrics contain no incremental information. The raw
ledger, provenance hashes, and complete result tables are in
[`ARTIFACTS.md`](../experiments/15_causal_text_factorial_replication/ARTIFACTS.md).

This remains one environment. It is evidence that MBE can expose failure in
its own analysis specification, not evidence that any metric family is
universally reliable or unreliable.

## Prospective GPU Artifacts: Analysis Locked

On 2026-08-11, two new private Kaggle runs completed from code and protocols
hashed before submission:

- the corrected CIFAR-10 image factorial completed 96 / 96 valid rows across
  48 configurations, two seeds, and three architectures in 1.984 P100-hours;
- the multi-corpus causal-LM atlas completed 144 / 144 valid rows across 72
  configurations, two seeds, and three corpora in 1.264 P100-hours.

Both artifacts have zero failed rows, zero duplicate run IDs, complete
configuration/seed balance, matching source and dataset or split hashes, and
passing preregistered completion gates. The text atlas also passed its causal
mask and unmasked negative-control checks. Independent structural validation
is reproducible with
[`experiments/validate_gpu_followups.py`](../experiments/validate_gpu_followups.py).

No target-metric association from either ledger has been interpreted. The
protected analysis remains locked until design-matched known-truth calibration
selects eligible nuisance families without consulting the real metric
outcomes. Completion therefore upgrades the project from "missing datasets"
to "complete prospective artifacts awaiting a frozen analysis gate"; it does
not yet add survivor, washout, or transport claims.

That gate was frozen and completed in
[`experiments/21_design_matched_calibration`](../experiments/21_design_matched_calibration/README.md).
It reconstructs the 96-row image and 48-row per-corpus text geometries without
reading either protected result CSV, screens five prespecified nuisance
learners on known-truth null and signal surfaces, and requires full-refit
confirmation before emitting a binding open-or-abstain decision. Its corrected
48,000-cell screen retained zero eligible finalists, so both protected analyses
remain locked.

Subsequent orthogonal-score development is preserved in experiments 22 and 25.
The first 240-model PGDL transfer calibration failed null control. A
lower-shrinkage revision then passed every null criterion but missed the B3
power gate by `0.492` versus the frozen `0.500` minimum in experiment 28. No
protected PGDL association was opened. The strong conditional comparator study
in experiment 23 retained 153,600 rows and found no tested procedure with both
strict worst-cell calibration and useful worst-cell power at 24/48 independent
configurations.

## Grantmaker Snapshot

What is already built and inspectable:

- an MIT-licensed Python package, CLI, public notebook, and reproduction path;
- a frozen MBE 2.0 research program with explicit non-claims;
- synthetic calibration, comparator, and refit-aware inference harnesses;
- machine-readable claim gates, provenance manifests, and failure records;
- a corrected causal-LM pipeline, a preserved 100-run abstention artifact, and
  a completed 180-run full-refit text replication;
- complete, structurally validated 96-run image and 144-run multi-corpus text
  artifacts whose protected analyses remain locked.

What funding and compute unlock:

- a locked external holdout and a PGDL metric atlas after a future calibration
  rule earns the frozen opening gate;
- a calibrated protected analysis of the completed image and multi-corpus
  artifacts;
- prospective selector outcomes and independent reproduction;
- a public benchmark release whose claims are tied to raw, reproducible
  evidence rather than model-count rhetoric.

## Curation Rules

- A result becomes public evidence only with a source script, raw ledger or
  source pointer, manifest, integrity check, scope statement, and reproduction
  command.
- Dataset copies, transient Kaggle logs, credentials, and local client tools
  are not committed.
- Failures are preserved and linked from the evidence index; they are not
  silently repaired away.
- Legacy outputs are not promoted to MBE 2.0 claims until separately reviewed
  against the current estimand and inference protocol.
