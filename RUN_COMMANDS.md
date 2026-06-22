# Manual Run Commands

Use these commands from project root.

## 1) Smoke test (cheap connectivity check)

```powershell
docker compose run --rm app
```

## 2) Baseline single-shot run

```powershell
docker compose run --rm app python -m src.pipeline.baseline_single_shot
```

## 3) Baseline run with reason label (recommended)

```powershell
$env:RUN_REASON="hospital_scenario_first_baseline"; docker compose run --rm app python -m src.pipeline.baseline_single_shot
```

## 4) Inspect latest runs

- Check folders in `data/runs/`
- Check run registry in `data/runs/run_registry.jsonl`
