from pathlib import Path

import geopandas as gpd

from .config import PipelineConfig
from .logging_config import setup_logging


logger = setup_logging(__name__)


def export(gpkg_path: Path, config: PipelineConfig) -> None:
  """
  Export the observations layer to CSV and GeoJSON next to the input GeoPackage.
  """
  layer = config.main_layer
  logger.info("Exporting layer %s from %s", layer, gpkg_path)

  gdf = gpd.read_file(gpkg_path, layer=layer)

  base = gpkg_path.with_suffix("")
  csv_path = base.with_suffix(".csv")
  geojson_path = base.with_suffix(".geojson")

  logger.info("Writing CSV to %s", csv_path)
  gdf.drop(columns="geometry").to_csv(csv_path, index=False)

  logger.info("Writing GeoJSON to %s", geojson_path)
  gdf.to_file(geojson_path, driver="GeoJSON")

