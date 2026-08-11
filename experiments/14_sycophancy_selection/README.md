# Anthropic Sycophancy Candidate Inspection

This directory records the selection-stage inspection of Anthropic's released
sycophancy evaluation data. It is deliberately separate from a benchmark
analysis. The inspection describes the source, repeated-unit structure, and
missing information before any candidate result is computed.

## Reproduce the source inspection

```bash
git clone https://github.com/anthropics/evals.git ../anthropic-evals
git -C ../anthropic-evals checkout 84fcc677e52e1902d696c32cd1a6b663e70d3993
python experiments/14_sycophancy_selection/inspect_source.py \
  --source-root ../anthropic-evals \
  --source-commit 84fcc677e52e1902d696c32cd1a6b663e70d3993 \
  --output experiments/14_sycophancy_selection/artifacts/source_inspection.json
```

The official release is licensed under CC BY 4.0. It contains three JSONL
files covering NLP survey questions, PhilPapers 2020 questions, and Pew
political typology questions.

## Important boundary

The released files contain generated user biographies, questions, and the
answers defined as matching or not matching sycophantic behavior. They do not
contain model responses, answer probabilities, model capability metadata, or
an external per-example outcome target.

That means the release is enough to define and generate an evaluation, but not
enough by itself to run the proposed E1 and E2 audit. A defensible audit would
require a separately frozen model-output collection and a clear decision about
whether the result is only an internal diagnostic or is linked to an external
target.

See [SELECTION_RECORD.md](SELECTION_RECORD.md) for the current gate decision.

