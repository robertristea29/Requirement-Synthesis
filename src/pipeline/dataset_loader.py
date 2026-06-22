from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GoldenDataset:
    transcript: str
    ground_truth: dict


def _repo_root() -> Path:
    # src/pipeline/dataset_loader.py -> repo root is two levels up from src.
    return Path(__file__).resolve().parents[2]


def load_golden_dataset(base_path: Path | None = None) -> GoldenDataset:
    root = base_path or _repo_root()
    transcript_path = root / "data" / "golden" / "stakeholder_transcript.md"
    truth_path = root / "data" / "golden" / "ground_truth.json"

    transcript = transcript_path.read_text(encoding="utf-8")
    ground_truth = json.loads(truth_path.read_text(encoding="utf-8"))

    return GoldenDataset(transcript=transcript, ground_truth=ground_truth)


if __name__ == "__main__":
    dataset = load_golden_dataset()
    print("Golden dataset loaded.")
    print(f"Transcript length: {len(dataset.transcript)} characters")
    print(f"Requirements: {len(dataset.ground_truth.get('requirements', []))}")
    print(f"Contradictions: {len(dataset.ground_truth.get('contradictions', []))}")
