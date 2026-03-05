## Field Data Pipeline Manual (Mergin Maps → Evidence Packages)

This manual describes how to use the **field data pipeline** scaffolded in `field_pipeline/` to process Mergin Maps field data (GeoPackage + attachments) into validated, enriched, and report‑ready outputs, while keeping raw data immutable and relying on free/open‑source tooling.

For a **Gold Standard–specific EO/MRV workflow** (including forest/non‑forest eligibility, land‑cover mapping, leakage support, and how this pipeline plugs into the A/R methodology and LUF requirements), see:

- `docs/gold-standard/EO_workflow_GS_AR_field_pipeline.md`

Target users: GIS/MRV analysts, data engineers, and reviewers working with certification‑style projects (ground truth, monitoring evidence, leakage checks).

---

### 1. End‑to‑end workflow overview

1. **Collect**  
   - Field staff use **Mergin Maps** (mobile) with a QGIS project and a GeoPackage backend.  
   - They capture:
     - Geometries (points/polygons)
     - Attributes (e.g. `id`, `obs_type`, `date_time`, `collector`, `notes`, `photo_path`)
     - Photos/attachments (stored alongside the GPKG, typically in an `attachments/` folder).

2. **Sync to “incoming” folder**  
   - A local clone/sync of the Mergin project is available on disk.  
   - The pipeline assumes:
     - GeoPackage: `data/incoming/project.gpkg`
     - Attachments directory: `data/incoming/attachments/` (configurable).

3. **Ingest** (copy to `data/processed/`)  
   - The `ingest` command copies the current incoming GeoPackage and attachments to a **timestamped run directory** under `data/processed/`, e.g. `data/processed/run_20260302T120000Z/`.  
   - Raw data in `data/incoming/` is treated as **read‑only**.

4. **Validate**  
   - The `validate` command checks:
     - Required fields and basic schema
     - Geometry sanity (non‑empty, valid geometries)
     - CRS presence (and applies a configured fallback if missing)
   - Validation results are printed to the console (and can later be extended to write a dedicated validation table or file).

5. **Enrich**  
   - The `enrich` command joins observations with configured **context layers** (admin boundaries, protected areas, land cover, etc.) found in `data/context/`.  
   - Output is a new enriched GeoPackage (e.g. `project_enriched.gpkg`) that carries additional attributes from context layers.

6. **Summarize & export**  
   - `summarize` creates simple tabular summaries (e.g. counts by `obs_type`, `collector`).  
   - `export` writes:
     - A **CSV** table (attributes only, no geometry)
     - A **GeoJSON** export for mapping and sharing.

7. **Report**  
   - The `report` command generates a Markdown report with:
     - Dataset metadata (source path, CRS, feature counts, timestamp)
     - Optional AI‑assisted narrative (if enabled in config).
   - This Markdown can later be rendered to PDF using external tools (Pandoc, Quarto, etc.).

Throughout, the raw incoming GeoPackage is never modified; all operations happen on copies in `data/processed/`.

---

### 2. Folder structure and key files

At the repository root (`gold-standard/`):

- `data/`
  - `incoming/`
    - `project.gpkg` – main GeoPackage coming from Mergin Maps (configurable).
    - `attachments/` – photos and other files linked from attributes (optional but recommended).
  - `processed/`
    - `run_<timestamp>/` – per‑run copies of `project.gpkg` and `attachments/` created by `ingest`.
    - `report.md` – default report output (can be overridden).
  - `context/`
    - `admin_boundaries.gpkg` – optional admin boundaries.
    - `protected_areas.gpkg` – optional protected areas.
    - `land_cover.gpkg` – optional land‑cover dataset.

- `field_pipeline/`
  - `README.md` – quickstart and developer notes.
  - `PROCESS_MANUAL.md` – this manual.
  - `requirements.txt` – Python dependencies.
  - `config/pipeline.yaml` – **main configuration file**.
  - `field_pipeline/` – Python package:
    - `cli.py` – Typer‑based CLI entry‑point.
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
    - `test_cli.py` – pytest placeholder.

---

### 3. Configuration (`pipeline.yaml`)

The central configuration file is `field_pipeline/config/pipeline.yaml`. It controls:

- **Paths**
- **Main layer name**
- **Fallback CRS**
- **Required fields and simple rules**
- **Enrichment layers**
- **AI options**

Default example:

```yaml
paths:
  incoming_gpkg: data/incoming/project.gpkg
  incoming_attachments_dir: data/incoming/attachments
  processed_dir: data/processed
  context_dir: data/context

main_layer: observations
crs_fallback: "EPSG:4326"

required_fields:
  id:
    required: true
  obs_type:
    required: true
  date_time:
    required: true
  collector:
    required: true
  geometry:
    required: true
  photo_path:
    required_if_photo: true
  gnss_accuracy_m:
    min_gnss_accuracy_m: 0.0

enrichment_layers:
  - name: admin_boundaries
    path: data/context/admin_boundaries.gpkg
    join_type: spatial
  - name: protected_areas
    path: data/context/protected_areas.gpkg
    join_type: spatial
  - name: land_cover
    path: data/context/land_cover.gpkg
    join_type: spatial

ai:
  enabled: false
  provider: null
```

#### 3.1. Paths

- **`incoming_gpkg`** – path to the raw GeoPackage from Mergin Maps.
- **`incoming_attachments_dir`** – directory with raw photos/attachments.
- **`processed_dir`** – where timestamped run directories and derived files are stored.
- **`context_dir`** – base directory for context layers (admin, PA, land‑cover).

> You can point these to any folder layout you like; the defaults assume you keep everything inside this repo.

#### 3.2. Main layer and CRS

- **`main_layer`** – the name of the feature layer that holds field observations. Default: `observations`.
- **`crs_fallback`** – EPSG code used when a layer has no CRS defined (e.g. `"EPSG:4326"`).

#### 3.3. Required fields and rules

Each key under `required_fields` corresponds to an attribute you expect in the main layer:

- `required: true` – field must exist in the schema and be non‑null for all rows.
- `required_if_photo: true` – field is required in cases where the observation has an associated photo (logic can be extended later).
- `min_gnss_accuracy_m` – optional numeric constraint on GNSS accuracy (e.g. 0.0 ensures no negative values; future rules can enforce maximum allowed values).

> TODO (extensibility): you can expand `required_fields` semantics and corresponding checks in `validate.py` to cover more complex rules (e.g. “require photo for certain `obs_type` values”).

#### 3.4. Enrichment layers

Each entry under `enrichment_layers` describes a context dataset:

- `name` – logical name used in logs.
- `path` – path to the context dataset (GeoPackage).
- `join_type` – currently `spatial` (spatial join via `geopandas.sjoin`).

> TODO: To support attribute joins, extend `join_type` semantics and add join field configuration in `config.py` and `enrich.py`.

#### 3.5. AI configuration

The AI module is **off by default**:

- `enabled: false` – pipeline behaves entirely without AI.
- `provider: null` – no provider is set.

To enable later:

1. Set `enabled: true`.  
2. Set `provider: "openai"` (or another string of your choice).  
3. Implement the corresponding provider logic in `field_pipeline/ai.py` and set any required env vars (e.g. `OPENAI_API_KEY`).

Until then, any AI‑related output is a stub and clearly marked as such.

---

### 4. Commands and usage (CLI)

All commands are exposed via the Typer CLI in `field_pipeline/field_pipeline/cli.py`.

#### 4.1. Setup

From the repository root:

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r field_pipeline/requirements.txt
```

Verify CLI:

```bash
python -m field_pipeline.cli --help
```

#### 4.2. `ingest`

**Purpose**: Copy the current incoming GeoPackage + attachments into a timestamped run directory in `data/processed/`.

```bash
python -m field_pipeline.cli ingest --config field_pipeline/config/pipeline.yaml
```

Behavior:

- Reads config (paths, etc.).
- Copies:
  - `paths.incoming_gpkg` → `data/processed/run_<timestamp>/project.gpkg`
  - `paths.incoming_attachments_dir` → `data/processed/run_<timestamp>/attachments/` (if it exists).
- Prints the destination GeoPackage and attachments directory.

> This step preserves the raw `data/incoming/` data and gives you an immutable snapshot per processing run.

#### 4.3. `validate`

**Purpose**: Schema + basic geometry sanity checks.

```bash
python -m field_pipeline.cli validate --config field_pipeline/config/pipeline.yaml
```

Options:

- `--gpkg PATH` – optionally override the GeoPackage to validate (default: `incoming_gpkg` from config).

Checks performed (current minimal implementation):

- **Schema**:
  - Ensures required fields from `required_fields` exist in the main layer (except for the synthetic `geometry` entry).
- **Rows**:
  - For each observation:
    - Required fields are non‑null (according to `required_fields`).
    - Geometry is non‑null and non‑empty.
    - Geometry is valid (otherwise reports `shapely.validation.explain_validity`).
- **CRS**:
  - If CRS is missing, assigns the configured `crs_fallback` and logs a warning.

Output:

- Prints a table of issues (id, field, severity, message) or “no issues found”.
- You can redirect this to a CSV/JSON file if needed.

> TODO: Extend `validate.py` with more rules (e.g. temporal checks, GNSS accuracy thresholds, required photos for certain `obs_type` values).

#### 4.4. `enrich`

**Purpose**: Enrich observations with configured context layers.

```bash
python -m field_pipeline.cli enrich --config field_pipeline/config/pipeline.yaml
```

Options:

- `--gpkg PATH` – override target GeoPackage (defaults to `incoming_gpkg` from config).

Behavior:

- Loads the main layer from the given GeoPackage.
- Ensures all context layers exist; if not, logs a warning and skips them.
- For each `enrichment_layers` entry with `join_type: "spatial"`:
  - Reads context GeoPackage.
  - Reprojects context to main layer CRS if needed.
  - Performs a spatial join (`geopandas.sjoin`) and drops `index_right` helper column.
- Writes the enriched layer to `<original_stem>_enriched.gpkg` alongside the input file.

> TODO: Add control over which context columns to keep, join predicates, and conflict resolution between overlapping context layers.

#### 4.5. `summarize`

**Purpose**: Produce quick descriptive summaries.

```bash
python -m field_pipeline.cli summarize --config field_pipeline/config/pipeline.yaml
```

Options:

- `--gpkg PATH` – override target GeoPackage.

Current behavior:

- Counts:
  - Features by `obs_type` (if the field exists).
  - Features by `collector` (if the field exists).
- Prints a DataFrame with counts and a `metric` column (e.g. `count_by_obs_type`).

> This is deliberately minimal; you can extend `summarize.py` with project‑specific metrics (e.g. per admin area, per monitoring period).

#### 4.6. `export`

**Purpose**: Export the main layer to CSV and GeoJSON for use in other tools.

```bash
python -m field_pipeline.cli export --config field_pipeline/config/pipeline.yaml
```

Options:

- `--gpkg PATH` – override target GeoPackage.

Behavior:

- Reads the main layer.
- Writes:
  - `<gpkg_base>.csv` – attribute table without geometry.
  - `<gpkg_base>.geojson` – full layer including geometry.

This is useful for:

- Data exchange with non‑GIS tools
- Quick checks in web map viewers
- Feeding into analysis notebooks.

#### 4.7. `report`

**Purpose**: Generate a human‑readable Markdown report.

```bash
python -m field_pipeline.cli report --config field_pipeline/config/pipeline.yaml
```

Options:

- `--gpkg PATH` – target GeoPackage (default: `incoming_gpkg`).
- `--output/-o PATH` – output Markdown path (default: `data/processed/report.md`).

Behavior:

- Computes:
  - Number of features in the main layer.
  - CRS.
  - Timestamp of report generation.
- Writes a Markdown document with:
  - Metadata bullet list.
  - A narrative section:
    - If AI is **disabled**: a placeholder statement.
    - If AI is **enabled** and a provider is configured: calls `ai.draft_text` (currently a stub; you need to wire it to a real API).

> You can convert the Markdown to PDF using external tools such as Pandoc or Quarto. This is intentionally **not** hard‑wired to keep dependencies light and open‑source.

---

### 5. Attachments handling

The scaffold focuses on copying and preserving attachments rather than deeply parsing EXIF/metadata (that can be added later).

Current behavior:

- **Ingest**:
  - If `paths.incoming_attachments_dir` exists, it is copied wholesale to the run directory as `attachments/`.
  - This creates a 1:1 snapshot of the current attachment set.

> TODO: Implement attachment indexing and hashing (e.g. compute SHA‑256 for each file, extract EXIF timestamps and GPS, cross‑check with `date_time` and geometry).

Recommended pattern:

- In your QGIS / Mergin project, store file paths or filenames in a field (e.g. `photo_path`).  
- Later, add a small `attachments.py` module that:
  - Scans the attachments folder for referenced files.
  - Computes hashes.
  - Builds an attachments table (e.g. in the GeoPackage or as a CSV/Parquet) linked by observation id.

---

### 6. “Review” outputs and immutability

The current scaffold:

- Treats `data/incoming/project.gpkg` as **read‑only**.
- Works primarily on copies in `data/processed/`.

The manual design intent (even if not fully implemented yet) is:

- Raw observations layer is a **source of truth** for collected data.
- Additional tables (e.g. `observations_review`) can be created alongside to hold:
  - Validation flags (error/warning codes)
  - Enrichment status
  - Reviewer decisions and notes.

> TODO: Add a dedicated `review.py`/`review_table.py` module that creates and updates a review layer, similar to what you have for MRV validation in `mrv_validation/`. This can be wired into `validate` and `enrich` steps.

---

### 7. AI integration (optional, pluggable)

The AI module (`field_pipeline/ai.py`) is intentionally a **no‑op stub**:

- It never calls any API unless:
  - `ai.enabled: true` in `pipeline.yaml`, and
  - `ai.provider` is set (e.g. `"openai"`), and
  - You implement the corresponding call and set required environment variables.

Current behavior:

- `draft_text(prompt, provider=None)`:
  - If `provider` is falsy: returns a stub string indicating AI is disabled.
  - If `provider == "openai"` but `OPENAI_API_KEY` is not set: returns a stub.
  - Otherwise: returns a placeholder indicating that integration is not yet implemented.

To enable in the future:

1. Choose a provider (e.g. OpenAI API, local LLM).  
2. Implement the actual call in `ai.py` using the chosen library.  
3. Set secrets as environment variables (never commit them to the repo).  
4. Turn on `ai.enabled` and set `ai.provider` accordingly in `pipeline.yaml`.

This preserves:

- Clear separation between the **core open pipeline** and any AI augmentation.
- A safe default where AI is completely off.

---

### 8. Testing and CI

#### 8.1. Local tests

From the repository root:

```bash
pytest field_pipeline/tests
```

Current tests:

- `test_cli.py` – a basic smoke test ensuring the CLI loads and responds to `--help`.  
  - TODO: add tests per command (e.g. ingest copies files, validate catches missing fields, enrich writes an output, etc.).

#### 8.2. GitHub Actions

The workflow `.github/workflows/field-pipeline-ci.yml`:

- Triggers on pushes/PRs affecting `field_pipeline/**`.
- Runs on Ubuntu:
  - Installs GDAL system packages.
  - Installs Python dependencies from `field_pipeline/requirements.txt`.
  - Executes `pytest field_pipeline/tests -vv`.

You can extend this CI with:

- Linting (e.g. `flake8`, `ruff`).
- Formatting checks (e.g. `black`).
- Additional integration tests (e.g. minimal sample GeoPackage in the repo).

---

### 9. Customization roadmap (TODOs)

This scaffold is intentionally minimal and opinionated; likely next steps for a production‑style pipeline:

- **Validation rules**
  - Temporal checks: `date_time` not in the future, falls within monitoring period.
  - GNSS accuracy bounds: max allowed accuracy per `obs_type`.
  - Photo rules: require photos for specific `obs_type` values; verify referenced files exist.
  - Duplicate detection: same location/time/collector within specified tolerances.

- **Enrichment logic**
  - Configurable join predicates and retained columns per context layer.
  - Derived fields (e.g. admin codes, protection status, land‑cover class summaries).

- **Review tables**
  - Dedicated `observations_review` table that captures:
    - Validation status
    - Enrichment completeness
    - Reviewer decisions and notes
    - Timestamps and user IDs for audit trails.

- **Attachments index**
  - Build a structured `attachments` table (within GPKG or as a separate DB) with:
    - Observation id
    - File path
    - SHA‑256 hash
    - EXIF timestamps/GPS (when available).

- **Reporting**
  - Richer Markdown or HTML reports, including:
    - Maps (rendered separately in QGIS and linked/embedded).
    - Summary tables.
    - Links to underlying CSV/GeoPackage/GeoJSON outputs.

- **AI**
  - When and if desired, plug in AI to:
    - Draft narrative for reports.
    - Suggest data quality flags or highlight suspicious patterns (but always with human oversight).

This manual should give you a stable reference for how the current scaffold works and where to extend it for your specific certification or MRV use case.

