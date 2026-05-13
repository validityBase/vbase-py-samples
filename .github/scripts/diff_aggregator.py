"""
Diff aggregation and two-pass strategy for doc-sync workflow.

Responsibilities:
- Collect diffs for a list of commits
- Detect whether total size exceeds the context budget
- Produce metadata summaries (commit msg + first 10 lines per file) for Pass 1
- Fetch full targeted diffs for Pass 2
"""

from __future__ import annotations

from typing import Optional

from .github_client import get_commit_diff

# Rough token estimate: 1 token ≈ 4 chars. Threshold = 50k tokens → ~200k chars.
DIFF_SIZE_THRESHOLD_CHARS = 200_000


def _first_n_lines(text: str, n: int = 10) -> str:
    return "\n".join(text.splitlines()[:n])


def collect_diffs(commits: list[dict]) -> list[dict]:
    """
    Fetch raw diffs for each commit.
    Returns list of {"sha": ..., "message": ..., "url": ..., "diff": ...}
    """
    result = []
    for commit in commits:
        print(f"  Fetching diff for {commit['sha'][:8]}: {commit['message'][:60]}")
        diff = get_commit_diff(commit["sha"])
        result.append({**commit, "diff": diff})
    return result


def total_diff_size(commit_diffs: list[dict]) -> int:
    return sum(len(c["diff"]) for c in commit_diffs)


def needs_two_pass(commit_diffs: list[dict]) -> bool:
    return total_diff_size(commit_diffs) > DIFF_SIZE_THRESHOLD_CHARS


def build_metadata_summary(commit_diffs: list[dict]) -> str:
    """
    Build a compact metadata summary for Pass 1 of the two-pass strategy.
    For each commit: message + per-file (name + first 10 diff lines).
    """
    lines = []
    for c in commit_diffs:
        lines.append(f"## Commit {c['sha'][:8]}: {c['message']}")
        lines.append(f"URL: {c['url']}")
        # Split diff into per-file sections
        file_sections = _split_diff_by_file(c["diff"])
        for fname, fdiff in file_sections.items():
            lines.append(f"### File: {fname}")
            lines.append(_first_n_lines(fdiff, 10))
            lines.append("")
        lines.append("")
    return "\n".join(lines)


def build_full_diff_for_files(
    commit_diffs: list[dict], selected_files: list[str]
) -> str:
    """
    Build a full diff string containing only the sections for `selected_files`
    across all commits. Used for Pass 2.
    """
    selected_set = set(selected_files)
    lines = []
    for c in commit_diffs:
        file_sections = _split_diff_by_file(c["diff"])
        relevant = {f: d for f, d in file_sections.items() if f in selected_set}
        if relevant:
            lines.append(f"## Commit {c['sha'][:8]}: {c['message']}")
            lines.append(f"URL: {c['url']}")
            for fname, fdiff in relevant.items():
                lines.append(f"### File: {fname}")
                lines.append(fdiff)
                lines.append("")
    return "\n".join(lines)


def build_single_pass_diff(commit_diffs: list[dict]) -> str:
    """Concatenate all diffs into one string for single-pass analysis."""
    lines = []
    for c in commit_diffs:
        lines.append(f"## Commit {c['sha'][:8]}: {c['message']}")
        lines.append(f"URL: {c['url']}")
        lines.append(c["diff"])
        lines.append("")
    return "\n".join(lines)


def _split_diff_by_file(diff_text: str) -> dict[str, str]:
    """
    Parse a unified diff and return a dict of {filename: diff_section}.
    Filenames are taken from `diff --git a/... b/...` headers.
    """
    sections: dict[str, list[str]] = {}
    current: Optional[str] = None
    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            parts = line.split(" b/", 1)
            current = parts[1] if len(parts) == 2 else line
            sections.setdefault(current, [])
        if current is not None:
            sections[current].append(line)
    return {k: "\n".join(v) for k, v in sections.items()}
