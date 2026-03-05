## Customization Roadmap

This page outlines likely **next steps** for evolving the field pipeline toward a production‑grade MRV system. It is adapted from section 9 of `field_pipeline/PROCESS_MANUAL.md`.

---

### Validation rules

Potential enhancements:

- Temporal checks:
  - `date_time` not in the future.
  - `date_time` falls within the configured monitoring period.
- GNSS accuracy bounds:
  - Maximum allowed accuracy per `obs_type`.
- Photo rules:
  - Require photos for specific `obs_type` values.
  - Verify that referenced files exist and are valid image types.
- Duplicate detection:
  - Flag observations with same location/time/collector within specified tolerances.

These rules can be implemented by extending `validate.py` and, where needed, configuration options in `pipeline.yaml`.

---

### Enrichment logic

Extensions for `enrich.py`:

- More flexible join types:
  - Attribute joins (not just spatial).
  - User‑configured join fields and predicates.
- Column selection and conflict resolution:
  - Control which context columns are retained.
  - Handle overlapping attributes from multiple context layers.
- Derived fields:
  - Admin codes.
  - Protection status.
  - Land‑cover class summaries or categories (for example grouping detailed classes into IPCC classes).

---

### Review tables

Introduce a dedicated `observations_review` table that captures:

- Validation status (error/warning counts).
- Enrichment completeness.
- Reviewer decisions (APPROVED/REJECTED) and notes.
- Timestamps and user IDs for audit trails.

This aligns the field pipeline with the approach used in `mrv_validation`, making it easier to use the outputs in certification settings.

---

### Attachments index

Add a structured `attachments` index (in the GeoPackage or a separate DB) capturing:

- Observation id.
- File path.
- SHA‑256 hash.
- EXIF timestamps and GPS (if available).

This would support:

- Stronger evidence chains for certification and audits.
- Automated checks for mismatches between EXIF data and recorded observation attributes.

---

### Reporting

Enhance reporting to include:

- Richer Markdown or HTML layouts.
- Maps rendered separately in QGIS and linked or embedded.
- Summary tables and charts.
- Direct links to underlying CSV/GeoPackage/GeoJSON outputs.

---

### AI

When and if appropriate, plug in AI capabilities to:

- Draft narrative summaries for reports based on structured metrics.
- Suggest data‑quality flags or highlight suspicious patterns.

Any AI‑driven outputs should remain clearly flagged and be subject to human review before use in certification documents.

