# A Benchmark Is a Claim, Not Just a Score

**A short reviewer guide to MBE: Benchmark Audit Toolkit**

Benchmarks are supposed to referee AI progress. Yet we spend far more effort
auditing the models than auditing the referees.

A score can rank models cleanly while measuring some mixture of the ability on
its label, general capability, answer length, response style, formatting, or a
quirk of the dataset. The leaderboard may still look precise. The scientific
claim beneath it may not be.

MBE: Benchmark Audit Toolkit treats each benchmark metric as a falsifiable
claim. It asks what the score predicts, what it adds beyond declared
alternatives, whether that added signal survives a change of environment, and
exactly where the evidence stops. The aim is not to invent one more universal
score. It is to make benchmark claims easier to inspect, reproduce, challenge,
and revise.

## The three-minute review path

If you only have three minutes, follow this path:

1. **See the real result:** [TruthfulQA pilot results](experiments/08_truthfulqa_real_audit/artifacts/RESULTS.md)
2. **See the claim with its boundaries attached:** [generated claim card](experiments/08_truthfulqa_real_audit/artifacts/claim_card.md)
3. **See what changed before the result was known:** [frozen protocol and leakage amendment](experiments/08_truthfulqa_real_audit/PROTOCOL.md)
4. **See what the prototype can and cannot claim:** [benchmark audit specification](docs/BENCHMARK_AUDIT_PROTOTYPE.md)

If you have another five minutes, the [reproduction guide](experiments/08_truthfulqa_real_audit/README.md)
provides the exact command, pinned source commit, source hashes, and regenerated
artifacts.

## What the toolkit actually does

The prototype takes a candidate benchmark score, a named outcome, declared
baselines or proxies, an environment, and an independence unit. It separates
questions that are often compressed into a single correlation:

| Check | Question | Current prototype |
|---|---|---|
| E0 | Is the score associated with the outcome at all? | Descriptive diagnostic |
| E1 | Does it add held-out predictive information beyond the declared proxies? | Implemented |
| E2 | Does that increment survive when an environment is held out? | Implemented |
| E3 | Does it behave correctly under a matched intervention? | Not yet implemented |
| E4 | Is it reliable, stable, and affordable to measure? | Not yet implemented |

The output is a scoped claim card, not a certificate. It keeps the target,
proxies, environments, grouping, thresholds, controls, estimand-level outcomes,
and limitations together. Reviewers can also rerun named alternative
specifications and see whether the conclusion changes. The toolkit exposes
disagreement instead of silently selecting the specification most favorable to
the metric.

The project is **built from the MBE codebase and audit specification**. It is
not "validated by MBE." MBE 2.0 remains an active, unvalidated research design,
and this prototype currently implements only selected E0 to E2 checks. That
distinction matters.

## The first real-data pilot

The working demonstration audits a transparent ROUGE-1-style
reference-difference score against TruthfulQA v0's released human truth
judgments.

The most important result in this repository may not be the final `12.33%`. It
may be the decision to make the test harder before learning the answer.

Source inspection after the initial protocol freeze revealed duplicated
question-answer pairs, conflicting labels, exact benchmark-reference answers
inside the released label pool, and a historical alignment with TruthfulQA v0
rather than the later v1 table. Those facts could have mechanically favored a
reference-similarity score. Before computing the candidate result, I amended
the protocol to:

- collapse duplicate question-answer pairs;
- discard 27 pairs with conflicting truth labels;
- exclude 6,625 exact benchmark-reference pairs;
- reject 34 pairs without an exact v0 question match;
- keep every answer for a question inside the same cross-validation fold; and
- restrict the main transport analysis to categories with at least 20 eligible
  questions.

The governing amendment was frozen in Git at commit
[`827e192`](https://github.com/AparajeetS/marginal-baseline-eval/commit/827e192729b1b26dd8c470ae70f028214c942090)
before the score was run. Git history is not third-party preregistration, but it
does create a visible boundary between changing the test and seeing its result.

The final cohort contains 7,920 unique, nonconflicting, non-reference answer
pairs from 541 questions across 15 sufficiently represented categories.

| Test | Frozen threshold | Observed result | Decision |
|---|---:|---:|---|
| E1, increment beyond declared response and task proxies | 1% relative held-out MSE improvement | **12.33%** | Meets threshold |
| E2, aggregate leave-one-category-out transport | 1% relative held-out MSE improvement | **11.01%** | Meets threshold |
| Length-derived deceptive control | Same thresholds | Crossed neither | Below threshold |
| Deterministic hash-noise control | Same thresholds | Crossed neither | Below threshold |

For E1, the absolute MSE improvement was `0.007281`, with a 95% bootstrap
interval of `[0.005920, 0.008398]`. For aggregate E2 it was `0.006547`, with a
95% interval of `[0.004494, 0.008911]`. A non-decisional sensitivity analysis
that added the released human informativeness label left the complete
estimand-state signature unchanged on 7,912 matched rows.

This supports one narrow statement: under the frozen exclusions, declared
proxies, question grouping, category holdouts, estimator, and practical
thresholds, the lexical score added out-of-question predictive information for
the released human labels and transported in aggregate across the retained
categories.

It does **not** establish that TruthfulQA measures truthfulness, validate MBE,
control model family or general capability, reproduce the exact official T5
ROUGE implementation, establish causality or construct validity, or certify any
model or benchmark. The labels and references come from the same broader
TruthfulQA framework, so this is a real-data method demonstration rather than
an independent confirmatory validation.

## Why this is truth-seeking work

Truth-seeking is not only a property we want models to display. It is also a
discipline for deciding which evidence deserves belief.

A useful benchmark-audit system should be able to embarrass its author. It
should preserve negative and inconclusive results, reveal when a conclusion
depends on a convenient baseline, and narrow a claim when the data cannot
sustain it. Here, discovering leakage did not become a reason to quietly replace
the dataset. It became a public amendment, an exclusion ledger, and a harder
test.

That is the deeper purpose of MBE. It turns "this score measures truthfulness"
from a persuasive sentence into a structured object that other people can
rerun and contest.

## What would make the project change course

This is not a project that succeeds only when benchmark scores look good.

- If a plausible, predeclared baseline erases the result, the claim card should
  say so.
- If a conclusion changes across reasonable specifications, the contestation
  bundle should expose that dependence.
- If the second benchmark audit produces a negative or unresolved result, that
  result will still be part of the public deliverable.
- If careful comparison with prior work collapses the methodological novelty,
  the contribution should be narrowed rather than defended by rhetoric.

The product is not a favorable verdict. It is a better way to earn one.

## What the Cosmos grant would unlock

The **$6,500 Cosmos request is deliberately scoped**. It is not a request to
treat MBE as established, and it is separate from the longer-horizon full MBE
2.0 validation program documented elsewhere in this repository.

The exact research questions, evidence gates, 90-day schedule, deliverables,
failure policy, and proposed use of funds are defined in the
[Cosmos 90-Day Research and Execution Plan](COSMOS_90_DAY_EXECUTION_PLAN.md).
Current work is tracked separately in the
[Cosmos project landing area](cosmos/README.md), including a dated baseline
freeze and a public deliverable checklist.

Over a focused 90-day build, the grant would turn the current prototype and
single real-data pilot into a stronger public benchmark-audit instrument:

1. harden the claim-card and contestation interfaces;
2. complete a second audit on an independently structured benchmark, with
   Anthropic's sycophancy evaluations as the leading candidate;
3. add stronger baseline and environment sensitivity checks;
4. publish frozen protocols, scripts, derived ledgers, machine-readable cards,
   correction histories, and negative results; and
5. make the workflow usable by researchers who did not build MBE.

A reasoning-faithfulness audit is a stretch goal only if the available data
provide an honest external target, grouping structure, and suitable controls.
If they do not, it will not be forced into the project because it sounds
impressive.

## Who is building it

I am Aparajeet Shadangi, an independent researcher working across machine
learning and cosmology. I am an Emergent Ventures grantee and have shipped
open-source tools for ML training and evaluation, including the installable
`mbe-eval` and `traintools` packages, command-line interfaces, public notebooks,
experiment ledgers, and reproducibility documentation.

I am drawn to foundational questions, especially the quiet assumptions beneath
apparently settled measurements. My instinct is not to reject those assumptions
for effect. It is to ask what evidence they carry, where they stop working, and
what instrument would let someone else check the answer.

MBE is one such instrument. It is unfinished, testable, and already capable of
disagreeing with its maker. I think that is the right place for serious
truth-seeking work to begin.

---

**Contact:** [aparajeet.shadangi@proton.me](mailto:aparajeet.shadangi@proton.me)  
**Research profile:** [aparajeets.github.io](https://aparajeets.github.io/)  
**Code:** [AparajeetS on GitHub](https://github.com/AparajeetS)
