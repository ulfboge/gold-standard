from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class PathsConfig:
  incoming_gpkg: Path
  incoming_attachments_dir: Path
  processed_dir: Path
  context_dir: Path


@dataclass
class FieldRule:
  name: str
  required: bool = False
  required_if_photo: bool = False
  min_gnss_accuracy_m: Optional[float] = None
  max_gnss_accuracy_m: Optional[float] = None
  allowed_values: Optional[List[str]] = None


@dataclass
class EnrichmentLayer:
  name: str
  path: Path
  join_type: str  # e.g. "spatial", "attribute"
  # TODO: add CRS override, join fields, filters as needed


@dataclass
class PipelineConfig:
  paths: PathsConfig
  main_layer: str
  crs_fallback: str
  required_fields: Dict[str, FieldRule]
  enrichment_layers: List[EnrichmentLayer]
  ai_enabled: bool
  ai_provider: Optional[str]
  rules: Dict[str, Dict[str, Any]]
  rag_enabled: bool
  rag_docs_dir: Path
  rag_top_k: int


def _load_yaml(path: Path) -> Dict[str, Any]:
  with path.open("r", encoding="utf-8") as f:
    return yaml.safe_load(f)


def load_config(path: Path) -> PipelineConfig:
  raw = _load_yaml(path)

  paths_cfg = raw.get("paths", {})
  paths = PathsConfig(
    incoming_gpkg=Path(paths_cfg.get("incoming_gpkg", "data/incoming/project.gpkg")),
    incoming_attachments_dir=Path(
      paths_cfg.get("incoming_attachments_dir", "data/incoming/attachments")
    ),
    processed_dir=Path(paths_cfg.get("processed_dir", "data/processed")),
    context_dir=Path(paths_cfg.get("context_dir", "data/context")),
  )

  req_fields_raw = raw.get("required_fields", {})
  required_fields: Dict[str, FieldRule] = {}
  for name, cfg in req_fields_raw.items():
    required_fields[name] = FieldRule(
      name=name,
      required=bool(cfg.get("required", False)),
      required_if_photo=bool(cfg.get("required_if_photo", False)),
      min_gnss_accuracy_m=cfg.get("min_gnss_accuracy_m"),
      max_gnss_accuracy_m=cfg.get("max_gnss_accuracy_m"),
      allowed_values=cfg.get("allowed_values"),
    )

  enrich_raw = raw.get("enrichment_layers", [])
  enrichment_layers: List[EnrichmentLayer] = []
  for layer in enrich_raw:
    enrichment_layers.append(
      EnrichmentLayer(
        name=layer["name"],
        path=Path(layer["path"]),
        join_type=layer.get("join_type", "spatial"),
      )
    )

  ai_cfg = raw.get("ai", {}) or {}
  rules_cfg = raw.get("rules", {}) or {}
  rag_cfg = raw.get("rag", {}) or {}

  return PipelineConfig(
    paths=paths,
    main_layer=raw.get("main_layer", "observations"),
    crs_fallback=raw.get("crs_fallback", "EPSG:4326"),
    required_fields=required_fields,
    enrichment_layers=enrichment_layers,
    ai_enabled=bool(ai_cfg.get("enabled", False)),
    ai_provider=ai_cfg.get("provider"),
    rules=rules_cfg,
    rag_enabled=bool(rag_cfg.get("enabled", False)),
    rag_docs_dir=Path(rag_cfg.get("docs_dir", "docs")),
    rag_top_k=int(rag_cfg.get("top_k", 3)),
  )

