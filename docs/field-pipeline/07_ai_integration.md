## AI Integration (Optional)

This page summarises how **AI integration** is handled in the field pipeline. It is adapted from section 7 of `field_pipeline/PROCESS_MANUAL.md`.

---

### Current design

The AI module (`field_pipeline/ai.py`) is intentionally a **no‑op stub**:

- It never calls any external API unless:
  - `ai.enabled: true` is set in `pipeline.yaml`, and
  - `ai.provider` is set (for example `"openai"`), and
  - You implement the corresponding provider logic and set required environment variables.

Current behaviour of `draft_text(prompt, provider=None)`:

- If `provider` is falsy: returns a stub string indicating AI is disabled.
- If `provider == "openai"` but `OPENAI_API_KEY` is not set: returns a stub string.
- Otherwise: returns a placeholder indicating integration is not yet implemented.

This preserves:

- A clear separation between the **core open pipeline** and any AI augmentation.
- A safe default where AI is completely off.

---

### Enabling AI (optional)

To add real AI support in future:

1. Choose a provider (for example OpenAI API or a local LLM).  
2. Implement the actual call in `field_pipeline/ai.py` using the chosen library.  
3. Set secrets as environment variables (never commit keys or tokens to the repo).  
4. Turn on `ai.enabled` and set `ai.provider` in `pipeline.yaml`.

Potential use cases (always with human oversight):

- Draft narrative for internal/external reports.
- Suggest data‑quality flags or highlight suspicious patterns in field data.

