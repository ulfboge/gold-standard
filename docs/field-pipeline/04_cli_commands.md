## CLI Commands and Usage

This page describes the **CLI commands** exposed by the field pipeline. It is adapted from section 4 of `field_pipeline/PROCESS_MANUAL.md`.

All commands are provided via a Typer‑based CLI in `field_pipeline/field_pipeline/cli.py`.

---

### Setup

From the repository root:

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r field_pipeline/requirements.txt
```

Verify the CLI:

```bash
python -m field_pipeline.cli --help
```

---

### `ingest`

**Purpose**: Copy the current incoming GeoPackage and attachments into a timestamped run directory under `data/processed/`.

```bash
python -m field_pipeline.cli ingest --config field_pipeline/config/pipeline.yaml
```

Behaviour:

- Reads configuration (paths, etc.).
- Copies:
  - `paths.incoming_gpkg` → `data/processed/run_<timestamp>/project.gpkg`
  - `paths.incoming_attachments_dir` → `data/processed/run_<timestamp>/attachments/` (if it exists).
- Prints the destination GeoPackage and attachments directory.

This preserves the raw `data/incoming/` data and creates an immutable snapshot per processing run.

---

### `validate`

**Purpose**: Perform schema and basic geometry sanity checks.

```bash
python -m field_pipeline.cli validate --config field_pipeline/config/pipeline.yaml
```

Options:

- `--gpkg PATH` – optionally override the GeoPackage to validate (default: `incoming_gpkg` from config).

Checks performed (current implementation):

- **Schema**:
  - Ensures required fields from `required_fields` exist in the main layer (except for the synthetic `geometry` entry).
- **Rows**:
  - For each observation:
    - Required fields are non‑null (according to `required_fields`).
    - Geometry is non‑null and non‑empty.
    - Geometry is valid (reports `shapely.validation.explain_validity` if not).
- **CRS**:
  - If CRS is missing, assigns `crs_fallback` and logs a warning.

Output:

- Prints a table of issues (id, field, severity, message) or “no issues found”.
- Can be redirected to CSV/JSON for further analysis.

You can extend `validate.py` with more rules (for example temporal checks, GNSS accuracy thresholds, photo requirements).

---

### `enrich`

**Purpose**: Enrich observations with configured context layers.

```bash
python -m field_pipeline.cli enrich --config field_pipeline/config/pipeline.yaml
```

Options:

- `--gpkg PATH` – override target GeoPackage (defaults to `incoming_gpkg` from config).

Behaviour:

- Loads the main layer from the given GeoPackage.
- Ensures all configured context layers exist; logs a warning and skips missing ones.
- For each `enrichment_layers` entry with `join_type: "spatial"`:
  - Reads the context GeoPackage.
  - Reprojects context to main layer CRS if needed.
  - Performs a spatial join (`geopandas.sjoin`) and drops the helper column `index_right`.
- Writes the enriched layer to `<original_stem>_enriched.gpkg` alongside the input file.

---

### `summarize`

**Purpose**: Produce quick descriptive summaries.

```bash
python -m field_pipeline.cli summarize --config field_pipeline/config/pipeline.yaml
```

Options:

- `--gpkg PATH` – override target GeoPackage.

Current behaviour:

- Counts:
  - Features by `obs_type` (if present).
  - Features by `collector` (if present).
- Prints a DataFrame with counts and a `metric` column (for example `count_by_obs_type`).

This is intentionally minimal; you can extend `summarize.py` with project‑specific metrics (for example, by admin area or monitoring period).

---

### `export`

**Purpose**: Export the main layer to CSV and GeoJSON for use in other tools.

```bash
python -m field_pipeline.cli export --config field_pipeline/config/pipeline.yaml
```

Options:

- `--gpkg PATH` – override target GeoPackage.

Behaviour:

- Reads the main layer.
- Writes:
  - `<gpkg_base>.csv` – attribute table without geometry.
  - `<gpkg_base>.geojson` – full layer including geometry.

Typical uses:

- Data exchange with non‑GIS tools.
- Quick checks in web map viewers.
- Feeding into analysis notebooks.

---

### `report`

**Purpose**: Generate a human‑readable Markdown report.

```bash
python -m field_pipeline.cli report --config field_pipeline/config/pipeline.yaml
```

Options:

- `--gpkg PATH` – target GeoPackage (default: `incoming_gpkg`).
- `--output/-o PATH` – output Markdown path (default: `data/processed/report.md`).

Behaviour:

- Computes:
  - Number of features in the main layer.
  - CRS.
  - Timestamp of report generation.
- Writes a Markdown document with:
  - A metadata bullet list.
  - A narrative section:
    - If AI is **disabled**: a placeholder statement.
    - If AI is **enabled** and a provider is configured: calls `ai.draft_text` (stub unless you wire it to a real API).

You can convert the Markdown to PDF using external tools such as Pandoc or Quarto; this is intentionally not hard‑wired into the pipeline.

