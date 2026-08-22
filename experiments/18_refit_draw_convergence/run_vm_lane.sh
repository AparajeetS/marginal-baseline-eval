#!/usr/bin/env bash
set -u

cd "$(dirname "$0")/../.."
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1

output="experiments/18_refit_draw_convergence/out"
log_dir="experiments/18_refit_draw_convergence/vm_campaign_artifacts"
status_file="${log_dir}/lane_status.tsv"
mkdir -p "${output}" "${log_dir}"

if [[ -f "${output}/draw_convergence_ledger.csv" ]]; then
  echo "final convergence ledger already exists" >&2
  exit 2
fi
if pgrep -f "run_draw_convergence.py.*experiments/18_refit_draw_convergence/out" \
  >/dev/null; then
  echo "refit-draw convergence lane is already running" >&2
  exit 2
fi

printf "state\tpid\texit_status\nrunning\t%s\t\n" "$$" >"${status_file}"
set -o pipefail
date -u --iso-8601=seconds
/usr/bin/time -v .venv/bin/python \
  experiments/18_refit_draw_convergence/run_draw_convergence.py \
  --repetitions 100 \
  --n 150 \
  --draws 99 199 499 999 \
  --permutations 199 \
  --workers 8 \
  --seed 20260731 \
  --output-dir "${output}"
status=$?
date -u --iso-8601=seconds
echo "EXIT_STATUS=${status}"
printf "state\tpid\texit_status\ncompleted\t%s\t%s\n" \
  "$$" "${status}" >"${status_file}"
if [[ -d "${output}" ]]; then
  find "${output}" -maxdepth 1 -type f -print0 |
    sort -z |
    xargs -0 sha256sum
fi
exit "${status}"
