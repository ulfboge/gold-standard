## Testing and CI

This page summarises how to run tests locally and how CI is configured. It is adapted from section 8 of `field_pipeline/PROCESS_MANUAL.md`.

---

### Local tests

From the repository root:

```bash
pytest field_pipeline/tests
```

Current tests:

- `field_pipeline/tests/test_cli.py` – a basic smoke test ensuring the CLI loads and responds to `--help`.

You can add more tests per command, for example:

- Verifying that `ingest` copies files correctly into a `run_<timestamp>/` directory.
- Ensuring `validate` detects and reports missing fields or invalid geometries.
- Checking that `enrich` produces an output GeoPackage with expected columns.

---

### GitHub Actions

The workflow `.github/workflows/field-pipeline-ci.yml`:

- Triggers on pushes and pull requests affecting `field_pipeline/**`.
- Runs on Ubuntu and:
  - Installs necessary GDAL system packages.
  - Installs Python dependencies from `field_pipeline/requirements.txt`.
  - Executes `pytest field_pipeline/tests -vv`.

You can extend this CI setup with:

- Linting (for example `ruff`, `flake8`).
- Formatting checks (for example `black`).
- Additional integration tests (for example minimal sample GeoPackages committed to the repo).

