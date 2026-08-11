# Candidate Selection Record: Anthropic Sycophancy Evaluations

**Inspection date:** 11 August 2026

**Decision:** unresolved, additional data design required

**Candidate result computed:** no

## Dataset and source

- Dataset: Anthropic model-written sycophancy evaluations
- Official source: <https://github.com/anthropics/evals/tree/main/sycophancy>
- Pinned commit: `84fcc677e52e1902d696c32cd1a6b663e70d3993`
- License: CC BY 4.0
- Released files: NLP survey, PhilPapers 2020, and political typology JSONL
  collections

## Proposed claim

A model's score on the released evaluation carries information about
agreement-seeking behavior beyond inexpensive prompt, task, response, and
general-capability proxies, and the increment transports across meaningful
question families.

This wording is provisional. It cannot be frozen until the model-output
collection and target are specified.

## Candidate score

The natural released scoring rule is the probability or frequency with which a
model selects `answer_matching_behavior` rather than
`answer_not_matching_behavior` after receiving the generated user biography
and survey question.

The scoring rule is clear, but the repository does not include model outputs or
token probabilities. They would have to be collected under a separate frozen
protocol.

## Target

**Not yet adequate.** The release labels which answer matches the user's stated
view. Using the same label as both the score definition and the outcome would
be circular. The release contains no external per-example judgment of whether
a response is sycophantic, harmful, misleading, or less truthful.

Without an additional target, the strongest honest use may be an internal
diagnostic of whether a simpler heuristic predicts the released scoring rule.
It would not independently validate sycophancy as a construct.

## Declared baselines under consideration

Potential inexpensive baselines include:

- answer position and matching-answer identity;
- source collection and source-question identity;
- generated biography length and question length;
- explicit agreement, disagreement, ideology, or stance tokens in the
  biography;
- response length and answer-token prior, once outputs exist;
- model identity, parameter scale, and a general-capability score, once a model
  panel is defined.

The final baseline set must be frozen before candidate-score analysis.

## Environment

The three released collections provide a possible top-level environment split:

- NLP research survey;
- PhilPapers 2020;
- political typology.

This gives three named domains, but three environments alone provide a fragile
aggregate transport test. A stronger design may hold out source questions or
prespecified subfamilies within each collection as well.

## Independence unit

The JSONL rows are generated biography variants, not independent source
questions. The current inspection extracts the repeated survey question or
answer-choice block as the conservative source unit. Any model-output
collection and resampling procedure must block on that source unit and model.
Random row-level splitting would leak near-identical question structure across
train and test data.

The pinned source inspection found:

| Collection | Released rows | Extracted source units | Variants per unit |
|---|---:|---:|---:|
| NLP survey | 9,984 | 32 | 312 for every unit |
| PhilPapers 2020 | 9,867 | 109 | 66 median, 66 to 231 range |
| Political typology | 10,200 | 15 | 600 median, 600 to 1,200 range |
| **Total** | **30,051** | **156** | |

All 30,051 full prompts are unique, but uniqueness comes from generated
biography variation. It does not make them 30,051 independent survey
questions.

## Known leakage and validity concerns

- The user stance is stated directly in the generated biography, so lexical
  stance extraction may explain a large part of the score.
- The behavior-matching label defines the released scoring rule and is not an
  external validation target.
- Generated biography variants repeat a much smaller set of source questions.
- Prompt format and answer-token priors may affect model probabilities.
- The three domains differ in answer structure, including list-valued
  nonmatching answers in the PhilPapers collection.
- The release contains no model capability proxy or model-response ledger.
- The data were model-generated and filtered under the process described in
  the associated paper, so generation and filtering artifacts may remain.

## Reproducibility and access

The source is public, versionable, and licensed for reuse with attribution. The
inspection script pins the repository commit, hashes every JSONL source file,
checks required fields, counts full-prompt duplicates, extracts repeated source
units, and records label structure. Its output states explicitly that no
candidate result was computed.

## Gate assessment

| Selection requirement | Current assessment |
|---|---|
| Clear candidate score | Pass |
| Defensible target | Not yet met |
| Declared baselines | Feasible, not frozen |
| Valid independence unit | Feasible through source-question blocking |
| At least three environments | Minimum met, scientific strength unresolved |
| Sufficient coverage | Row coverage is high, independent-unit coverage under inspection |
| Reproducible access | Pass |
| Claim can fail | Pass in principle, thresholds not frozen |

## Decision

The candidate is **not accepted for analysis yet**. It remains viable only if
we can define a noncircular target or explicitly narrow the work to an internal
diagnostic, collect a versioned model-output panel with capability metadata,
and show that source-question blocking leaves enough independent units for the
planned holdouts.

No sycophancy score will be computed until those questions are resolved and the
protocol is frozen. If they cannot be resolved, this record will change to
`rejected` and the audit will move to a fallback dataset without deleting this
decision trail.
