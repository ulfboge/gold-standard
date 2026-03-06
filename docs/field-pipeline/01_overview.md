## Field Data Pipeline – Overview

This page summarises the overall **end‑to‑end workflow** of the field data pipeline scaffolded in `field_pipeline/`. It is adapted from section 1 of `field_pipeline/PROCESS_MANUAL.md`.

The default documentation assumes a **file‑based pipeline input**: a GeoPackage in `data/incoming/`. If you maintain observations in a **PostGIS-compatible backend such as Supabase**, treat that database as an **upstream editing backend** and export a pipeline‑ready GeoPackage before running the CLI. See `10_supabase_postgis_workflow.md`.

### What the pipeline does

The pipeline turns Mergin Maps / QGIS field data (GeoPackage + attachments) into validated, enriched, and report‑ready outputs, while keeping raw data immutable and using open‑source tooling.

At a high level, each run performs:

1. **Collect**
   - Field staff use **Mergin Maps** (mobile) with a QGIS project connected to a GeoPackage backend.
   - They capture:
     - Geometries (points/polygons)
     - Attributes (e.g. `id`, `obs_type`, `date_time`, `collector`, `notes`, `photo_path`)
     - Photos/attachments (stored alongside the GPKG, typically in an `attachments/` folder).

2. **Sync to the “incoming” folder**
   - A local clone/sync of the Mergin project is available on disk.
   - The pipeline assumes:
     - GeoPackage at `data/incoming/project.gpkg`
     - Attachments directory at `data/incoming/attachments/` (configurable in `pipeline.yaml`).
   - Optional database-backed variant:
     - Observations are edited in a PostGIS-compatible backend such as Supabase.
     - A refreshed export table is written back out to `data/incoming/project.gpkg`.
     - The rest of the pipeline then runs exactly as it does for the default file-based workflow.

3. **Ingest (copy to `data/processed/`)**
   - The `ingest` command copies the current incoming GeoPackage and attachments to a **timestamped run directory** under `data/processed/`, e.g.:
     - `data/processed/run_20260302T120000Z/`
   - Raw data in `data/incoming/` is treated as **read‑only**.

4. **Validate**
   - The `validate` command checks:
     - Required fields and basic schema.
     - Geometry sanity (non‑empty, valid geometries).
     - CRS presence (and applies a configured fallback if missing).
   - Validation results are printed to the console (and can be extended to write dedicated validation tables/files).

5. **Enrich**
   - The `enrich` command joins observations with configured **context layers** under `data/context/`, for example:
     - `admin_boundaries.gpkg`
     - `protected_areas.gpkg`
     - `land_cover.gpkg`
   - It writes an enriched GeoPackage (e.g. `project_enriched.gpkg`) carrying additional attributes from context layers.

6. **Summarize & export**
   - `summarize` creates simple tabular summaries (for example, counts by `obs_type` or by `collector`).
   - `export` writes:
     - A **CSV** table (attributes only, no geometry).
     - A **GeoJSON** export (full layer with geometry and attributes).

7. **Report**
   - The `report` command generates a Markdown report with:
     - Dataset metadata (source path, CRS, feature counts, timestamp).
     - Optional AI‑assisted narrative (if enabled in `pipeline.yaml`).
   - The Markdown can be rendered to PDF using tools like Pandoc or Quarto.

Throughout this process the raw incoming GeoPackage is never modified; all operations happen on copies under `data/processed/`.

