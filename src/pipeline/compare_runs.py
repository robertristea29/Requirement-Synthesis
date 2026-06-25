"""
Phase 6 — Comparison Report

Reads every entry in data/runs/run_registry.jsonl, loads the
phase5_metrics.json for each run that has been evaluated, and
produces a side-by-side comparison table (terminal output + two
saved files: comparison_report.json and comparison_report.csv).

No API calls are made. This script is purely read-only.

Usage:
    python -m src.pipeline.compare_runs
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_registry(repo_root: Path) -> list[dict]:
    """Return all records from run_registry.jsonl as a list of dicts."""
    path = repo_root / "data" / "runs" / "run_registry.jsonl"
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def _load_phase5_metrics(run_dir: Path) -> dict | None:
    """Load phase5_metrics.json from a run folder, or None if missing."""
    p = run_dir / "phase5_metrics.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def _phase_label(phase_field: str) -> str:
    """Normalise the phase field from the registry to 'baseline' or 'pipeline'."""
    if "baseline" in phase_field:
        return "baseline"
    if "pipeline" in phase_field:
        return "pipeline"
    return phase_field


def _fmt(value: object, decimals: int = 4) -> str:
    """Format a metric value for terminal display."""
    if value is None:
        return "N/A"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:.{decimals}f}"
    return str(value)


# ---------------------------------------------------------------------------
# Core report builder
# ---------------------------------------------------------------------------

def build_report(repo_root: Path) -> dict:
    """
    Walk the run registry, load metrics for each run, and return a report dict
    with two keys:
      - 'rows':     one dict per run, all metrics included
      - 'averages': per-phase averages for the three primary metrics
    """
    registry = _load_registry(repo_root)
    rows: list[dict] = []

    for entry in registry:
        run_id = entry["run_id"]
        phase = _phase_label(entry.get("phase", ""))
        run_dir = repo_root / entry["output_dir"]
        metrics = _load_phase5_metrics(run_dir)

        base_row = {
            "run_id": run_id,
            "phase": phase,
            "date": entry.get("timestamp_utc", "")[:10],
            "model": entry.get("model", ""),
            "cost_usd": entry.get("estimated_cost_usd"),
        }

        if metrics is None:
            # Run exists in registry but phase5_metrics.json was never written.
            # This happens for very early runs made before Phase 5 was added.
            rows.append({
                **base_row,
                "recall": None,
                "precision": None,
                "contradiction_catch": None,
                "context_valid": None,
                "container_valid": None,
                "c4_consistent": None,
                "srs_structure": None,
                "overall_pass": None,
                "has_metrics": False,
            })
        else:
            s = metrics.get("summary", {})
            rows.append({
                **base_row,
                "recall": s.get("requirement_recall"),
                "precision": s.get("requirement_precision"),
                "contradiction_catch": s.get("contradiction_catch_rate"),
                "context_valid": s.get("context_diagram_valid"),
                "container_valid": s.get("container_diagram_valid"),
                "c4_consistent": s.get("c4_consistency_passed"),
                "srs_structure": s.get("srs_structure_passed"),
                "overall_pass": metrics.get("overall_pass"),
                "has_metrics": True,
            })

    # Compute per-phase averages for the three primary numeric metrics.
    def _avg(subset: list[dict], key: str) -> float | None:
        vals = [r[key] for r in subset if isinstance(r.get(key), (int, float))]
        return round(sum(vals) / len(vals), 4) if vals else None

    baselines = [r for r in rows if r["phase"] == "baseline"]
    pipelines = [r for r in rows if r["phase"] == "pipeline"]

    averages = {
        "baseline": {
            "count": len(baselines),
            "recall": _avg(baselines, "recall"),
            "precision": _avg(baselines, "precision"),
            "contradiction_catch": _avg(baselines, "contradiction_catch"),
        },
        "pipeline": {
            "count": len(pipelines),
            "recall": _avg(pipelines, "recall"),
            "precision": _avg(pipelines, "precision"),
            "contradiction_catch": _avg(pipelines, "contradiction_catch"),
        },
    }

    return {"rows": rows, "averages": averages}


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def print_table(report: dict) -> None:
    """Print a formatted comparison table to stdout."""
    rows = report["rows"]
    avgs = report["averages"]

    # Column layout: fixed-width fields so the table aligns in the terminal.
    col_widths = {
        "run_id":   36,
        "phase":    10,
        "date":     11,
        "recall":    7,
        "prec":      7,
        "contra":    7,
        "ctx":       5,
        "cnt":       5,
        "c4":        5,
        "srs":       5,
        "pass":      5,
        "cost":      9,
    }

    def row_line(r: dict) -> str:
        return (
            f"{r['run_id']:<{col_widths['run_id']}}"
            f"{r['phase']:<{col_widths['phase']}}"
            f"{r['date']:<{col_widths['date']}}"
            f"{_fmt(r['recall']):>{col_widths['recall']}}"
            f"{_fmt(r['precision']):>{col_widths['prec']}}"
            f"{_fmt(r['contradiction_catch']):>{col_widths['contra']}}"
            f"{_fmt(r['context_valid']):>{col_widths['ctx']}}"
            f"{_fmt(r['container_valid']):>{col_widths['cnt']}}"
            f"{_fmt(r['c4_consistent']):>{col_widths['c4']}}"
            f"{_fmt(r['srs_structure']):>{col_widths['srs']}}"
            f"{_fmt(r['overall_pass']):>{col_widths['pass']}}"
            f"{_fmt(r['cost_usd'], 5):>{col_widths['cost']}}"
        )

    header = (
        f"{'Run ID':<{col_widths['run_id']}}"
        f"{'Phase':<{col_widths['phase']}}"
        f"{'Date':<{col_widths['date']}}"
        f"{'Recall':>{col_widths['recall']}}"
        f"{'Prec':>{col_widths['prec']}}"
        f"{'Contra':>{col_widths['contra']}}"
        f"{'Ctx':>{col_widths['ctx']}}"
        f"{'Cnt':>{col_widths['cnt']}}"
        f"{'C4C':>{col_widths['c4']}}"
        f"{'SRS':>{col_widths['srs']}}"
        f"{'Pass':>{col_widths['pass']}}"
        f"{'Cost$':>{col_widths['cost']}}"
    )
    sep = "-" * len(header)

    print("\n" + sep)
    print(header)
    print(sep)
    for r in rows:
        print(row_line(r))
    print(sep)

    print("\nAVERAGES BY PHASE (evaluated runs only)")
    print(sep)
    for phase_name in ("baseline", "pipeline"):
        a = avgs[phase_name]
        print(
            f"  {phase_name:<10}  n={a['count']}"
            f"  recall={_fmt(a['recall'])}"
            f"  precision={_fmt(a['precision'])}"
            f"  contradiction_catch={_fmt(a['contradiction_catch'])}"
        )
    print(sep + "\n")

    # Print a short interpretation note.
    b = avgs["baseline"]
    p = avgs["pipeline"]
    if b["recall"] is not None and p["recall"] is not None:
        recall_diff = round((p["recall"] - b["recall"]) * 100, 1)
        prec_diff = round((p["precision"] - b["precision"]) * 100, 1) if b["precision"] is not None and p["precision"] is not None else None
        contra_diff = round((p["contradiction_catch"] - b["contradiction_catch"]) * 100, 1) if b["contradiction_catch"] is not None and p["contradiction_catch"] is not None else None

        print("INTERPRETATION")
        print(f"  Recall:               pipeline {'+' if recall_diff >= 0 else ''}{recall_diff}pp vs baseline")
        if prec_diff is not None:
            print(f"  Precision:            pipeline {'+' if prec_diff >= 0 else ''}{prec_diff}pp vs baseline")
        if contra_diff is not None:
            print(f"  Contradiction catch:  pipeline {'+' if contra_diff >= 0 else ''}{contra_diff}pp vs baseline")
        print()


def save_json(report: dict, out_path: Path) -> None:
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")


def save_csv(report: dict, out_path: Path) -> None:
    rows = report["rows"]
    if not rows:
        return
    fieldnames = [k for k in rows[0] if k != "has_metrics"]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    repo_root = _repo_root()
    report = build_report(repo_root)

    print_table(report)

    out_dir = repo_root / "data" / "runs"
    json_path = out_dir / "comparison_report.json"
    csv_path = out_dir / "comparison_report.csv"

    save_json(report, json_path)
    save_csv(report, csv_path)

    print(f"Saved: data/runs/comparison_report.json")
    print(f"Saved: data/runs/comparison_report.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
