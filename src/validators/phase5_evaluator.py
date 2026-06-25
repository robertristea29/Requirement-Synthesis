from __future__ import annotations

import argparse
import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from src.validators.srs_spec_validator import validate_srs_spec


def _repo_root() -> Path:
    # Resolve the repository root so the evaluator can read saved run artifacts
    # from any location without depending on the current working directory.
    return Path(__file__).resolve().parents[2]


def _read_text(path: Path) -> str:
    # Phase 5 must be able to validate old runs, so every helper tolerates
    # missing files and returns an empty string instead of failing immediately.
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    # Same rule as _read_text: missing artifacts should not crash evaluation.
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text.lower())).strip()


def _score_text(left: str, right: str) -> float:
    # Use a blended similarity score so requirement matching is tolerant of
    # wording changes while still preferring close semantic overlap.
    left_norm = _normalize(left)
    right_norm = _normalize(right)
    if not left_norm or not right_norm:
        return 0.0

    ratio = SequenceMatcher(None, left_norm, right_norm).ratio()
    left_tokens = set(left_norm.split())
    right_tokens = set(right_norm.split())
    union = left_tokens | right_tokens
    jaccard = len(left_tokens & right_tokens) / len(union) if union else 0.0
    return (ratio * 0.7) + (jaccard * 0.3)


def _extract_requirement_items(srs_text: str) -> list[dict[str, str]]:
    # Pull FR/NFR lines out of the generated SRS so we can compare them against
    # the golden requirements stored in the dataset.
    # Accept both "FR-1: text" (pipeline format) and "FR-1 text" (baseline format).
    pattern = re.compile(r"(?m)^(?:-\s*)?((?:FR|NFR)-\d+)[: ]\s*(.+?)\s*$")
    items: list[dict[str, str]] = []
    for match in pattern.finditer(srs_text):
        requirement_id = match.group(1).strip()
        requirement_text = match.group(2).strip()
        items.append(
            {
                "id": requirement_id,
                "kind": "functional" if requirement_id.startswith("FR-") else "non_functional",
                "text": requirement_text,
            }
        )
    return items


def _matches_statement(statement: str, critique_text: str, threshold: float = 0.45) -> bool:
    # A contradiction is considered caught if the critique mentions both source
    # statements strongly enough or verbatim.
    statement_norm = _normalize(statement)
    critique_norm = _normalize(critique_text)
    return statement_norm in critique_norm or _score_text(statement, critique_text) >= threshold


def _evaluate_requirements(ground_truth: list[dict[str, Any]], srs_text: str) -> dict[str, Any]:
    # Compare every ground-truth requirement against the extracted SRS items and
    # compute recall/precision style metrics for the run.
    extracted_items = _extract_requirement_items(srs_text)
    requirement_threshold = 0.45

    ground_truth_details: list[dict[str, Any]] = []
    matched_ground_truth = 0
    for gt in ground_truth:
        gt_kind = gt.get("type", "")
        candidates = [item for item in extracted_items if item["kind"] == gt_kind]
        scored_candidates = [
            {"id": item["id"], "score": _score_text(gt.get("text", ""), item["text"])}
            for item in candidates
        ]
        best_score = max((candidate["score"] for candidate in scored_candidates), default=0.0)
        matched_ids = [candidate["id"] for candidate in scored_candidates if candidate["score"] >= requirement_threshold]
        covered = best_score >= requirement_threshold
        if covered:
            matched_ground_truth += 1
        ground_truth_details.append(
            {
                "id": gt.get("id"),
                "type": gt_kind,
                "covered": covered,
                "best_score": round(best_score, 4),
                "matched_extracted_ids": matched_ids,
            }
        )

    extracted_details: list[dict[str, Any]] = []
    matched_extracted = 0
    for item in extracted_items:
        candidates = [gt for gt in ground_truth if gt.get("type", "") == item["kind"]]
        scored_candidates = [
            {"id": gt.get("id"), "score": _score_text(item["text"], gt.get("text", ""))}
            for gt in candidates
        ]
        best_score = max((candidate["score"] for candidate in scored_candidates), default=0.0)
        matched_ids = [candidate["id"] for candidate in scored_candidates if candidate["score"] >= requirement_threshold]
        relevant = best_score >= requirement_threshold
        if relevant:
            matched_extracted += 1
        extracted_details.append(
            {
                "id": item["id"],
                "kind": item["kind"],
                "relevant": relevant,
                "best_score": round(best_score, 4),
                "matched_ground_truth_ids": matched_ids,
            }
        )

    ground_truth_total = len(ground_truth)
    extracted_total = len(extracted_items)
    recall = matched_ground_truth / ground_truth_total if ground_truth_total else 0.0
    precision = matched_extracted / extracted_total if extracted_total else 0.0

    return {
        "ground_truth_total": ground_truth_total,
        "extracted_total": extracted_total,
        "matched_ground_truth": matched_ground_truth,
        "matched_extracted": matched_extracted,
        "recall": round(recall, 4),
        "precision": round(precision, 4),
        "ground_truth_details": ground_truth_details,
        "extracted_details": extracted_details,
    }


def _evaluate_contradictions(ground_truth: list[dict[str, Any]], critique_text: str) -> dict[str, Any]:
    # This checks whether the Critic actually surfaced both sides of each
    # planted contradiction from the transcript.
    contradiction_details: list[dict[str, Any]] = []
    caught = 0

    for contradiction in ground_truth:
        statement_a = contradiction.get("statement_a", "")
        statement_b = contradiction.get("statement_b", "")
        statement_a_present = _matches_statement(statement_a, critique_text)
        statement_b_present = _matches_statement(statement_b, critique_text)
        contradiction_caught = statement_a_present and statement_b_present
        if contradiction_caught:
            caught += 1
        contradiction_details.append(
            {
                "id": contradiction.get("id"),
                "category": contradiction.get("category"),
                "statement_a_present": statement_a_present,
                "statement_b_present": statement_b_present,
                "caught": contradiction_caught,
            }
        )

    total = len(ground_truth)
    catch_rate = caught / total if total else 0.0
    return {
        "ground_truth_total": total,
        "caught": caught,
        "catch_rate": round(catch_rate, 4),
        "details": contradiction_details,
    }


def _validate_mermaid_diagram(diagram_text: str, expected_kind: str) -> dict[str, Any]:
    # Lightweight Mermaid validation: confirm the right diagram type exists and
    # that the expected C4 tokens are present.
    clean_text = diagram_text.strip()
    issues: list[str] = []

    if not clean_text:
        issues.append("diagram text is missing")
    elif not clean_text.startswith(expected_kind):
        issues.append(f"diagram does not start with {expected_kind}")

    if expected_kind == "C4Context":
        required_tokens = ["title", "Person(", "System(", "System_Ext(", "Rel("]
        forbidden_tokens = ["C4Container", "ENDC4"]
    else:
        required_tokens = ["title", "System_Boundary(", "Container(", "Rel("]
        forbidden_tokens = ["C4Context", "ENDC4"]

    for token in required_tokens:
        if token not in clean_text:
            issues.append(f"missing required token: {token}")

    for token in forbidden_tokens:
        if token in clean_text:
            issues.append(f"contains forbidden token: {token}")

    entity_counts = {
        "persons": len(re.findall(r"\bPerson\(", clean_text)),
        "systems": len(re.findall(r"\bSystem\(", clean_text)),
        "system_exts": len(re.findall(r"\bSystem_Ext\(", clean_text)),
        "containers": len(re.findall(r"\bContainer\(", clean_text)),
        "boundaries": len(re.findall(r"\bSystem_Boundary\(", clean_text)),
        "relations": len(re.findall(r"\bRel\(", clean_text)),
    }

    valid = not issues
    return {
        "diagram_kind": expected_kind,
        "valid": valid,
        "issues": issues,
        "entity_counts": entity_counts,
    }


def _extract_labels(text: str, pattern: str) -> list[str]:
    return re.findall(pattern, text)


def _evaluate_c4_consistency(context_text: str, container_text: str) -> dict[str, Any]:
    # The container diagram should reuse the same external system names that
    # appeared in the context diagram.
    context_external_systems = set(
        _extract_labels(context_text, r'System_Ext\(\s*[^,]+,\s*"([^"]+)"')
    )
    container_external_systems = set(
        _extract_labels(container_text, r'System_Ext\(\s*[^,]+,\s*"([^"]+)"')
    )
    context_systems = set(_extract_labels(context_text, r'System\(\s*[^,]+,\s*"([^"]+)"'))
    container_boundaries = set(
        _extract_labels(container_text, r'System_Boundary\(\s*[^,]+,\s*"([^"]+)"')
    )

    missing_in_container = sorted(context_external_systems - container_external_systems)
    extra_in_container = sorted(container_external_systems - context_external_systems)
    main_system_alignment = sorted(context_systems & container_boundaries)

    passed = not missing_in_container and not extra_in_container and bool(main_system_alignment)

    return {
        "passed": passed,
        "context_external_systems": sorted(context_external_systems),
        "container_external_systems": sorted(container_external_systems),
        "missing_in_container": missing_in_container,
        "extra_in_container": extra_in_container,
        "main_system_alignment": main_system_alignment,
    }


def evaluate_run(run_dir: str | Path, ground_truth_path: str | Path | None = None) -> dict[str, Any]:
    # Main entry point: load an existing run folder, score it, and write the
    # phase5_metrics.json file back into that same folder.
    run_path = Path(run_dir)
    repo_root = _repo_root()
    truth_path = Path(ground_truth_path) if ground_truth_path else repo_root / "data" / "golden" / "ground_truth.json"

    ground_truth = _read_json(truth_path)
    srs_text = _read_text(run_path / "srs.md")
    critique_text = _read_text(run_path / "critique.md")
    # Strip legacy ENDC4 artifacts that appeared in early runs before the
    # diagram extraction bug was fixed.  Stripping them here means old run
    # folders are scored fairly without manual file edits.
    context_text = re.sub(r"ENDC4\w*", "", _read_text(run_path / "architecture_context.mmd")).strip()
    container_text = re.sub(r"ENDC4\w*", "", _read_text(run_path / "architecture_container.mmd")).strip()
    run_metadata = _read_json(run_path / "run_metadata.json")
    srs_validation_path = run_path / "srs_validation.json"
    srs_validation = _read_json(srs_validation_path) if srs_validation_path.exists() else {}

    if not srs_validation and srs_text:
        # Older runs may not have an srs_validation.json file yet. In that case,
        # recompute the SRS structure checks directly from the saved SRS text.
        validation = validate_srs_spec(srs_text)
        srs_validation = {
            "passed": validation.passed,
            "missing_headings": validation.missing_headings,
            "fr_count": validation.fr_count,
            "nfr_count": validation.nfr_count,
            "contradiction_count": validation.contradiction_count,
        }

    requirements = _evaluate_requirements(ground_truth.get("requirements", []), srs_text)
    contradictions = _evaluate_contradictions(ground_truth.get("contradictions", []), critique_text)
    mermaid_context = _validate_mermaid_diagram(context_text, "C4Context")
    mermaid_container = _validate_mermaid_diagram(container_text, "C4Container")
    c4_consistency = _evaluate_c4_consistency(context_text, container_text)

    summary = {
        "requirement_recall": requirements["recall"],
        "requirement_precision": requirements["precision"],
        "contradiction_catch_rate": contradictions["catch_rate"],
        "context_diagram_valid": mermaid_context["valid"],
        "container_diagram_valid": mermaid_container["valid"],
        "c4_consistency_passed": c4_consistency["passed"],
        "srs_structure_passed": bool(srs_validation.get("passed", False)),
    }

    overall_pass = all(
        [
            summary["srs_structure_passed"],
            summary["context_diagram_valid"],
            summary["container_diagram_valid"],
            summary["c4_consistency_passed"],
        ]
    )

    metrics = {
        "run_id": run_metadata.get("run_id", run_path.name),
        "timestamp_utc": run_metadata.get("timestamp_utc"),
        "overall_pass": overall_pass,
        "summary": summary,
        "requirements": requirements,
        "contradictions": contradictions,
        "mermaid": {
            "context": mermaid_context,
            "container": mermaid_container,
        },
        "c4_consistency": c4_consistency,
        "srs_validation": srs_validation,
    }

    (run_path / "phase5_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


def _latest_run_dir() -> Path:
    # Convenience helper for manual use: if no run path is provided, evaluate
    # the newest run folder that already exists on disk.
    runs_root = _repo_root() / "data" / "runs"
    candidates = [path for path in runs_root.iterdir() if path.is_dir() and (path / "run_metadata.json").exists()]
    if not candidates:
        raise FileNotFoundError("No run folders found in data/runs")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def main() -> int:
    # Command-line entry point for manual validation of any saved run folder.
    parser = argparse.ArgumentParser(description="Evaluate a run folder with Phase 5 validators")
    parser.add_argument("run_dir", nargs="?", help="Path to a run folder. Defaults to the latest run folder.")
    args = parser.parse_args()

    run_dir = Path(args.run_dir) if args.run_dir else _latest_run_dir()
    metrics = evaluate_run(run_dir)
    print(json.dumps(metrics["summary"], indent=2))
    print(f"phase5_metrics_written_to: {run_dir / 'phase5_metrics.json'}")
    return 0 if metrics["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())