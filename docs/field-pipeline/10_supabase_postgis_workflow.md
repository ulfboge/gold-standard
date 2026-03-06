## Optional PostGIS-Compatible Backend Workflow

This page describes an optional workflow where a **PostGIS-compatible backend such as Supabase** is used as the editing backend, while the existing field pipeline still runs against an exported GeoPackage. It is adapted from section 2.1 of `field_pipeline/PROCESS_MANUAL.md`.

---

### When to use this pattern

Use this workflow when:

- You want multi-user editing, database constraints, or central hosting in a PostGIS-compatible backend such as Supabase.
- You want to keep the current CLI and file-based pipeline unchanged.
- You are comfortable using QGIS as the bridge between the database and the GeoPackage-based pipeline.

This is an **upstream handoff pattern**, not a separate pipeline implementation. The CLI still expects a GeoPackage input.

If you are already using Mergin Maps, it is also worth evaluating the official Mergin Maps DB Sync approach, which supports **two-way synchronization between a Mergin Maps project and PostGIS** and includes a QGIS configuration wizard. See the Mergin Maps documentation: [PostgreSQL DB Sync](https://merginmaps.com/docs/dev/dbsync/).

---

### Recommended database pattern

Use separate editable tables for different geometry types, plus a refreshed export table for handoff:

- `public.observations_point` – editable point observations.
- `public.observations_polygon` – editable polygon observations.
- `public.observations_export` – a refreshed export table used only to hand data off to the file-based pipeline.

The repository includes helper SQL in `field_pipeline/sql/`, especially:

- `field_pipeline/sql/refresh_observations_export_table.sql`

That script rebuilds `public.observations_export` from the editable tables so QGIS can export a single pipeline-ready layer.

---

### Data handoff flow

The intended sequence is:

1. Edit observations in your PostGIS-compatible tables.
2. Re-run `refresh_observations_export_table.sql` in your SQL editor.
3. In QGIS, add `observations_export` as a fresh PostGIS layer.
4. Export that layer to `data/incoming/project.gpkg`.
5. Run the usual CLI commands against the exported GeoPackage.

After step 4, the existing pipeline commands behave exactly as they do in the default workflow:

- `ingest`
- `validate`
- `enrich`
- `summarize`
- `export`
- `report`

This remains the most explicit and controllable workflow when you want a dedicated export table such as `observations_export` to mediate between editable database tables and the pipeline input.

---

### Alternative: Mergin Maps DB Sync

The Mergin Maps documentation describes **DB Sync**, a tool for two-way synchronization between a Mergin Maps project and a PostGIS database. According to the docs, it can:

- Push changes from PostGIS into the configured Mergin Maps project.
- Push changes made in the Mergin project GeoPackage back into PostGIS.
- Generate an initial DB Sync configuration file from QGIS using **Mergin Maps -> Configure DB sync**.

Reference:

- [Mergin Maps PostgreSQL DB Sync docs](https://merginmaps.com/docs/dev/dbsync/)
- [MerginMaps/db-sync repository](https://github.com/MerginMaps/db-sync)

For this repository, DB Sync is most relevant when you want the local Mergin project and the database to stay aligned with less manual export work. Even in that setup, the current field pipeline still conceptually starts from the GeoPackage that lands in `data/incoming/`.

In practice, that means there are two optional database-backed patterns:

- **Manual handoff via export table**: refresh `observations_export`, then export to `data/incoming/project.gpkg`.
- **DB Sync-backed handoff**: let Mergin Maps and PostGIS stay synchronized, then run the pipeline on the synced GeoPackage copy.

The manual export-table pattern is still useful when you need strict control over exactly which fields, geometry types, and identifiers are exposed to the pipeline.

---

### Export table design

The export table should provide one geometry column and a stable, pipeline-safe identifier. The current design includes:

- `id` – text identifier such as `point_12` or `polygon_7`.
- `source_id` – original numeric identifier from the source table.
- `source_geometry_type` – whether the feature came from the point or polygon table.
- `geom` – unified geometry column for QGIS export.

This avoids mixed-source ambiguity while preserving enough provenance for traceability.

---

### QGIS export steps

Once `observations_export` has been refreshed in the database:

1. In QGIS, open **Layer -> Add Layer -> Add PostGIS Layers...**
2. Choose the relevant database connection.
3. Add `observations_export`.
4. If prompted, use `geom` as the geometry column and `qgis_fid` as the feature ID.
5. Right-click `observations_export` and choose **Export -> Save Features As...**
6. Set format to **GeoPackage**.
7. Save to `data/incoming/project.gpkg`.
8. Use `observations` as the layer name.

At that point the GeoPackage becomes the pipeline input just like a directly synced Mergin/QGIS dataset.

---

### Configuration implications

The current `pipeline.yaml` does not define database connection settings for the CLI.

- `paths.incoming_gpkg` should point to the exported GeoPackage.
- `paths.incoming_attachments_dir` should still point to the attachments folder used by the pipeline.
- Validation, enrichment, export, and reporting settings remain unchanged.

In other words, a PostGIS-compatible backend changes how observations are edited and handed off, but not how the current CLI processes them.

---

### Attachments in this workflow

If photos or other evidence files are referenced from database records:

- Keep `photo_path` values aligned with the files you place in `data/incoming/attachments/`.
- Ensure the exported GeoPackage uses the same attribute conventions expected by the pipeline.
- Treat the attachments folder as part of the handoff package alongside `project.gpkg`.

This keeps the downstream ingest and review flow consistent with the default file-based setup.

If media handling grows more complex over time, also consider whether Mergin Maps Media Sync is useful for moving or copying attachments into external storage. See `05_attachments.md` for notes and references.

---

### When native DB ingestion becomes interesting

The current export-to-GeoPackage handoff is often the right choice for small teams and explicit review workflows. A move toward native database ingestion becomes more attractive when:

- Multiple editors or reviewers are working concurrently and you need stronger database-side permissions, constraints, and auditability.
- You want validation, enrichment, or reporting to run automatically when records change rather than after a manual export step.
- Dataset size or update frequency makes repeated GeoPackage exports slow or operationally awkward.
- Downstream dashboards, QA workers, or MRV automation already treat the database as the main system of record.
- You want to rely more heavily on database-native logic such as triggers, views, materialized tables, or event-driven processing.

In contrast, the current handoff pattern is still a good fit when:

- You value a simple, explicit export artifact for review and reproducibility.
- Data volumes are modest and processing happens in clear batches.
- QGIS remains the main operational tool for analysts and data stewards.
- You want low infrastructure overhead while the workflow is still evolving.

As a practical rule of thumb, stay GeoPackage-first until the export step becomes a recurring bottleneck or a source of process risk. At that point, native database ingestion is likely worth designing as a separate enhancement.

---

### Limits of the current approach

This workflow is practical, but it is still a bridge into the file-based pipeline rather than native database execution.

Current limitations:

- The CLI does not read directly from a PostGIS-compatible backend.
- Export to GeoPackage is a manual or semi-manual handoff step.
- Attachments are still managed as files outside the database.

If direct database ingestion becomes a project goal later, that would be a separate enhancement to document and implement.
