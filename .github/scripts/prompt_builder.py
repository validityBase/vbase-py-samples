"""
LLM prompt builder for doc-sync workflow.

Builds the system and user prompts for:
  - Pass 1: metadata summary → ask LLM which files to inspect
  - Pass 2 / single-pass: full diff analysis → ask LLM for doc updates
  - fresh_check: full codebase audit
"""

from __future__ import annotations

import json


SYSTEM_PROMPT = """\
You are a documentation maintenance assistant for the vBase Python library (vbase-py).
This repository (vbase-py-samples) contains documentation (docs/*.md) and sample \
scripts (samples/*.py) that explain how to use the library.

Your ONLY job is to identify specific lines in existing docs that have become \
INACCURATE due to the product changes described below, and report exactly what \
needs to change and why.

STRICT RULES — follow without exception:
1. NEVER suggest creating new documentation files or new sections.
2. ONLY report changes needed in files that already exist in the doc-map.
3. If a new API, class, or method appears in the product with no existing doc \
   entry, IGNORE IT.
4. Do NOT modify: README.md, CONTRIBUTING.md, docs/conf.py, docs/index.rst, \
   docs/requirements.txt.
5. For uncertain cases, flag them in the "uncertain" list rather than guessing.
6. "current_text" MUST be a verbatim short excerpt (1-3 sentences or a code block) \
   copied exactly from the current doc content provided — it will be used to \
   locate the line in the file.
7. "suggested_text" should be the minimal replacement for that excerpt only, \
   not the entire file.
8. "product_ref.snippet" should be the specific diff line or code from the \
   product repo that proves this change is needed.

Always respond with valid JSON matching this exact schema:
{
  "changes_needed": <bool>,
  "findings": [
    {
      "docs_file": "<repo-relative path to doc/sample file>",
      "current_text": "<verbatim excerpt from the current doc that is now wrong>",
      "suggested_text": "<the corrected replacement for that excerpt only>",
      "reason": "<one sentence: what product change makes this text inaccurate>",
      "product_ref": {
        "file": "<product repo file path that drives this change>",
        "snippet": "<the relevant product code or diff line>"
      }
    }
  ],
  "uncertain": [
    {
      "path": "<repo-relative path>",
      "question": "<what a human needs to verify>"
    }
  ]
}

If changes_needed is false, "findings" and "uncertain" may be empty arrays.
"""

PASS1_SYSTEM_PROMPT = """\
You are a triage assistant for a documentation sync workflow.

Below is a metadata summary of recent commits to the vBase Python library.
Each entry shows the commit message and the first 10 lines of the diff for \
each changed file.

Your job: identify which product source files are likely to affect the existing \
documentation listed in the doc-map. Return ONLY a JSON object:
{
  "selected_files": ["<product repo file path>", ...]
}

List only files whose changes could make existing documentation inaccurate. \
If no files are relevant, return an empty list.
"""


def build_pass1_prompt(metadata_summary: str, doc_map: dict) -> tuple[str, str]:
    """Return (system, user) prompts for Pass 1 (triage)."""
    user = (
        f"## Doc-map (existing documented symbols)\n"
        f"```json\n{json.dumps(doc_map, indent=2)}\n```\n\n"
        f"## Commit metadata summary\n{metadata_summary}"
    )
    return PASS1_SYSTEM_PROMPT, user


def build_analysis_prompt(
    diff_text: str,
    doc_map: dict,
    doc_contents: dict[str, str],
) -> tuple[str, str]:
    """
    Return (system, user) prompts for full diff analysis (Pass 2 or single-pass).

    doc_contents: {repo-relative-path: file_content} for all mapped doc files.
    """
    doc_map_block = json.dumps(doc_map, indent=2)

    doc_files_block_parts = []
    for path, content in doc_contents.items():
        doc_files_block_parts.append(f"### {path}\n```\n{content}\n```")
    doc_files_block = "\n\n".join(doc_files_block_parts)

    user = (
        f"## Doc-map (existing documented symbols)\n"
        f"```json\n{doc_map_block}\n```\n\n"
        f"## Current documentation file contents\n{doc_files_block}\n\n"
        f"## Product code changes (git diffs)\n{diff_text}"
    )
    return SYSTEM_PROMPT, user


def build_fresh_check_prompt(
    product_files: list[dict],
    doc_map: dict,
    doc_contents: dict[str, str],
) -> tuple[str, str]:
    """
    Return (system, user) prompts for fresh_check full audit mode.

    product_files: [{"path": ..., "content": ...}] for all product .py files.
    """
    doc_map_block = json.dumps(doc_map, indent=2)

    product_block_parts = []
    for f in product_files:
        product_block_parts.append(f"### {f['path']}\n```python\n{f['content']}\n```")
    product_block = "\n\n".join(product_block_parts)

    doc_files_block_parts = []
    for path, content in doc_contents.items():
        doc_files_block_parts.append(f"### {path}\n```\n{content}\n```")
    doc_files_block = "\n\n".join(doc_files_block_parts)

    fresh_system = SYSTEM_PROMPT.replace(
        "due to the product changes described below.",
        "by comparing the FULL current product codebase against the existing docs.",
    )

    user = (
        f"## Doc-map (existing documented symbols)\n"
        f"```json\n{doc_map_block}\n```\n\n"
        f"## Current documentation file contents\n{doc_files_block}\n\n"
        f"## Full product codebase\n{product_block}"
    )
    return fresh_system, user
