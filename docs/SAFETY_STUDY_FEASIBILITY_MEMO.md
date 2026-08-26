# Safety Study Feasibility Memo: Automated Jailbreak Judges

Status: outcome-blind design memo, version 0.1, 2026-08-27. No real
target-metric association was calculated while preparing this memo.

## Decision To Be Audited

A safety team is choosing an automated judge for a red-team campaign. The
judge will determine which attacks count as successful, which defenses appear
effective, and which models receive further review. The operational choice is
between a judge selected by ordinary benchmark agreement, a fixed default
judge, and an MBE-supported judge or abstention.

The proposed study asks a narrow question: for an independently defined human
target, does a named automated judge improve prediction beyond information the
evaluator already has, and does that increment survive a held-out model or
attack family? It does not ask whether one judge is universally trustworthy.

## Outcome-Blind Data Intake

The intake inspected source provenance, hashes, columns, missingness, and the
number of candidate inference units. It did not inspect associations between
human targets and automated scores.

### StrongREJECT: development candidate

The [StrongREJECT paper](https://arxiv.org/abs/2402.10260) validates automated
evaluators against human judgments. Its
[maintained repository](https://github.com/dsbowen/strong_reject) publishes the
human-label table and reproduction code. The public paper reports 1,361
prompt-response pairs scored by five workers; the repository's cleaned table
also contains 1,361 rows.

The schema audit found four victim models, 17 jailbreak labels, and only 47
observed model-by-jailbreak cells, with 26 to 33 responses per cell. The
aggregate human target is complete, although some individual rater columns are
missing. This is a useful development and pipeline-checking artifact, but it
does not meet MBE's current floor of 48 configuration blocks and has only four
model groups. It is therefore **not eligible as the sole confirmatory safety
study**. It can become eligible only through a prospectively designed
expansion with an independent human target, or by serving strictly as
development data before a separate eligible confirmation.

### HarmBench: transfer candidate

[HarmBench](https://arxiv.org/abs/2402.04249) compared 18 red-teaming methods
and 33 target models and defenses, and its
[public repository](https://github.com/centerforaisafety/HarmBench) includes a
human-labeled classifier validation artifact. The inspected repository
snapshot contains 602 records, three human-label fields, 22 recorded model
strings, ten attack-method labels, and 147 observed model-by-method cells. The
matrix is sparse, and one model string is malformed. A recent independent
[jailbreak-judge audit](https://arxiv.org/abs/2606.25487) reports a filtered
596-completion subset, confirming that inclusion rules and source versions
must be reconciled rather than assumed.

HarmBench remains the leading transfer candidate, not a declared holdout. It
must first pass a public adapter audit covering the canonical row set, model
and method lineage, licensing, duplicate handling, missingness, and whether its
human labels were constructed independently of every candidate judge.

## Frozen Study Shape

If intake eligibility and MBE's known-truth calibration gate both pass, the
safety study will freeze the following before opening any target-metric table.

**Target.** The source-specific aggregate human harmfulness or attack-success
assessment, normalized to a declared scale. Individual ratings will be used
for reliability analysis, not treated as independent model evaluations.

**Candidate metrics.** Exact automated-judge implementations, model versions,
prompts, decoding settings, and score transformations. A judge version changed
after the freeze becomes a new metric and cannot silently replace the frozen
one.

**Baseline information.** A preregistered ladder containing model family,
general capability proxy, base refusal rate, attack and prompt family, refusal
markers, and response length. Every variable must have been available at the
time the evaluator would choose a judge. Variables derived from the human
target or from post-decision outcomes are prohibited.

**Inference unit.** A model-by-attack configuration block. Prompts,
generations, and raters are repeated measurements within that block. Shared
models and attacks require multi-way grouping. At least 48 eligible blocks are
required, and outcome-blind power analysis may raise that number.

**Primary estimand.** Learner-relative held-out risk improvement:

`Delta_L = Risk(Y | B) - Risk(Y | B, M)`

where `Y` is the human target, `B` the baseline information, and `M` the
candidate judge. Positive values mean that the judge improves prediction for
the declared learner and split. Raw association, incremental value,
model-family transport, attack-family transport, reliability, coverage,
runtime, and cost will be reported separately.

**Splits and decision comparison.** Grouped cross-fitting will isolate entire
configuration blocks. The protected comparison will hold out an entire model
or attack family and compare: (1) the judge selected by raw benchmark
association, (2) a fixed global judge, and (3) the MBE-supported judge or
abstention. A method cannot win by abstaining on every difficult case.

## Calibration And Practical Gates

The deployable rule must first pass fresh, disjoint, design-matched known-truth
confirmation. The existing published benchmark gate requires at least 98%
estimability in every cell, a maximum 95% Wilson upper bound of 7.5% across
known-null cells, and a minimum 95% Wilson lower bound of 50% across the frozen
effect-0.50 cells. These are calibration requirements, not claims about the
real judges.

For the safety study, a judge will be labeled practically useful only if its
point estimate reduces grouped held-out risk by at least 10% relative to the
baseline-only learner and its full-refit 95% interval excludes no improvement.
Results below that threshold may be statistically detectable but will be
reported as operationally small. Sensitivity at 5% and 15% will be shown
without changing the primary threshold.

## Leakage, Stop Rules, And Holdout

The study stops or abstains if any of the following holds:

- the human target is partly constructed from a candidate automated judge;
- fewer than 48 eligible configuration blocks remain after frozen exclusions;
- source lineage, consent, or licensing cannot support the intended release;
- grouped label reliability is too weak to resolve the practical threshold;
- the design-matched known-truth rule fails calibration or useful power;
- development and holdout environments cannot be separated credibly; or
- any frozen code, split, threshold, or hash changes after the protected table
  is opened.

One eligible holdout will be opened once. A failure to pass a gate is not
evidence that automated judges are useless; it means this design cannot
support that claim. New harmful generations or annotations are not a default
requirement. Public, consented labels will be used first, and no harmful
response text needs to appear in the public report.

## Deliverables And Decision Value

The study will produce a versioned data adapter, a schema and provenance
report, a preregistration, known-truth calibration results, a one-shot holdout
report, metric claim cards, and an executable replication packet. A positive
result would justify one judge for one declared decision. A redundant,
non-transporting, underpowered, or abstaining result would prevent that judge
from receiving stronger evidential status than the data support.

This is the intended safety contribution: not another judge leaderboard, but
a public gate between a measurement result and the decision made from it.

## Intake Receipts

- StrongREJECT repository snapshot and public OSF files were inspected on
  2026-08-27 at commit
  `7a551d5b440ec7b75d4f6f5bb7c1719965b76b47`. `labelbox.csv` SHA-256:
  `7a5928a4f09b4cbfce274001873ccf095510d5a990f8be52e4323d4c069fbad2`.
- HarmBench repository snapshot was inspected on 2026-08-27 at commit
  `8e1604d1171fe8a48d8febecd22f600e462bdcdd`.
  `text_behaviors_val_set.json` SHA-256:
  `8fb5e86b94f07dac3cf8501e32e4b12f0ba76b4bc9c88343164bb5b37b1796bf`.
- These receipts freeze source identity only. Final eligibility, canonical
  filtering, and train/holdout assignment remain prospective milestones.
