from __future__ import annotations

import json
import sys
from pathlib import Path

from src.validators.phase5_evaluator import evaluate_run


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python -m src.pipeline.evaluate_run <run_dir>")
        print("Example: python -m src.pipeline.evaluate_run data/runs/pipeline_20260624_131555")
        return 1

    run_dir = Path(sys.argv[1])
    if not run_dir.is_absolute():
        # Resolve relative path from the repo root inside the container.
        from src.validators.phase5_evaluator import _repo_root
        run_dir = _repo_root() / run_dir

    metrics = evaluate_run(run_dir)

    print(f"\nResults for: {run_dir.name}")
    print(json.dumps(metrics["summary"], indent=2))
    print(f"\nFull metrics written to: {run_dir / 'phase5_metrics.json'}")
    return 0 if metrics["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
