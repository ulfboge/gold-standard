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

---

### Future option: Mergin Maps Media Sync

If attachment volume grows or you want more durable media storage, it may become useful to evaluate **Mergin Maps Media Sync**. According to the Mergin Maps documentation, Media Sync can synchronize media files from a Mergin Maps project to external storage backends such as Google Drive, Amazon S3, or MinIO, using either copy or move mode.

References:

- [Mergin Maps Media Sync docs](https://merginmaps.com/docs/dev/media-sync/)
- [MerginMaps/media-sync repository](https://github.com/MerginMaps/media-sync)

For this repository, Media Sync is most relevant as a future extension when:

- Photos or other media become too large to manage comfortably only inside the project attachments folder.
- You want a more durable or centrally managed evidence store.
- Downstream QA, reporting, or audit workflows need media files in object storage.

If adopted later, keep the integration explicit:

- Decide whether `data/incoming/attachments/` remains the working copy used by the pipeline.
- Preserve a stable link between each observation record and its media object path.
- Add hashing or indexing so object-storage files still support audit-grade traceability.

