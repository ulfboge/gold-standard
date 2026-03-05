import shutil
from datetime import datetime
from pathlib import Path
from typing import Tuple

from .config import PipelineConfig
from .logging_config import setup_logging


logger = setup_logging(__name__)


def ingest(config: PipelineConfig) -> Tuple[Path, Path]:
  """
  Copy the latest GeoPackage and attachments into processed/ with a timestamp.

  Raw data in data/incoming/ is treated as immutable.
  """
  src_gpkg = config.paths.incoming_gpkg
  src_att_dir = config.paths.incoming_attachments_dir

  if not src_gpkg.exists():
    raise FileNotFoundError(f"Incoming GeoPackage not found: {src_gpkg}")

  ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
  run_dir = config.paths.processed_dir / f"run_{ts}"
  run_dir.mkdir(parents=True, exist_ok=True)

  dst_gpkg = run_dir / src_gpkg.name
  logger.info("Copying GeoPackage %s -> %s", src_gpkg, dst_gpkg)
  shutil.copy2(src_gpkg, dst_gpkg)

  dst_att_dir = run_dir / "attachments"
  if src_att_dir.exists():
    logger.info("Copying attachments %s -> %s", src_att_dir, dst_att_dir)
    if dst_att_dir.exists():
      shutil.rmtree(dst_att_dir)
    shutil.copytree(src_att_dir, dst_att_dir)
  else:
    logger.info("No attachments directory found at %s", src_att_dir)

  logger.info("Ingest complete. Run directory: %s", run_dir)
  return dst_gpkg, dst_att_dir

