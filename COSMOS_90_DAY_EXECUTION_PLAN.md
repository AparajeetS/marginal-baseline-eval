# Cosmos Institute Grant: 90-Day Research and Execution Plan

## Project title

**A Benchmark Is a Claim, Not Just a Score: Building the MBE Benchmark Audit Toolkit**

## Funding request and project boundary

- **Requested support:** $6,500
- **Planned duration:** 90 days
- **Primary output:** a public, usable toolkit for auditing whether an AI benchmark score supports a narrowly stated claim under declared baselines, environments, and evidence thresholds
- **Starting point:** a working E0-E2 prototype, a frozen real-data TruthfulQA pilot, machine-readable claim cards, a specification-contestation interface, and an installable Python package
- **Important boundary:** this is not the full MBE 2.0 validation program, not a benchmark certification service, and not a claim that MBE has already been independently validated

This document defines what the Cosmos-supported project will do, how each part will be executed, what evidence will be produced, which decisions will be frozen before results are known, and what outcomes would cause the project to narrow or change course.

The project succeeds by making benchmark claims easier to inspect and challenge. It does not require a positive result. A benchmark audit that ends in a negative or unresolved conclusion is a successful deliverable if the protocol was frozen, the analysis was executed correctly, the limitations are explicit, and another researcher can reproduce the result.

---

## 1. The problem we are addressing

AI benchmarks often compress several scientific claims into one score. A metric may be described as measuring truthfulness, honesty, reasoning quality, sycophancy, factuality, safety, or robustness. Yet its observed variation can also reflect general model capability, response length, formatting, refusal style, judge preferences, prompt construction, data contamination, or dataset-specific artifacts.

A leaderboard can therefore rank systems consistently while leaving the underlying measurement claim uncertain. Conventional validation usually asks whether a score correlates with another outcome. That is useful, but insufficient. A high raw correlation does not tell us whether the score adds information beyond inexpensive alternatives, whether the relationship survives outside the environments used to establish it, or whether the conclusion depends on a convenient analysis specification.

The Benchmark Audit Toolkit will turn a benchmark claim into a structured and falsifiable object. Instead of reporting only a score or correlation, it will keep the following together:

- the exact claim being tested;
- the candidate metric;
- the outcome or criterion it is expected to predict;
- the baseline information available without that metric;
- the environment or domain across which the claim should transport;
- the independence unit used to prevent repeated observations from being treated as independent evidence;
- the practical evidence thresholds fixed before analysis;
- the controls used to catch misleading positive results;
- the result for each estimand;
- the alternative specifications that were tested;
- the limitations and omitted checks; and
- the strongest conclusion the evidence permits.

The output will be a scoped claim card and a contestation bundle, not a certificate.

---

## 2. What already exists before the grant

The grant begins from a functioning research prototype rather than an idea alone.

### 2.1 Implemented software

The current branch includes:

- a Python implementation of selected E0-E2 benchmark-audit checks;
- a command-line interface that maps a candidate metric, target, baselines, environment, and configuration unit to an audit;
- Markdown and JSON claim-card generation;
- deterministic synthetic controls;
- named specification comparisons through a contestation bundle;
- automated tests for the claim-card and contestation interfaces; and
- an installable package structure inherited from `mbe-eval`.

The prototype currently implements only:

| Estimand | Question | Current status |
|---|---|---|
| E0 | Is the candidate score associated with the target without metadata? | Implemented as a descriptive diagnostic |
| E1 | Does the score add held-out predictive information beyond declared baselines? | Implemented |
| E2 | Does that increment transport to a held-out environment? | Implemented when sufficient environments exist |
| E3 | Does the score behave correctly under a matched intervention? | Not implemented in the current prototype |
| E4 | Is the score reliable, stable, and affordable to measure? | Not implemented in the current prototype |

E3 and E4 are not silently implied by E0-E2 results. They remain outside the core Cosmos promise unless a stretch analysis is justified by suitable data and the core deliverables are already complete.

### 2.2 Synthetic implementation check

The repository includes a deterministic synthetic demonstration in which a candidate score appears useful in pooled analysis but is explained by a declared proxy or fails to transport. A negative control is also included.

This fixture is useful for detecting implementation mistakes such as leakage between folds, reversed target columns, broken baseline handling, or a procedure that merely repeats raw correlation. It is not evidence that the method is valid for real benchmarks. Passing a known synthetic trap is permission to proceed, not validation.

### 2.3 Frozen TruthfulQA real-data pilot

The first real-data demonstration audits a transparent ROUGE-1-style reference-difference score against released TruthfulQA v0 human truth labels.

Source inspection found duplicated question-answer pairs, conflicting labels, exact benchmark-reference answers in the label pool, and historical alignment with TruthfulQA v0 rather than the later v1 table. Before computing the candidate result, the protocol was amended and frozen to:

- collapse duplicate question-answer pairs;
- remove pairs with conflicting truth labels;
- require exact v0 question matching;
- remove exact correct, incorrect, and no-comment reference answers;
- keep all answers to one question inside the same fold; and
- restrict the main transport analysis to categories with at least 20 eligible questions.

The resulting cohort contains 7,920 unique, nonconflicting, non-reference answer pairs from 541 questions across 15 sufficiently represented categories.

Under the frozen 1 percent practical thresholds:

- E1 relative held-out MSE improvement was 12.33 percent;
- aggregate E2 category-holdout improvement was 11.01 percent;
- the length-derived deceptive control crossed neither threshold; and
- deterministic hash noise crossed neither threshold.

The permitted conclusion is narrow. Under the declared exclusions, proxies, question grouping, category environments, estimator, and thresholds, the lexical score added out-of-question predictive information for the released labels and transported in aggregate across retained categories.

The result does not validate TruthfulQA as a measure of truthfulness, validate MBE, establish causality, control general model capability, reproduce the exact official T5 ROUGE implementation, or certify any benchmark or model. The labels and references come from the same broader evaluation framework, so the pilot is a real-data method demonstration rather than an independent confirmation.

---

## 3. The exact questions the Cosmos project will answer

The 90-day project is organized around six concrete research and engineering questions.

### RQ1. Can benchmark claims be represented precisely enough to audit?

We will test whether a claim-card schema can force the author to name the metric, target, baselines, environment, independence unit, evidence thresholds, controls, omitted checks, and permitted conclusion without collapsing them into a universal verdict.

### RQ2. Can the software reliably separate association from incremental information and transport?

We will strengthen the E0-E2 implementation and verify it against synthetic fixtures with known ground truth, adversarial edge cases, repeated units, missing values, imbalanced environments, and misleading pooled associations.

### RQ3. Does a second, independently structured benchmark produce an informative audit?

We will run a protocol-frozen audit on a benchmark that differs materially from the TruthfulQA pilot. Anthropic's released sycophancy evaluations are the leading candidate because they concern a different behavior and dataset structure. They will be used only if the source data support a defensible target, baseline set, environment definition, and independence unit.

### RQ4. How sensitive is the conclusion to reasonable analysis choices?

We will define named alternative specifications before the main result is opened. The toolkit will preserve all resulting claim cards and show whether the conclusion changes, without automatically choosing the most favorable specification.

### RQ5. Can someone other than the author understand and reproduce the workflow?

We will test the documentation and command-line path with at least one cold-start reproduction attempt by a person or clean environment that did not create the analysis. Every ambiguity, missing dependency, undocumented assumption, and failed step will enter a discrepancy log.

### RQ6. Where does the method fail or need to abstain?

We will record negative and unresolved outcomes, insufficient-environment cases, unstable specifications, failed controls, missing external targets, and cases where the dataset cannot support the desired claim. The toolkit must be able to say that the evidence is insufficient.

---

## 4. Deliverables

The project will produce the following public artifacts.

### 4.1 Cosmos reviewer landing area

A dedicated Cosmos-facing directory or landing page will separate the grant project from the broader MBE training-metric research program. It will contain:

- a short project overview;
- this execution plan;
- the current evidence and limitations;
- a map of the software and experiment artifacts;
- the 90-day deliverable checklist;
- links to the runnable demonstration and real-data audits; and
- an explicit distinction between the Cosmos toolkit and the longer-horizon MBE 2.0 program.

### 4.2 Claim-card schema and renderer

The final claim card will be available in both machine-readable JSON and human-readable Markdown. At minimum it will record:

- schema version;
- claim identifier and plain-language statement;
- source dataset and immutable source identifiers;
- candidate metric and construction method;
- target and whether it is external or internal to the benchmark;
- declared baselines and their justification;
- environment definition;
- configuration or independence unit;
- cohort construction and exclusions;
- sample counts and effective unit counts;
- E0, E1, and E2 outcomes;
- practical thresholds and uncertainty intervals;
- deceptive and negative controls;
- named alternative specifications;
- omitted E3 and E4 checks;
- limitations;
- evidence state; and
- permitted interpretation.

### 4.3 Contestation bundle

The contestation bundle will retain the complete result from every named specification. It will answer:

- Did the overall evidence state change?
- Did any individual estimand change state?
- Which baseline, environment, cohort, or estimator choice produced the change?
- Is the conclusion stable, fragile, or unresolved across the declared alternatives?

It will not rank specifications by favorability or hide an inconvenient result.

### 4.4 Expanded synthetic calibration suite

The suite will include fixtures for:

- true incremental signal beyond baselines;
- complete baseline washout;
- sign reversal after adjustment;
- pooled association caused entirely by environment mixture;
- signal that works in training environments but fails transport;
- repeated observations that create false precision if not grouped;
- a deceptive length or formatting proxy;
- deterministic noise;
- a missing-data pattern that changes the eligible cohort; and
- one environment too small to support a meaningful holdout.

Each fixture will state the data-generating process and expected qualitative result. Tests will verify that the toolkit detects the intended pattern or explicitly abstains.

### 4.5 Second real-data benchmark audit

The second audit will include:

- an immutable source manifest with repository commit or release identifier;
- file hashes and license notes;
- a source-inspection report;
- a pre-result protocol;
- any pre-result amendments with reasons;
- a cohort and exclusion ledger;
- the primary result;
- all named sensitivity analyses;
- a machine-readable claim card;
- a contestation bundle;
- a result interpretation boundary;
- a negative-result statement if the claim is not supported; and
- exact reproduction commands.

### 4.6 Public release and reproduction bundle

The final release will include:

- installable Python code;
- pinned dependencies or a lockable environment specification;
- CLI help and examples;
- automated tests;
- continuous-integration checks;
- one-command synthetic demonstration;
- one-command regeneration of derived public artifacts where licensing allows;
- source hashes;
- an artifact manifest;
- a correction and amendment history; and
- a final Cosmos completion report.

---

## 5. How the second benchmark will be selected

The second benchmark will not be chosen only because it is famous or likely to produce a positive result. It must pass a documented selection gate before analysis.

### 5.1 Required selection criteria

A candidate dataset must provide:

1. **A clearly defined candidate score or scoring rule.** We must be able to state exactly what quantity is being audited.
2. **A target with a defensible relationship to the claim.** The target should be external to the candidate score where possible. If it shares labels, prompts, judges, or references, the audit will be labeled an internal diagnostic.
3. **Declared baseline information.** There must be plausible inexpensive predictors or metadata against which incremental value can be assessed.
4. **A valid independence unit.** Repeated answers, prompt variants, models, or seeds must be groupable so they are not counted as independent evidence.
5. **At least three meaningful environments for E2.** Environments may be task families, behavior categories, prompt regimes, model families, or another prespecified domain structure.
6. **Sufficient coverage.** Each main environment must contain enough independent units to support a holdout estimate.
7. **Reproducible access.** The source must be public, versionable, and licensed or otherwise permitted for research redistribution or scripted retrieval.
8. **A claim that can fail.** The planned conclusion must have a negative and unresolved state, not only a favorable interpretation.

### 5.2 Leading candidate: sycophancy evaluations

Anthropic's released sycophancy evaluations are the leading candidate because they address agreement-seeking behavior rather than lexical truthfulness and may offer distinct task or prompt environments. Before committing to this dataset, we will inspect:

- how sycophancy labels or outcomes were produced;
- whether the candidate score and target share the same judge or annotation process;
- whether model identity and capability proxies are available;
- whether prompt templates create repeated units;
- whether categories are sufficiently populated;
- whether the dataset contains contamination or duplicate structures;
- whether environment holdout is scientifically meaningful; and
- whether the result can support an external claim or only an internal diagnostic.

If these conditions fail, we will publish the rejection note and select another dataset using the same criteria. We will not force a sycophancy audit merely because it appeared in the proposal.

### 5.3 Selection record

For every serious candidate, the repository will contain a short record with:

- dataset name and source;
- proposed claim;
- candidate metric;
- target;
- baselines;
- environment;
- independence unit;
- known leakage or validity concerns;
- license and reproducibility status;
- selection decision; and
- exact reason for acceptance or rejection.

This record prevents the project from quietly switching datasets after seeing an unfavorable preliminary result.

---

## 6. Exact analysis workflow for each real-data audit

### Step 1. Source acquisition and immutable manifest

We will retrieve the source from an official repository or release, pin the exact revision, calculate file hashes, record expected row counts, and document the license. Hash or row-count failures will stop the pipeline until explained.

Raw data will not be silently edited. Every transformation will be scripted, and every exclusion will be counted.

### Step 2. Source inspection before score computation

Before calculating the candidate audit result, we will inspect:

- duplicated units;
- conflicting labels;
- exact or near-exact reference overlap;
- repeated prompt templates;
- missing or malformed values;
- category sizes;
- target prevalence;
- model or configuration duplication;
- shared judges, labels, or references between metric and target;
- possible train-test contamination; and
- whether the proposed independence unit matches the data-generating process.

The inspection may narrow the cohort or the claim. Any amendment must be committed before the candidate result is computed and must explain why the change was necessary.

### Step 3. Freeze the primary claim

The protocol will state, in plain language:

- exactly what the score is claimed to predict;
- the population and cohort to which the claim applies;
- the baselines the score must beat;
- the environments across which the result should transport;
- the independence unit;
- the estimator and fold structure;
- the uncertainty procedure;
- the practical thresholds;
- the controls;
- the named sensitivity analyses;
- the stopping conditions; and
- the strongest permitted interpretation.

The repository commit becomes a visible time boundary between designing the test and seeing the result. It is not described as third-party preregistration unless an external registration service is actually used.

### Step 4. Build the analysis cohort

Cohort construction will use only frozen rules that do not consult the final candidate result. The pipeline will produce:

- raw row count;
- rows removed at each exclusion step;
- retained row count;
- number of independent units;
- environment counts;
- target prevalence by environment;
- missingness summary; and
- a stable identifier for every retained unit.

Where raw data cannot be redistributed, the public ledger will contain stable identifiers, hashes, transformation metadata, and aggregate counts rather than restricted text.

### Step 5. Run E0 as a descriptive diagnostic

E0 will report unconditional association between the candidate score and target. It will be clearly labeled descriptive. A strong E0 result alone cannot support the main claim.

### Step 6. Run E1 for incremental held-out information

E1 will compare a baseline-only predictor against a baseline-plus-candidate predictor on held-out units.

The workflow will:

1. split data by the declared independence unit;
2. fit preprocessing using training folds only;
3. fit the baseline model using only declared proxies;
4. fit the augmented model with the candidate score added;
5. evaluate both models on the same held-out units;
6. calculate absolute and relative held-out error improvement;
7. estimate uncertainty at the independence-unit level; and
8. compare the result with the frozen practical threshold.

The claim is always conditional on the named baseline set. We will not write "after controlling for capability" when the data contain only incomplete capability proxies.

### Step 7. Run E2 for environment transport

E2 will hold out one declared environment at a time, train on the others, and compare baseline-only with baseline-plus-candidate predictions in the unseen environment.

The output will include:

- one result for every held-out environment;
- an aggregate environment-equal result;
- uncertainty intervals;
- environment sample and unit counts;
- failures or unresolved environments; and
- a warning when aggregate transport hides substantial environment disagreement.

If fewer than three usable environments remain, E2 will be marked unresolved rather than approximated with an inappropriate split.

### Step 8. Run controls

Every main audit will include at least:

- one deceptive control designed to look useful for an ordinary reason already represented in the baseline set; and
- one deterministic negative control that should contain no meaningful signal.

If a control crosses a primary evidence threshold, the main conclusion will become unresolved until the cause is understood. Controls are part of the decision rule, not decorative appendix material.

### Step 9. Run named alternative specifications

Alternatives will be chosen before opening the final result and may include:

- a broader baseline set;
- an alternative but defensible environment definition;
- a stricter cohort rule;
- a simpler estimator;
- a different practical threshold;
- inclusion or exclusion of a potentially unavailable proxy; and
- an all-environment descriptive sensitivity.

The contestation bundle will retain each complete claim card. It will report disagreement without declaring that the specification yielding the strongest result is correct.

### Step 10. Assign evidence states

Each estimand will receive one of three states:

- `meets-declared-threshold`;
- `below-declared-threshold`; or
- `unresolved`.

The overall claim will receive one of:

- `supports-claim-under-declared-tests`;
- `does-not-support-claim-under-declared-tests`; or
- `unresolved-under-declared-tests`.

Every label remains tied to the exact protocol. None is presented as universal benchmark validity.

### Step 11. Publish the result regardless of direction

The result report will contain:

- the primary outcome;
- all controls;
- all frozen sensitivity analyses;
- cohort and environment summaries;
- unexpected failures;
- protocol deviations;
- interpretation limits;
- reproduction instructions; and
- the claim card and contestation bundle.

A null, negative, fragile, or unresolved result will not be removed from the release.

---

## 7. Software engineering plan

### 7.1 Input validation

The CLI will fail closed when:

- required columns are absent;
- the metric and target are identical;
- the unit identifier is missing;
- environment coverage is insufficient for E2;
- requested baselines are missing;
- identifiers are null where grouping is required;
- the analysis would create an empty fold; or
- output paths would silently overwrite frozen artifacts.

### 7.2 Reproducibility

Every public audit will include:

- deterministic seeds;
- exact dependency versions;
- source commit identifiers;
- file hashes;
- one primary analysis command;
- generated artifact checksums;
- a machine-readable manifest;
- CI coverage for the synthetic path; and
- a clean-environment reproduction record.

### 7.3 Testing strategy

Tests will cover:

- schema validation;
- grouped fold integrity;
- no preprocessing leakage from test folds;
- repeated-unit handling;
- metric and baseline column mapping;
- environment holdout behavior;
- control behavior;
- deterministic regeneration;
- Markdown and JSON agreement;
- contestation-state comparison; and
- failure modes for insufficient data.

### 7.4 Interface design

The main user should be able to run an audit from a CSV with a single explicit command. The CLI will require semantic roles rather than infer them from convenient column names.

Example:

```bash
mbe-eval-claim \
  --csv benchmark_results.csv \
  --metric candidate_score \
  --target external_criterion \
  --baselines capability_proxy,format_proxy \
  --environment benchmark_family \
  --unit configuration_id \
  --claim-id benchmark-claim-v1 \
  --claim-text "The score adds held-out information beyond the declared proxies" \
  --output-prefix artifacts/claim_card
```

The command will produce human-readable and machine-readable outputs with the same substantive content.

---

## 8. Ninety-day work schedule

The schedule is organized by evidence gates rather than by a promise to move forward regardless of what is found.

### Days 1-10: Project separation and baseline freeze

We will:

- create a Cosmos-specific repository landing area;
- document the difference between the Benchmark Audit Toolkit and full MBE 2.0;
- inventory every existing implementation, test, claim, and artifact;
- freeze the starting version of the claim-card schema;
- run the current synthetic and TruthfulQA reproduction paths from a clean environment;
- record failures and documentation gaps; and
- publish the initial 90-day deliverable checklist.

**Gate:** the project does not proceed to new analysis until the existing prototype and TruthfulQA artifacts reproduce or every discrepancy is explained.

### Days 11-25: Interface hardening and calibration suite

We will:

- strengthen input validation;
- implement or refine evidence-state rules;
- expand deceptive and negative synthetic controls;
- test repeated-unit blocking and environment holdout behavior;
- harden claim-card Markdown and JSON generation;
- harden contestation bundles;
- add deterministic artifact manifests; and
- update CI.

**Gate:** every synthetic fixture must produce its expected qualitative result or a documented abstention. A failing deceptive control blocks real-data expansion.

### Days 26-35: Second-benchmark selection

We will:

- inspect Anthropic's sycophancy data and at least one fallback dataset;
- complete a structured candidate record for each;
- identify target, baselines, environment, and independence unit;
- inspect licenses and reproducibility;
- document shared-label or shared-judge limitations;
- choose one dataset through the published selection criteria; and
- publish rejection reasons for candidates that fail.

**Gate:** no dataset is selected without a defensible unit, baselines, target, and environment structure. If none qualifies, the honest deliverable is a dataset-gap report plus a stronger synthetic and TruthfulQA toolkit, not a forced second audit.

### Days 36-45: Source inspection and protocol freeze

We will:

- pin source revisions and hashes;
- create the source manifest;
- inspect duplicates, conflicts, leakage, and environment coverage;
- write cohort rules;
- define controls and alternatives;
- define thresholds and uncertainty procedures;
- write the permitted interpretation; and
- commit the frozen protocol before calculating the candidate result.

**Gate:** any material source problem discovered here must narrow the cohort or claim before analysis.

### Days 46-60: Main audit and contestation analysis

We will:

- construct the frozen cohort;
- run E0, E1, and E2;
- run deceptive and negative controls;
- generate the primary claim card;
- run all frozen alternative specifications;
- generate the contestation bundle;
- inspect environment disagreement; and
- document deviations or unexpected failures.

**Gate:** controls that cross primary thresholds, broken folds, source mismatches, or unstable reruns make the result unresolved until corrected through a visible amendment.

### Days 61-72: Interpretation and usability

We will:

- write the main result with explicit interpretation boundaries;
- produce a short reviewer path;
- improve CLI help and example datasets;
- create a clean-start tutorial;
- ensure the JSON can be consumed by other tools; and
- remove assumptions that only the project author would understand.

**Gate:** a user must be able to identify the claim, inputs, outcome, controls, and limitations without reading the implementation source.

### Days 73-82: Independent cold-start reproduction

We will provide a clean reproduction bundle to an external reader or execute it in a genuinely clean environment with no cached data or local state. The test will record:

- setup time;
- failed commands;
- undocumented dependencies;
- ambiguous instructions;
- artifact differences;
- questions asked; and
- whether the main claim card was regenerated exactly.

Every discrepancy will be fixed or retained in a public discrepancy log.

**Gate:** the project cannot claim one-command reproducibility until the clean run succeeds.

### Days 83-90: Public release and completion report

We will:

- tag the release;
- archive source and derived artifacts;
- publish the artifact manifest and checksums;
- publish the correction history;
- publish the final claim cards and contestation bundles;
- publish any negative or unresolved result;
- write the Cosmos completion report; and
- identify the next evidential step without presenting it as completed work.

---

## 9. Proposed use of the $6,500

This is a working allocation for execution planning, not an expansion of the promised scope. Material changes will be recorded in the final spend ledger.

| Category | Planned ceiling | Purpose |
|---|---:|---|
| Research engineering and analysis | $4,000 | Implementation, source inspection, protocol design, analysis, testing, documentation, and release work |
| Compute, storage, and archival services | $800 | Reproducible analysis runs, storage, artifact transfer, and public archival costs |
| External reproduction and technical feedback | $700 | Honorarium or support for a cold-start reproduction and focused methodological review |
| Documentation and public release | $600 | Usability materials, packaging, persistent release preparation, and reviewer-facing artifacts |
| Contingency | $400 | Failed jobs, data-access variance, or approved reproducibility costs; unused funds remain visible |
| **Total** | **$6,500** | Final public spend and variance ledger |

The project does not require large training runs. Compute is used for audit execution, resampling, source processing, and reproducibility rather than training frontier models. Unused compute or contingency funds will not be converted into unnecessary experiments merely to exhaust the budget.

---

## 10. Risks and response plans

### Risk 1. The second dataset does not support a defensible external target

**Response:** label the analysis as an internal diagnostic or reject the dataset. Publish why it failed the selection gate. Do not claim construct validity.

### Risk 2. Shared labels, judges, or references mechanically favor the candidate score

**Response:** perform source-level leakage inspection, exclude exact mechanical overlaps where justified before analysis, create deceptive controls, and narrow the claim. If the dependence cannot be separated, report the limitation as central.

### Risk 3. Too few independent units or environments remain

**Response:** mark E2 unresolved, publish descriptive evidence, and do not manufacture transport evidence from arbitrary random splits.

### Risk 4. Results change across reasonable specifications

**Response:** preserve the disagreement in the contestation bundle and classify the claim as fragile or unresolved. Do not choose the favorable specification after seeing results.

### Risk 5. A synthetic control fails

**Response:** stop real-data interpretation, debug the pipeline, document the correction, and rerun from the frozen source. A failed control invalidates permission to interpret the main result.

### Risk 6. The second audit is negative

**Response:** publish it. A negative result demonstrates that the toolkit can narrow claims rather than only manufacture favorable conclusions.

### Risk 7. The method is not sufficiently distinct from existing approaches

**Response:** narrow the novelty claim. Present the contribution as an integrated, reproducible audit workflow if the statistical components are established elsewhere. Do not defend novelty through wording alone.

### Risk 8. Documentation works only for the author

**Response:** run a cold-start reproduction, maintain a discrepancy log, and treat setup failures as product defects.

### Risk 9. The 90-day scope becomes confused with the full MBE 2.0 program

**Response:** keep Cosmos artifacts in a dedicated landing area, label E3 and E4 as omitted, avoid references to the 340-run image and language-model validation matrix as Cosmos deliverables, and keep the $25,000 plan in a clearly separate document.

---

## 11. Decision and amendment policy

Every material decision will be placed in one of three categories:

1. **Pre-result decision:** made before the relevant candidate result is calculated. This may define the cohort, target, baselines, environments, thresholds, controls, or estimator.
2. **Pre-result amendment:** made after source inspection but before the result is calculated. The amendment must state the discovered problem and why the change is necessary.
3. **Post-result sensitivity:** performed after the primary outcome is known. It cannot replace the frozen primary analysis and must be labeled non-decisional unless an entirely new protocol is frozen for a future analysis.

The decision log will include dates, commit identifiers, affected artifacts, and whether the result was known at the time.

No primary result will be silently overwritten. Corrected versions will retain the earlier artifact or its checksum, explain the change, and state whether the evidence state changed.

---

## 12. Definition of success

The Cosmos project is complete when all of the following are true:

- reviewers can enter through a Cosmos-specific landing page without first understanding the entire MBE repository;
- the E0-E2 prototype has a stable, tested input and output contract;
- the claim card records scope, thresholds, controls, omitted checks, and permitted interpretation;
- the contestation bundle exposes named specification disagreement;
- the expanded synthetic suite passes or produces justified abstentions;
- the TruthfulQA pilot reproduces from its pinned sources;
- a second benchmark has either passed the selection gate and been audited, or failed through a published dataset-gap decision that explains why forcing the audit would be misleading;
- all primary and negative-control outcomes are public;
- a clean reproduction attempt and discrepancy log exist;
- code, protocols, claim cards, ledgers, and manifests are publicly accessible; and
- the final report distinguishes completed evidence from proposed future work.

Success does not require the second benchmark to support its candidate claim. Success requires an honest, inspectable test whose conclusion cannot be improved by hiding inconvenient evidence.

---

## 13. Explicit non-goals

During the Cosmos-funded period, the project will not claim to:

- validate MBE 2.0 as a complete statistical framework;
- certify that a benchmark measures truthfulness, honesty, reasoning, or alignment;
- certify individual models;
- establish causal effects from observational benchmark data;
- prove that declared proxies exhaust general capability;
- implement the full E3 intervention program;
- implement the full E4 reliability and cost program;
- complete the separate 340-run image and causal-language-model validation matrix;
- complete the separate protected-holdout and independent-replication program proposed for the $25,000 MBE 2.0 plan; or
- turn a single successful audit into a universal claim about AI evaluation.

These boundaries are part of the project, not disclaimers added after the result.

---

## 14. Final public artifact map

The intended release structure is:

```text
cosmos/
|-- README.md                         # reviewer landing page
|-- EXECUTION_PLAN.md                 # this detailed plan
|-- DELIVERABLES.md                   # status and completion checklist
|-- DECISION_LOG.md                   # freezes, amendments, and corrections
|-- DATASET_SELECTION.md              # candidate comparison and decision
|-- COMPLETION_REPORT.md              # final results and spend summary
|
|-- demo/
|   |-- README.md                     # one-command demonstration
|   |-- expected_claim_card.md
|   `-- expected_claim_card.json
|
|-- audit_01_truthfulqa/
|   |-- SOURCE_MANIFEST.json
|   |-- PROTOCOL.md
|   |-- RESULTS.md
|   |-- claim_card.md
|   |-- claim_card.json
|   `-- reproduction.md
|
`-- audit_02_second_benchmark/
    |-- SOURCE_MANIFEST.json
    |-- PROTOCOL.md
    |-- RESULTS.md
    |-- claim_card.md
    |-- claim_card.json
    |-- contestation_bundle.json
    |-- discrepancy_log.md
    `-- reproduction.md
```

The existing repository paths may be linked or reorganized rather than duplicated when duplication would create conflicting sources of truth. The Cosmos landing page will always identify the canonical artifact.

---

## 15. The principle governing the work

The toolkit is not designed to make benchmark scores look stronger. It is designed to make the evidence behind them harder to overstate.

If a plausible baseline erases the result, the claim card should say so. If transport fails, the environment result should remain visible. If reasonable specifications disagree, the contestation bundle should expose that dependence. If a dataset cannot support the desired claim, the project should reject the audit rather than create a persuasive but invalid number.

The product is not a favorable verdict. It is a reproducible way to earn, narrow, or refuse one.
