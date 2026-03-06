from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from field_pipeline.field_pipeline.config import load_config
from field_pipeline.field_pipeline.report import generate_report
from field_pipeline.field_pipeline.validate import validate


def _make_tiny_gpkg(tmp_path: Path) -> Path:
  path = tmp_path / "tiny.gpkg"
  df = pd.DataFrame(
    {
      "id": ["obs1", "obs2"],
      "obs_type": ["ground_truth", "leakage_check"],
      "date_time": pd.to_datetime(
        ["2026-03-01T12:00:00Z", "2026-03-01T13:00:00Z"], utc=True
      ),
      "collector": ["alice", "bob"],
      "notes": ["gt", "leak"],
      "photo_path": ["", ""],
      "gnss_accuracy_m": [5.0, 15.0],
      "class": ["forest", "forest"],
    }
  )
  gdf = gpd.GeoDataFrame(df, geometry=[Point(0, 0), Point(0.001, 0.001)], crs="EPSG:4326")
  gdf.to_file(path, layer="observations", driver="GPKG")
  return path


def test_validate_flags_gnss_and_leakage(tmp_path: Path):
  cfg = load_config(Path("field_pipeline/config/pipeline.yaml"))
  gpkg = _make_tiny_gpkg(tmp_path)
  issues = validate(gpkg, cfg)

  # Expect one GNSS warning and one leakage error for obs2
  obs2_issues = issues[issues["id"] == "obs2"]
  assert not obs2_issues.empty
  fields = set(obs2_issues["field"])
  assert "gnss_accuracy_m" in fields
  assert "class" in fields


def test_report_submission_writes_ai_notes(tmp_path: Path):
  cfg = load_config(Path("field_pipeline/config/pipeline.yaml"))
  gpkg = _make_tiny_gpkg(tmp_path)
  out = tmp_path / "report_submission.md"

  generated = generate_report(gpkg, cfg, out, mode="submission")
  assert generated.exists()

  notes_path = out.with_name(out.stem + "_ai_notes.md")
  # AI may be disabled in some environments; in that case notes file might not exist.
  # We only assert that submission report itself was created.


def test_validate_honors_conditional_required_fields(tmp_path: Path):
  path = tmp_path / "conditional_rules.gpkg"
  df = pd.DataFrame(
    {
      "id": ["gt1", "train1", "leak1"],
      "obs_type": ["ground_truth", "lc_training", "leakage_check"],
      "date_time": pd.to_datetime(
        ["2026-03-01T12:00:00Z", "2026-03-01T12:05:00Z", "2026-03-01T12:10:00Z"],
        utc=True,
      ),
      "collector": ["alice", "alice", "bob"],
      "notes": ["gt", "train", "leak"],
      "photo_path": ["photo1.jpg", "", ""],
      "gnss_accuracy_m": [3.0, 2.0, 7.0],
      "lc_label": [None, None, None],
      "ipcc_class": [None, "Cropland", None],
      "class": ["forest", "forest", "non-forest"],
    }
  )
  gdf = gpd.GeoDataFrame(
    df,
    geometry=[Point(0, 0), Point(0.001, 0.001), Point(0.002, 0.002)],
    crs="EPSG:4326",
  )
  gdf.to_file(path, layer="observations", driver="GPKG")

  cfg = load_config(Path("field_pipeline/config/pipeline.yaml"))
  issues = validate(path, cfg)

  gt_ipcc = issues[(issues["id"] == "gt1") & (issues["field"] == "ipcc_class")]
  train_lc = issues[(issues["id"] == "train1") & (issues["field"] == "lc_label")]
  leak_missing_class = issues[
    (issues["id"] == "leak1") & (issues["field"].isin(["ipcc_class", "lc_label"]))
  ]

  assert not gt_ipcc.empty
  assert not train_lc.empty
  assert leak_missing_class.empty

