#!/usr/bin/env bash
set -euo pipefail

ROOT=/home/apara/mbe-calibration
EXPERIMENT="$ROOT/experiments/30_oracle_feasibility_frontier"
OUTPUT="$EXPERIMENT/out/v1"
STATE="$EXPERIMENT/CAMPAIGN_STATE"

mkdir -p "$OUTPUT"
printf 'RUNNING %s\n' "$(date --utc --iso-8601=seconds)" > "$STATE"

set +e
"$ROOT/.venv/bin/python" "$EXPERIMENT/run_frontier.py" \
  --output-dir "$OUTPUT" --workers 16 \
  > "$EXPERIMENT/campaign.stdout.log" \
  2> "$EXPERIMENT/campaign.stderr.log"
run_status=$?
set -e

if [[ $run_status -ne 0 ]]; then
  printf 'RUN_FAILED exit=%s %s\n' "$run_status" "$(date --utc --iso-8601=seconds)" > "$STATE"
  exit "$run_status"
fi

set +e
"$ROOT/.venv/bin/python" "$EXPERIMENT/validate_outputs.py" \
  --output-dir "$OUTPUT" \
  > "$EXPERIMENT/validation.json" \
  2> "$EXPERIMENT/validation.stderr.log"
validation_status=$?
set -e

if [[ $validation_status -ne 0 ]]; then
  printf 'VALIDATION_FAILED exit=%s %s\n' "$validation_status" "$(date --utc --iso-8601=seconds)" > "$STATE"
  exit "$validation_status"
fi

printf 'COMPLETE %s\n' "$(date --utc --iso-8601=seconds)" > "$STATE"
touch "$EXPERIMENT/CAMPAIGN_COMPLETE"

