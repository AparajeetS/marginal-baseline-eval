# AI Safety Measurement Case

Status: proposed primary application of MBE. The study described here has not
been run and does not count as completed safety evidence.

## One-Minute Summary

AI-safety decisions increasingly depend on measurements: monitor scores,
jailbreak rates, automated harmfulness judgments, robustness scores, and
interpretability metrics. A score can correlate with the desired outcome for
the wrong reason. It may mainly track model family, general capability,
response length, prompt family, attack family, refusal markers, or another
signal that the evaluator already has.

Marginal Baseline Evaluation (MBE) asks the extra question: for a declared
target, baseline information set, environment, and decision, does the metric
add reliable out-of-sample information? It separates raw association,
incremental value, transport, intervention response, and measurement
reliability. When the study cannot support a conclusion, the intended output
is abstention rather than a metric ranking.

The first proposed safety-facing case is an audit of automated jailbreak and
harmfulness judges against independently defined human assessments. The goal
is not to certify one judge universally. It is to test whether a particular
judge earns trust for a particular evaluator choice and whether that evidence
survives a held-out model or attack family.

## Why This Decision Matters

Automated judges make safety evaluation cheaper and faster, but they can also
inherit shortcuts. If a judge appears accurate because response length,
refusal language, model capability, or attack family gives away the label, a
safety team may become more confident without becoming better informed. The
opposite error matters too: a useful judge can be rejected because unlike
models or attacks were pooled together or because uncertainty was counted at
the prompt level instead of the configuration level.

MBE is intended to sit upstream of decisions such as:

- selecting an automated evaluator for a red-team campaign;
- comparing jailbreak defenses;
- deciding whether a monitor transfers to a new model family;
- deciding whether a numerical interpretability result supports an
  intervention claim.

MBE does not solve alignment directly. Its proposed safety value is narrower:
make the evidential scope of a measurement explicit before that measurement
guides deployment, model selection, or confidence in a safeguard.

## Proposed Study

StrongREJECT is the leading development candidate because its automated
evaluators were studied alongside human evaluation. HarmBench offers a broader
model-and-attack structure and is the leading transfer candidate. Neither is
assumed eligible in advance. Data provenance, licensing, human-label
reliability, score construction, and the number of genuinely independent units
must pass a public intake audit first.

The preregistered design will specify:

- an independently defined human target and its reliability checks;
- candidate automated judges and the exact versions used;
- cheap baselines available to an evaluator, including model family, general
  capability, base refusal rate, attack and prompt family, refusal markers,
  and response length;
- at least 48 model/attack configuration blocks, or a larger number if
  outcome-blind power calibration requires it;
- multi-way grouping for shared models and attack families;
- held-out model- or attack-family transfer;
- minimum practical effects, exclusion rules, missingness rules, and runtime;
- one target-metric opening after code, splits, thresholds, and hashes are
  frozen.

Repeated prompts, generations, and human ratings will measure uncertainty
within a block. They will not be counted as independent models or attacks.

## Decision Comparison

Before the protected holdout, the study will freeze three evaluator choices:

1. the judge selected by raw benchmark correlation;
2. a simple globally fixed judge;
3. the MBE-supported judge, or an MBE abstention.

Their prediction of held-out human assessments will test whether the audit
changes a real decision and whether that change helps. Coverage and abstention
will be reported with accuracy; a method does not win by declining every hard
case.

## Opening Gate

No safety-facing target-metric association will be interpreted unless a fixed
rule first passes disjoint known-truth calibration with:

- controlled support on null, proxy-only, heteroskedastic, and deliberately
  deceptive cases;
- useful power at the study's design-matched sample size;
- complete accounting of every prespecified cell;
- stable conclusions under reasonable nuisance-model sensitivities; and
- an implementation that can be executed from frozen artifacts by someone who
  did not develop the rule.

If the gate fails, the safety study remains closed. That is not evidence that
the real judges are useless. It means the available design cannot support the
intended claim.

## Evidence That Justifies The Study

The current evidence supports doing the larger test, not declaring MBE
validated:

- a 48,000-cell screen selected no eligible learned rule;
- 9,600 paired known-truth datasets produced 153,600 comparator results and no
  uniformly reliable method at 24-48 independent configurations;
- a 10,080-row repeated-split screen rejected all six frozen candidates;
- a 126,000-row oracle frontier found the studied observable regime
  underpowered at 24 configurations, while an observable oracle passed at 48;
- at 48 configurations, current learned rules retained useful power but
  supported 14.2-15.2% of the worst known-null cells;
- a prospective 360-model image artifact completed every planned row and
  integrity gate, but its associations remain sealed because each environment
  contains only 24 independent configurations.

The central open problem is therefore concrete: recover the design-specific
48-configuration signal without manufacturing support through nuisance
estimation.

## What A Result Would And Would Not Establish

A positive result would support a scoped claim that a named automated judge
adds information beyond named baselines for a named target and environment. A
negative result could show redundancy, failed transfer, insufficient power, or
measurement unreliability. These are different outcomes and will be reported
separately.

The study will not establish that:

- automated judges are generally trustworthy or untrustworthy;
- human labels are perfect ground truth;
- observational incremental information is a causal effect;
- 48 configurations are sufficient in every safety study;
- one result transfers to future model families without another audit.

## Public Trail

- [Current project status](PROJECT_STATUS.md)
- [Evidence index](EVIDENCE_INDEX.md)
- [Experiment synthesis](EXPERIMENT_EVIDENCE_SYNTHESIS.md)
- [Credibility ledger](MBE_CREDIBILITY_LEDGER.md)
- [Statistical specification](STATISTICAL_ESTIMAND_AND_INFERENCE.md)
- [Oracle feasibility frontier](../experiments/30_oracle_feasibility_frontier/RESULT_SUMMARY.md)
- [External evidence intake rules](EXTERNAL_EVIDENCE_HANDOFFS.md)
- [Independent replication protocol](INDEPENDENT_REPLICATION_PROTOCOL.md)

An external executor has not yet been selected. External execution, dataset
eligibility, and a passing calibrated rule are milestones, not current claims.
