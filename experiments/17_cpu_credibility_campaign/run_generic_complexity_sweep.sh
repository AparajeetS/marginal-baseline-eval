#!/usr/bin/env bash
set -u

cd "$(dirname "$0")/../.."
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1

out_root="experiments/17_cpu_credibility_campaign/out"
log_root="experiments/17_cpu_credibility_campaign/vm_campaign_artifacts/logs"
status_file="${out_root}/generic_complexity_status.tsv"
mkdir -p "${out_root}" "${log_root}"

if pgrep -f "run_monte_carlo.py.*complexity_generic_" >/dev/null; then
  echo "generic complexity sweep is already running" >&2
  exit 2
fi

printf "label\tpid\texit_status\n" >"${status_file}"
declare -a labels=()
declare -a pids=()

for nuisance in polynomial_ridge polynomial_ridge_interactions; do
  for degree in 1 3 4; do
    label="${nuisance}_degree${degree}"
    output="${out_root}/complexity_generic_${label}"
    log="${log_root}/complexity_generic_${label}.log"
    labels+=("${label}")
    (
      set -o pipefail
      date -u --iso-8601=seconds
      /usr/bin/time -v .venv/bin/python \
        experiments/08_protocol_calibration/run_monte_carlo.py \
        --sample-sizes 100,200,400,800 \
        --degrees "${degree}" \
        --repetitions 100 \
        --permutations 499 \
        --bootstrap 499 \
        --nuisance-model "${nuisance}" \
        --seed 20260716 \
        --output-dir "${output}"
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
    pids+=("$!")
  done
done

overall=0
for index in "${!pids[@]}"; do
  status=0
  wait "${pids[$index]}" || status=$?
  printf "%s\t%s\t%s\n" \
    "${labels[$index]}" "${pids[$index]}" "${status}" >>"${status_file}"
  if [[ "${status}" -ne 0 ]]; then
    overall=1
  fi
done

exit "${overall}"
