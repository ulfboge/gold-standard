"""
Optional AI-assisted text drafting.

By default this module is effectively a no-op unless:
- a provider is configured (e.g. "openai"), and
- the required environment variables are set (e.g. OPENAI_API_KEY).

This keeps the core pipeline free/open and offline-friendly, while allowing
you to plug in AI later without changing the rest of the code.
"""

import os
from typing import Optional

try:
  # OpenAI Python client (installed only if you want to use it)
  from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency
  OpenAI = None


def _draft_openai(prompt: str) -> str:
  """
  Use OpenAI's API to draft text, if configured.

  Expects:
  - OPENAI_API_KEY in the environment.
  """
  if OpenAI is None:
    return "[AI DISABLED] openai Python package is not installed."

  api_key = os.getenv("OPENAI_API_KEY")
  if not api_key:
    return "[AI DISABLED] OPENAI_API_KEY not set."

  client = OpenAI(api_key=api_key)

  resp = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
      {
        "role": "system",
        "content": "You write concise, neutral technical summaries for field data reports.",
      },
      {"role": "user", "content": prompt},
    ],
    temperature=0.4,
  )

  content = resp.choices[0].message.content
  if isinstance(content, str):
    return content
  try:
    return "".join(part.get("text", "") for part in content)  # type: ignore[union-attr]
  except Exception:
    return str(content)


def draft_text(prompt: str, provider: Optional[str] = None) -> str:
  """
  Draft text using an AI backend, if enabled. Otherwise, return a stub.

  - No network calls are made unless a known provider is explicitly selected
    and its environment variables are present.
  """
  if not provider:
    return "_AI-assisted narrative is disabled in config._"

  if provider == "openai":
    return _draft_openai(prompt)

  return f"[AI DISABLED] Unknown provider {provider!r}."

