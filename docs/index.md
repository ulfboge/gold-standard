## Gold Standard MRV Field & Land‑Cover Pipeline

This site documents a prototype **Gold Standard–aligned MRV pipeline** for EO and field data, focused on Afforestation/Reforestation (A/R) projects.

The repository brings together:

- **Field data pipeline** – a Mergin Maps → GeoPackage → evidence workflow (`field_pipeline/`).
- **MRV GeoPackage validation** – schema + rules for structuring MRV observations (`mrv_validation/`).
- **EO workflow** – end‑to‑end tasks for remote sensing and GIS specialists working under Gold Standard A/R requirements.

---

## Documentation

- **EO workflow for Gold Standard A/R projects**  
  High‑level checklist for EO/GIS specialists, aligned with GS4GG Principles & Requirements, Land‑Use & Forests Activity Requirements, and the A/R GHG Methodology:
  - [`EO_workflow_GS_AR_field_pipeline.md`](gold-standard/EO_workflow_GS_AR_field_pipeline.md)

- **Forest / non-forest notebook prototype**  
  Notebook-based prototype for running a forest/non-forest classification workflow and opening it in Google Colab:
  - [`forest_nonforest_prototype.md`](forest_nonforest_prototype.md)

- **Field data pipeline (Mergin Maps → evidence packages)**  
  How to run the field pipeline locally, split into focused pages:
  - [1. Overview](field-pipeline/01_overview.md)
  - [2. Folder structure and key files](field-pipeline/02_folder_structure.md)
  - [3. Configuration (`pipeline.yaml`)](field-pipeline/03_configuration.md)
  - [4. CLI commands](field-pipeline/04_cli_commands.md)
  - [5. Attachments handling](field-pipeline/05_attachments.md)
  - [6. Review outputs and immutability](field-pipeline/06_review_outputs.md)
  - [7. AI integration (optional)](field-pipeline/07_ai_integration.md)
  - [8. Testing and CI](field-pipeline/08_testing_ci.md)
  - [9. Customization roadmap](field-pipeline/09_customization_roadmap.md)
  - [10. Optional PostGIS-compatible backend workflow](field-pipeline/10_supabase_postgis_workflow.md)

- **Field schema for land‑cover training**  
  Suggested schema and aliases for land‑cover training / validation points:
  - [`field_pipeline/docs/field_schema_lc_training.md` on GitHub](https://github.com/ulfboge/gold-standard/blob/main/field_pipeline/docs/field_schema_lc_training.md)

> More internal/technical documents (e.g. validation schemas, scripts, tests) are available directly in the repository view on GitHub.

---

## Using this Site with GitHub Pages

To publish this documentation as a GitHub Pages site:

1. In the GitHub UI for `ulfboge/gold-standard`, go to **Settings → Pages**.  
2. Under **Build and deployment**, set:
   - **Source**: `Deploy from a branch`
   - **Branch**: `main`, folder: `/docs`
3. Save – GitHub Pages will build the site from this `docs/` folder.

The home page will be this `index.md`, and additional pages under `docs/` (such as the EO workflow) will appear as separate URLs.

