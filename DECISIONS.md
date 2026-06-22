# Decision Log

Purpose: Track project decisions, rationale, and changes.

## Current Decisions

- Date: 2026-06-12
- Area: Orchestration Framework
- Decision: LangGraph
- Rationale: Better deterministic control, state handling, and validation loops for evaluator-heavy pipelines.
- Owner: Project team
- Status: Accepted

- Date: 2026-06-12
- Area: Model Provider (Primary)
- Decision: OpenAI
- Rationale: Better structured-output workflow fit for strict pipeline contracts.
- Owner: Project team
- Status: Accepted

- Date: 2026-06-12
- Area: Cost Strategy
- Decision: Cheapest viable path for school project.
- Rationale: 2-week timeline and budget-first constraints.
- Owner: Project team
- Status: Accepted

- Date: 2026-06-12
- Area: Default Development Model
- Decision: gpt-5.4-mini
- Rationale: Lowest practical cost while preserving acceptable quality for MVP.
- Owner: Project team
- Status: Accepted

- Date: 2026-06-12
- Area: API Spend Cap
- Decision: Start with 5 USD credit, auto-recharge disabled.
- Rationale: Hard budget control and low-risk experimentation.
- Owner: Project team
- Status: Accepted

- Date: 2026-06-12
- Area: Runtime Environment
- Decision: Docker-first workflow; no host virtualenv required.
- Rationale: Simpler reproducibility with minimal setup overhead.
- Owner: Project team
- Status: Accepted

- Date: 2026-06-12
- Area: Docker Naming
- Decision: Compose project name set to requirement-synthesis, app container name set to requirement-synthesis-app.
- Rationale: Clearer visibility in Docker Desktop and logs.
- Owner: Project team
- Status: Accepted

- Date: 2026-06-12
- Area: Golden Dataset v1
- Decision: Synthetic dataset fixed at 10 requirements and 2 contradictions.
- Rationale: Enables deterministic and measurable evaluation against known ground truth.
- Owner: Project team
- Status: Accepted

- Date: 2026-06-12
- Area: Baseline Strategy (Phase 3)
- Decision: Implement single-shot baseline that generates SRS + Mermaid in one model call and logs token/cost metadata per run.
- Rationale: Establishes measurable reference point before multi-agent pipeline.
- Owner: Project team
- Status: Accepted

- Date: 2026-06-12
- Area: Golden Dataset Scenario
- Decision: Use Hospital Appointment and Triage Coordination scenario.
- Rationale: Provides realistic ambiguity and medically relevant contradiction patterns for Critic evaluation.
- Owner: Project team
- Status: Accepted

- Date: 2026-06-12
- Area: Run Governance
- Decision: Maintain `data/runs/run_registry.jsonl` with human-readable run reasons.
- Rationale: Preserve cost control and auditability of why each run was executed.
- Owner: Project team
- Status: Accepted

## Pending Decisions (Decide Later)

- Output contract format per agent (JSON schemas)
- Retry and failover policy
- Validation pass/fail thresholds

## Template For New Decision

- Date: YYYY-MM-DD
- Area: <topic>
- Decision: <what was decided>
- Rationale: <why>
- Owner: <who>
- Status: Proposed | Accepted | Superseded
- Supersedes: <optional link to previous decision>
