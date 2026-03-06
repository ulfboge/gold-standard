## Configuration (`pipeline.yaml`)

This page explains how the field pipeline is configured via `field_pipeline/config/pipeline.yaml`. It is adapted from section 3 of `field_pipeline/PROCESS_MANUAL.md`.

---

### What `pipeline.yaml` controls

The central configuration file `field_pipeline/config/pipeline.yaml` controls:

- **Paths** – where to find incoming data, processed runs, and context layers.
- **Main layer name** – the name of the feature layer holding field observations.
- **Fallback CRS** – used when a layer has no CRS defined.
- **Required fields and simple rules** – basic schema and quality expectations.
- **Enrichment layers** – which context datasets to spatially join.
- **AI options** – whether AI is used to draft narrative text in reports.

Important scope note:

- `pipeline.yaml` configures the **file-based pipeline**.
- It does **not** currently configure a direct connection from the CLI to a PostGIS-compatible backend such as Supabase.
- If you use a PostGIS-compatible backend for editing, export the database contents to `paths.incoming_gpkg` first, then run the same commands described here. See `10_supabase_postgis_workflow.md`.

An example:

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

---

### Paths

- **`paths.incoming_gpkg`**  
  Path to the raw GeoPackage consumed by the CLI.
  
  In the default workflow, this is synced from Mergin Maps. In the optional PostGIS-compatible backend workflow, this is the exported GeoPackage produced from the database handoff step.

- **`paths.incoming_attachments_dir`**  
  Directory containing raw photos/attachments referenced from the GeoPackage.

- **`paths.processed_dir`**  
  Base directory where timestamped run directories and derived files are stored.

- **`paths.context_dir`**  
  Base directory for context layers (admin, protected areas, land‑cover).

You can point these paths to any layout you like; the defaults assume everything stays inside this repo.

---

### Main layer and CRS

- **`main_layer`**  
  Name of the feature layer that holds field observations. Default: `observations`.

- **`crs_fallback`**  
  EPSG code to assign when a layer has no CRS defined, for example `"EPSG:4326"`.

---

### Required fields and rules

Each key under `required_fields` corresponds to an expected attribute in the main layer:

- `required: true` – field must exist in the schema and be non‑null for all rows.
- `required_if_photo: true` – field is required when an observation has an associated photo (logic implemented in `validate.py`).
- `min_gnss_accuracy_m` – numeric constraint on GNSS accuracy (for example, `0.0` to ensure no negative values; can be extended with maximum thresholds).

You can extend both the semantics of `required_fields` and the checks in `validate.py` to cover more complex rules (for example, “require photo for certain `obs_type` values”).

---

### Enrichment layers

Each entry under `enrichment_layers` describes a context dataset to be joined:

- `name` – logical name used in logs.
- `path` – path to the context dataset (GeoPackage).
- `join_type` – currently `spatial` (spatial join via `geopandas.sjoin`).

Future extensions could include:

- Attribute joins (not just spatial).
- Configuration of join fields and which columns to retain from each context layer.

---

### AI configuration

The AI module (`field_pipeline/ai.py`) is **off by default**:

- `enabled: false` – pipeline behaves entirely without AI.
- `provider: null` – no provider is set.

To enable later:

1. Set `ai.enabled: true`.  
2. Set `ai.provider: "openai"` (or another provider string).  
3. Implement the corresponding provider logic in `field_pipeline/ai.py` and set required environment variables (for example `OPENAI_API_KEY`).

Until then, any AI‑related output is a stub and clearly marked as such.

