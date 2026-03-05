from pathlib import Path

import geopandas as gpd

from .config import PipelineConfig
from .logging_config import setup_logging


logger = setup_logging(__name__)


def enrich(gpkg_path: Path, config: PipelineConfig) -> Path:
  """
  Enrich the main observations layer with configured context layers.

  Writes a new GeoPackage in the same directory with suffix `_enriched.gpkg`
  and returns its path.
  """
  obs_layer = config.main_layer
  logger.info("Enriching layer %s in %s", obs_layer, gpkg_path)

  gdf = gpd.read_file(gpkg_path, layer=obs_layer)

  if gdf.crs is None:
    logger.info("Setting CRS to fallback %s", config.crs_fallback)
    gdf.set_crs(config.crs_fallback, inplace=True)

  for layer_cfg in config.enrichment_layers:
    ctx_path = layer_cfg.path
    if not ctx_path.exists():
      logger.warning("Context layer %s not found at %s (skipping)", layer_cfg.name, ctx_path)
      continue

    logger.info("Joining context layer %s from %s", layer_cfg.name, ctx_path)
    ctx_gdf = gpd.read_file(ctx_path)
    if ctx_gdf.crs and ctx_gdf.crs != gdf.crs:
      logger.info("Reprojecting context layer %s to %s", layer_cfg.name, gdf.crs)
      ctx_gdf = ctx_gdf.to_crs(gdf.crs)

    # TODO: make join parameters configurable per layer.
    if layer_cfg.join_type == "spatial":
      ctx_cols = [c for c in ctx_gdf.columns if c != "geometry"]
      gdf = gpd.sjoin(gdf, ctx_gdf[ctx_cols + ["geometry"]], how="left")
      gdf = gdf.drop(columns=[c for c in ("index_right",) if c in gdf.columns])
    else:
      logger.warning("Join type %s not implemented; skipping layer %s", layer_cfg.join_type, layer_cfg.name)

  out_path = gpkg_path.with_name(gpkg_path.stem + "_enriched.gpkg")
  logger.info("Writing enriched data to %s", out_path)
  gdf.to_file(out_path, layer=obs_layer, driver="GPKG")
  return out_path

