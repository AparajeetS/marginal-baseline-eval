#!/usr/bin/env sh
set -eu
SMOKE_DIR="${TMPDIR:-/tmp}/mbe_credibility_smoke"
mkdir -p "$SMOKE_DIR/calibration" "$SMOKE_DIR/method"
python -m pytest -q
python experiments/08_protocol_calibration/run_calibration.py --permutations 19 --output-dir "$SMOKE_DIR/calibration"
python experiments/10_method_comparison/run_factorial_benchmark.py --repetitions 2 --seeds-per-config 3 --permutations 19 --bootstrap 19 --output-dir "$SMOKE_DIR/method"
python experiments/11_credibility_freeze/validate_claims.py experiments/11_credibility_freeze/claim_ledger.json
python paper/build_tables.py
