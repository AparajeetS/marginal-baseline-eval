# MBE Research Overview

## Problem

Machine-learning metrics are often judged by pooled correlation with a final
outcome. That test can reward a metric for rediscovering architecture,
hyperparameters, training progress, dataset difficulty, or another variable
already available to the evaluator.

This creates two practical failures:

1. a metric appears informative when it adds little beyond cheap baselines;
2. a metric is treated as globally reliable when its value is conditional on
   the target, task, intervention, or measurement regime.

## Research Objective

Marginal Baseline Evaluation asks whether a candidate metric contributes
information after the evaluator declares:

- the target being predicted;
- the baseline information already available;
- the environment in which the claim should hold;
- the intervention, if a causal response is being discussed;
- the measurement procedure and uncertainty unit.

The long-term goal is a public reliability atlas and an abstaining selector:
given a task and target, recommend only metrics with relevant evidence and
decline to recommend when transfer support is insufficient.

## Primary AI-Safety Application

The first proposed safety-facing study will audit automated jailbreak and
harmfulness judges against independently defined human assessments. It will
test whether a judge predicts the human target beyond cheap model, attack,
prompt, refusal, and response-length baselines, and whether that increment
survives a held-out model or attack family.

StrongREJECT is the leading development candidate and HarmBench is a transfer
candidate, subject to public eligibility checks for provenance, licensing,
target independence, label reliability, and independent-unit structure. This
is a proposed application, not completed evidence. The protected analysis may
proceed only after a prospectively frozen MBE rule passes design-matched
known-truth calibration. See the [AI-safety measurement case](AI_SAFETY_MEASUREMENT_CASE.md).

## Method

The active MBE 2.0 design separates five estimands:

1. unconditional association;
2. incremental information beyond a baseline ladder;
3. cross-environment transport;
4. matched-intervention consistency;
5. measurement reliability.

The reference implementation uses grouped cross-fitting, nonlinear nuisance
models, blocked resampling, explicit control sets, negative and deceptive
controls, and scoped claim cards. Competing conditional-dependence methods are
evaluated on the same known-truth cases.

## Current Evidence

The repository contains:

- a stable MBE v1 package and command-line interface;
- corrected artifacts from 96 image runs, 144 multi-corpus causal-language
  runs, and a separate 180-run causal-text replication;
- a 48,000-cell design-matched calibration screen;
- a 9,600-dataset, 153,600-row benchmark against MBE, GCM, WGCM, KCI,
  orthogonal-score, rank, and CRT procedures;
- a source-faithful published-study reaudit;
- a structurally validated 240-model PGDL holdout intake whose protected
  associations remain sealed;
- follow-on confirmation and development studies, including a binding PGDL
  power near miss and a rejected 10,080-row repeated-split screen;
- a 126,000-row oracle feasibility frontier that found a design-specific
  observable-information boundary at 48 independent configurations while
  current learned nuisance rules remained anti-conservative;
- a completed 360-model CIFAR-10, CIFAR-100, and SVHN transport artifact whose
  protected associations remain sealed;
- an executable, hash-sealed independent-replication packet;
- public preregistrations, validators, canonical ledgers, hashes, failure
  provenance, and explicit non-claims.

The public [credibility ledger](MBE_CREDIBILITY_LEDGER.md) records supported,
provisional, blocked, withdrawn, and falsified claims. The project does not
promote exploratory row counts into claims of independent replication, and it
has not opened protected metric-target associations after failed gates.

## Research Outputs

- installable Python package and CLI;
- protocol and statistical specification;
- known-truth calibration benchmark;
- published-study reaudit workflow;
- metric reliability profiles and claim cards;
- prospective selection and abstention evaluation;
- reproducible experiment ledgers, manifests, and paper tables;
- a public paper reporting positive, null, or adverse results.

## Success Criteria

The research direction succeeds only if it can:

- control false positives on known-null and deliberately deceptive metrics;
- preserve power for genuine incremental signal;
- add information beyond established conditional-dependence methods;
- produce stable conclusions across nuisance models and blocked uncertainty;
- transport across genuinely distinct task environments;
- improve metric selection relative to a globally fixed metric;
- abstain when evidence does not support transfer;
- reproduce under an independent implementation.

Failure at any gate narrows the corresponding claim. A negative protected
holdout remains a publishable outcome.

## Scope Boundaries

MBE is not:

- a causal claim from observational residual association;
- proof that one metric is universally good or bad;
- a substitute for a valid held-out target;
- reliable when controls contain descendants or colliders without a defensible
  causal interpretation;
- meaningful on a single model run;
- validated merely because a large number of correlated rows were collected.

## Next Gates

The active sequence is maintained in [the roadmap](../ROADMAP.md). The immediate
work is to develop a substantively different opening rule for the observed
48-configuration oracle gap on fresh known-truth data; freeze and confirm it
prospectively; run the safety-measurement audit and a genuinely external
holdout only if it passes; obtain an externally executed and signed
replication; test prospective selection on future task families; and finish
the paper with failed calibration gates retained as results.
