-- Rebuild a pipeline-ready export table from the PostGIS editing tables.
-- Use this instead of a view when QGIS does not recognize a mixed-geometry
-- union view as a spatial layer.

DROP VIEW IF EXISTS public.observations_export;
DROP TABLE IF EXISTS public.observations_export;

CREATE TABLE public.observations_export AS
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

ALTER TABLE public.observations_export
  ADD PRIMARY KEY (qgis_fid);

CREATE INDEX observations_export_geom_gix
  ON public.observations_export
  USING gist (geom);
