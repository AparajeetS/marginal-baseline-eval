# Metric Reliability Audit Service

Status: product hypothesis derived from the open MBE research program. This is
not a claim that the selector has already been validated across arbitrary tasks.

## Service Thesis

ML teams frequently monitor or publish scalar signals without knowing whether
those signals add information beyond training loss, validation performance,
architecture, hyperparameters, or task composition. MBE can support a service
that audits those claims for a customer's declared decision problem.

The service does not sell a universal best metric. It answers:

> For this target, at this decision point, and with this historical evidence,
> which metrics add reliable information, what do they cost, and where should
> the system abstain?

## Likely Customers

- research teams proposing or comparing training metrics;
- model-platform teams maintaining experiment tracking and model-selection
  policies;
- evaluation teams choosing robustness, calibration, or monitoring signals;
- benchmark designers checking whether a leaderboard measure rewards cheap
  proxies;
- organizations preparing high-stakes metric claims for internal review or
  publication.

The initial market is technical teams with repeated experiments and held-out
outcomes. A team with one model and no historical outcomes is not yet a good
customer for task-calibrated selection.

## Engagement Modes

### Ledger audit

The customer supplies a run ledger containing candidate metrics, outcomes,
baselines, configuration IDs, and environment IDs. No checkpoints are needed.

### Checkpoint audit

The customer supplies checkpoints or grants controlled access. The service
computes a frozen metric battery, records runtime/coverage, and audits the
resulting ledger.

### Continuous metric governance

An integration consumes experiment-tracker exports, detects reliability drift,
and reissues recommendations when the task, model family, or training regime
changes materially.

Self-hosted execution should be available for sensitive models and data.

## Required Customer Inputs

- a specific decision and target;
- target timing and data-split policy;
- candidate metrics or permission to compute them;
- baseline information available at decision time;
- repeated historical runs with configuration and seed identifiers;
- task/environment metadata;
- cost, latency, and data-access constraints.

Without target-task outcomes, the service can provide only an L1 transfer
assessment or L0 abstention. It cannot honestly produce an L2 task-calibrated
recommendation.

## Deliverable

Each audit produces:

- data-quality and leakage checks;
- target and estimand declaration;
- baseline information ladder;
- conditional reliability profile for every eligible metric;
- uncertainty, sign stability, transport, and intervention results;
- metric cost, coverage, and implementation provenance;
- recommended metric or Pareto set;
- evidence level L0-L3;
- explicit abstentions and reasons;
- machine-readable JSON/CSV plus a reviewable report;
- a frozen reproduction bundle or self-hosted command.

The report distinguishes statistical detectability, practical decision value,
and operational cost.

## Product Validation

Before selling automated selection as a validated product, the research must
show:

1. lower held-out task-family regret than a globally fixed metric;
2. lower regret than pooled and within-task raw-correlation selection;
3. calibrated intervals or confidence bands;
4. improving risk as abstention coverage decreases;
5. robustness to reasonable nuisance models and metric missingness;
6. correct evidence-level labeling on new and shifted tasks.

Until those gates pass, the commercial offer should be described as an expert
metric audit using open MBE methods, not an autonomous metric-selection oracle.

## Open-Core Boundary

Remain open:

- MBE definitions and statistical methods;
- core Python package and command-line tools;
- public metric cards and benchmark protocols;
- public-corpus reliability atlas;
- synthetic calibration and reproduction scripts;
- paper results, failures, and protected-holdout protocol.

Paid value can include:

- secure managed execution;
- private checkpoint metric extraction;
- customer-specific experiment schema and baseline design;
- integrations with experiment tracking and model registries;
- recurring drift and reliability monitoring;
- review meetings, interpretation, and implementation support;
- service-level support and private deployment.

Commercial work cannot alter the public benchmark, access a protected research
holdout early, or turn private favorable results into public claims without a
separate consent and preregistration process.

## Safety And Claim Boundaries

The service is not:

- a certification of model safety, robustness, or regulatory compliance;
- evidence that the selected metric causally improves a model;
- a replacement for held-out evaluation;
- a guarantee that historical reliability survives distribution shift;
- permission to optimize a proxy without monitoring the target.

Reports must warn about Goodhart risk when a recommended diagnostic becomes an
optimization objective. Selection and optimization are separate uses requiring
separate evidence.

## Privacy And Security

- minimize collected data and support ledger-only audits;
- offer self-hosted extraction for checkpoints and sensitive datasets;
- separate customer workspaces and credentials;
- encrypt data in transit and at rest in managed deployments;
- define deletion and retention periods contractually;
- never reuse private customer runs for research or model training without
  explicit permission;
- record package, configuration, and report versions for auditability.

## Minimum Viable Service

The first credible service does not need a learned router. It needs:

1. a strict run-ledger schema and validator;
2. target and baseline declaration workflow;
3. grouped MBE analysis with uncertainty;
4. transparent recommendation and abstention rules;
5. metric cards and data-quality warnings;
6. reproducible HTML/PDF and JSON reports;
7. one or two design-partner audits evaluated against decisions made after the
   recommendation was frozen.

The learned task router should be added only after the reliability atlas
contains enough independent task families to evaluate it honestly.
