# Requirement Synthesis

A multi-agent AI pipeline for synthesising software requirements from messy stakeholder input. Built as a FONTYS Semester 6 individual research project.

---

## Project Overview

The system ingests a raw stakeholder transcript (emails, meeting notes, Slack threads) and produces a structured Software Requirements Specification (SRS) and C4 architecture diagrams. Two approaches are compared:

- **Baseline** — a single OpenAI API call that does everything at once.
- **Multi-agent pipeline** — three specialised AI agents (Analyst, Critic, Architect) that run in sequence, each focused on one task. This is the research contribution.

The final output is a quantitative comparison: does the multi-agent pipeline produce more complete, more precise, and more contradiction-aware requirements than the single-shot baseline?

---

## Roadmap

| Phase | What | Status |
|---|---|---|
| 1 | Docker + environment setup | Complete |
| 2 | Golden dataset (hospital scenario, 10 requirements, 2 contradictions) | Complete |
| 3 | Baseline single-shot pipeline + SRS spec validation | Complete |
| 4 | Multi-agent pipeline (Analyst → Critic → Architect) | Complete |
| 5 | Quantitative validators (recall, precision, contradiction catch, Mermaid syntax) | Complete |
| 6 | Comparison report across all runs | Complete |

---

## How the Multi-Agent Pipeline Works

### The Problem: Why Multiple Agents?

A single LLM call asked to do everything at once tends to miss contradictions, hallucinate requirements, and produce diagrams inconsistent with the SRS. Splitting the work into focused roles produces better output — this is the central hypothesis of the project.

### LangGraph and StateGraph

[LangGraph](https://github.com/langchain-ai/langgraph) is the orchestration library used to connect the three agents. It provides a `StateGraph` — a directed graph where:

- Each **node** is a Python function (one agent).
- Each **edge** defines which node runs next.
- A single **shared state object** is passed from node to node.

When you call `graph.invoke(initial_state)`, LangGraph runs the nodes in the defined order, passing the updated state forward after each one. There is no parallelism — the agents run sequentially: Analyst → Critic → Architect.

### The Shared State (TypedDict)

Python's `TypedDict` (from the `typing` module) is used to define the shape of the shared state. A `TypedDict` is a regular Python dict that has a declared structure — each key has a fixed type. This lets the code be clear about what fields exist without defining a class.

The pipeline state looks like this:

```python
class PipelineState(TypedDict):
    transcript: str        # the raw stakeholder input
    srs: str               # written by the Analyst agent
    critique: str          # written by the Critic agent
    context_diagram: str   # written by the Architect agent (C4 Level 1)
    container_diagram: str # written by the Architect agent (C4 Level 2)
    usage_log: list        # token usage from every API call
```

Every agent receives the entire state and returns only the fields it changed. LangGraph merges the returned fields back into the state before passing it to the next agent.

### The Three Agents and How They Communicate

```
Stakeholder Transcript
        │
        ▼
┌───────────────────┐
│   Analyst Agent   │  Reads: transcript
│                   │  Writes: srs
│  Prompt:          │
│  analyst_prompt   │
└────────┬──────────┘
         │  srs is now in state
         ▼
┌───────────────────┐
│   Critic Agent    │  Reads: transcript + srs
│                   │  Writes: critique
│  Prompt:          │
│  critic_prompt    │
└────────┬──────────┘
         │  critique is now in state
         ▼
┌───────────────────┐
│  Architect Agent  │  Reads: srs (call 1), srs + context_diagram (call 2)
│                   │  Writes: context_diagram, container_diagram
│  Prompts:         │
│  architect_prompt │
│  architect_       │
│  container_prompt │
└───────────────────┘
        │
        ▼
   Artifacts saved to data/runs/pipeline_TIMESTAMP/
```

**Analyst** — reads the raw transcript and writes a structured SRS. It identifies functional requirements (FR-x), non-functional requirements (NFR-x), and contradictions (C-x). It does not see ground truth. Its only job is to read messy input and produce structured output.

**Critic** — reads both the original transcript AND the Analyst's SRS. It checks for missing requirements the Analyst skipped, hallucinated requirements the Analyst invented, and contradictions between statements. It writes a critique document with an overall verdict: APPROVED or NEEDS REVISION. In this implementation the Critic's verdict is recorded but does not block the pipeline — the Architect always runs regardless.

**Architect** — reads the Analyst's SRS and produces two C4 architecture diagrams. It makes two separate API calls: first it generates the C4Context diagram (the big-picture view: users, the system, external services), then it generates the C4Container diagram (what is inside the system: services, databases, APIs). The second call receives the first diagram so naming stays consistent between levels.

Agents communicate **only through the shared state dict**. No agent calls another agent directly. LangGraph handles the passing of state between them.

---

## Repository Structure

```
Requirement-Synthesis/
├── data/
│   ├── golden/
│   │   ├── stakeholder_transcript.md   # synthetic messy hospital input
│   │   └── ground_truth.json           # 10 requirements + 2 contradictions (never shown to AI)
│   └── runs/
│       ├── run_registry.jsonl          # one line per run: id, phase, cost, timestamp
│       ├── comparison_report.json      # Phase 6 output: all runs compared
│       ├── comparison_report.csv       # same data as CSV for spreadsheets/reports
│       └── <run_folder>/               # one folder per run, e.g. pipeline_20260624_164625/
│           ├── srs.md
│           ├── critique.md             # pipeline runs only
│           ├── architecture_context.mmd
│           ├── architecture_container.mmd
│           ├── srs_validation.json
│           ├── run_metadata.json
│           └── phase5_metrics.json
├── prompts/
│   ├── baseline_single_shot_prompt.txt
│   ├── analyst_prompt.txt
│   ├── critic_prompt.txt
│   ├── architect_prompt.txt
│   ├── architect_container_prompt.txt
│   └── srs_spec.md
├── src/
│   ├── pipeline/
│   │   ├── dataset_loader.py           # reads transcript + ground_truth
│   │   ├── baseline_single_shot.py     # Phase 3: single API call baseline
│   │   ├── multi_agent_pipeline.py     # Phase 4: LangGraph 3-agent pipeline
│   │   ├── evaluate_run.py             # CLI: score any existing run folder
│   │   └── compare_runs.py             # Phase 6: side-by-side comparison table
│   └── validators/
│       ├── srs_spec_validator.py       # checks SRS heading/ID structure
│       └── phase5_evaluator.py         # scores recall, precision, C4, contradictions
├── .env                                # API key + config (never committed)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## How to Run

### Prerequisites

- Docker Desktop must be open and running (green icon in system tray).
- A `.env` file must exist at the project root with your OpenAI API key.

### Available Commands

**Smoke test** — sends one tiny prompt to verify Docker and the API key work. No output files saved.

```powershell
docker compose run --rm app
```

**Baseline run** — single API call. Produces SRS + C4 diagrams + metrics.

```powershell
docker compose run --rm app python -m src.pipeline.baseline_single_shot
```

**Multi-agent pipeline run** — runs the 3-agent LangGraph pipeline.

```powershell
docker compose build
docker compose run --rm app python -m src.pipeline.multi_agent_pipeline
```

**Evaluate an existing run folder** — scores any run without making API calls.

```powershell
docker compose run --rm app python -m src.pipeline.evaluate_run data/runs/pipeline_20260624_164625
```

**Comparison report** — reads all evaluated runs and prints a side-by-side table.

```powershell
docker compose run --rm app python -m src.pipeline.compare_runs
```

### Changing the Model

The model is set in `.env`:

```
OPENAI_MODEL=gpt-5.4-mini
```

Change that value and save. No rebuild needed — the `.env` file is injected at container startup, not baked into the image. The new model is used on the very next run.

---

## Output Files Per Run

| File | What it contains |
|---|---|
| `srs.md` | Generated Software Requirements Specification |
| `critique.md` | Critic agent's review (pipeline runs only) |
| `architecture_context.mmd` | C4 Level 1 diagram — paste into https://mermaid.live |
| `architecture_container.mmd` | C4 Level 2 diagram — paste into https://mermaid.live |
| `srs_validation.json` | Did the SRS follow the required heading/ID structure? |
| `run_metadata.json` | Token usage, estimated cost, parse success flags |
| `raw_response.txt` | Full unprocessed model output (baseline only) |
| `phase5_metrics.json` | Recall, precision, contradiction catch, C4 validity scores |

---

## Evaluation and Metrics

Every run is automatically scored at the end against `data/golden/ground_truth.json`. The ground truth is never shown to the AI agents — it is only used for scoring after the fact.

### What the Metrics Mean

| Metric | Question it answers |
|---|---|
| `recall` | Did the AI cover every real requirement? 1.0 = all 10 found. |
| `precision` | Of everything the AI extracted, how much maps to something real? Low precision means the AI invented extra requirements. |
| `contradiction_catch_rate` | Of the 2 planted contradictions, how many did the Critic flag? Only meaningful for pipeline runs. |
| `context_diagram_valid` | Does the C4Context diagram parse correctly? |
| `container_diagram_valid` | Does the C4Container diagram parse correctly? |
| `c4_consistency_passed` | Do the external systems named in the context diagram also appear in the container diagram? |
| `srs_structure_passed` | Does the SRS contain all required headings and use FR-x / NFR-x / C-x IDs? |

Requirement matching uses **fuzzy similarity** (SequenceMatcher + Jaccard). A match is accepted if the blended score exceeds 0.45. This tolerates wording differences while still requiring meaningful overlap.

### Baseline vs Pipeline Comparison (Phase 6)

`src/pipeline/compare_runs.py` reads every entry in `run_registry.jsonl`, loads the `phase5_metrics.json` from each run folder that has been evaluated, and produces a side-by-side comparison table. No API calls are made — it is purely read-only.

```powershell
docker compose run --rm app python -m src.pipeline.compare_runs
```

**What the table columns mean:**

| Column | Meaning |
|---|---|
| `Recall` | Fraction of ground-truth requirements the AI covered |
| `Prec` | Fraction of the AI's extracted requirements that map to something real |
| `Contra` | Fraction of planted contradictions the Critic caught (always 0 for baselines) |
| `Ctx` | C4Context diagram syntactically valid (yes/no) |
| `Cnt` | C4Container diagram syntactically valid (yes/no) |
| `C4C` | External systems consistent between context and container diagrams (yes/no) |
| `SRS` | SRS headings and FR-x/NFR-x/C-x IDs present (yes/no) |
| `Pass` | Overall pass — all checks above passed |
| `Cost$` | Estimated USD cost of that run |

After the table, the script prints an interpretation block showing the percentage-point difference between average pipeline and average baseline on the three primary metrics. This is the evidence you cite directly in your report.

**Saved outputs:**
- `data/runs/comparison_report.json` — full structured report, machine-readable
- `data/runs/comparison_report.csv` — same data as a spreadsheet for thesis appendices

---

## Execution Flow (Baseline)

```
Terminal command
      │
      ▼
Docker spins up container
      │
      ▼
baseline_single_shot.py starts
      │
      ▼
Reads .env → API key, model, cost limits
      │
      ▼
dataset_loader.py reads stakeholder_transcript.md
      │
      ▼
Prompt template loaded, transcript injected
      │
      ▼
Single API call to OpenAI
      │
      ▼
Response parsed: SRS block + Mermaid block extracted
      │
      ▼
srs_spec_validator.py checks heading and ID structure
      │
      ▼
phase5_evaluator.py scores recall, precision, C4, contradictions
      │
      ▼
All files written to data/runs/baseline_TIMESTAMP/
      │
      ▼
One line appended to run_registry.jsonl
```

# Baseline runs (no critique.md, so contradiction catch will always be 0)
docker compose run --rm app python -m src.pipeline.evaluate_run data/runs/baseline_20260613_122123


# Comparison command
docker compose run --rm app python -m src.pipeline.compare_runs