from pathlib import Path

import geopandas as gpd
import pandas as pd

from .config import PipelineConfig
from .logging_config import setup_logging


logger = setup_logging(__name__)


def summarize(gpkg_path: Path, config: PipelineConfig) -> pd.DataFrame:
  """
  Produce basic summaries from the observations layer.

  Returns a DataFrame (e.g. per obs_type, per collector).
  """
  layer = config.main_layer
  logger.info("Summarizing layer %s in %s", layer, gpkg_path)
  gdf = gpd.read_file(gpkg_path, layer=layer)

  summaries = []

  if "obs_type" in gdf.columns:
    ct = gdf["obs_type"].value_counts().rename_axis("obs_type").reset_index(name="count")
    ct["metric"] = "count_by_obs_type"
    summaries.append(ct)

  if "collector" in gdf.columns:
    ct = gdf["collector"].value_counts().rename_axis("collector").reset_index(name="count")
    ct["metric"] = "count_by_collector"
    summaries.append(ct)

  if summaries:
    out = pd.concat(summaries, ignore_index=True, sort=False)
  else:
    out = pd.DataFrame(columns=["metric"])

  logger.info("Summaries generated: %d rows", len(out))
  return out

