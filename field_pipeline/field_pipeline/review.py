from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import geopandas as gpd
import pandas as pd


def write_observations_review(
  gpkg_path: Path,
  issues: pd.DataFrame,
  id_column: str = "id",
  layer_name: str = "observations_review",
) -> None:
  """
  Aggregate validation issues per observation id and write a review table
  into the same GeoPackage.

  - state = APPROVED if no issues, else NEEDS_REVIEW.
  - error_count / warning_count are based on severity values.
  """
  now = datetime.now(timezone.utc)

  if issues.empty:
    # No issues: we still want a review table, but need ids from source layer.
    src = gpd.read_file(gpkg_path)
    ids = src[id_column].tolist() if id_column in src.columns else []
    rows = [
      {
        id_column: oid,
        "state": "APPROVED",
        "error_count": 0,
        "warning_count": 0,
        "last_checked_at": now,
      }
      for oid in ids
    ]
  else:
    # Aggregate issues per id
    grouped = (
      issues.groupby(id_column)["severity"]
      .agg(
        error_count=lambda s: int((s == "error").sum()),
        warning_count=lambda s: int((s == "warning").sum()),
      )
      .reset_index()
    )

    def _state(row) -> Literal["APPROVED", "NEEDS_REVIEW"]:
      return "APPROVED" if row["error_count"] == 0 and row["warning_count"] == 0 else "NEEDS_REVIEW"

    grouped["state"] = grouped.apply(_state, axis=1)
    grouped["last_checked_at"] = now
    rows = grouped.to_dict(orient="records")

  review_df = pd.DataFrame(rows)
  review_gdf = gpd.GeoDataFrame(review_df, geometry=None)
  review_gdf.to_file(gpkg_path, layer=layer_name, driver="GPKG")

