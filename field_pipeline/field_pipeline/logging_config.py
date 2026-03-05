import logging
from typing import Optional


def setup_logging(name: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
  """
  Configure a simple console logger.

  This is intentionally minimal so it works well in local scripts, CI, and QGIS.
  """
  logger = logging.getLogger(name)
  if logger.handlers:
    return logger

  logger.setLevel(level)
  handler = logging.StreamHandler()
  fmt = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
  )
  handler.setFormatter(fmt)
  logger.addHandler(handler)
  return logger


