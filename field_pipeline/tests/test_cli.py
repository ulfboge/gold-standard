import pytest
from typer.testing import CliRunner

from field_pipeline.field_pipeline.cli import app


runner = CliRunner()


def test_cli_help():
  """
  Basic smoke test to ensure the CLI loads.

  TODO: add more specific tests per command as the pipeline is implemented.
  """
  result = runner.invoke(app, ["--help"])
  assert result.exit_code == 0
  assert "Field data pipeline CLI" in result.output

