# Requirement Synthesis

This repository is initialized with a minimal, Docker-first Phase 1 foundation.

## Phase 1 Status

Completed:

- Runtime setup with `Dockerfile` and `docker-compose.yml`.
- Dependency setup in `requirements.txt`.
- API and pricing smoke test in `src/smoke_test.py`.
- Secure Docker build context via `.dockerignore`.
- Initial project folders for upcoming phases:
	- `data/golden/`
	- `data/runs/`
	- `src/pipeline/`
	- `src/validators/`

## Phase 2 Status

Completed:

- Golden stakeholder transcript in `data/golden/stakeholder_transcript.md`.
- Ground truth annotations in `data/golden/ground_truth.json`.
- Dataset loader utility in `src/pipeline/dataset_loader.py`.

Golden dataset currently includes:

- 10 requirements
- 2 intentional contradictions

Current dataset scenario:

- Hospital Appointment and Triage Coordination

## Phase 3 Status

Completed:

- Single-shot baseline pipeline in `src/pipeline/baseline_single_shot.py`.
- Baseline prompt template in `prompts/baseline_single_shot_prompt.txt`.
- SRS specification reference in `prompts/srs_spec.md`.
- SRS spec validator in `src/validators/srs_spec_validator.py`.
- Baseline run artifacts written per run under `data/runs/baseline_YYYYMMDD_HHMMSS/`.

Each baseline run writes:

- `raw_response.txt` (full model output)
- `srs.md` (extracted SRS block)
- `architecture.mmd` (primary Mermaid diagram)
- `architecture_context.mmd` (context-level Mermaid diagram, if present)
- `architecture_container.mmd` (container-level Mermaid diagram, if present)
- `run_metadata.json` (model, token usage, estimated cost, parse status)
- `srs_validation.json` (SRS structure compliance results)

Run tracking:

- `data/runs/run_registry.jsonl` stores one record per run with reason and estimated cost.
- Detailed run-output file descriptions are in `data/runs/README.md`.
- Baseline prompt text is in `prompts/baseline_single_shot_prompt.txt`.

Manual command reference:

- `RUN_COMMANDS.md` contains the exact commands for smoke test and baseline runs.

## How to Run (Step by Step)

### Prerequisites

- Docker Desktop must be open and running (green engine icon in system tray).
- A `.env` file must exist at the project root containing your OpenAI API key.

### Step 1 — Open a terminal in the project folder

In VS Code: open the Terminal menu → New Terminal. Make sure the path shown ends with `Requirement-Synthesis`.

### Step 2 — Choose what to run

**Smoke test** — cheapest connectivity check. Sends one tiny prompt and prints token/cost. No output files are saved. Use this to confirm Docker and your API key work.

```powershell
docker compose run --rm app
```

**Baseline run** — the real experiment. Sends the hospital transcript to the model, extracts SRS + C4 diagrams, validates SRS structure, and saves all output files under `data/runs/`.

```powershell
docker compose run --rm app python -m src.pipeline.baseline_single_shot
```

**Multi-agent pipeline run** — 3-agent pipeline (Analyst → Critic → Architect). Rebuild image first if not done yet.

```powershell
docker compose build
docker compose run --rm app python -m src.pipeline.multi_agent_pipeline
```

### Step 3 — Find the output

After a baseline run completes, a new timestamped folder appears under `data/runs/`, for example `data/runs/baseline_20260613_122123/`.

Inside that folder:

| File | What it contains |
|---|---|
| `srs.md` | The generated Software Requirements Specification |
| `architecture_context.mmd` | C4 Level 1 diagram — paste into https://mermaid.live to view |
| `architecture_container.mmd` | C4 Level 2 diagram — paste into https://mermaid.live to view |
| `srs_validation.json` | Did the SRS follow the required structure? |
| `run_metadata.json` | Token usage, estimated cost, parse success flags |
| `raw_response.txt` | Full unprocessed model output |

### Step 4 — Check the run registry

`data/runs/run_registry.jsonl` — one line per run with reason and cost. Lets you track all spending.

---

## Current Roadmap

| Phase | What | Status |
|---|---|---|
| 1 | Docker + environment setup | Complete |
| 2 | Golden dataset (hospital scenario, 10 requirements, 2 contradictions) | Complete |
| 3 | Baseline single-shot pipeline + SRS spec validation | Complete |
| 4 | Multi-agent pipeline (Analyst → Critic → Architect) | Complete (not yet run) |
| 5 | Quantitative validators (recall, precision, contradiction catch, Mermaid syntax) | **Next** |
| 6 | Repeated experiments + comparison report | Pending |


FLOW

Your terminal command
      ↓
Docker spins up a container
      ↓
Python runs baseline_single_shot.py
      ↓
Reads .env for secrets and config
      ↓
dataset_loader.py reads the hospital transcript from data/golden/
      ↓
baseline_single_shot_prompt.txt is loaded and transcript is injected into it
      ↓
Full prompt is sent to OpenAI API
      ↓
Model returns SRS text + Mermaid text
      ↓
Text is parsed and split into separate pieces
      ↓
srs_spec_validator.py checks the SRS structure
      ↓
All files are saved into data/runs/baseline_TIMESTAMP/
      ↓
run_registry.jsonl gets one new line appended