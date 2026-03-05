from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Chunk:
  doc_name: str
  text: str


def load_chunks(docs_dir: Path) -> List[Chunk]:
  """
  Load simple text/Markdown chunks from the given directory.

  This is intentionally minimal: we split on blank lines and keep paragraphs
  that are long enough to be meaningful. It works as a small, local RAG helper
  without any extra infrastructure.
  """
  chunks: List[Chunk] = []
  if not docs_dir.exists():
    return chunks

  for path in docs_dir.glob("*.md"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    for p in paras:
      # Keep only reasonably sized paragraphs
      if len(p) < 80:
        continue
      chunks.append(Chunk(doc_name=path.name, text=p))
  return chunks


def _score(query: str, chunk: Chunk) -> int:
  """
  Very simple keyword overlap score between query and chunk text.
  This keeps the RAG helper lightweight and local.
  """
  q_tokens = set(query.lower().split())
  c_tokens = set(chunk.text.lower().split())
  return len(q_tokens & c_tokens)


def retrieve_snippets(query: str, docs_dir: Path, top_k: int = 3) -> List[Chunk]:
  """
  Retrieve top_k chunks from docs_dir that roughly match the query.

  This is not semantic search; it's a small, dependency-free helper that still
  adds useful context to AI prompts.
  """
  chunks = load_chunks(docs_dir)
  if not chunks:
    return []

  scored = [(c, _score(query, c)) for c in chunks]
  scored = [s for s in scored if s[1] > 0]
  scored.sort(key=lambda x: x[1], reverse=True)
  return [c for c, _ in scored[:top_k]]

