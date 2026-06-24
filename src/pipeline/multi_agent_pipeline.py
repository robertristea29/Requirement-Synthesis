from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from openai import OpenAI

from src.pipeline.dataset_loader import load_golden_dataset
from src.validators.phase5_evaluator import evaluate_run
from src.validators.srs_spec_validator import validate_srs_spec


class PipelineState(TypedDict):
    transcript: str
    srs: str
    critique: str
    context_diagram: str
    container_diagram: str
    usage_log: list[dict]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_prompt(filename: str) -> str:
    return (_repo_root() / "prompts" / filename).read_text(encoding="utf-8")


def _call_model(client: OpenAI, model: str, prompt: str, max_tokens: int) -> tuple[str, dict]:
    response = client.responses.create(
        model=model,
        input=prompt,
        max_output_tokens=max_tokens,
    )
    usage_raw = getattr(response, "usage", None)
    usage = {
        "input_tokens": int(getattr(usage_raw, "input_tokens", 0) or 0),
        "output_tokens": int(getattr(usage_raw, "output_tokens", 0) or 0),
        "total_tokens": int(getattr(usage_raw, "total_tokens", 0) or 0),
    }
    return (response.output_text or "").strip(), usage


def _extract_block(text: str, start: str, end: str) -> str:
    s = text.find(start)
    if s < 0:
        return text.strip()
    content_start = s + len(start)
    e = text.find(end, content_start)
    if e < 0:
        return text[content_start:].strip()
    return text[content_start:e].strip()


def _split_c4(mermaid_text: str) -> tuple[str, str]:
    content = mermaid_text.strip()
    ctx_idx = content.find("C4Context")
    con_idx = content.find("C4Container")
    if ctx_idx >= 0 and con_idx > ctx_idx:
        return content[ctx_idx:con_idx].strip(), content[con_idx:].strip()
    if ctx_idx >= 0:
        return content, ""
    if con_idx >= 0:
        return "", content
    return "", content


def _estimate_cost(model: str, usage_log: list[dict]) -> float:
    if model != "gpt-5.4-mini":
        return -1.0
    total_input = sum(u["input_tokens"] for u in usage_log)
    total_output = sum(u["output_tokens"] for u in usage_log)
    return (total_input / 1_000_000) * 0.75 + (total_output / 1_000_000) * 4.50


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _append_registry(entry: dict[str, Any]) -> None:
    reg = _repo_root() / "data" / "runs" / "run_registry.jsonl"
    reg.parent.mkdir(parents=True, exist_ok=True)
    with reg.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def build_pipeline(client: OpenAI, model: str, max_tokens: int) -> Any:

    def analyst(state: PipelineState) -> dict:
        prompt = _load_prompt("analyst_prompt.txt").replace(
            "{{STAKEHOLDER_TRANSCRIPT}}", state["transcript"]
        )
        text, usage = _call_model(client, model, prompt, max_tokens)
        srs = _extract_block(text, "BEGIN_SRS", "END_SRS")
        return {"srs": srs, "usage_log": state["usage_log"] + [{"agent": "analyst", **usage}]}

    def critic(state: PipelineState) -> dict:
        prompt = (
            _load_prompt("critic_prompt.txt")
            .replace("{{STAKEHOLDER_TRANSCRIPT}}", state["transcript"])
            .replace("{{SRS}}", state["srs"])
        )
        text, usage = _call_model(client, model, prompt, max_tokens)
        critique = _extract_block(text, "BEGIN_CRITIQUE", "END_CRITIQUE")
        return {"critique": critique, "usage_log": state["usage_log"] + [{"agent": "critic", **usage}]}

    def architect(state: PipelineState) -> dict:
        context_prompt = _load_prompt("architect_prompt.txt").replace("{{SRS}}", state["srs"])
        context_text, context_usage = _call_model(client, model, context_prompt, max_tokens)
        ctx = context_text[context_text.find("C4Context"):].strip() if "C4Context" in context_text else context_text.strip()

        container_prompt = (
            _load_prompt("architect_container_prompt.txt")
            .replace("{{SRS}}", state["srs"])
            .replace("{{C4CONTEXT}}", ctx)
        )
        container_text, container_usage = _call_model(client, model, container_prompt, max_tokens)
        con = container_text[container_text.find("C4Container"):].strip() if "C4Container" in container_text else container_text.strip()

        return {
            "context_diagram": ctx,
            "container_diagram": con,
            "usage_log": state["usage_log"] + [
                {"agent": "architect_context", **context_usage},
                {"agent": "architect_container", **container_usage},
            ],
        }

    graph = StateGraph(PipelineState)
    graph.add_node("analyst", analyst)
    graph.add_node("critic", critic)
    graph.add_node("architect", architect)
    graph.set_entry_point("analyst")
    graph.add_edge("analyst", "critic")
    graph.add_edge("critic", "architect")
    graph.add_edge("architect", END)
    return graph.compile()


def main() -> int:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY")

    model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini").strip() or "gpt-5.4-mini"
    max_tokens = int(os.getenv("MAX_TOKENS_PER_CALL", "2500"))
    max_run_usd = float(os.getenv("MAX_RUN_USD", "0.25"))

    dataset = load_golden_dataset()
    client = OpenAI(api_key=api_key)
    pipeline = build_pipeline(client, model, max_tokens)

    result = pipeline.invoke({
        "transcript": dataset.transcript,
        "srs": "",
        "critique": "",
        "context_diagram": "",
        "container_diagram": "",
        "usage_log": [],
    })

    srs_validation = validate_srs_spec(result["srs"])
    estimated_cost = _estimate_cost(model, result["usage_log"])

    run_id = datetime.now(timezone.utc).strftime("pipeline_%Y%m%d_%H%M%S")
    run_dir = _repo_root() / "data" / "runs" / run_id

    _write_text(run_dir / "srs.md", result["srs"])
    _write_text(run_dir / "critique.md", result["critique"])

    if result["context_diagram"]:
        _write_text(run_dir / "architecture_context.mmd", result["context_diagram"])
    if result["container_diagram"]:
        _write_text(run_dir / "architecture_container.mmd", result["container_diagram"])

    _write_text(run_dir / "srs_validation.json", json.dumps({
        "passed": srs_validation.passed,
        "missing_headings": srs_validation.missing_headings,
        "fr_count": srs_validation.fr_count,
        "nfr_count": srs_validation.nfr_count,
        "contradiction_count": srs_validation.contradiction_count,
    }, indent=2))

    metadata = {
        "run_id": run_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "agent_usage": result["usage_log"],
        "estimated_cost_usd": estimated_cost,
        "cost_guardrail_max_run_usd": max_run_usd,
        "parsed": {
            "srs_extracted": bool(result["srs"]),
            "critique_extracted": bool(result["critique"]),
            "context_diagram_extracted": bool(result["context_diagram"]),
            "container_diagram_extracted": bool(result["container_diagram"]),
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

    _append_registry({
        "run_id": run_id,
        "phase": "phase_4_pipeline",
        "reason": os.getenv("RUN_REASON", "manual_pipeline_run"),
        "timestamp_utc": metadata["timestamp_utc"],
        "model": model,
        "estimated_cost_usd": estimated_cost,
        "output_dir": str(run_dir.relative_to(_repo_root())),
    })

    print("Pipeline run completed.")
    print(f"run_dir: {run_dir}")
    for entry in result["usage_log"]:
        print(f"  {entry['agent']}: {entry['total_tokens']} tokens")
    if estimated_cost >= 0:
        print(f"estimated_cost_usd: {estimated_cost:.6f}")
        if estimated_cost > max_run_usd:
            print(f"WARNING: cost {estimated_cost:.6f} exceeded MAX_RUN_USD={max_run_usd:.2f}", file=sys.stderr)

    if not result["srs"] or not result["context_diagram"]:
        print("WARNING: SRS or diagrams not fully extracted.", file=sys.stderr)
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
