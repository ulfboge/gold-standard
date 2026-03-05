## Suggested field schema and aliases for land-cover training

This document suggests a **standardized schema** and human-friendly aliases for the
`observations` layer when used for land-cover (LC) training and validation, to be
configured in the QGIS/Mergin project.

### Core identification and geometry

| Field name      | Suggested alias      | Type    | Notes |
|-----------------|----------------------|---------|-------|
| `id`            | Observation ID       | string  | Unique ID per observation (UUID or project-specific code). |
| `geometry`      | Location             | point   | Captured by GNSS; stored as Point (WGS84 or project CRS). |
| `date_time`     | Observation time     | datetime (UTC) | Use ISO 8601 with timezone. |
| `collector`     | Collector            | string  | Person or team ID. |

### Observation type and purpose

| Field name      | Suggested alias      | Type    | Notes |
|-----------------|----------------------|---------|-------|
| `obs_type`      | Observation type     | enum    | Suggested values: `ground_truth`, `lc_training`, `lc_validation`, `leakage_check`. |

### Land-cover labelling

| Field name      | Suggested alias      | Type    | Notes |
|-----------------|----------------------|---------|-------|
| `lc_label`      | LC class (detailed)  | enum/string | Local legend class used for training (e.g. dense forest, degraded forest, agroforestry, annual crops, etc.). Required. |
| `ipcc_class`    | IPCC land-use class  | enum    | One of: `Forest land`, `Cropland`, `Grassland`, `Wetlands`, `Settlements`, `Other land`. Required. |

### Quality and evidence

| Field name        | Suggested alias      | Type    | Notes |
|-------------------|----------------------|---------|-------|
| `gnss_accuracy_m` | GNSS accuracy (m)    | float   | Horizontal accuracy in metres; pipeline enforces max thresholds. |
| `photo_path`      | Photo                | string  | Relative path to photo under `attachments/`; required for `ground_truth` / `lc_training`. |
| `notes`           | Notes                | text    | Free-text comments. |

### Best-practice rules (reflected in `pipeline.yaml`)

- **Always capture**:
  - `lc_label` and `ipcc_class` for any observation used as `lc_training` or `lc_validation`.
  - `photo_path` and `gnss_accuracy_m` for those observations as well.

- **obs_type semantics**:
  - `ground_truth`: general MRV observation (plots, checks), may be reused for multiple purposes.
  - `lc_training`: point explicitly intended as training data for land-cover classifiers.
  - `lc_validation`: independent validation point (hold-out from training).
  - `leakage_check`: observation used for leakage analysis.

- **Validation behaviour** (implemented in `validate.py` and `pipeline.yaml`):
  - `lc_label`: required for all observations.
  - `ipcc_class`: required and must be one of the six IPCC land-use categories.
  - `gnss_accuracy_m`:
    - Hard max (e.g. 10 m) for all obs (rule `gnss_accuracy`).
    - Stricter preferred max (5 m) for `lc_training` and `lc_validation` (rule `gnss_accuracy_training` – currently a warning).
  - `photo_path`:
    - Required for `ground_truth` (and can be extended to apply to `lc_training` in forms).
    - If non-empty, the file path is checked under `attachments/`.

These aliases should be configured in QGIS under **Layer Properties → Fields → Alias**
so that field collectors see intuitive labels while the underlying schema remains
stable for the pipeline and code.

