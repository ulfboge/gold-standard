## EO Workflow for Gold Standard A/R Projects

**Title**: Gold Standard MRV Field & Land‑Cover Pipeline – EO Specialist Workflow  
**Scope**: EO/GIS tasks for Afforestation/Reforestation (A/R) projects under Gold Standard for the Global Goals (GS4GG), aligned with internal `field_pipeline` and `mrv_validation` tooling.

---

## 1. Purpose, Scope & Key References

- **Purpose**: Define the end‑to‑end workflow for the EO/GIS specialist supporting a Gold Standard A/R project, from spatial eligibility assessment to monitoring and performance certification.
- **Applies to**:
  - Gold Standard A/R projects using the **Gold Standard MRV Field & Land‑Cover Pipeline** (`field_pipeline/` plus `mrv_validation/`).
  - Projects that rely on field data collected via **Mergin Maps + QGIS** and remote‑sensing products (forest/non‑forest, land‑cover, leakage indicators).
- **Core GS documents** (see [Gold Standard core documents](https://globalgoals.goldstandard.org/all-documents/#core)):
  - `Principles & Requirements` (PAR)
  - `Safeguarding Principles & Requirements`
  - `Stakeholder Consultation and Engagement Requirements`
  - `Requirements for selection of Monitoring Indicators in the SDG Impact Tool`
  - `Validation and Verification Standard`
- **Activity / Methodology / Product**:
  - `Land Use & Forests Activity Requirements` (LUF), including **Annex C – Spatial forest/non‑forest assessment**.
  - `A/R GHG emission reduction & sequestration methodology` (v2.1).
  - `GHG Emissions Reductions & Sequestration Product Requirements` (for GS VERs).

---

## 2. Pre‑Project Setup (Once per Project)

### 2.1 Confirm project configuration & standards

- Agree with the project developer and MRV lead on:
  - Which GS versions apply (PAR, LUF, A/R Methodology, Product Requirements).
  - Which PDD / consolidated A/R template sections the EO specialist provides (e.g. spatial eligibility, baseline land‑cover, MU maps, RS methods annexes).

### 2.2 Configure QGIS + Mergin field project

- Set up the QGIS project as described in `field_pipeline/qgis_project/SETUP_QGIS_PROJECT.md`:
  - Main observations layer name: typically `observations`.
  - GeoPackage backend: `project.gpkg`.
  - Attachments stored alongside in `attachments/`.
- Align schema and forms with:
  - `field_pipeline/config/pipeline.yaml` (fields such as `id` / `obs_id`, `obs_type`, `date_time` / `obs_time`, `collector` / `collector_id`, `landcover_class`, `photo_path`, `gnss_accuracy_m`).
  - `mrv_validation/mrv_schema.yaml` (long‑term MRV GeoPackage structure: `observations`, `observations_review`, `attachments`, `aoi`, `monitoring_periods`, lookups, validation rules).

### 2.3 Configure context data & RS environment

- Prepare `data/context/` datasets referenced in `field_pipeline/config/pipeline.yaml`, for example:
  - `admin_boundaries.gpkg`
  - `protected_areas.gpkg`
  - `land_cover.gpkg`
- Decide on and document:
  - Project CRS(es): WGS84 for global consistency plus any local projected CRS for area/biomass.
  - RS tooling stack: GEE, QGIS, Python/R for classifications, time‑series analyses, and uncertainty calculations.

---

## 3. Forest / Non‑Forest Eligibility Assessment (Design Stage)

**Goal**: Identify the eligible planting area according to LUF and A/R Methodology rules, using remote sensing and (where needed) field data.

### 3.1 Define forest criteria and minimum mapping unit

- Confirm the **forest definition** to be used:
  - Prefer **DNA definition** for the host country.
  - If not available, use FAO or national definition as allowed in LUF and A/R Methodology.
- From this definition, document:
  - Minimum tree height, canopy cover, and minimum area.
  - Mapping unit or tree‑cover threshold used in classification.

### 3.2 Acquire and preprocess imagery

- Acquire imagery covering the full **project area** for:
  - At least **10 years before project start date**.
  - Around **project start date** (or as close as possible, justified).
- Preprocess:
  - Atmospheric correction.
  - Cloud and shadow masking.
  - Mosaicking and seasonal consistency.
  - CRS harmonisation to project CRS.

### 3.3 Forest / non‑forest classification

- For each required date, create a forest/non‑forest classification over the project area:
  - Use supervised classification or well‑defined thresholds/rules.
  - Apply the agreed forest definition and minimum mapping unit.
- Treat clouds and shadows conservatively as per LUF Annex C:
  - In the image ~10 years before start: areas under clouds/shadows are considered **non‑eligible** unless explicitly ground‑truthed and documented.
  - At project start: apply combined cloud/shadow masks and ground‑truthing where necessary, following Annex C rules.

### 3.4 Accuracy assessment & eligibility masks

- Conduct accuracy assessment for each classification using:
  - Independent ground‑truth points from field campaigns, or
  - Higher‑resolution imagery / reference datasets.
- Report:
  - Confusion matrix, per‑class and overall accuracy, aiming for ≥90% per class (LUF Annex C).
- Derive final GIS products:
  - Forest vs non‑forest classification layers for each date.
  - Mask of non‑eligible forest areas (union of forest areas from both dates).
  - Final **eligible planting area** polygons:
    - Excluding forest as per non‑deforestation rule (LUF 2.1.2).
    - Excluding 10% biodiversity set‑aside and riparian buffer strips (15 m) as required.

### 3.5 Documentation for PDD / templates

- Provide to the PDD / consolidated A/R template:
  - Description of sensor(s), dates, resolutions and pre‑processing.
  - Classification method, training data, and validation approach.
  - Handling of clouds/shadows and conservative assumptions.
  - Area statistics:
    - Total project area.
    - Eligible planting area.
    - Non‑eligible forest and conservation set‑aside.

---

## 4. Baseline Land‑Cover and Carbon Inputs

**Goal**: Provide EO‑derived land‑cover information and support baseline carbon stock estimation in line with A/R Methodology and LUF.

### 4.1 Baseline land‑cover / land‑use mapping

- Create a land‑cover and/or land‑use map at project start (and historic dates if needed) that distinguishes:
  - Grassland, shrubland, cropland, degraded forest, wetlands, settlements, etc.
  - Any classes needed for leakage and baseline biomass calculations.
- Use a combination of RS data, existing maps, and field data, documenting all sources.

### 4.2 Baseline biomass and carbon pools

- For each relevant stratum and Modelling Unit (MU):
  - Assign baseline tree and non‑tree biomass values using:
    - Project‑specific field data (preferred).
    - Regional/national datasets.
    - IPCC defaults only when no other credible data exist (A/R Methodology 3.5.2).
- Provide a MU‑level baseline carbon table with:
  - Carbon stocks by pool (tree biomass, non‑tree biomass, soil where applicable).
  - Uncertainty estimates calculated according to LUF Annex A.

### 4.3 Leakage risk mapping

- Prepare spatial layers for:
  - Current fuelwood/charcoal collection areas.
  - Timber harvesting areas.
  - Agricultural expansion fronts.
  - Livestock grazing areas likely to be displaced.
- Use these to help parameterise A/R Methodology leakage equations:
  - Area affected, percent activity shift, CO₂ stock in receiving areas.

---

## 5. Modelling Units (MUs) and Project Design Support

### 5.1 Define and map MUs

- Delineate MU polygons across the eligible planting area such that each MU is homogeneous in:
  - Planned planting year(s).
  - Species mix and silvicultural regime (conservation, selective harvesting, rotation).
  - Site conditions that significantly affect growth (soil type, climate zone, altitude) where relevant.
- Ensure MU mapping supports:
  - Growth model application and CO₂ removal calculations as per A/R Methodology 3.3 and 3.6.
  - Inventory design and uncertainty calculations (LUF Annex A and A/R Methodology 3.11).

### 5.2 Inputs for growth and carbon models

- For each MU, compile:
  - Growth model choice (and parameters, if applicable).
  - Wood density, BEF, root‑to‑shoot ratios, carbon fractions.
  - Any site‑specific allometries or conversion factors, clearly referenced.
- Provide MU‑level parameter tables and ensure a robust link between spatial MUs and tabular model inputs.

### 5.3 Buffer, HCV, and safeguards layers

- Prepare and maintain:
  - Riparian buffer zones (≥15 m either side of water bodies) with associated restrictions.
  - HCV/biodiversity set‑aside areas and critical habitats.
  - Settlements and infrastructure vector layers.
- These layers directly support LUF safeguard requirements and Stakeholder and HCV assessments.

---

## 6. Field Evidence Collection – Design & Support

**Goal**: Make field campaigns maximally useful for RS products, eligibility checks, and GS auditability, using the `field_pipeline` and `mrv_validation` schemas.

### 6.1 Observation types and schema alignment

- Align observation semantics and schema across:
  - `field_pipeline` (`id`/`obs_id`, `obs_type`, `date_time`, `collector`, `landcover_class`, `photo_path`, `gnss_accuracy_m`, etc.).
  - `mrv_validation/mrv_schema.yaml` (`observations`, `attachments`, `monitoring_periods`, `aoi`, and lookup tables).
- Standardise `obs_type` values such as:
  - `ground_truth` – general MRV observations / plots.
  - `lc_training` / `lc_validation` – destined for land‑cover classifier training/validation (as the schema evolves).
  - `leakage_check` – focused on potential leakage areas.

### 6.2 Sampling design for ground‑truth & inventories

- With the MRV and forestry teams, design sampling to:
  - Achieve ±20% uncertainty at 90% confidence for key biomass/area estimates (LUF Annex A, A/R Methodology 3.11).
  - Cover:
    - All relevant land‑cover/land‑use strata.
    - Interfaces between eligible and non‑eligible areas.
    - Key MUs and risk zones (e.g. leakage belts).
- Provide maps and coordinates for planned sampling locations.

### 6.3 Configure QGIS/Mergin project for fieldwork

- In the QGIS project:
  - Add background layers: forest/non‑forest maps, land‑cover maps, MUs, AOI, boundaries, protected areas.
  - Configure forms:
    - Dropdowns from `lookups_obs_type` and `lookups_landcover_class`.
    - Validation rules (e.g. require photo for `ground_truth`, GNSS accuracy hints).
- Confirm on test devices that:
  - Attributes and photos are correctly stored in `project.gpkg` and `attachments/`.
  - Offline workflows function in expected field conditions.

---

## 7. Field Pipeline Runs (Per Monitoring Period or Campaign)

**Goal**: Convert raw field data into validated, enriched, and report‑ready evidence packages that can feed GS reporting and RS workflows.

### 7.1 Prepare incoming data

- Ensure Mergin sync has updated:
  - `data/incoming/project.gpkg`
  - `data/incoming/attachments/`
- Optionally validate against MRV schema early:
  - `python mrv_validation/validate_mrv_geopackage.py <gpkg> mrv_validation/mrv_schema.yaml [--report-csv ...]`
  - Fix structural issues (missing tables, invalid geometries, lookup mismatches) before more detailed EO analysis.

### 7.2 Run `field_pipeline` commands

From the repository root, using `field_pipeline/config/pipeline.yaml`:

1. **Ingest**
   - `python -m field_pipeline.cli ingest --config field_pipeline/config/pipeline.yaml`
   - Copies `project.gpkg` and `attachments/` into `data/processed/run_<timestamp>/`, creating an immutable snapshot.

2. **Validate**
   - `python -m field_pipeline.cli validate --config field_pipeline/config/pipeline.yaml`
   - Tasks for EO specialist:
     - Review reported schema/geometry issues (missing required fields, invalid geometries, missing photos, GNSS anomalies).
     - Coordinate corrections with field teams if necessary.

3. **Enrich**
   - `python -m field_pipeline.cli enrich --config field_pipeline/config/pipeline.yaml`
   - Produces an enriched GPKG (e.g. `project_enriched.gpkg`) with attributes from context layers (admin, PA, land‑cover, etc.).

4. **Summarize**
   - `python -m field_pipeline.cli summarize --config field_pipeline/config/pipeline.yaml`
   - Use summaries by `obs_type`, `collector`, and other metrics to:
     - Check coverage against sampling plans.
     - Spot gaps (e.g. missing leakage checks in high‑risk zones).

5. **Export**
   - `python -m field_pipeline.cli export --config field_pipeline/config/pipeline.yaml`
   - Produces:
     - `<gpkg_base>.csv` (attributes only).
     - `<gpkg_base>.geojson` (full geometry and attributes).
   - Deliver selected subsets as inputs to RS classification and monitoring analyses.

6. **Report**
   - `python -m field_pipeline.cli report --config field_pipeline/config/pipeline.yaml`
   - Generates a Markdown report with:
     - Dataset metadata (path, CRS, feature counts, timestamp).
     - Narrative summary (stub or AI‑assisted, depending on config).
   - Use this as internal documentation of each field campaign and evidence bundle.

### 7.3 Prepare GS‑ready evidence subsets

- From validated + enriched data, derive:
  - Ground‑truth datasets used in RS classification and accuracy assessment.
  - Leakage check observations summarised by land‑use/land‑cover and area.
  - Monitoring plots used to update biomass/growth models.
- Ensure each dataset:
  - Has stable IDs and is clearly linked to the corresponding run directory.
  - Can be cited in PDD / Monitoring Reports and easily re‑generated if needed.

---

## 8. Monitoring & Performance Certification Cycles

**Goal**: For each performance certification, provide updated EO products and field evidence aligned with GS requirements.

### 8.1 Update land‑cover and eligibility

- Using recent imagery and field data:
  - Update forest/non‑forest classification and land‑cover maps over the project area and leakage regions.
  - Detect:
    - Any deforestation or degradation inside the project area.
    - Land‑use changes in potential leakage belts.
- Reflect any changes in:
  - Eligible planting area (e.g. as new areas are added).
  - Conservation set‑asides and buffers.

### 8.2 Integrate new inventory and field data

- Incorporate latest forest inventory measurements to:
  - Update growth models and MU‑level biomass estimates.
  - Re‑calculate uncertainties and apply required deductions (LUF Annex A, A/R Methodology 3.11).
- Ensure updated MU‑level results are spatially consistent with MU polygons.

### 8.3 EO inputs to Monitoring Reports

- Provide:
  - Maps of project area, eligible planting area, MUs, land‑cover, and change detection results.
  - Tables of area by MU and land‑cover/land‑use, including changes since last verification.
  - Summaries of leakage indicators (e.g. observed clearing just outside project area, supported by field and RS data).
- Keep text concise and traceable, referencing specific run directories and datasets.

---

## 9. New Area Certification & Design Changes

### 9.1 EO tasks for New Area inclusion

- For each new area proposed for inclusion (LUF 2.1.15–2.1.18):
  - Repeat forest/non‑forest assessment with imagery 10 years before and at inclusion date.
  - Re‑apply eligibility rules and delineate new MUs.
  - Derive baseline land‑cover and biomass inputs for the new area.
- Update:
  - Project region/area layers.
  - Eligible planting area, buffer and HCV layers.
  - MU maps and tables.

### 9.2 EO support for design changes

- If project design changes (e.g. silvicultural system, planting density, species mix, boundary adjustments):
  - Provide before/after maps and tables showing the changes.
  - Supply revised MU parameters and any updated baseline/leakage spatial assumptions to support Design Change Requests.

---

## 10. Data Management, Traceability & Handover

### 10.1 Evidence archiving and provenance

- Maintain a clear structure under `data/processed/`:
  - `run_<timestamp>/project.gpkg`, `attachments/`, enriched GPKGs, CSV/GeoJSON exports, reports.
- For RS products:
  - Archive classification rasters/vectors, training/validation datasets, accuracy assessment results, and scripts.
  - Store minimal metadata (sensor, date, processing chain, CRS, parameters) so products can be reproduced.

### 10.2 Support for VVBs and GS reviews

- Provide an “EO appendix” or short memo (per monitoring period) that:
  - Explains which field runs and RS analyses were used.
  - Points to specific files and directories.
  - Summarises methods and key assumptions, with references to GS documents and clauses where relevant.
- Be available to:
  - Answer clarifications from VVBs on EO methods and data.
  - Provide sample data or scripts if deeper technical review is requested.

---

This workflow is meant to be a practical checklist for EO/GIS specialists working with the Gold Standard MRV Field & Land‑Cover Pipeline. It should be updated as the `field_pipeline` and `mrv_validation` tools evolve and as GS requirements are revised.

