$ErrorActionPreference = "Stop"
$smokeDir = Join-Path $env:TEMP "mbe_credibility_smoke"
$calibrationDir = Join-Path $smokeDir "calibration"
$methodDir = Join-Path $smokeDir "method"
New-Item -ItemType Directory -Force -Path $calibrationDir, $methodDir | Out-Null
python -m pytest -q
python experiments/08_protocol_calibration/run_calibration.py --permutations 19 --output-dir $calibrationDir
python experiments/10_method_comparison/run_factorial_benchmark.py --repetitions 2 --seeds-per-config 3 --permutations 19 --bootstrap 19 --output-dir $methodDir
python experiments/11_credibility_freeze/validate_claims.py experiments/11_credibility_freeze/claim_ledger.json
python paper/build_tables.py
