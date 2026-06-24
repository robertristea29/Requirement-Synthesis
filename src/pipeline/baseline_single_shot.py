from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from src.pipeline.dataset_loader import load_golden_dataset
from src.validators.phase5_evaluator import evaluate_run
from src.validators.srs_spec_validator import validate_srs_spec


@dataclass
class UsageStats:
    input_tokens: int
    output_tokens: int
    total_tokens: int


def _read_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _estimate_cost_usd(model: str, usage: UsageStats) -> float:
    if model != "gpt-5.4-mini":
        return -1.0

    input_price_per_million = 0.75
    output_price_per_million = 4.50

    input_cost = (usage.input_tokens / 1_000_000) * input_price_per_million
    output_cost = (usage.output_tokens / 1_000_000) * output_price_per_million
    return input_cost + output_cost


def _extract_block(text: str, start_marker: str, end_marker: str) -> str:
    start_idx = text.find(start_marker)
    if start_idx < 0:
        return ""
    content_start = start_idx + len(start_marker)
    end_idx = text.find(end_marker, content_start)
    if end_idx < 0:
        return ""
    return text[content_start:end_idx].strip()


def _extract_mermaid_fenced_block(text: str) -> str:
    pattern = re.compile(r"```mermaid\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        return ""
    return match.group(1).strip()


def _extract_srs_fallback(text: str, mermaid_block: str) -> str:
    cleaned = text
    if mermaid_block:
        cleaned = re.sub(r"```mermaid\s*.*?\s*```", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = cleaned.strip()
    return cleaned


def _load_prompt_template() -> str:
    template_path = _repo_root() / "prompts" / "baseline_single_shot_prompt.txt"
    return template_path.read_text(encoding="utf-8")


def _build_prompt(transcript: str) -> str:
    template = _load_prompt_template()
    return template.replace("{{STAKEHOLDER_TRANSCRIPT}}", transcript)


def _split_c4_diagrams(mermaid_text: str) -> tuple[str, str]:
    content = mermaid_text.strip()
    if not content:
        return "", ""

    context_idx = content.find("C4Context")
    container_idx = content.find("C4Container")

    if context_idx >= 0 and container_idx > context_idx:
        context_part = content[context_idx:container_idx].strip()
        container_part = content[container_idx:].strip()
        return context_part, container_part

    if content.startswith("C4Context"):
        return content, ""

    if content.startswith("C4Container"):
        return "", content

    return "", content


def _extract_c4_from_plain_text(text: str) -> str:
    # Last-resort fallback when marker/fenced extraction fails.
    context_idx = text.find("C4Context")
    container_idx = text.find("C4Container")

    if context_idx < 0 and container_idx < 0:
        return ""

    first_idx_candidates = [idx for idx in (context_idx, container_idx) if idx >= 0]
    first_idx = min(first_idx_candidates)
    return text[first_idx:].strip()


def _append_run_registry(entry: dict[str, Any]) -> None:
    registry_path = _repo_root() / "data" / "runs" / "run_registry.jsonl"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    with registry_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry) + "\n")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    load_dotenv()

    api_key = _read_required_env("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini").strip() or "gpt-5.4-mini"

    max_run_usd = float(os.getenv("MAX_RUN_USD", "0.25"))
    max_tokens_per_call = int(os.getenv("MAX_TOKENS_PER_CALL", "2500"))

    dataset = load_golden_dataset()
    prompt = _build_prompt(dataset.transcript)

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        input=prompt,
        max_output_tokens=min(2200, max_tokens_per_call),
    )

    response_text = (response.output_text or "").strip()
    srs_text = _extract_block(response_text, "BEGIN_SRS", "END_SRS")
    mermaid_text = _extract_block(response_text, "BEGIN_MERMAID", "END_MERMAID")

    # Fallback parsing keeps baseline usable even when the model ignores strict markers.
    if not mermaid_text:
        mermaid_text = _extract_mermaid_fenced_block(response_text)
    if not mermaid_text:
        mermaid_text = _extract_c4_from_plain_text(response_text)
    if not srs_text:
        srs_text = _extract_srs_fallback(response_text, mermaid_text)

    context_diagram, container_diagram = _split_c4_diagrams(mermaid_text)

    usage_raw = getattr(response, "usage", None)
    usage = UsageStats(
        input_tokens=int(getattr(usage_raw, "input_tokens", 0) or 0),
        output_tokens=int(getattr(usage_raw, "output_tokens", 0) or 0),
        total_tokens=int(getattr(usage_raw, "total_tokens", 0) or 0),
    )

    estimated_cost = _estimate_cost_usd(model=model, usage=usage)

    run_id = datetime.now(timezone.utc).strftime("baseline_%Y%m%d_%H%M%S")
    run_dir = _repo_root() / "data" / "runs" / run_id

    _write_text(run_dir / "raw_response.txt", response_text)
    _write_text(run_dir / "srs.md", srs_text)

    srs_validation = validate_srs_spec(srs_text)
    _write_text(
        run_dir / "srs_validation.json",
        json.dumps(
            {
                "passed": srs_validation.passed,
                "missing_headings": srs_validation.missing_headings,
                "fr_count": srs_validation.fr_count,
                "nfr_count": srs_validation.nfr_count,
                "contradiction_count": srs_validation.contradiction_count,
            },
            indent=2,
        ),
    )

    # Write one file per C4 level. No combined/duplicate file.
    if context_diagram:
        _write_text(run_dir / "architecture_context.mmd", context_diagram)
    if container_diagram:
        _write_text(run_dir / "architecture_container.mmd", container_diagram)

    metadata = {
        "run_id": run_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "max_tokens_per_call": max_tokens_per_call,
        "usage": {
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "total_tokens": usage.total_tokens,
        },
        "estimated_cost_usd": estimated_cost,
        "cost_guardrail_max_run_usd": max_run_usd,
        "parsed": {
            "srs_extracted": bool(srs_text),
            "mermaid_extracted": bool(mermaid_text),
            "context_diagram_extracted": bool(context_diagram),
            "container_diagram_extracted": bool(container_diagram),
        },
        "srs_spec_validation": {
            "passed": srs_validation.passed,
            "missing_headings": srs_validation.missing_headings,
            "fr_count": srs_validation.fr_count,
            "nfr_count": srs_validation.nfr_count,
            "contradiction_count": srs_validation.contradiction_count,
        },
    }
    _write_text(run_dir / "run_metadata.json", json.dumps(metadata, indent=2))

    phase5_metrics = evaluate_run(run_dir)
    metadata["phase5_summary"] = phase5_metrics["summary"]
    _write_text(run_dir / "run_metadata.json", json.dumps(metadata, indent=2))

    run_reason = os.getenv("RUN_REASON", "manual_baseline_run")
    _append_run_registry(
        {
            "run_id": run_id,
            "phase": "phase_3_baseline",
            "reason": run_reason,
            "timestamp_utc": metadata["timestamp_utc"],
            "model": model,
            "estimated_cost_usd": estimated_cost,
            "output_dir": str(run_dir.relative_to(_repo_root())),
        }
    )

    print("Baseline run completed.")
    print(f"run_dir: {run_dir}")
    print(f"input_tokens: {usage.input_tokens}")
    print(f"output_tokens: {usage.output_tokens}")
    print(f"total_tokens: {usage.total_tokens}")
    if estimated_cost >= 0:
        print(f"estimated_cost_usd: {estimated_cost:.6f}")
        if estimated_cost > max_run_usd:
            print(
                f"WARNING: estimated run cost {estimated_cost:.6f} exceeded MAX_RUN_USD={max_run_usd:.2f}",
                file=sys.stderr,
            )
    else:
        print("estimated_cost_usd: not computed for this model")

    if not srs_text or (not context_diagram and not container_diagram):
        print(
            "WARNING: SRS or C4 diagrams not fully extracted. Check raw_response.txt.",
            file=sys.stderr,
        )
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
