# JMLR Milestone Roadmap

Status: gated execution plan for MBE 2.0.

The dates below are effort estimates, not promises. A gate must pass before the
next compute-heavy milestone begins. Failed gates trigger redesign or a venue
reassessment; they do not trigger narrative tuning.

## Definition Of Done

The project is ready for JMLR submission only when:

- the paper's novelty over Jiang-style conditional evaluation and robust
  environment evaluation is explicit and empirically demonstrated;
- the primary method is calibrated under known synthetic ground truth;
- all headline claims replicate under configuration/seed block uncertainty;
- one external environment remains locked until the method and paper claims are
  frozen;
- the reliability atlas keeps generalization, robustness, calibration, final
  performance, and optimization targets separate;
- any selector claim is evaluated by leave-one-task-family-out regret and
  calibrated abstention against frozen simple baselines;
- the text model and data splits are valid and leakage-tested;
- raw ledgers, hashes, metric cards, code, and one-command table regeneration
  are public;
- the manuscript survives an adversarial internal review against the strongest
  plausible rejection arguments.

## Milestone Summary

| Milestone | Main output | Compute | Gate |
|---|---|---:|---|
| M0 | v1 evidence quarantine and corrected claim ledger | CPU | historical claims corrected |
| M1 | frozen MBE 2.0 specification and metric cards | CPU | estimands and controls approved |
| M2 | calibrated statistical implementation | CPU | synthetic null/proxy tests pass |
| M3 | public-corpus reliability atlas | 60-100 GPU-h | conditionality and novelty demonstrated |
| M3b | selector feasibility and abstention calibration | CPU | held-out-family baselines beaten or claim narrowed |
| M4 | end-to-end pilot and runtime calibration | 15-25 GPU-h | no leakage, IDs or pipeline failures |
| M5 | corrected image factorial | 70-120 GPU-h | block-level replication succeeds |
| M6 | corrected causal text factorial | 70-120 GPU-h | text findings valid and stable |
| M7 | locked external holdout | 30-80 GPU-h | preregistered primary result reported |
| M8 | final statistics and artifact release | CPU plus 20-40 GPU-h | all tables reproducible |
| M9 | manuscript and adversarial review | CPU | submission checklist passes |
| M10 | JMLR submission | none | package archived and submitted |

GPU-hour ranges are 4090-equivalent planning estimates. The compute budget is
defined in `COMPUTE_AND_COST_PLAN.md`.

## M0: Quarantine Legacy Evidence

Estimated effort: 3-5 focused days.

Tasks:

1. Preserve all v1 raw files and hashes.
2. Create a canonical deduplicated configuration ledger.
3. Mark the v1 character-transformer evidence invalid because it lacks causal
   masking.
4. Recompute image results using configuration weighting and baseline ladders
   that include training loss.
5. Recompute MLP results using cross-fitted nonlinear nuisance models.
6. List every withdrawn, pilot-only, and still-supported claim.
7. Separate FIM effective rank from CEI-R in all project-facing documents.

Deliverables:

- `LEGACY_V1_AUDIT.md`;
- canonical legacy ledger with duplicate groups;
- corrected pilot figures;
- test demonstrating the old text leakage.

Gate M0:

- no public document presents 680 rows as 680 IID observations;
- no text result is described as valid LM evidence;
- no v1 result is labeled confirmatory.

## M1: Freeze The Scientific Questions

Estimated effort: 5-7 days.

Tasks:

1. Freeze the E0-E4 estimands and B0-B3 baseline ladder.
2. Define environments and target variables.
3. Select 12-18 mechanism-distinct metrics.
4. Write a metric card for every selected metric.
5. Specify expected direction separately for every target.
6. Define primary and secondary hypotheses.
7. Define minimum practically relevant predictive improvement after pilot
   variance estimates are available.
8. Specify missingness, failure, and exclusion rules.
9. Write the external preregistration template.
10. Freeze the conditional reliability profile, selector comparators, decision
    metrics, evidence levels, and abstention semantics.

Gate M1:

- every table planned for the paper maps to a named estimand;
- no baseline variable is included or excluded using an unverified causal DAG;
- seed is a block/random factor, never an ordered covariate;
- metric definitions and provenance pass independent code review.
- no metric is assigned a global verdict without a target and environment;
- selector evaluation follows `CONDITIONAL_METRIC_RELIABILITY_PROTOCOL.md`.

## M2: Implement And Calibrate MBE 2.0

Estimated effort: 7-12 days.

Engineering tasks:

1. Add strict schema validation and fail on missing controls.
2. Implement grouped cross-fitting and leave-environment-out evaluation.
3. Implement nonlinear nuisance models with a frozen tuning grid.
4. Implement paired predictive-loss and concordance deltas.
5. Implement configuration/seed block bootstrap.
6. Implement within-environment permutation tests and FDR correction.
7. Add metric coverage, runtime, and repeatability reporting.
8. Preserve linear partial Spearman as a labeled descriptive baseline.

Scientific calibration:

- null metric false-positive rate;
- hyperparameter-only proxy detection;
- nonlinear confounding;
- task pooling and Simpson reversal;
- suppressor/post-training baseline examples;
- transportable versus environment-specific metric signals.

Gate M2:

- nominal null error is calibrated within Monte Carlo uncertainty;
- deceptive controls receive the expected audit profiles;
- cross-fitting does not leak groups or environments;
- results reproduce across at least two nuisance-model families;
- the comparison to CMI, granulated Kendall, and robust sign error is runnable.

No main GPU sweep is permitted before Gate M2 passes.

## M3: Public-Corpus Reliability Atlas

Estimated effort: 7-14 days plus 60-100 GPU-hours for metric extraction.

Tasks:

1. Acquire and hash at least one suitable public model corpus.
2. Reconstruct its environments, targets, and hyperparameter records.
3. Reproduce published baseline evaluation scores where possible.
4. Run E0-E4 comparisons and deceptive controls separately by target and
   environment.
5. Reserve at least one corpus or environment as an untouched external holdout
   if licensing and artifact coverage allow.
6. Document unavailable checkpoints or unsupported metrics.
7. Produce the task-by-metric reliability atlas with uncertainty, sign
   stability, transport, coverage, and measurement cost.

Gate M3:

- MBE 2.0 reveals an interpretable distinction not already supplied by the
  prior evaluation methods;
- at least one finding is stable across public environments;
- missingness does not determine the metric-family ranking;
- the paper's novelty statement can be written without claiming priority for
  hyperparameter conditioning itself.
- apparent global rankings are decomposed into target- and environment-specific
  profiles rather than promoted as universal verdicts.

If Gate M3 fails, reassess JMLR before purchasing the main compute block.

## M3b: Conditional Selector Feasibility

Estimated effort: 5-10 CPU-focused days after the atlas is frozen.

Tasks:

1. Implement a transparent reliability-rule baseline before any learned
   selector.
2. Implement nested leave-one-task-family-out evaluation.
3. Compare against the globally best metric, pooled raw correlation,
   within-task raw correlation where permitted, baseline-only prediction,
   regularized stacking, and the task-specific oracle upper bound.
4. Report selection regret, top-k utility recovery, sign error, interval
   calibration, and coverage-regret curves.
5. Test whether adding architecture or dataset identity merely memorizes task
   families.
6. Separate L1 transport recommendations from L2 target-calibrated
   recommendations in every output.

Gate M3b:

- all selector tuning occurs inside the outer training-task folds;
- protected tasks do not set thresholds, features, or metric eligibility;
- abstention reduces regret at reduced coverage rather than merely suppressing
  unfavorable examples;
- a selector is promoted to a primary claim only if it improves held-out-family
  regret over the globally best and pooled-correlation selectors;
- with fewer than 12 task families, results are labeled feasibility evidence.

## M4: End-To-End Pilot

Estimated effort: 3-5 days and 15-25 GPU-hours.

Pilot matrix:

- one image dataset;
- one CNN and one transformer architecture;
- two configurations;
- three seeds;
- one causal text configuration with three seeds;
- all metrics and baseline levels.

Tests:

- causal attention mask unit and behavioral tests;
- fixed split and fixed metric-batch hashes;
- unique run/config/seed identifiers;
- deterministic resume behavior;
- metric implementation agreement with references;
- runtime and peak-memory measurement;
- preemption recovery and ledger integrity.

Gate M4:

- zero label or split leakage;
- zero duplicate primary keys;
- all required metrics meet coverage targets;
- projected main-run cost remains inside the approved budget;
- one command regenerates pilot tables from raw outputs.

## M5: Corrected Image Factorial

Estimated effort: 1-2 execution weeks and 70-120 GPU-hours minimum.

Minimum matrix:

```text
2 datasets x 3 architectures x 8 configurations x 5 seeds = 240 runs
```

Recommended matrix:

```text
2 datasets x 3 architectures x 12 configurations x 5 seeds = 360 runs
```

The configuration design must support matched interventions to learning rate,
weight decay, optimizer or augmentation while maintaining useful coverage of
ordinary training regimes.

Gate M5:

- configuration/seed block confidence intervals are available;
- negative controls remain calibrated;
- at least one metric-family result replicates across both image datasets;
- conclusions are stable under the preregistered nuisance-model sensitivity;
- both final performance and generalization-gap targets are reported.
- each dataset/architecture subgroup retains an explicit environment ID so it
  can contribute to grouped transport analysis without being miscounted as a
  fully independent task family.

## M6: Corrected Causal Text Factorial

Estimated effort: 1-2 execution weeks and 70-120 GPU-hours minimum.

Minimum matrix:

```text
1 dataset x 2 model sizes x 10 configurations x 5 seeds = 100 runs
```

Recommended extension:

- third model size or second text task;
- 150-200 total runs;
- one public pretrained-model environment for transport testing.

Gate M6:

- causal-mask leakage tests pass on every code path;
- perplexity or token NLL is primary and accurately computed;
- metric batch-size sensitivity is quantified;
- at least one result is stable across model sizes;
- no claim depends on pooling image accuracy with text accuracy.
- the text environment tests cross-modality abstention rather than assuming an
  image-trained recommendation should transfer.

## M7: Locked External Holdout

Estimated effort: 3-7 days and 30-80 GPU-hours if new training is required.

Before unblinding:

1. Freeze repository commit and container digest.
2. Freeze metric cards, primary hypotheses, nuisance models, and commands.
3. Publish a timestamped preregistration and artifact manifest.
4. Verify that no result from the environment has been inspected during
   method development.
5. Freeze the selector, utility definition, comparators, and abstention
   threshold using development/validation task families only.

After unblinding:

- execute the frozen analysis once;
- report deviations and failures before exploratory follow-up;
- retain the primary result regardless of direction.

Gate M7:

- the main methodological conclusion replicates, or the paper is rewritten to
  accurately report the failure;
- no post-hoc threshold, metric-list, or exclusion change affects the primary
  table.
- recommendation evidence levels and abstentions remain correct after transfer.

## M8: Final Analysis And Artifact Release

Estimated effort: 7-12 days.

Tasks:

- finalize block-bootstrap and permutation results;
- run all ablations and nuisance-model sensitivity checks;
- generate metric-family and environment-level figures;
- generate the reliability atlas and selector coverage-regret figures;
- produce runtime, memory, coverage, and reliability tables;
- package raw ledgers, hashes, split manifests, and metric cards;
- release an MBE 2.0 package candidate;
- verify all reproduction commands in a clean environment.

Gate M8:

- no table depends on an untracked file;
- all headline values trace to raw ledgers;
- package and experiment implementations agree;
- automated tests cover known v1 failures;
- an external reader can regenerate the paper tables without GPU training.

## M9: Manuscript And Adversarial Review

Estimated effort: 2-3 weeks.

Draft order:

1. related work and novelty matrix;
2. estimands and method;
3. synthetic calibration;
4. public benchmark;
5. new image/text evidence;
6. locked holdout;
7. limitations and reporting recommendations;
8. FIM effective-rank case study;
9. CEI-R exploratory appendix.

Adversarial review questions:

- Is MBE 2.0 merely a standard conditional-independence test?
- Does the contribution remain after removing FIM effective rank?
- Are metric implementations faithful and comparable?
- Are targets truly generalization rather than optimization success?
- Is the external holdout genuinely untouched?
- Do results survive environment and configuration weighting?
- Is the method practically useful relative to its complexity?
- Does the selector outperform a globally fixed metric, or is the atlas the
  actual contribution?
- Is the effective sample size counted in task families rather than models?

Gate M9:

- every strong claim has a direct table, figure, theorem, or calibrated
  simulation supporting it;
- the manuscript uses the JMLR template and contains no placeholder metadata;
- related work accurately credits prior conditional and robust evaluation;
- limitations state the non-causal scope plainly;
- all coauthors approve the artifact and claims.

## M10: Submission

Estimated effort: 2-3 days.

Checklist:

- final JMLR PDF and supplement;
- anonymization or author metadata per current submission instructions;
- repository release tag and archival DOI;
- code/data license check;
- funding and compute-credit disclosure;
- cover letter with novelty statement;
- suggested reviewers and conflicts checked;
- no simultaneous submission elsewhere.

## Stop-Loss Rules

Pause GPU spending and reassess if:

- synthetic calibration cannot distinguish genuine signal from deceptive
  proxies;
- public-corpus results are fully explained by prior methods;
- metric missingness exceeds 10% in a primary environment;
- pilot cost is more than 1.5 times the planned rate;
- the main conclusion changes across reasonable nuisance models without a
  principled resolution;
- the external holdout cannot be protected from development leakage.
