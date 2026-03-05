import argparse
import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import geopandas as gpd
import pandas as pd
from shapely.validation import explain_validity
import yaml


@dataclass
class ValidationIssue:
  table: str
  obs_id: Any
  rule_id: str
  severity: str
  message: str


class MRVValidator:
  def __init__(self, gpkg_path: Path, config_path: Path):
    self.gpkg_path = Path(gpkg_path)
    self.config = self._load_config(config_path)
    self._load_layers()

  def _load_config(self, path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
      return yaml.safe_load(f)

  def _load_layers(self) -> None:
    self.layers: Dict[str, gpd.GeoDataFrame] = {}
    for layer_name in self.config["geopackage"]["layers"].keys():
      try:
        gdf = gpd.read_file(self.gpkg_path, layer=layer_name)
      except Exception:
        gdf = gpd.GeoDataFrame()
      self.layers[layer_name] = gdf

  def run(self) -> pd.DataFrame:
    issues: List[ValidationIssue] = []
    validation_cfg = self.config.get("validation", {})

    for _, rules in validation_cfg.items():
      for rule in rules:
        handler_name = f"run_rule_{rule['type']}"
        handler = getattr(self, handler_name, None)
        if handler is None:
          print(f"[WARN] No handler for rule type {rule['type']}")
          continue
        issues.extend(handler(rule))

    issues_df = pd.DataFrame([i.__dict__ for i in issues]) if issues else pd.DataFrame(
      columns=["table", "obs_id", "rule_id", "severity", "message"]
    )
    self._update_observations_review(issues_df)
    return issues_df

  def run_rule_datetime_not_in_future(self, rule: Dict[str, Any]) -> List[ValidationIssue]:
    table = rule["table"]
    field = rule["field"]
    severity = rule["severity"]
    gdf = self.layers[table]
    issues: List[ValidationIssue] = []
    now = dt.datetime.utcnow()

    for _, row in gdf.iterrows():
      obs_time = row.get(field)
      if pd.isna(obs_time):
        continue
      if obs_time > now:
        issues.append(
          ValidationIssue(
            table=table,
            obs_id=row.get("obs_id"),
            rule_id=rule["id"],
            severity=severity,
            message=f"{field} {obs_time} is in the future (> {now}).",
          )
        )
    return issues

  def run_rule_geometry_not_empty(self, rule: Dict[str, Any]) -> List[ValidationIssue]:
    table = rule["table"]
    severity = rule["severity"]
    gdf = self.layers[table]
    issues: List[ValidationIssue] = []

    for _, row in gdf.iterrows():
      geom_val = row.geometry if "geometry" in row else None
      if geom_val is None or geom_val.is_empty:
        issues.append(
          ValidationIssue(
            table=table,
            obs_id=row.get("obs_id"),
            rule_id=rule["id"],
            severity=severity,
            message="Geometry is empty or null.",
          )
        )
    return issues

  def run_rule_geometry_is_valid(self, rule: Dict[str, Any]) -> List[ValidationIssue]:
    table = rule["table"]
    severity = rule["severity"]
    gdf = self.layers[table]
    issues: List[ValidationIssue] = []

    for _, row in gdf.iterrows():
      g = row.geometry if "geometry" in row else None
      if g is None:
        continue
      if not g.is_valid:
        issues.append(
          ValidationIssue(
            table=table,
            obs_id=row.get("obs_id"),
            rule_id=rule["id"],
            severity=severity,
            message=f"Invalid geometry: {explain_validity(g)}",
          )
        )
    return issues

  def run_rule_geometry_within(self, rule: Dict[str, Any]) -> List[ValidationIssue]:
    table = rule["table"]
    severity = rule["severity"]
    aoi_table = rule["aoi_table"]
    obs_aoi_field = rule["obs_aoi_id_field"]
    aoi_id_field = rule["aoi_id_field"]

    obs_gdf = self.layers[table]
    aoi_gdf = self.layers[aoi_table]
    issues: List[ValidationIssue] = []

    aoi_by_id = {r[aoi_id_field]: r.geometry for _, r in aoi_gdf.iterrows()}

    for _, row in obs_gdf.iterrows():
      g = row.geometry if "geometry" in row else None
      if g is None or g.is_empty:
        continue
      aoi_id = row.get(obs_aoi_field)
      aoi_geom = aoi_by_id.get(aoi_id)
      if aoi_geom is None:
        continue
      if not g.within(aoi_geom):
        issues.append(
          ValidationIssue(
            table=table,
            obs_id=row.get("obs_id"),
            rule_id=rule["id"],
            severity=severity,
            message=f"Geometry not within AOI {aoi_id}.",
          )
        )
    return issues

  def run_rule_required_fields(self, rule: Dict[str, Any]) -> List[ValidationIssue]:
    table = rule["table"]
    severity = rule["severity"]
    req_fields = rule["required_fields"]
    gdf = self.layers[table]
    issues: List[ValidationIssue] = []

    for _, row in gdf.iterrows():
      for f in req_fields:
        if pd.isna(row.get(f)):
          issues.append(
            ValidationIssue(
              table=table,
              obs_id=row.get("obs_id"),
              rule_id=rule["id"],
              severity=severity,
              message=f"Required field {f} is null.",
            )
          )
    return issues

  def run_rule_required_if_obs_type(self, rule: Dict[str, Any]) -> List[ValidationIssue]:
    table = rule["table"]
    severity = rule["severity"]
    target_type = rule["obs_type"]
    req_fields = rule["required_fields"]
    gdf = self.layers[table]
    issues: List[ValidationIssue] = []

    for _, row in gdf.iterrows():
      if row.get("obs_type") != target_type:
        continue
      for f in req_fields:
        if pd.isna(row.get(f)):
          issues.append(
            ValidationIssue(
              table=table,
              obs_id=row.get("obs_id"),
              rule_id=rule["id"],
              severity=severity,
              message=f"For obs_type={target_type}, field {f} is required.",
            )
          )
    return issues

  def run_rule_lookup_membership(self, rule: Dict[str, Any]) -> List[ValidationIssue]:
    table = rule["table"]
    field = rule["field"]
    lookup_table = rule["lookup_table"]
    lookup_field = rule["lookup_field"]
    severity = rule["severity"]

    gdf = self.layers[table]
    lookup_df = self.layers[lookup_table]
    allowed = set(lookup_df[lookup_field].astype(str)) if not lookup_df.empty else set()

    issues: List[ValidationIssue] = []
    for _, row in gdf.iterrows():
      val = row.get(field)
      if pd.isna(val):
        continue
      if str(val) not in allowed:
        issues.append(
          ValidationIssue(
            table=table,
            obs_id=row.get("obs_id"),
            rule_id=rule["id"],
            severity=severity,
            message=f"Value {val!r} for {field} not in lookup {lookup_table}.{lookup_field}.",
          )
        )
    return issues

  def run_rule_lookup_membership_nullable(self, rule: Dict[str, Any]) -> List[ValidationIssue]:
    return self.run_rule_lookup_membership(rule)

  def run_rule_min_attachments_per_obs(self, rule: Dict[str, Any]) -> List[ValidationIssue]:
    table = rule["table"]
    severity = rule["severity"]
    join_table = rule["join_table"]
    obs_types = rule["for_obs_types"]
    min_count = rule["min_count"]
    allowed_file_types = set(rule["allowed_file_types"])

    att_df = self.layers[table]
    obs_df = self.layers[join_table]

    obs_sub = obs_df[obs_df["obs_type"].isin(obs_types)]
    att_sub = att_df[att_df["file_type"].isin(allowed_file_types)]

    counts = att_sub.groupby("obs_id")["attachment_id"].count().to_dict() if not att_sub.empty else {}
    issues: List[ValidationIssue] = []

    for _, row in obs_sub.iterrows():
      oid = row["obs_id"]
      c = counts.get(oid, 0)
      if c < min_count:
        issues.append(
          ValidationIssue(
            table=join_table,
            obs_id=oid,
            rule_id=rule["id"],
            severity=severity,
            message=f"Observation requires at least {min_count} attachments of type {allowed_file_types}, found {c}.",
          )
        )
    return issues

  def run_rule_numeric_max_if_present(self, rule: Dict[str, Any]) -> List[ValidationIssue]:
    table = rule["table"]
    field = rule["field"]
    max_value = rule["max_value"]
    severity = rule["severity"]
    gdf = self.layers[table]
    issues: List[ValidationIssue] = []

    for _, row in gdf.iterrows():
      v = row.get(field)
      if pd.isna(v):
        continue
      if v > max_value:
        issues.append(
          ValidationIssue(
            table=table,
            obs_id=row.get("obs_id"),
            rule_id=rule["id"],
            severity=severity,
            message=f"{field}={v} exceeds max {max_value}.",
          )
        )
    return issues

  def run_rule_potential_duplicate(self, rule: Dict[str, Any]) -> List[ValidationIssue]:
    table = rule["table"]
    severity = rule["severity"]
    fields = rule["fields_for_exact_match"]
    dist_thr = rule["distance_threshold_m"]
    time_thr = dt.timedelta(minutes=rule["time_threshold_minutes"])

    gdf = self.layers[table].copy()
    issues: List[ValidationIssue] = []

    if gdf.empty:
      return issues

    gdf["__group_key"] = gdf[fields].astype(str).agg("|".join, axis=1)

    for _, group in gdf.groupby("__group_key"):
      if len(group) < 2:
        continue
      for i, row_i in group.iterrows():
        for j, row_j in group.iterrows():
          if j <= i:
            continue
          t_i = row_i.get("obs_time")
          t_j = row_j.get("obs_time")
          if pd.isna(t_i) or pd.isna(t_j):
            continue
          if abs(t_i - t_j) > time_thr:
            continue
          g_i = row_i.geometry if "geometry" in row_i else None
          g_j = row_j.geometry if "geometry" in row_j else None
          if g_i is None or g_j is None:
            continue
          dist_deg = g_i.distance(g_j)
          dist_m = dist_deg * 111_139
          if dist_m <= dist_thr:
            for r in (row_i, row_j):
              issues.append(
                ValidationIssue(
                  table=table,
                  obs_id=r.get("obs_id"),
                  rule_id=rule["id"],
                  severity=severity,
                  message=f"Potential duplicate within {dist_thr} m and {time_thr} "
                  f"(group {group['__group_key'].iloc[0]}).",
                )
              )
    return issues

  def _update_observations_review(self, issues_df: pd.DataFrame) -> None:
    obs_gdf = self.layers["observations"]
    now = dt.datetime.utcnow()

    if issues_df.empty:
      agg = pd.DataFrame(columns=["obs_id", "error_count", "warning_count"])
    else:
      def _err_count(x: pd.Series) -> int:
        return int((x == "error").sum())

      def _warn_count(x: pd.Series) -> int:
        return int((x == "warning").sum())

      issue_counts = (
        issues_df.groupby("obs_id")["severity"]
        .agg(error_count=_err_count, warning_count=_warn_count)
        .reset_index()
      )
      agg = issue_counts

    review_rows: List[Dict[str, Any]] = []
    for _, row in obs_gdf.iterrows():
      oid = row["obs_id"]
      counts = agg[agg["obs_id"] == oid]
      if counts.empty:
        e_cnt, w_cnt = 0, 0
      else:
        e_cnt = int(counts["error_count"].iloc[0])
        w_cnt = int(counts["warning_count"].iloc[0])

      auto_passed = e_cnt == 0

      if e_cnt == 0 and w_cnt == 0:
        state = "APPROVED"
      else:
        state = "NEEDS_REVIEW"

      review_rows.append(
        {
          "obs_id": oid,
          "state": state,
          "auto_checks_passed": auto_passed,
          "auto_error_count": e_cnt,
          "auto_warning_count": w_cnt,
          "reviewer_id": None,
          "reviewer_decision": None,
          "reviewer_notes": None,
          "last_checked_at": now,
          "last_updated_at": now,
        }
      )

    review_df = pd.DataFrame(review_rows)
    review_gdf = gpd.GeoDataFrame(review_df, geometry=None)
    review_gdf.to_file(self.gpkg_path, layer="observations_review", driver="GPKG")


def main() -> None:
  parser = argparse.ArgumentParser(description="Validate MRV GeoPackage.")
  parser.add_argument("gpkg", type=str, help="Path to GeoPackage")
  parser.add_argument("config", type=str, help="Path to YAML config")
  parser.add_argument(
    "--report-csv", type=str, default=None, help="Optional path to write validation issues as CSV"
  )
  args = parser.parse_args()

  validator = MRVValidator(args.gpkg, args.config)
  issues_df = validator.run()

  if args.report_csv:
    issues_df.to_csv(args.report_csv, index=False)
  else:
    print(issues_df)


if __name__ == "__main__":
  main()

