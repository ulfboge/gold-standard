from datetime import datetime, timezone
from pathlib import Path
from typing import List

import geopandas as gpd
import pandas as pd
from shapely.validation import explain_validity

from .config import PipelineConfig
from .review import write_observations_review
from .logging_config import setup_logging


logger = setup_logging(__name__)


def _is_missing(value) -> bool:
  if pd.isna(value):
    return True
  if isinstance(value, str) and not value.strip():
    return True
  return False


def validate(gpkg_path: Path, config: PipelineConfig) -> pd.DataFrame:
  """
  Perform schema, geometry, and basic temporal/accuracy checks on the main layer.

  Returns a DataFrame of issues (can be empty).
  """
  layer = config.main_layer
  logger.info("Validating layer %s in %s", layer, gpkg_path)

  gdf = gpd.read_file(gpkg_path, layer=layer)
  issues: List[dict] = []

  # CRS check
  if gdf.crs is None:
    logger.warning("Layer %s has no CRS; using fallback %s", layer, config.crs_fallback)
    gdf.set_crs(config.crs_fallback, inplace=True)

  # Required fields in schema
  for field_name, rule in config.required_fields.items():
    if field_name not in gdf.columns and field_name != "geometry":
      issues.append(
        {
          "id": None,
          "field": field_name,
          "severity": "error",
          "message": f"Missing required field in schema: {field_name}",
        }
      )

  now_utc = datetime.now(timezone.utc)

  rules = config.rules or {}

  def _rule_severity(rule_id: str, default: str) -> str:
    cfg = rules.get(rule_id, {})
    return cfg.get("severity", default)

  # Row-level checks
  for _, row in gdf.iterrows():
    obs_id = row.get("id")
    obs_type = row.get("obs_type")

    # Required fields non-null
    for field_name, rule in config.required_fields.items():
      if field_name == "geometry":
        continue
      field_value = row.get(field_name)
      required_for_this_row = rule.required or (
        rule.required_for_obs_types is not None and obs_type in rule.required_for_obs_types
      )
      if required_for_this_row and _is_missing(field_value):
        issues.append(
          {
            "id": obs_id,
            "field": field_name,
            "severity": "error",
            "message": f"Required field {field_name} is null.",
          }
        )
      # Simple allowed_values check (for e.g. ipcc_class) if configured
      if rule.allowed_values is not None:
        val = field_value
        if pd.notna(val) and str(val) not in rule.allowed_values:
          issues.append(
            {
              "id": obs_id,
              "field": field_name,
              "severity": "error",
              "message": f"Value {val!r} for {field_name} not in allowed set {rule.allowed_values}.",
            }
          )

    # Temporal check: date_time not in the future (if present)
    if "date_time" in gdf.columns:
      dt_val = row.get("date_time")
      if pd.notna(dt_val):
        # Ensure timezone-aware comparison where possible
        if not isinstance(dt_val, datetime):
          # pandas may give Timestamp; convert to python datetime
          dt_val = pd.to_datetime(dt_val).to_pydatetime()
        if dt_val.tzinfo is None:
          dt_val = dt_val.replace(tzinfo=timezone.utc)
        if dt_val > now_utc:
          issues.append(
            {
              "id": obs_id,
              "field": "date_time",
              "severity": "error",
              "message": f"date_time {dt_val.isoformat()} is in the future (>{now_utc.isoformat()}).",
            }
          )

    # GNSS accuracy checks (if configured)
    if "gnss_accuracy_m" in gdf.columns:
      rule = config.required_fields.get("gnss_accuracy_m")
      acc_val = row.get("gnss_accuracy_m")
      if rule and pd.notna(acc_val):
        try:
          acc_val = float(acc_val)
        except (TypeError, ValueError):
          issues.append(
            {
              "id": obs_id,
              "field": "gnss_accuracy_m",
              "severity": _rule_severity("gnss_accuracy", "warning"),
              "message": f"gnss_accuracy_m value {acc_val!r} is not numeric.",
            }
          )
        else:
          if rule.min_gnss_accuracy_m is not None and acc_val < rule.min_gnss_accuracy_m:
            issues.append(
              {
                "id": obs_id,
                "field": "gnss_accuracy_m",
                "severity": _rule_severity("gnss_accuracy", "warning"),
                "message": f"gnss_accuracy_m={acc_val} is below minimum {rule.min_gnss_accuracy_m}.",
              }
            )
          if rule.max_gnss_accuracy_m is not None and acc_val > rule.max_gnss_accuracy_m:
            issues.append(
              {
                "id": obs_id,
                "field": "gnss_accuracy_m",
                "severity": _rule_severity("gnss_accuracy", "warning"),
                "message": f"gnss_accuracy_m={acc_val} exceeds max {rule.max_gnss_accuracy_m}.",
              }
            )
          # Extra, tighter check for lc_training / lc_validation (e.g. <= 5 m)
          if obs_type in ("lc_training", "lc_validation") and acc_val > 5.0:
            issues.append(
              {
                "id": obs_id,
                "field": "gnss_accuracy_m",
                "severity": _rule_severity("gnss_accuracy_training", "warning"),
                "message": f"gnss_accuracy_m={acc_val} exceeds preferred max 5.0 for {obs_type}.",
              }
            )

    # Land-cover / context-based rule:
    # - ground_truth should be in forest
    # - leakage_check should not be in forest or protected areas
    if "obs_type" in gdf.columns:
      # Ground truth in forest
      if obs_type == "ground_truth" and "class" in gdf.columns:
        lc_class = row.get("class")
        if pd.isna(lc_class):
            issues.append(
              {
                "id": obs_id,
                "field": "class",
                "severity": _rule_severity("ground_truth_in_forest", "warning"),
                "message": "Land-cover class is missing for ground_truth observation.",
              }
            )
        elif str(lc_class).lower() != "forest":
          issues.append(
            {
              "id": obs_id,
              "field": "class",
              "severity": _rule_severity("ground_truth_in_forest", "warning"),
              "message": f"Ground-truth observation has non-forest land-cover class: {lc_class!r}.",
            }
          )

      # Leakage check outside forest/protected areas (if attributes present)
      if obs_type == "leakage_check":
        # Land cover
        if "class" in gdf.columns:
          lc_class = row.get("class")
          if pd.notna(lc_class) and str(lc_class).lower() == "forest":
            issues.append(
              {
                "id": obs_id,
                "field": "class",
                "severity": _rule_severity("leakage_in_forest", "error"),
                "message": "leakage_check observation falls in forest land cover.",
              }
            )

        # Protected area membership: presence of a non-null pa_id indicates overlap
        if "pa_id" in gdf.columns:
          pa_id = row.get("pa_id")
          if pd.notna(pa_id):
            issues.append(
              {
                "id": obs_id,
                "field": "pa_id",
                "severity": "warning",
                "message": f"leakage_check observation is inside protected area {pa_id!r}.",
              }
            )

    # Photo rules:
    # - For ground_truth observations, photo_path must be non-empty
    # - If photo_path is non-empty, file should exist under attachments/
    if "photo_path" in gdf.columns:
      photo_path = row.get("photo_path")
      if obs_type == "ground_truth" and (not isinstance(photo_path, str) or not photo_path.strip()):
        issues.append(
          {
            "id": obs_id,
            "field": "photo_path",
            "severity": _rule_severity("ground_truth_photo_missing", "warning"),
            "message": "ground_truth observation is missing a required photo_path.",
          }
        )

      if isinstance(photo_path, str) and photo_path.strip():
        att_root = gpkg_path.parent / "attachments"
        candidate = att_root / photo_path
        if not candidate.exists():
          issues.append(
            {
              "id": obs_id,
              "field": "photo_path",
              "severity": "warning",
              "message": f"Photo file not found at expected path: {candidate}",
            }
          )

    # Geometry sanity
    geom_val = row.geometry
    if geom_val is None or geom_val.is_empty:
      issues.append(
        {
          "id": obs_id,
          "field": "geometry",
          "severity": "error",
          "message": "Geometry is empty or null.",
        }
      )
    elif not geom_val.is_valid:
      issues.append(
        {
          "id": obs_id,
          "field": "geometry",
          "severity": "error",
          "message": f"Invalid geometry: {explain_validity(geom_val)}",
        }
      )

  issues_df = pd.DataFrame(issues)
  if not issues_df.empty:
    logger.info("Validation finished with %d issues.", len(issues_df))
  else:
    logger.info("Validation finished: no issues found.")

  # Write/update observations_review table to support QGIS review workflows
  try:
    write_observations_review(gpkg_path, issues_df)
  except Exception as exc:
    logger.warning("Failed to write observations_review table: %s", exc)

  return issues_df


