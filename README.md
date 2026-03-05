## Gold Standard MRV Field & Land‑Cover Pipeline

This repository hosts a prototype **MRV pipeline** for projects seeking certification under **Gold Standard for the Global Goals (GS4GG)**, with an initial focus on **Afforestation/Reforestation (A/R)** activities.

The project brings together:

- **Field data pipeline (`field_pipeline/`)**  
  A Mergin Maps + QGIS → GeoPackage → evidence workflow:
  - Ingest incoming field GeoPackages and attachments into timestamped run folders.
  - Validate schema, geometry and basic data‑quality rules.
  - Enrich observations with context layers (admin boundaries, protected areas, land‑cover).
  - Export to CSV/GeoJSON and generate Markdown reports for internal and external use.

- **MRV validation (`mrv_validation/`)**  
  A schema and rule set for validating MRV GeoPackages against a structured specification:
  - Tables for observations, attachments, AOI, monitoring periods, and lookup values.
  - Validation rules for temporal consistency, geometry, lookups, attachments and GNSS precision.

- **EO workflow for Gold Standard A/R**  
  A checklist‑style description of all key tasks for EO/GIS specialists:
  - Forest/non‑forest eligibility assessment (LUF Annex C).
  - Baseline land‑cover and carbon pool inputs.
  - Leakage mapping support.
  - Monitoring and performance‑certification cycles.

For a user‑friendly overview, see the GitHub Pages site generated from the `docs/` folder.

---

## Documentation

High‑level docs for GitHub Pages live under `docs/`:

- `docs/index.md` – site landing page and navigation.
- `docs/gold-standard/EO_workflow_GS_AR_field_pipeline.md` – EO workflow for Gold Standard A/R projects.

More detailed, implementation‑focused docs are kept close to the code:

- `field_pipeline/PROCESS_MANUAL.md` – how to run and extend the field data pipeline.
- `field_pipeline/docs/field_schema_lc_training.md` – suggested field schema for land‑cover training/validation.
- `mrv_validation/mrv_schema.yaml` – MRV GeoPackage schema and validation configuration.

---

## GitHub Pages

The documentation in `docs/` is set up to be served via **GitHub Pages**.

- **Hosted docs URL** (once Pages is enabled on GitHub):  
  `https://ulfboge.github.io/gold-standard/`

See `docs/index.md` for more details on how the site is structured.

