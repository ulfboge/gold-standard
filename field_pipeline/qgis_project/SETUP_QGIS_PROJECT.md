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

#### 5.3 Auto-fill `id` for new features in GeoPackage-only projects

Use this only when the layer is stored in a local file such as a GeoPackage.
For PostgreSQL/PostGIS, let the database assign `id` values with an identity
column or sequence instead of using a QGIS expression.

For GeoPackage-backed layers:

1. In **Attributes Form**, select the `id` field.
2. Set **Default value** to this expression (click the expression icon to open
   the editor):
   ```text
   coalesce(maximum("id"), 0) + 1
   ```
   This uses the current maximum `id` in the layer (or 0 if empty) and adds 1.
3. Leave **Apply default value on update** unchecked so the value is set only
   when a new feature is created, not when you edit existing ones.

If `id` is a text field (e.g. for UUIDs), use instead:
`uuid()` as the default value.

#### 5.4 Other helpful form settings

- For `date_time`:
  - Widget Type: **DateTime**.
  - Default value: `now()` (or use “Apply default on new features”).
- For `photo_path`:
  - Widget Type: **Text** or “Attachment” if you want a file browser.
- For `gnss_accuracy_m`:
  - Widget Type: **Double** with reasonable range (e.g. 0–100).

You can also use the **Drag and Drop Designer** in the Attributes Form tab to
group fields into logical sections. A suggested grouping:

| Group name        | Fields to include     | Purpose                                      |
|-------------------|------------------------|----------------------------------------------|
| **Observation**   | `id`, `obs_type`, `date_time`, `collector` | Who, when, and what type of observation.     |
| **Position**      | `gnss_accuracy_m`     | GNSS quality for the recorded location.      |
| **Land cover**    | `lc_label`, `ipcc_class` | Detailed LC class and IPCC land-use class.   |
| **Media & notes** | `photo_path`, `notes` | Photo reference and free-text notes.        |

Drag each field into the appropriate group in the form designer so the form
appears in a clear order: identity first, then position quality, land-cover
classification, and finally attachments and notes.

#### 5.5 When using PostgreSQL/PostGIS instead of GeoPackage

Split the setup between database rules and QGIS form design:

**Database-side (SQL)**

- Let PostgreSQL fill `id` automatically with `GENERATED ALWAYS AS IDENTITY`
  or a sequence.
- Let PostgreSQL fill `uuid` with `gen_random_uuid()` if you use UUIDs.
- Let PostgreSQL fill `date_time` with `now()` if you want a database-side
  timestamp.
- Enforce allowed values for `obs_type` and `ipcc_class` with lookup tables
  plus foreign keys. `CHECK` constraints are acceptable for a simple setup, but
  lookup tables are usually better once QGIS forms use `Value Relation`.

Simple `CHECK`-constraint example for both point and polygon tables:

```sql
ALTER TABLE public.observations_point
ADD CONSTRAINT observations_point_obs_type_chk
CHECK (obs_type IN ('ground_truth', 'lc_training', 'lc_validation', 'leakage_check'));

ALTER TABLE public.observations_polygon
ADD CONSTRAINT observations_polygon_obs_type_chk
CHECK (obs_type IN ('ground_truth', 'lc_training', 'lc_validation', 'leakage_check'));

ALTER TABLE public.observations_point
ADD CONSTRAINT observations_point_ipcc_class_chk
CHECK (
  ipcc_class IS NULL OR
  ipcc_class IN ('Forest land', 'Cropland', 'Grassland', 'Wetlands', 'Settlements', 'Other land')
);

ALTER TABLE public.observations_polygon
ADD CONSTRAINT observations_polygon_ipcc_class_chk
CHECK (
  ipcc_class IS NULL OR
  ipcc_class IN ('Forest land', 'Cropland', 'Grassland', 'Wetlands', 'Settlements', 'Other land')
);
```

Preferred lookup-table + foreign-key example:

```sql
ALTER TABLE public.observations_point
DROP CONSTRAINT IF EXISTS observations_point_obs_type_chk;

ALTER TABLE public.observations_polygon
DROP CONSTRAINT IF EXISTS observations_polygon_obs_type_chk;

ALTER TABLE public.observations_point
DROP CONSTRAINT IF EXISTS observations_point_ipcc_class_chk;

ALTER TABLE public.observations_polygon
DROP CONSTRAINT IF EXISTS observations_polygon_ipcc_class_chk;

ALTER TABLE public.observations_point
ADD CONSTRAINT observations_point_obs_type_fk
FOREIGN KEY (obs_type) REFERENCES public.lu_obs_type (code);

ALTER TABLE public.observations_polygon
ADD CONSTRAINT observations_polygon_obs_type_fk
FOREIGN KEY (obs_type) REFERENCES public.lu_obs_type (code);

ALTER TABLE public.observations_point
ADD CONSTRAINT observations_point_ipcc_class_fk
FOREIGN KEY (ipcc_class) REFERENCES public.lu_ipcc_class (code);

ALTER TABLE public.observations_polygon
ADD CONSTRAINT observations_polygon_ipcc_class_fk
FOREIGN KEY (ipcc_class) REFERENCES public.lu_ipcc_class (code);
```

Before adding the foreign keys, make sure any existing values in
`observations_point` and `observations_polygon` already match the `code`
values in `lu_obs_type` and `lu_ipcc_class`, or the `ALTER TABLE` statements
will fail.

**QGIS-side (project/form only)**

- Set `id` to **Read-only**.
- Set `uuid` to **Read-only**.
- Set `date_time` to **Read-only** if the database should always supply it.
- Keep `obs_type` and `ipcc_class` as **Value Relation** widgets so users get a
  friendly dropdown backed by the lookup tables.
- Keep the field groups (`Observation`, `Position`, `Land cover`,
  `Media & notes`) in the form designer.
- For editing, load `observations_point` and `observations_polygon` as your
  working layers.
- For pipeline handoff, load `observations_export` as a fresh PostGIS layer via
  **Layer → Add Layer → Add PostGIS Layers...** rather than trying to repair an
  older broken layer in the project.

Schema visibility in the QGIS Browser is also a QGIS-only preference. It
cannot be controlled from SQL; simply collapse or hide schemas such as `auth`,
`graphql`, `graphql_public`, `pgbouncer`, `realtime`, `storage`, and `vault`
if you do not need them.

#### 5.6 Export PostGIS edits into the pipeline GeoPackage

If you are using PostgreSQL/PostGIS for editing, the existing
`field_pipeline` still expects a file-based GeoPackage input. Use this handoff
workflow:

1. Save edits to `observations_point` and `observations_polygon`.
2. In Supabase, run:
   - `field_pipeline/sql/refresh_observations_export_table.sql`
3. In QGIS, add `observations_export` as a fresh PostGIS vector layer:
   - **Layer → Add Layer → Add PostGIS Layers...**
   - choose the `gold-standard` connection,
   - select `observations_export`,
   - if prompted, use `geom` as geometry column and `qgis_fid` as feature ID.
4. Right-click `observations_export` → **Export → Save Features As...**
5. Set:
   - Format: **GeoPackage**
   - File: `data/incoming/project.gpkg`
   - Layer name: `observations`
6. Open `data/incoming/project.gpkg` and confirm the `observations` layer looks
   correct.

After that, the normal pipeline commands can be run against the exported
GeoPackage.

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

