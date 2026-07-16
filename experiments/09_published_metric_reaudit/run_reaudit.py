from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mbe_eval.reaudit import run_manifest_reaudit


def main() -> int:
    parser = argparse.ArgumentParser(description="Reaudit a published metric study from a frozen manifest.")
    parser.add_argument("manifest", help="Path to the study JSON manifest.")
    parser.add_argument("--data", help="Optional CSV override for the manifest data path.")
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--permutations", type=int, default=199)
    parser.add_argument("--bootstrap", type=int, default=0)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    report = run_manifest_reaudit(
        args.manifest,
        data_path=args.data,
        output_prefix=args.output_prefix,
        permutations=args.permutations,
        bootstrap=args.bootstrap,
        seed=args.seed,
    )
    print(report.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
