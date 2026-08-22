#!/usr/bin/env bash
set -u

cd "$(dirname "$0")/../.."
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1

experiment="experiments/16_causal_text_observed_design_power"
source_csv="experiments/15_causal_text_factorial_replication/kaggle_downloads/v1/mbe2_causal_text_factorial_replication.csv"
log_root="${experiment}/vm_campaign_artifacts"
status_file="${log_root}/complexity_status.tsv"
mkdir -p "${log_root}"

if pgrep -f "run_power.py.*out_sensitivity_degree[134]" >/dev/null; then
  echo "observed-design complexity sweep is already running" >&2
  exit 2
fi

printf "degree\tpid\texit_status\n" >"${status_file}"
for degree in 1 3 4; do
  output="${experiment}/out_sensitivity_degree${degree}"
  log="${log_root}/complexity_degree${degree}.log"
  if [[ -f "${output}/power_ledger.csv" ]]; then
    echo "refusing to overwrite completed degree ${degree} output" >&2
    exit 2
  fi
  (
    set -o pipefail
    date -u --iso-8601=seconds
    /usr/bin/time -v .venv/bin/python \
      "${experiment}/run_power.py" \
      "${source_csv}" \
      --output-dir "${output}" \
      --repetitions 100 \
      --refit-bootstrap 199 \
      --permutations 99 \
      --degree "${degree}" \
      --workers 8 \
      --seed 20260729
    status=$?
    date -u --iso-8601=seconds
    echo "EXIT_STATUS=${status}"
    if [[ -d "${output}" ]]; then
      find "${output}" -maxdepth 1 -type f -print0 |
        sort -z |
        xargs -0 sha256sum
    fi
    exit "${status}"
  ) >"${log}" 2>&1 &
  pid=$!
  status=0
  wait "${pid}" || status=$?
  printf "%s\t%s\t%s\n" "${degree}" "${pid}" "${status}" >>"${status_file}"
  if [[ "${status}" -ne 0 ]]; then
    exit "${status}"
  fi
done
