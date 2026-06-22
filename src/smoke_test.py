import os
import sys
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI


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


def _estimate_cost_usd(model: str, usage: UsageStats) -> float:
    # Phase 1 is intentionally minimal: we price only the selected cheap default model.
    if model != "gpt-5.4-mini":
        return -1.0

    input_price_per_million = 0.75
    output_price_per_million = 4.50

    input_cost = (usage.input_tokens / 1_000_000) * input_price_per_million
    output_cost = (usage.output_tokens / 1_000_000) * output_price_per_million
    return input_cost + output_cost


def main() -> int:
    load_dotenv()

    api_key = _read_required_env("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini").strip() or "gpt-5.4-mini"

    max_run_usd = float(os.getenv("MAX_RUN_USD", "0.25"))
    max_tokens_per_call = int(os.getenv("MAX_TOKENS_PER_CALL", "2500"))

    client = OpenAI(api_key=api_key)

    # Keep prompt tiny to minimize spend during environment checks.
    prompt = (
        "You are a strict API smoke test. "
        "Reply in one short sentence confirming availability."
    )

    response = client.responses.create(
        model=model,
        input=prompt,
        max_output_tokens=min(80, max_tokens_per_call),
    )

    usage_raw = getattr(response, "usage", None)
    input_tokens = int(getattr(usage_raw, "input_tokens", 0) or 0)
    output_tokens = int(getattr(usage_raw, "output_tokens", 0) or 0)
    total_tokens = int(getattr(usage_raw, "total_tokens", input_tokens + output_tokens) or 0)

    usage = UsageStats(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
    )

    print("Smoke test response:")
    print(response.output_text.strip())
    print("\nUsage:")
    print(f"- input_tokens: {usage.input_tokens}")
    print(f"- output_tokens: {usage.output_tokens}")
    print(f"- total_tokens: {usage.total_tokens}")

    estimated_cost = _estimate_cost_usd(model=model, usage=usage)
    if estimated_cost >= 0:
        print(f"- estimated_cost_usd: {estimated_cost:.6f}")
        if estimated_cost > max_run_usd:
            print(
                f"WARNING: Estimated run cost {estimated_cost:.6f} exceeds MAX_RUN_USD={max_run_usd:.2f}",
                file=sys.stderr,
            )
            return 2
    else:
        print("- estimated_cost_usd: not computed for this model")

    print("\nSmoke test completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
