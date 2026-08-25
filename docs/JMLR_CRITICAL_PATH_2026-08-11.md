# MBE JMLR Critical Path

> Superseded by the [2026-08-26 critical path](JMLR_CRITICAL_PATH_2026-08-26.md).
> This file is retained as a dated record of the state through experiment 29.

Status: superseded roadmap after the experiment 21 calibration abstention,
experiment 26 pooled-PGDL failure, experiment 28 binding near miss, and
experiment 23 conditional-comparator benchmark.

## 1. Estimator Development

- Develop on synthetic known-truth data only.
- Target the exact 24- and 48-configuration regimes.
- Keep conditional rank signal and learner-relative predictive gain as separate
  estimands.
- Retain every failed candidate and calibration artifact.

Exit: at least one fixed candidate controls the worst null cell while retaining
useful positive power under the recorded development diagnostic.

Current evidence: the experiment 25 rule passed its 192-group synthetic
confirmation, but experiment 26 showed that it did not transfer with controlled
false support to the 240-model pooled PGDL geometry. Development therefore
continues on fresh known-truth seeds; the PGDL associations remain sealed.

Experiment 27 selected a lower-shrinkage degree-2 rule. In the untouched
experiment 28 confirmation it controlled every null cell, while B3 missed the
effect-0.50 power gate by Wilson lower bound 0.492 versus 0.500. The global gate
therefore remained failed and no protected PGDL association was opened.

Experiment 29 tested a distinct repeated-split intersection family on fresh
24/48-configuration geometries. All 10,080 planned rows were estimable, but no
candidate met both the 5% worst-null and 50% weakest effect-0.50 development
floors. This simple stability rule is rejected as a primary opening candidate;
future development must be outcome-blind and methodologically distinct.

## 2. Frozen Confirmation

- Freeze one primary candidate, limited sensitivities, untouched seeds, 100
  repetitions per cell, and exact thresholds.
- Require at least 98% estimability, worst-null Wilson upper bound at most 10%,
  and worst effect-0.50 power Wilson lower bound at least 50%.
- Hash the opening decision before accessing protected outcomes.

Exit: a pass authorizes only the prespecified analyses; failure binds the paper
to abstention or further method development.

Current evidence: experiment 28 was the disjoint confirmation. It passed all
null-control cells but missed one frozen power bound, so the global decision is
failure and the protected associations remain sealed.

## 3. Comparator Study

Compare on identical simulations and independent units:

- original MBE grouped cross-fit and full-refit bootstrap;
- unweighted generalized covariance score with asymptotic inference;
- the frozen multiplier-bootstrap score;
- a prespecified weighted-GCM sensitivity;
- a conditional-randomization or kernel conditional-independence comparator
  where its assumptions are satisfied;
- raw and residualized rank association as deliberately weaker references.

Report runtime, estimability, type-I error by null family, power by effect size,
and sensitivity to nuisance misspecification. No method is ranked outside its
stated estimand and assumptions.

Current evidence: experiment 23 completed 9,600 paired datasets and 153,600
method rows across the listed estimands. No tested procedure combined strict
worst-cell null control with useful worst-cell effect-0.50 power at 24 and 48
independent configurations. The result is a calibration-power frontier, not a
winner.

## 4. Protected And External Evidence

- Open only authorized image/text associations with multiplicity control and
  the random negative control retained.
- Add one externally sourced run-level holdout whose design was not used in
  method development.
- Provide a frozen replication packet to an independent researcher or lab;
  accept signed zero-result or failure reports as valid replication outcomes.

Exit: complete raw ledgers, manifests, environment locks, hashes, and one
independent reproduction report.

Current evidence: the PGDL Tasks 6-9 intake and replication packet v2 are
structurally validated and hash-sealed. The PGDL opening decision is negative,
and the packet has passed only an internal dry run. A genuinely external
holdout and an independent signed execution remain required.

## 5. Paper And Artifact

- State the estimand, assumptions, and abstention behavior precisely.
- Present the original metric case study and the 48,000-cell zero-finalist
  calibration as motivating evidence rather than hidden history.
- Separate exploratory, development, confirmation, protected, and external
  evidence in every table.
- Include calibration, nuisance-complexity, sample-size, comparator, negative
  control, holdout, and replication sections.
- Release code, package, benchmark ledger, paper, and archival snapshot from
  one hashed version.

The submission gate is scientific completeness, not a positive headline.
