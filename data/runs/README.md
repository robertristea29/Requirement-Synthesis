# Run Artifacts Folder

This folder stores generated outputs and evaluation artifacts for each experiment run.

## Files generated per run folder

- raw_response.txt: Exact model output as returned.
- srs.md: Extracted SRS section.
- architecture.mmd: Primary Mermaid diagram for quick viewing.
- architecture_context.mmd: Context-level C4 diagram (if present).
- architecture_container.mmd: Container-level C4 diagram (if present).
- run_metadata.json: Model, usage, cost estimate, and parse status.
- srs_validation.json: SRS spec compliance checks (headings and ID counts).

## Run registry

- run_registry.jsonl: One JSON record per run with reason and summary.
- This file helps track why a run was executed and what it cost.
