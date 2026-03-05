from pathlib import Path
from typing import Optional

import typer

from .config import load_config
from .enrich import enrich as enrich_cmd
from .export import export as export_cmd
from .ingest import ingest as ingest_cmd
from .logging_config import setup_logging
from .report import generate_report
from .summarize import summarize as summarize_cmd
from .validate import validate as validate_cmd


app = typer.Typer(help="Field data pipeline CLI for Mergin Maps GeoPackages.")
logger = setup_logging(__name__)


def _load_pipeline_config(config_path: Path):
  return load_config(config_path)


@app.command()
def ingest(
  config: Path = typer.Option(
    Path("field_pipeline/config/pipeline.yaml"),
    "--config",
    "-c",
    help="Path to pipeline configuration YAML.",
  ),
) -> None:
  """
  Ingest latest incoming GeoPackage + attachments into data/processed/.
  """
  cfg = _load_pipeline_config(config)
  dst_gpkg, dst_att = ingest_cmd(cfg)
  typer.echo(f"Ingested to: {dst_gpkg} (attachments: {dst_att})")


@app.command()
def validate(
  gpkg: Optional[Path] = typer.Option(
    None,
    "--gpkg",
    help="Path to GeoPackage to validate (defaults to incoming_gpkg from config).",
  ),
  config: Path = typer.Option(
    Path("field_pipeline/config/pipeline.yaml"),
    "--config",
    "-c",
    help="Path to pipeline configuration YAML.",
  ),
) -> None:
  """
  Validate schema, required fields, and geometry sanity.
  """
  cfg = _load_pipeline_config(config)

  target = gpkg or cfg.paths.incoming_gpkg
  issues = validate_cmd(target, cfg)
  if issues.empty:
    typer.echo("Validation OK, no issues found.")
  else:
    typer.echo(issues.to_string(index=False))


@app.command()
def enrich(
  gpkg: Optional[Path] = typer.Option(
    None,
    "--gpkg",
    help="Path to GeoPackage to enrich (defaults to incoming_gpkg from config).",
  ),
  config: Path = typer.Option(
    Path("field_pipeline/config/pipeline.yaml"),
    "--config",
    "-c",
    help="Path to pipeline configuration YAML.",
  ),
) -> None:
  """
  Enrich observations with configured context layers.
  """
  cfg = _load_pipeline_config(config)

  target = gpkg or cfg.paths.incoming_gpkg
  out = enrich_cmd(target, cfg)
  typer.echo(f"Enriched GeoPackage written to: {out}")


@app.command()
def summarize(
  gpkg: Optional[Path] = typer.Option(
    None,
    "--gpkg",
    help="Path to GeoPackage to summarize (defaults to incoming_gpkg from config).",
  ),
  config: Path = typer.Option(
    Path("field_pipeline/config/pipeline.yaml"),
    "--config",
    "-c",
    help="Path to pipeline configuration YAML.",
  ),
) -> None:
  """
  Produce simple summaries (per obs_type, per collector).
  """
  cfg = _load_pipeline_config(config)

  target = gpkg or cfg.paths.incoming_gpkg
  df = summarize_cmd(target, cfg)
  typer.echo(df.to_string(index=False))


@app.command()
def export(
  gpkg: Optional[Path] = typer.Option(
    None,
    "--gpkg",
    help="Path to GeoPackage to export (defaults to incoming_gpkg from config).",
  ),
    config: Path = typer.Option(
    Path("field_pipeline/config/pipeline.yaml"),
    "--config",
    "-c",
    help="Path to pipeline configuration YAML.",
  ),
) -> None:
  """
  Export observations to CSV and GeoJSON next to the GeoPackage.
  """
  cfg = _load_pipeline_config(config)

  target = gpkg or cfg.paths.incoming_gpkg
  export_cmd(target, cfg)
  typer.echo("Exports written.")


@app.command()
def report(
  gpkg: Optional[Path] = typer.Option(
    None,
    "--gpkg",
    help="Path to GeoPackage to report on (defaults to incoming_gpkg from config).",
  ),
  output: Optional[Path] = typer.Option(
    None,
    "--output",
    "-o",
    help="Output Markdown path (defaults to data/processed/report.md).",
  ),
  mode: str = typer.Option(
    "internal",
    "--mode",
    help="Report mode: 'internal' (AI narrative inline) or 'submission' (AI notes separate).",
  ),
  config: Path = typer.Option(
    Path("field_pipeline/config/pipeline.yaml"),
    "--config",
    "-c",
    help="Path to pipeline configuration YAML.",
  ),
) -> None:
  """
  Generate a human-readable Markdown report.
  """
  cfg = _load_pipeline_config(config)

  target = gpkg or cfg.paths.incoming_gpkg
  out = output or Path("data/processed/report.md")
  generated = generate_report(target, cfg, out, mode=mode)
  typer.echo(f"Report written to: {generated}")


if __name__ == "__main__":
  app()

