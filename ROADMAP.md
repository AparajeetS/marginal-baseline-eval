# MBE Research Roadmap

Status: active, gated plan for MBE 2.0.

Milestones advance only when their evidence gate passes. A failed gate narrows
the claim, changes the design, or stops that line of work. It does not justify
post-hoc threshold tuning or repeated execution until a preferred result
appears.

## Definition Of Done

The project is ready for peer review when:

- novelty over established conditional and robust evaluation methods is stated
  precisely and demonstrated empirically;
- false-positive behavior and power are calibrated on known-truth cases;
- headline results use configuration- or task-level uncertainty rather than
  treating correlated model rows as independent;
- one external environment remains protected until the method and claims are
  frozen;
- generalization, robustness, calibration, optimization, and final-performance
  targets remain separate;
- selector claims use held-out task families, explicit regret, and calibrated
  abstention;
- image and causal-language pipelines pass leakage and schema checks;
- raw ledgers, hashes, metric cards, code, and table regeneration are public;
- an independent executor reports agreement or discrepancies from frozen
  artifacts;
- one safety-facing measurement audit uses an independently defined target and
  reports support or abstention under a prospectively calibrated rule;
- the manuscript survives adversarial review against the strongest plausible
  rejection arguments.

## Milestone Summary

| ID | Milestone | Current status | Main output | New compute |
|---|---|---|---|---:|
| M0 | Quarantine legacy evidence | Passed | corrected claim and provenance boundary | CPU |
| M1 | Freeze scientific questions | Passed | estimands, controls, metrics, and non-claims | CPU |
| M2 | Calibrate MBE 2.0 | Blocked; 48-configuration oracle gap identified | known-truth calibration and strong-comparator benchmark | CPU |
| M3 | Public-corpus reliability atlas | 360-model image artifact complete; associations sealed | task-conditioned metric profiles | 60-100 GPU-h |
| M3a | AI-safety measurement audit | Design specified; blocked behind M2 | automated-judge support or abstention report | design-calibrated GPU/API work |
| M3b | Selector feasibility | Protocol frozen; blocked behind M2/M3 | held-out-family selector and abstention test | CPU after M3 |
| M4 | End-to-end pilot | Passed | validated image and causal-text pipelines | completed |
| M5 | Corrected image factorial | 96-run artifact complete; scale confirmation pending | blocked multi-architecture image evidence | 70-120 GPU-h |
| M6 | Corrected causal-text factorial | 144-run atlas and 180-run replication complete; scale confirmation pending | leakage-tested language evidence | 70-120 GPU-h |
| M7 | Protected external holdout | Intake passed; opening denied | one frozen external test | 30-80 GPU-h |
| M8 | Final analysis and release | Pending | reproducible tables, atlas, and package candidate | CPU + 20-40 GPU-h |
| M9 | Manuscript and adversarial review | In progress | review-ready paper and external critique | CPU |
| M10 | Submission and archive | Pending | paper, release tag, data archive, and DOI | none |

GPU-hour ranges are planning estimates in RTX 4090-equivalent hours. They are
scientific workload estimates, not prices or commitments. See
[execution resources](docs/EXECUTION_RESOURCES.md).

## M0: Quarantine Legacy Evidence

Completed:

- preserved v1 artifacts and hashes;
- marked repeated configurations as non-independent;
- withdrew the historical causal-language interpretation;
- separated motivating FIM work from the active MBE contribution;
- created a public credibility ledger.

Gate:

- no public document presents the 680-row pilot as 680 independent models;
- no invalid text result supports an active claim;
- legacy evidence remains exploratory.

## M1: Freeze The Scientific Questions

Completed:

- defined association, incremental information, transport, intervention
  consistency, and measurement reliability as separate estimands;
- froze a baseline information ladder and control semantics;
- defined task environments and the unit of uncertainty;
- separated primary, secondary, exploratory, and prohibited claims;
- froze metric families and the ablation structure.

Gate:

- every primary table maps to a declared estimand;
- control sets are justified rather than selected for a preferred conclusion;
- training loss and task-proximal baselines are included where relevant;
- causal language is excluded from observational residual associations.

## M2: Calibrate MBE 2.0

Completed:

- grouped cross-fitting and fold-local rank transforms;
- nonlinear nuisance models;
- known-null, genuine-signal, proxy, deceptive-control, and interaction cases;
- full-refit predictive uncertainty;
- real-design semi-synthetic calibration;
- shared benchmarks against rank, conditional mutual information, and
  granulated criteria;
- a 48,000-cell design-matched screen and 153,600-row benchmark against GCM,
  WGCM, KCI, orthogonal-score, rank, and CRT procedures;
- disjoint confirmation and PGDL-transfer calibration;
- a repeated-split development screen with all six candidates rejected;
- a 126,000-row oracle feasibility frontier separating information,
  measurement-noise, and nuisance-estimation limits at 24-192 configurations;
- regression tests for failures discovered during calibration.

Remaining:

- design a substantively different estimator or calibrated abstention rule for
  the observed 48-configuration oracle gap on fresh development data;
- demonstrate controlled false support and useful power at the
  design-calibrated independent-unit count;
- confirm the frozen rule on disjoint known-truth data;
- obtain an independent implementation review.

The current methods did not pass the full gate. The comparator benchmark found
no procedure with both strict worst-cell calibration and useful worst-cell
power at 24/48 configurations. The PGDL transfer rule missed one frozen power
bound by 0.008, and the follow-on repeated-split family did not advance. These
are retained scientific results, not permission to tune on protected outcomes.

The oracle frontier narrowed the problem. At 24 independent configurations,
the observable oracle was calibrated but underpowered. At 48, it passed both
frozen gates, while learned residualization produced 14.2-15.2% worst-null
support. In that frozen design, usable information exists; learning the
baseline relationship without manufacturing support is the binding problem.
The 48-configuration boundary is design-specific, not a universal sample-size
rule.

Gate:

- acceptable false-support behavior under clustered nulls;
- useful power at the frozen minimum relevant improvement;
- no deceptive control is promoted as reliable;
- conclusions survive reasonable nuisance learners and fold assignments.

## M3: Public-Corpus Reliability Atlas

Tasks:

1. complete the declared metric battery on development task families;
2. preserve source definitions and metric provenance;
3. generate scoped reliability profiles by target and environment;
4. compare MBE against simpler selection rules;
5. quantify measurement failures, runtime, and missingness;
6. open validation tasks only after the implementation is frozen.

Gate:

- multiple genuinely distinct task families are present;
- conclusions are stable under task-level weighting;
- metric missingness is reported rather than silently filtered;
- the atlas adds a useful distinction beyond existing methods;
- protected transfer tasks remain unopened.

## M3a: AI-Safety Measurement Audit

Status: the decision and opening protocol are specified, but no safety-facing
target-metric association is authorized while M2 remains blocked.

The primary proposed case audits automated jailbreak and harmfulness judges
against independently defined human assessments. StrongREJECT is the leading
development candidate and HarmBench is a transfer candidate, subject to
provenance, licensing, target-independence, label-reliability, and
independent-unit checks.

Tasks:

1. freeze the target, candidate judges, cheap evaluator baselines, and
   practical effect threshold;
2. set the independent configuration count from outcome-blind,
   design-matched power calibration, with 48 as a floor rather than a
   universal answer;
3. use multi-way grouping for shared models and attack families;
4. compare raw-correlation selection, a globally fixed judge, and the
   MBE-supported judge or abstention;
5. test transport to a held-out model or attack family;
6. retain all exclusions, missing cells, leakage checks, and deviations.

Gate:

- a fixed MBE rule passes disjoint known-truth calibration before the
  target-metric table is opened;
- the human target is independent of the scores being audited;
- every prespecified cell and configuration-level uncertainty unit is
  accounted for;
- failed calibration produces abstention rather than a post-hoc rule;
- the final packet can be executed from frozen artifacts by an external
  researcher.

See the [AI-safety measurement case](docs/AI_SAFETY_MEASUREMENT_CASE.md).

## M3b: Selector Feasibility

The selector is secondary to the audit method. It may recommend a metric only
when the available evidence level supports the declared target and environment.

Comparators:

- globally fixed metric;
- best development-task metric;
- nearest-environment rule;
- metadata-only selector;
- oracle upper bound;
- abstain-always and recommend-always policies.

Gate:

- lower regret than frozen non-oracle comparators on held-out task families;
- coverage and abstention are reported together;
- no target labels from the held-out family influence the recommendation;
- failure narrows the project to an audit and atlas contribution.

## M4: End-To-End Pilot

Status: passed. Corrected image and causal-language pipelines completed schema,
duplicate-key, causal-mask, balance, manifest, and artifact-integrity checks.

Tasks:

- run small image and causal-text slices through acquisition, training,
  checkpointing, metric extraction, validation, and table generation;
- test duplicate keys, interrupted-job recovery, seed handling, causal masks,
  target computation, schema enforcement, and artifact hashes;
- measure per-family runtime and storage.

Gate:

- no leakage or duplicate-key failure;
- instrumented and control runs match where expected;
- every output row traces to a frozen configuration;
- runtime estimates are stable enough to schedule the main factorials.

## M5: Corrected Image Factorial

Current status: a corrected 96-run factorial is artifact-complete. Its
metric-target associations remain sealed because the outcome-blind opening
rule did not pass. The larger design below remains a future scale-confirmation
target, not completed evidence.

Minimum design:

```text
2 datasets x 3 architectures x 8 configurations x 5 seeds = 240 runs
```

Primary requirements:

- dataset and architecture remain explicit environment factors;
- five seeds repeat each configuration block;
- target and baseline columns are frozen before analysis;
- metric extraction uses documented checkpoints and batches;
- block-level uncertainty is primary.

Gate:

- headline effects replicate across configuration blocks;
- the conclusion is not driven by one architecture or corruption regime;
- raw and controlled results are both reported;
- selector evaluation remains untouched by protected tasks.

## M6: Corrected Causal-Text Factorial

Current status: a corrected 144-run multi-corpus atlas and a separate 180-run
sequential replication are public. The atlas associations remain sealed; the
replication produced no metric passing its frozen within-environment increment
rule. The larger design below remains a future scale-confirmation target.

Minimum design:

```text
1 dataset x 2 model sizes x 10 configurations x 5 seeds = 100 runs
```

Requirements:

- causal masking is tested on every code path;
- token NLL or perplexity is computed correctly;
- metric batch-size sensitivity is quantified;
- image and text targets are never pooled as though they share a scale;
- cross-modality transfer permits abstention.

Gate:

- at least one conclusion is stable across model sizes;
- no claim depends on the invalid legacy text setup;
- task-specific and cross-modality conclusions remain separate.

## M7: Protected External Holdout

Current status: the 240-model PGDL Tasks 6-9 intake passed structural checks.
The calibrated opening rule did not pass its frozen power gate, so the protected
checkpoint-metric associations remain unopened.

Before access:

1. freeze repository commit and container digest;
2. freeze metric cards, hypotheses, control sets, and commands;
3. publish a timestamped preregistration and artifact manifest;
4. verify that the environment was not used during method development;
5. freeze selector comparators and abstention threshold.

After access:

- execute the primary analysis once;
- retain the result regardless of direction;
- report all deviations before exploratory follow-up.

Gate:

- the primary conclusion replicates or is explicitly narrowed;
- no post-hoc metric, threshold, or exclusion change alters the primary table;
- recommendation evidence levels remain calibrated after transfer.

## M8: Final Analysis And Artifact Release

Tasks:

- finish blocked uncertainty and sensitivity analyses;
- generate metric-family, environment, coverage, and regret figures;
- release raw ledgers, split manifests, hashes, and metric cards;
- produce runtime, memory, missingness, and reliability tables;
- release an MBE 2.0 package candidate;
- verify reproduction in a clean environment.

Gate:

- no table depends on an untracked file;
- every headline value traces to a raw ledger;
- package and experiment implementations agree;
- an external reader can regenerate paper tables without GPU training.

## M9: Manuscript And Adversarial Review

The manuscript must answer:

- Is MBE more than a standard conditional-independence test?
- Does the contribution survive without the motivating FIM case study?
- Are metric implementations faithful and comparable?
- Are targets genuinely held out and scientifically meaningful?
- Is the external holdout protected?
- Do results survive environment and configuration weighting?
- Is the method practically useful relative to its complexity?
- Does selection beat a globally fixed metric, or is the atlas the real
  contribution?

Gate:

- every strong claim has a direct table, figure, calibrated simulation, or
  preregistered test;
- related work credits prior conditional and robust evaluation;
- limitations state the observational and task-specific scope plainly;
- an adversarial reviewer packet is answered without hiding failures.

## M10: Submission And Archive

Checklist:

- final manuscript and supplement;
- repository release tag;
- citable archive and DOI;
- code and data license check;
- complete artifact manifest;
- reproducibility smoke test from the release archive;
- conflicts and acknowledgements disclosed;
- no simultaneous submission conflict.

## Stop-Loss Rules

Pause the affected work package when:

- known-truth calibration cannot distinguish genuine signal from proxies;
- public-corpus results are fully explained by prior methods;
- primary metric missingness exceeds 10% in an environment;
- the pilot requires more than 1.5 times its planned GPU-hour range;
- conclusions change across reasonable nuisance models without a principled
  resolution;
- the protected holdout cannot remain protected;
- a selector cannot beat simple frozen comparators.
