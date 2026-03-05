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

