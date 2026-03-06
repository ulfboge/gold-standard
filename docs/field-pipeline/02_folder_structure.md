## Folder Structure and Key Files

This page describes the **recommended folder layout** and key files for the field data pipeline. It is adapted from section 2 of `field_pipeline/PROCESS_MANUAL.md`.

---

### Repository‑level structure

At the repository root (`gold-standard/`), the pipeline assumes:

- `data/`
  - `incoming/`
    - `project.gpkg` – main GeoPackage used as CLI input (configurable in `pipeline.yaml`).
      - In the default workflow, this is synced from Mergin Maps.
      - In the optional PostGIS-compatible backend workflow, this is exported from the database before running the CLI.
    - `attachments/` – photos and other files linked from attributes (optional but recommended).
  - `processed/`
    - `run_<timestamp>/` – per‑run copies of `project.gpkg` and `attachments/` created by `ingest`.
    - `report.md` – default report output (can be overridden via CLI options).
  - `context/`
    - `admin_boundaries.gpkg` – optional admin boundaries.
    - `protected_areas.gpkg` – optional protected areas.
    - `land_cover.gpkg` – optional land‑cover dataset.

- `field_pipeline/`
  - `README.md` – quickstart and developer notes.
  - `PROCESS_MANUAL.md` – full manual (the source for these docs pages).
  - `requirements.txt` – Python dependencies for the pipeline.
  - `config/pipeline.yaml` – **main configuration file** (paths, rules, enrichment, AI).
  - `sql/` – optional SQL scripts for a PostGIS-compatible editing workflow and export handoff.
  - `field_pipeline/` (Python package):
    - `cli.py` – Typer‑based CLI entry‑point (all commands exposed here).
    - `config.py` – configuration loader (YAML → dataclasses).
    - `logging_config.py` – minimal console logging setup.
    - `ingest.py` – ingest logic.
    - `validate.py` – validation logic.
    - `enrich.py` – enrichment logic (spatial joins).
    - `summarize.py` – summary statistics.
    - `export.py` – exports to CSV/GeoJSON.
    - `report.py` – Markdown report generation.
    - `ai.py` – optional AI text drafting stub.
  - `tests/`
    - `test_cli.py` – pytest placeholder (can be extended with more tests).

This structure keeps:

- Raw data (`data/incoming/`) separate from processed data (`data/processed/`).
- Pipeline implementation (`field_pipeline/`) and configuration (`config/pipeline.yaml`) together.
- Tests (`field_pipeline/tests/`) ready for use in CI (e.g. GitHub Actions).

