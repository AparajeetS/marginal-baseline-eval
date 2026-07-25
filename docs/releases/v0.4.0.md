# mbe-eval v0.4.0

PyPI: https://pypi.org/project/mbe-eval/0.4.0/

This release makes MBE safer and easier to use in research pipelines without
changing the stable MBE v1 statistical estimand.

## Highlights

- fails closed with a clear `MBEInputError` when a requested metric, target,
  control, or grouping column is missing;
- rejects empty ledgers, empty metric lists, negative bootstrap counts, and
  grouped-only audits without a grouping column;
- adds deterministic `--seed` control to the audit CLI;
- adds `--results FILE.csv` and `--results FILE.json` for machine-readable
  output while retaining the human-readable Markdown report;
- creates report output directories automatically;
- consolidates package metadata, dependencies, extras, links, and console
  scripts in `pyproject.toml`;
- installs scikit-learn with the development extra so the complete test suite
  runs in clean environments;
- exports `MBEInputError` and `validate_audit_inputs` as public API helpers.

## Compatibility

Valid v0.3.x audit calls continue to work. Calls that previously referred to
missing columns and silently omitted them now raise an actionable error.

## Validation

```bash
python -m pytest -q
python -m build
python -m twine check dist/*
mbe-eval-demo --bootstrap 20 --no-output
```
