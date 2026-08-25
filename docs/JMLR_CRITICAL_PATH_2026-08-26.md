# MBE JMLR Critical Path

Updated: 2026-08-26

Status: active submission path after the 126,000-row oracle feasibility
frontier and the completed 360-model image target-transport artifact.

The project is not submission-ready. The current evidence supports a serious
larger research program, but the main estimator, protected opening, external
holdout, and independent execution gates remain incomplete.

## 1. Close The 48-Configuration Oracle Gap

The oracle frontier found a design-specific boundary. At 24 independent
configurations, the observable oracle was calibrated but underpowered. At 48,
it passed the frozen null-control and effect-0.50 power gates. Current learned
degree-2 rules retained useful power but reached 14.2-15.2% worst-null support.

Required work:

- develop a substantively different estimator or calibrated abstention rule on
  fresh known-truth data;
- target the frozen 48-configuration geometry without treating 48 as a
  universal sample-size answer;
- compare against raw and residual rank tests, GCM, WGCM, KCI, orthogonal
  scores, and a principled conditional-randomization procedure on identical
  datasets;
- freeze one rule before a disjoint confirmation;
- retain every failed candidate and all estimability failures.

Exit: one fixed rule controls the worst prespecified null/proxy cell, retains
the prespecified minimum power, and passes on untouched known-truth data.

## 2. Run One Safety-Facing Measurement Audit

The primary proposed case audits automated jailbreak and harmfulness judges
against independently defined human assessments. StrongREJECT is the leading
development candidate and HarmBench is a transfer candidate, subject to public
eligibility checks.

Required work:

- freeze the target, judges, cheap baselines, grouping structure, missingness
  rules, and practical effect threshold;
- set the final independent-unit count from outcome-blind design-matched
  calibration, with 48 configurations as a floor;
- compare raw-correlation selection, a globally fixed judge, and the
  MBE-supported judge or abstention;
- test transport to a held-out model or attack family;
- report raw association, incremental value, transport, repeatability, cost,
  coverage, and abstention separately.

Exit: a configuration-level support-or-abstain result with complete provenance
and no outcome-dependent change to the opening rule. Failure of the calibration
gate leaves the safety-facing association unopened.

## 3. External Holdout And Independent Execution

The 240-model PGDL intake is structurally validated but is not wholly unseen,
and its opening gate failed. The replication packet has passed only an internal
dry run.

Required work:

- identify a genuinely external environment that did not influence estimator,
  nuisance-model, threshold, or metric selection;
- freeze repository commit, container digest, targets, baselines, metrics,
  splits, hypotheses, and commands before one opening;
- have a researcher who did not develop the rule execute a hash-sealed packet;
- publish identity, conflicts, discrepancies, and a signed conclusion;
- accept null and adverse results as complete outcomes.

Exit: one eligible one-shot external report and one externally executed signed
replication. An internal rerun does not satisfy either milestone.

## 4. Paper And Artifact

The paper should make the calibration failures part of the contribution rather
than hide them. It must separate exploratory, development, confirmation,
protected, and external evidence in every claim.

Required sections:

- estimand, baseline-information ladder, assumptions, and abstention behavior;
- motivating FIM_norm case and public-study reaudit;
- 48,000-cell zero-finalist screen and 153,600-result comparator benchmark;
- 10,080-row repeated-split negative result;
- 126,000-row oracle feasibility frontier;
- safety-facing measurement audit;
- external holdout and independent execution;
- runtime, missingness, measurement reliability, and practical decision value;
- limitations, failure modes, and explicit non-claims.

Exit: every headline value regenerates from public artifacts, the package and
paper implementation agree, and an adversarial review can be answered without
changing the claim boundary.

## Submission Decision

Submit only when all four stages above are complete. If no deployable rule
closes the oracle gap, the publishable result becomes a feasibility boundary
for metric-audit designs rather than a validated MBE selector. If the rule
passes but the safety audit or external holdout is null, publish the scoped null
result. Positive protected outcomes are not required; prospective calibration,
external evidence, and honest accounting are.

See the [roadmap](../ROADMAP.md), [project status](PROJECT_STATUS.md),
[AI-safety measurement case](AI_SAFETY_MEASUREMENT_CASE.md), and
[credibility ledger](MBE_CREDIBILITY_LEDGER.md).
