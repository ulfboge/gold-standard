## Field data pipeline (Mergin Maps → evidence packages)

This subproject scaffolds a **free/open-source geospatial field‑data pipeline** around a Mergin Maps project (QGIS project + GeoPackage) as the collection front‑end.

### Goals

- **Ingest** latest synced field data from `data/incoming/`.
- **Validate** schema + required fields + geometry sanity.
- **Enrich** observations with open “context layers” (admin, PA, land cover, etc.).
- **Summarize & export** CSV/GeoPackage/GeoJSON for analysis and certification evidence.
- **Report** human‑readable Markdown (PDF optional later).
- **Preserve raw data**: input GeoPackage is read‑only; enriched copies live in `data/processed/`.

### Layout

- `field_pipeline/field_pipeline/`
  - `cli.py` – Typer CLI entrypoint with `ingest`, `validate`, `enrich`, `summarize`, `export`, `report`.
  - `config.py` – config loading from YAML.
  - `logging_config.py` – basic logging setup.
  - `ingest.py` – copy & index raw GeoPackage + attachments into `data/processed/`.
  - `validate.py` – schema + required fields + geometry checks.
  - `enrich.py` – spatial joins with context layers (open datasets where possible).
  - `summarize.py` – tabular summaries (per type, per admin, etc.).
  - `export.py` – CSV / GeoPackage / GeoJSON exports.
  - `report.py` – Markdown report generation (PDF later).
  - `ai.py` – optional AI‑assisted text drafting stub (no‑AI mode by default).
- `field_pipeline/config/pipeline.yaml` – main configuration (paths, required fields, rules, enrichment layers).
- `field_pipeline/tests/` – pytest unit test placeholders.
- `data/`
  - `incoming/` – synced Mergin project GeoPackage(s), e.g. `project.gpkg`.
  - `processed/` – timestamped, enriched copies and derived outputs.
  - `context/` – open context layers (admin boundaries, protected areas, land cover, etc.).

### Quickstart

1. **Install dependencies (local dev)**

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r field_pipeline/requirements.txt
```

2. **Configure**

Edit `field_pipeline/config/pipeline.yaml` to match your environment (paths, required fields, enrichment layers, rules).

3. **Run CLI**

From the repo root:

```bash
python -m field_pipeline.cli --help

python -m field_pipeline.cli ingest   --config field_pipeline/config/pipeline.yaml
python -m field_pipeline.cli validate --config field_pipeline/config/pipeline.yaml
python -m field_pipeline.cli enrich   --config field_pipeline/config/pipeline.yaml
python -m field_pipeline.cli summarize --config field_pipeline/config/pipeline.yaml
python -m field_pipeline.cli export   --config field_pipeline/config/pipeline.yaml
python -m field_pipeline.cli report   --config field_pipeline/config/pipeline.yaml
```

4. **Tests**

```bash
pytest field_pipeline/tests
```

### Notes

- All components are designed to run **locally** with free/open libraries (GeoPandas, Shapely, Rasterio, GDAL, DuckDB optional, PostGIS optional).
- The AI layer is **optional and pluggable**; by default the pipeline runs in no‑AI mode and will only activate AI if configured via environment variables and config flags. TODO: fill in your chosen provider or keep disabled. 

