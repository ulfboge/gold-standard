-- LEGACY / REFERENCE ONLY
--
-- This older view-based export approach was kept for reference, but it is not
-- the recommended workflow anymore.
--
-- Use `field_pipeline/sql/refresh_observations_export_table.sql` instead.
-- The table-refresh approach was more reliable in QGIS for mixed point/polygon
-- geometry and is the workflow documented in the manuals.
--
-- Create a single export view for the file-based field pipeline.
-- This keeps PostGIS as the editing backend while producing one canonical
-- layer that can be exported from QGIS to data/incoming/project.gpkg
-- with layer name "observations".

CREATE OR REPLACE VIEW public.observations_export AS
SELECT
  row_number() OVER () AS qgis_fid,
  merged.source_geometry_type,
  merged.id,
  merged.source_id,
  merged.uuid,
  merged.obs_type,
  merged.date_time,
  merged.collector,
  merged.gnss_accuracy_m,
  merged.lc_label,
  merged.ipcc_class,
  merged.notes,
  merged.photo_path,
  merged.geom
FROM (
  SELECT
    'point'::text AS source_geometry_type,
    ('point_' || id::text) AS id,
    id AS source_id,
    uuid,
    obs_type,
    date_time,
    collector,
    gnss_accuracy_m,
    lc_label,
    ipcc_class,
    notes,
    photo_path,
    geom::geometry(Geometry, 4326) AS geom
  FROM public.observations_point

  UNION ALL

  SELECT
    'polygon'::text AS source_geometry_type,
    ('polygon_' || id::text) AS id,
    id AS source_id,
    uuid,
    obs_type,
    date_time,
    collector,
    gnss_accuracy_m,
    lc_label,
    ipcc_class,
    notes,
    photo_path,
    geom::geometry(Geometry, 4326) AS geom
  FROM public.observations_polygon
) AS merged;
