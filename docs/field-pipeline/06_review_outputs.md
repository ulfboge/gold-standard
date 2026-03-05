## Review Outputs and Immutability

This page describes how the pipeline treats **review outputs** and raw data **immutability**. It is adapted from section 6 of `field_pipeline/PROCESS_MANUAL.md`.

---

### Raw data as source of truth

The current scaffold:

- Treats `data/incoming/project.gpkg` as **read‑only**.
- Works primarily on copies in `data/processed/` created by `ingest`.

Design intent:

- The raw observations layer in the incoming GeoPackage is the **source of truth** for field‑collected data.
- Additional tables can be created alongside this to hold:
  - Validation flags (error/warning codes).
  - Enrichment status.
  - Reviewer decisions and notes.

This mirrors the approach used in the separate `mrv_validation` tooling, where an `observations_review` table tracks validation results and workflow state.

---

### Future review table integration

The next natural step is to add a dedicated review module (for example `review.py`) that:

- Creates and updates a review layer (for example `observations_review`) within the processed GeoPackage.
- Records:
  - Automatic validation outcomes.
  - Manual reviewer decisions (APPROVED / REJECTED).
  - Reviewer notes and timestamps.

This can then be wired into `validate` and `enrich` steps, aligning the field pipeline more closely with the `mrv_validation` workflow for certification‑grade MRV.

