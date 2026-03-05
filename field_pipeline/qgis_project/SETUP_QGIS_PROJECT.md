## QGIS project template for the MRV / land-cover pipeline

This guide explains how to create a **QGIS project template** that matches the
`field_pipeline` schema and can be reused for Mergin Maps field collection and
desktop QA.

The end goal is a project file:

- `field_pipeline/qgis_project/field_mrv_template.qgz`

that:

- Points to `data/incoming/project.gpkg` as the main `observations` layer.
- Uses intuitive **aliases** for fields.
- Provides good default forms for:
  - land-cover training (`lc_training`, `lc_validation`),
  - general ground truth,
  - leakage checks.

---

### 1. Prepare the repo structure

In this repository we assume:

- `field_pipeline/` – pipeline code.
- `data/incoming/project.gpkg` – main GeoPackage from Mergin Maps.
- `field_pipeline/qgis_project/` – folder where the QGIS project will live.

Make sure you have run the pipeline at least once so that a `project.gpkg` with an
`observations` layer exists in `data/incoming/` (or create it manually in QGIS).

---

### 2. Create or open a new QGIS project

1. Start **QGIS**.
2. Create a new blank project (Project → New).
3. Immediately save it into the repo:
   - Project → Save As…
   - Navigate to `field_pipeline/qgis_project/`.
   - Save as `field_mrv_template.qgz`.

This ensures relative paths will be resolved from the project folder.

---

### 3. Add the `observations` layer from the GeoPackage

1. In QGIS, go to **Layer → Add Layer → Add Vector Layer…**
2. Set:
   - Source type: `File`.
   - Source: `data/incoming/project.gpkg` (relative to repo root).
3. Click **Add** and choose the `observations` layer when prompted.
4. Confirm that the layer appears in the Layer Panel as `observations`.

> Tip: If QGIS stores an absolute path, you can later fix it by editing the
> layer source in Layer Properties or by re-adding the layer from a relative
> path with the project saved in `field_pipeline/qgis_project/`.

---

### 4. Configure field aliases (human-friendly labels)

1. Right-click the `observations` layer → **Properties**.
2. Go to the **Fields** (or “Attributes”) tab.
3. For each field, set an alias (double-click in the Alias column), for example:

| Field name        | Alias                         |
|-------------------|-------------------------------|
| `id`              | Observation ID                |
| `obs_type`        | Observation type              |
| `date_time`       | Observation time (UTC)        |
| `collector`       | Collector                     |
| `notes`           | Notes                         |
| `photo_path`      | Photo                         |
| `gnss_accuracy_m` | GNSS accuracy (m)             |
| `lc_label`        | LC class (detailed)           |
| `ipcc_class`      | IPCC land-use class           |
| any others        | As appropriate                |

4. Click **OK** or **Apply** to save aliases in the project.

These aliases make the forms friendlier while keeping the underlying schema
stable for the pipeline.

---

### 5. Configure value maps and forms for key fields

To standardize input and reduce errors, set **Value Maps** for certain fields:

1. Right-click `observations` → **Properties** → **Attributes Form** tab.
2. Click on the field you want to configure (e.g. `obs_type`).

#### 5.1 `obs_type` value map

Suggested values:

- `ground_truth`
- `lc_training`
- `lc_validation`
- `leakage_check`

In Attributes Form:

- Widget Type: **Value Map**.
- Add entries like:
  - Display: `Ground truth`, Value: `ground_truth`
  - Display: `LC training`, Value: `lc_training`
  - Display: `LC validation`, Value: `lc_validation`
  - Display: `Leakage check`, Value: `leakage_check`

#### 5.2 `ipcc_class` value map

Suggested values (exact strings match `pipeline.yaml`):

- `Forest land`
- `Cropland`
- `Grassland`
- `Wetlands`
- `Settlements`
- `Other land`

Configure as a Value Map with those display/value pairs identical.

#### 5.3 Other helpful form settings

- For `date_time`:
  - Widget Type: **DateTime**.
  - Default value: `now()` (or use “Apply default on new features”).
- For `photo_path`:
  - Widget Type: **Text** or “Attachment” if you want a file browser.
- For `gnss_accuracy_m`:
  - Widget Type: **Double** with reasonable range (e.g. 0–100).

You can also use the **Drag and Drop Designer** in the Attributes Form tab to
group fields into logical sections (Location, Land-cover, Quality, etc.).

---

### 6. Save the project as a reusable template

1. After configuring aliases and forms, go to **Project → Save**.
2. Confirm that the file is saved as:
   - `field_pipeline/qgis_project/field_mrv_template.qgz`.

This project file is now part of your repo and can be committed to version
control.

---

### 7. How to use this template in practice

For any new clone / environment:

1. Clone the repo.
2. Ensure there is a `data/incoming/project.gpkg`:
   - Either by copying a template GPKG,
   - Or by running the initial setup scripts / ingest.
3. Open QGIS and load:
   - `field_pipeline/qgis_project/field_mrv_template.qgz`.
4. Start editing/collecting data in the `observations` layer via forms with
friendly aliases and controlled vocabularies.
5. When ready, run the pipeline from the repo root:

```bash
.\.venv\Scripts\python.exe -m field_pipeline.field_pipeline.cli ingest   --config field_pipeline\config\pipeline.yaml
.\.venv\Scripts\python.exe -m field_pipeline.field_pipeline.cli validate --config field_pipeline\config\pipeline.yaml
.\.venv\Scripts\python.exe -m field_pipeline.field_pipeline.cli enrich   --config field_pipeline\config\pipeline.yaml
.\.venv\Scripts\python.exe -m field_pipeline.field_pipeline.cli summarize --config field_pipeline\config\pipeline.yaml
.\.venv\Scripts\python.exe -m field_pipeline.field_pipeline.cli export   --config field_pipeline\config\pipeline.yaml
.\.venv\Scripts\python.exe -m field_pipeline.field_pipeline.cli report   --config field_pipeline\config\pipeline.yaml --mode internal
```

This ensures a tight loop between:

- QGIS/Mergin field collection (with good UX via aliases and value maps),
- The GeoPackage schema expected by the pipeline,
- And the validation/enrichment/reporting logic you’ve already put in place.

