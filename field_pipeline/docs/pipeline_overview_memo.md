## Field data MRV pipeline – overview and external dependencies

### What this setup does

This repo contains a **prototype MRV field‑data pipeline** designed for Mergin Maps + GeoPackage workflows and early Gold Standard alignment.

At a high level, it does:

- **Ingest**
  - Copies the latest `data/incoming/project.gpkg` and `data/incoming/attachments/` into a timestamped run directory under `data/processed/`.
  - Treats `data/incoming/` as read‑only, so each run is an immutable snapshot.

- **Validate**
  - Loads the main `observations` layer.
  - Applies schema + CRS + geometry checks.
  - Applies business rules driven from `field_pipeline/config/pipeline.yaml`, for example:
    - Required fields (`id`, `obs_type`, `date_time`, `collector`, `geometry`, etc.).
    - Temporal check: `date_time` not in the future.
    - GNSS quality: `gnss_accuracy_m` within configured min/max.
    - Land‑cover context: `ground_truth` must be in forest; `leakage_check` must not be in forest or protected areas.
    - Photos: `ground_truth` must have a `photo_path`, and the file must exist under `attachments/`.
  - Writes an `observations_review` table back into the GPKG with:
    - `error_count`, `warning_count`, `state` (`APPROVED` / `NEEDS_REVIEW`), `last_checked_at`.

- **Enrich**
  - Spatially joins `observations` with context layers under `data/context/`:
    - `admin_boundaries.gpkg`, `protected_areas.gpkg`, `land_cover.gpkg`.
  - Writes an enriched GPKG (`project_enriched.gpkg`) for analysis and reporting.

- **Summarize / Export**
  - Produces simple summaries (by `obs_type`, `collector`).
  - Exports attributes to CSV and full data to GeoJSON alongside the GPKG.

- **Report (two modes)**
  - `--mode internal`:
    - Builds a Markdown report with metadata + AI‑generated narrative.
    - AI uses OpenAI (via `OPENAI_API_KEY`) and can be optionally conditioned by snippets from local Gold Standard docs in `docs/` (simple RAG helper).
  - `--mode submission`:
    - Generates an AI‑safe report skeleton for external use (no AI text embedded).
    - Optionally writes separate `*_ai_notes.md` with clearly marked “AI‑assisted draft notes” for internal review only.

- **Tests + CI**
  - Pytest smoke tests for the CLI, validation, and submission‑report behavior.
  - GitHub Actions workflow installs geospatial deps, runs tests on every change under `field_pipeline/**`.

### External services/components needed for real data

To run this pipeline with **real field data collection**, several external services need to be linked and tested.

#### 1. Mergin Maps & QGIS

- **Mergin Maps project**
  - QGIS project (`.qgz`) with:
    - `observations` layer schema matching `pipeline.yaml` (fields, types).
    - Forms, constraints, and value lists aligned with MRV rules.
  - Mobile collection configured to store data in a GeoPackage (`project.gpkg`) and media in an attachments folder.

- **Local sync/clone**
  - A mechanism (Mergin Maps Desktop / CLI / sync service) that:
    - Keeps a local clone of the Mergin project up to date.
    - Ensures `data/incoming/project.gpkg` and `data/incoming/attachments/` are updated before each pipeline run.

**What to test**

- Edits on devices → Mergin → local clone → `data/incoming/` happen reliably.
- Layer names and fields in the live GPKG still match `main_layer` and `required_fields`.

#### 2. Databases / backend storage

Right now everything is file‑based. For real projects, you’ll likely want:

- **PostGIS (recommended optional upgrade)**
  - Store ingested runs in PostGIS tables:
    - `observations_bronze` (raw), `observations_silver` (validated), `observations_gold` (reporting).
  - Use it for:
    - Spatial QC, multi‑run comparisons, dashboards.
    - Producing final issuance/monitoring tables.

- **DuckDB or similar (optional)**
  - For lightweight analytics and RAG indexing if you don’t want full Postgres.

**What to test**

- Ingestion from `project.gpkg` into DB tables (one run end‑to‑end).
- Round trips: DB → exports (GPKG/CSV) used in reports, without schema drift.

#### 3. Servers / automation

To move from manual runs to a service:

- **Application server / job runner**
  - Could be:
    - Cron + shell scripts on a VM, or
    - A lightweight scheduler (e.g. Airflow, Prefect, or a simple queue worker).
  - Responsibilities:
    - Trigger `ingest → validate → enrich → summarize → export → report` on a schedule (e.g. nightly) or when new data arrives.
    - Store logs and outputs with clear run IDs.

- **File storage**
  - For long‑term evidence:
    - `data/processed/` snapshots.
    - Generated CSV/GeoJSON.
    - Reports and `*_ai_notes.md`.
  - Could be:
    - A managed object store (e.g. S3, Azure Blob), or
    - A versioned fileshare with backup.

**What to test**

- That scheduled runs complete without manual intervention.
- That failed runs are logged and easy to rerun.
- That outputs are stored with clear, traceable paths (`run_<timestamp>`).

#### 4. OpenAI / AI services

- **OpenAI API**
  - `OPENAI_API_KEY` set securely in the environment where the pipeline runs.
  - Optionally, project‑level limits and monitoring in the OpenAI platform.

**What to test**

- That AI calls:
  - Work with your key and chosen model (`gpt-4.1-mini` or similar).
  - Fail gracefully when AI is disabled (no crashes, clear text in report).
- That AI usage and cost are within budget at expected run frequency.

#### 5. Gold Standard document management

- **Local GS library for RAG**
  - Curated set of GS core documents converted to Markdown/text in the repo `docs/` folder.
  - Clear naming convention (e.g. `101_principles_requirements.md`) and versioning.

- **Evidence indexing (future step)**
  - Hashing and indexing attachments and spatial layers into a searchable catalog (e.g. an `evidence_files` table, evidence index Markdown).

**What to test**

- That the RAG helper is actually pulling from the correct docs (spot‑check by changing text and observing narrative shifts).
- That you can map report sections back to specific GS documents and clauses.

### Note for next iteration – land‑cover training design

- For future land‑cover training / MRV work, align field collection with **IPCC land‑use categories**, while keeping a richer local legend:
  - Always capture both:
    - `lc_label` – detailed local class (e.g. dense forest, degraded forest, agroforestry, annual crops, etc.).
    - `ipcc_class` – one of: `Forest land`, `Cropland`, `Grassland`, `Wetlands`, `Settlements`, `Other land`.
  - This lets the ML training use `lc_label` (fine detail) but still guarantees that:
    - emissions/removals accounting, leakage and reporting can aggregate cleanly to `ipcc_class`, as expected by many GS methodologies.
- Next updates to the pipeline should:
  - Add `lc_label` and `ipcc_class` to the `observations` schema and `pipeline.yaml` (`required_fields` + any mapping/validation rules).
  - Reflect these fields in the Mergin/QGIS forms and in validation rules (e.g. required for `obs_type == "lc_training"`).


