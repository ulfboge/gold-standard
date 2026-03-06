# SQL script index

This folder contains SQL snippets for the PostGIS-backed field collection
workflow.

## Recommended script names in Supabase

If you save these queries in the Supabase SQL editor, use names like:

- `create_observation_tables`
- `create_lookup_tables`
- `add_lookup_foreign_keys`
- `add_conditional_required_checks`
- `refresh_observations_export_table`

## Current files in this folder

- `refresh_observations_export_table.sql`
  - Rebuilds `public.observations_export` from
    `public.observations_point` and `public.observations_polygon`.
  - This is the script to run repeatedly before exporting data to the
    file-based pipeline.

- `create_observations_export_view.sql`
  - Earlier view-based export approach.
  - Keep only as reference. The table-refresh approach is preferred because it
    was more reliable in QGIS for mixed point/polygon geometry.

## Typical setup order

Run these once when setting up the database:

1. Create the observation tables in PostGIS.
2. Create the lookup tables.
3. Add foreign keys from the observation tables to the lookup tables.
4. Add conditional `CHECK` constraints for `lc_label` and `ipcc_class`.

## Typical recurring workflow

Run these whenever you want to hand data off to the existing GeoPackage-based
pipeline:

1. Save edits to `observations_point` and `observations_polygon` in QGIS.
2. Run `refresh_observations_export_table.sql` in Supabase.
3. In QGIS, add `observations_export` as a fresh PostGIS layer.
4. Export it to `data/incoming/project.gpkg` with layer name `observations`.
5. Run the field pipeline commands against that GeoPackage.

## Notes

- `observations_export` is a snapshot table, not a live view. Re-run the
  refresh script after edits.
- The export table uses a pipeline-safe text `id` such as `point_12` or
  `polygon_7`, while preserving the original numeric ID as `source_id`.
