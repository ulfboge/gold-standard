## Attachments Handling

This page explains how the pipeline currently handles **attachments** (photos and other media). It is adapted from section 5 of `field_pipeline/PROCESS_MANUAL.md`.

---

### Current behaviour

The scaffold focuses on **copying and preserving attachments** rather than deeply parsing EXIF/metadata. This can be extended later as needed.

- **Ingest**
  - If `paths.incoming_attachments_dir` exists, `ingest` copies it wholesale into the run directory as `attachments/`.
  - This creates a 1:1 snapshot of the current attachment set for that run.

Attachments are therefore preserved alongside the per‑run copy of `project.gpkg` in `data/processed/run_<timestamp>/`.

---

### Recommended pattern

In your QGIS / Mergin project:

- Store file paths or filenames in an attribute (for example `photo_path`).
- Ensure this field is kept in sync with the actual files placed in `attachments/`.

In a future iteration you can add a dedicated module (for example `attachments.py`) that:

- Scans the attachments folder for referenced files.
- Computes hashes (for example SHA‑256) for integrity checking.
- Extracts EXIF timestamps and GPS coordinates when available.
- Builds an attachments index table (in the GeoPackage or as CSV/Parquet) linked by observation id.

This would provide:

- Stronger audit trails (proof that specific photos have not changed).
- Cross‑checks between EXIF timestamps/locations and the recorded observation `date_time` and geometry.

