import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_public_kaggle_notebook_matches_release_and_is_executed() -> None:
    path = (
        ROOT
        / "kaggle"
        / "mbe_metric_audit"
        / "how_to_audit_ml_training_metrics_mbe.ipynb"
    )
    notebook = json.loads(path.read_text(encoding="utf-8"))
    code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    assert code_cells
    assert all(cell["execution_count"] is not None for cell in code_cells)
    source = "\n".join("".join(cell["source"]) for cell in code_cells)
    assert (
        "releases/download/v0.5.0/mbe_eval-0.5.0-py3-none-any.whl" in source
    )


def test_corrected_validator_does_not_claim_machine_verified_custody() -> None:
    validator = (
        ROOT
        / "experiments"
        / "31_image_target_transport_atlas"
        / "validate_outputs.py"
    ).read_text(encoding="utf-8")
    assert '"custody_status": "not-machine-verifiable"' in validator
    assert '"metric_target_associations_inspected": None' in validator
