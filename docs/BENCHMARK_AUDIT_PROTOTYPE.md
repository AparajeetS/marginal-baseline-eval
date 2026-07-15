# Experimental Benchmark Audit Prototype

This prototype explores whether selected checks from the **candidate MBE 2.0
research design** can be usefully transferred to AI benchmark audits. It is a
research artifact for testing a method, including finding where the method
fails. It is not an independently validated benchmark evaluator, a
certification system, or evidence that MBE 2.0 is already established.

The defensible provenance claim is that the prototype is **implemented from
the MBE codebase and audit specification**. Results should not be described as
"validated by MBE," because neither this transfer nor the complete MBE 2.0
method has yet received independent validation.

## What The Prototype Checks

The prototype produces separate diagnostics instead of a universal pass/fail
verdict. Its current relationship to the five candidate MBE 2.0 estimands is:

| Estimand | Question | Prototype status | Permitted interpretation |
|---|---|---|---|
| E0 | Does the benchmark metric associate with an external target without metadata? | Implemented as an unconditional association diagnostic | Association in this dataset only |
| E1 | Does the metric add predictive information beyond a declared baseline set? | Implemented as an incremental-signal diagnostic conditional on named baselines | Incremental information beyond those declared columns, not beyond all possible confounders |
| E2 | Does the increment transfer to an unseen environment? | Implemented when at least three usable environments are supplied | Aggregate observed transport across the supplied environments only |
| E3 | Does the metric predict direction under a matched intervention? | **Omitted** | No intervention-consistency or causal claim |
| E4 | Can the metric be measured reliably and affordably? | **Omitted** | No repeatability, sensitivity, runtime, or operational-utility claim |

This is partial implementation of a candidate design, not a claim of full MBE
2.0 conformance. In particular, an E0-E2 result cannot substitute for the
matched interventions required by E3 or the repeated measurement and cost
studies required by E4.

## Required Inputs

The input CSV should contain one row per evaluation and a declared
**configuration-unit identifier**. Repeated measurements may occupy separate
rows, but they must share that identifier so they are blocked together rather
than counted as independent configurations. At minimum the CSV needs:

| Role | Example field | Requirement |
|---|---|---|
| Candidate metric | `truthfulness_score` | The benchmark score or diagnostic being audited |
| Target | `external_criterion` | A held-out outcome against which the metric is evaluated |
| Declared baselines | `capability_proxy`, `format_score` | Named columns available without the candidate metric |
| Environment | `benchmark_family` | A domain, task family, model family, or other prespecified transport unit |
| Configuration unit | `config_unit` | Identifier used to keep repeated seeds or evaluations from being treated as independent configurations |

Rows with repeated measurements of the same model or setup must share a
configuration-unit identifier. Environment definitions and baseline columns
should be chosen before examining the final results.

### Capability proxies are declared proxies

The report should say "conditional on the declared capability proxies," not
"after controlling for capability." Observed columns such as general benchmark
performance, parameter count, or compute are incomplete proxies for latent
capability. An apparently incremental benchmark signal may still reflect an
omitted capability dimension, data contamination, evaluator artifacts, or
another unmeasured factor. E1 therefore answers a conditional and
baseline-relative question.

### External criterion versus internal diagnostic

An external criterion should be held out from the construction of the
candidate metric and should not merely restate the same benchmark labels,
prompts, judge, or scoring rule. Plausible criteria might include prespecified
outcomes from an independently constructed evaluation, blinded human ratings,
or behavior under a separately collected test protocol.

If the supplied target is the audited benchmark itself, a transformation of
its score, or a measure sharing its labels or evaluator, the result must be
reported as an **internal diagnostic**. It may reveal redundancy, instability,
or environment sensitivity, but it cannot establish construct validity for
truthfulness, honesty, reasoning faithfulness, or truth-seeking behavior.

## CLI

The intended interface maps the semantic roles explicitly:

```bash
mbe-eval-claim \
  --csv benchmark_results.csv \
  --metric truthfulness_score \
  --target external_criterion \
  --baselines capability_proxy,format_score \
  --environment benchmark_family \
  --unit config_unit \
  --claim-id external-truthfulness-criterion-v1 \
  --claim-text "The score adds held-out information beyond the declared proxies" \
  --output-prefix claim_card
```

Here `metric`, `target`, `baselines`, `environment`, and `config unit` describe
the required CSV roles; the concrete column names can differ. The generated
claim card should record the mapping, sample and configuration-unit counts,
omitted checks, and conditions under which its interpretation would change.

For a self-contained smoke test, `mbe-eval-claim-demo` generates a
deterministic four-environment fixture, a deliberately confounded score, a
negative control, and JSON/Markdown claim cards. Its known-ground-truth result
tests implementation behavior only.

## Evidence States And Contestation

Schema 0.2 labels the card's reviewer-facing result as a **Predeclared test
outcome**. The overall evidence state is one of
`supports-claim-under-declared-tests`,
`does-not-support-claim-under-declared-tests`, or
`unresolved-under-declared-tests`. E0-E4 use only
`meets-declared-threshold`, `below-declared-threshold`, or `unresolved`.
These labels bind every outcome to the exact tests and practical thresholds in
the card instead of presenting a universal pass/fail judgment.

Reviewers can use `compare_benchmark_claim_specs` to rerun the same rows under
named alternatives, such as an expanded baseline set or a different
prespecified environment. The returned contestation bundle retains every
complete claim card and reports whether the overall or per-estimand states
change relative to the first named specification. The comparison exposes
specification sensitivity; it does not select a preferred specification, and
an unchanged result does not cover alternatives that were not supplied.

## Deceptive Synthetic Control

The included synthetic control is deliberately constructed so a candidate
score looks useful in a pooled analysis while its apparent signal is explained
by a declared capability proxy or fails to transport. Detecting that trap is a
minimum implementation check: it helps catch reversed columns, broken baseline
handling, leakage between folds, or an audit that merely repeats raw
correlation.

Passing the synthetic control does **not** validate the statistical method or
show that real benchmark confounding has been removed. The control reflects a
known data-generating process chosen by the authors. It does not represent the
unknown causal structure, measurement error, benchmark contamination, or
selection effects in real model evaluations. Failure on the control is a reason
to stop; success is only permission to continue testing.

## Claims This Prototype Does Not Support

The prototype does not:

- certify that a benchmark measures truthfulness or truth-seeking;
- certify a model as truthful, honest, aligned, safe, or reliable;
- identify the causal effect of a benchmark score or metric;
- establish construct validity from correlation or incremental prediction;
- prove that declared baselines capture general capability;
- turn a non-transfer result into evidence that a benchmark is useless; or
- validate MBE 2.0 itself.

Every result is scoped to the supplied target, baseline set, environments,
configuration units, and analysis choices. Negative and inconclusive outcomes
are first-class results.

## Relationship To Existing MBE Evidence

`mbe-eval` v0.3.2 implements the stable MBE v1 partial-rank audit and provides
feasibility evidence that the core workflow can be packaged and reproduced. It
does not validate this benchmark-audit transfer or the full candidate MBE 2.0
design.

The existing 680-row pilot ledger is also exploratory. It contains repeated
configurations, so 680 rows are not 680 independent models or experimental
units. Its legacy text experiment lacks a causal attention mask and permits
label leakage. Those results motivate better controls and blocked designs; they
must not be used as confirmatory evidence that the benchmark prototype works.

The next evidential step is adversarial testing on multiple independently
constructed datasets, followed by preregistered external evaluation and
independent replication. Until then, the prototype should be presented as a
working hypothesis embodied in code.
