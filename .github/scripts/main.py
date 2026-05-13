"""
Main entrypoint for the doc-sync workflow.

Usage:
  python -m scripts.main --mode MODE [--credential-check]

Modes:
  fresh_check    Full audit of all docs against entire product codebase
  from_last_run  Commits since last successful workflow run
  last_1_week    Commits in the past 7 days
  last_1_month   Commits in the past 30 days
  last_2_months  Commits in the past 60 days
  last_3_months  Commits in the past 90 days
  last_5_months  Commits in the past 150 days
  last_6_months  Commits in the past 180 days
  last_1_year    Commits in the past 365 days
  last_2_years   Commits in the past 730 days
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone

from .github_client import (
    validate_product_pat,
    get_last_successful_run_timestamp,
    get_commits_since,
    get_full_product_tree,
    PRODUCT_REPO,
)
from .diff_aggregator import (
    collect_diffs,
    needs_two_pass,
    build_metadata_summary,
    build_full_diff_for_files,
    build_single_pass_diff,
)
from .llm_backend import call_llm
from .prompt_builder import (
    build_pass1_prompt,
    build_analysis_prompt,
    build_fresh_check_prompt,
)

MODE_DAYS: dict[str, int] = {
    "last_1_week":   7,
    "last_1_month":  30,
    "last_2_months": 60,
    "last_3_months": 90,
    "last_5_months": 150,
    "last_6_months": 180,
    "last_1_year":   365,
    "last_2_years":  730,
}

WORKFLOW_FILENAME = "doc-sync.yml"
DOC_MAP_PATH = "doc-map.json"
GITHUB_OUTPUT = os.environ.get("GITHUB_OUTPUT", "")
GITHUB_STEP_SUMMARY = os.environ.get("GITHUB_STEP_SUMMARY", "")


def write_summary(text: str) -> None:
    """Append text to the GitHub Actions job summary."""
    if GITHUB_STEP_SUMMARY:
        with open(GITHUB_STEP_SUMMARY, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    print(text)


def load_doc_map() -> dict:
    if not os.path.exists(DOC_MAP_PATH):
        print(f"[WARN] {DOC_MAP_PATH} not found — LLM grounding will be reduced.")
        return {}
    with open(DOC_MAP_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_doc_contents(doc_map: dict) -> dict[str, str]:
    """Load the current content of every doc/sample file listed in doc-map."""
    contents: dict[str, str] = {}
    for path in doc_map:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                contents[path] = f.read()
        else:
            print(f"[WARN] doc-map entry {path!r} not found on disk — skipping.")
    return contents


def run_llm_analysis(
    diff_text: str,
    doc_map: dict,
    doc_contents: dict[str, str],
    commit_diffs: list[dict] | None = None,
) -> dict:
    """
    Run LLM analysis. Uses two-pass strategy if diff is large.
    Returns parsed LLM response dict.
    """
    if commit_diffs and needs_two_pass(commit_diffs):
        print("[INFO] Diff exceeds threshold — using two-pass strategy.")

        # Pass 1: metadata triage
        metadata = build_metadata_summary(commit_diffs)
        sys1, usr1 = build_pass1_prompt(metadata, doc_map)
        pass1_result = call_llm(sys1, usr1)
        selected_files = pass1_result.get("selected_files", [])
        print(f"[INFO] Pass 1: LLM selected {len(selected_files)} files for full analysis.")

        if not selected_files:
            return {"changes_needed": False, "files": [], "uncertain": []}

        # Pass 2: full diff for selected files only
        targeted_diff = build_full_diff_for_files(commit_diffs, selected_files)
        sys2, usr2 = build_analysis_prompt(targeted_diff, doc_map, doc_contents)
        return call_llm(sys2, usr2)

    # Single pass
    sys_p, usr_p = build_analysis_prompt(diff_text, doc_map, doc_contents)
    return call_llm(sys_p, usr_p)


def _find_line(file_path: str, text: str) -> int | None:
    """
    Return the 1-based line number of the first line in file_path that contains
    any word from the first sentence/line of text (best-effort).
    Returns None if the file doesn't exist or no match is found.
    """
    if not os.path.exists(file_path):
        return None
    # Use the first non-empty line of current_text as the search needle
    needle = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")[:80]
    if not needle:
        return None
    with open(file_path, encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            if needle in line:
                return i
    return None


def log_findings(
    llm_result: dict,
    commits: list[dict],
    since_timestamp: str | None,
    mode: str,
) -> None:
    """Print all LLM findings to console in a structured, readable format."""
    sep = "─" * 70
    findings = llm_result.get("findings", [])
    uncertain = llm_result.get("uncertain", [])

    write_summary(f"\n{'='*70}")
    write_summary(f" Doc Sync Report — mode: {mode}")
    if since_timestamp:
        write_summary(f" Analysis window: since {since_timestamp}")
    if commits:
        write_summary(f" Triggering commits ({len(commits)}):")
        for c in commits:
            write_summary(f"   [{c['sha'][:8]}] {c['message'][:72]}")
    write_summary(f"{'='*70}")

    if not findings and not uncertain:
        write_summary("\n  ✅  No documentation changes needed.\n")
        return

    write_summary(f"\n  Found {len(findings)} change(s) needed"
                  + (f", {len(uncertain)} uncertain item(s)" if uncertain else "") + "\n")

    for idx, finding in enumerate(findings, start=1):
        docs_file = finding.get("docs_file", "(unknown file)")
        current_text = finding.get("current_text", "")
        suggested_text = finding.get("suggested_text", "")
        reason = finding.get("reason", "")
        product_ref = finding.get("product_ref", {})
        product_file = product_ref.get("file", "")
        product_snippet = product_ref.get("snippet", "")

        line_num = _find_line(docs_file, current_text)
        location = f"{docs_file}, line {line_num}" if line_num else docs_file

        write_summary(sep)
        write_summary(f"  Finding {idx}/{len(findings)}: {location}")
        write_summary(sep)
        write_summary(f"  Reason:    {reason}")
        if product_file:
            write_summary(f"  Product:   {product_file}")
        if product_snippet:
            for ln in product_snippet.strip().splitlines():
                write_summary(f"  │  {ln}")
        write_summary("")
        write_summary("  Current text:")
        for ln in current_text.strip().splitlines():
            write_summary(f"  -  {ln}")
        write_summary("  Suggested replacement:")
        for ln in suggested_text.strip().splitlines():
            write_summary(f"  +  {ln}")
        write_summary("")

    if uncertain:
        write_summary(sep)
        write_summary(f"  ❓  Uncertain — needs human review ({len(uncertain)} item(s))")
        write_summary(sep)
        for u in uncertain:
            write_summary(f"  • {u.get('path', '')}")
            write_summary(f"    {u.get('question', '')}")
        write_summary("")


def run(mode: str = "from_last_run") -> None:
    doc_map = load_doc_map()
    doc_contents = load_doc_contents(doc_map)

    if mode == "fresh_check":
        print("[INFO] Mode: fresh_check — loading full product codebase.")
        product_files = get_full_product_tree()
        sys_p, usr_p = build_fresh_check_prompt(product_files, doc_map, doc_contents)
        llm_result = call_llm(sys_p, usr_p)
        commits: list[dict] = []
        since_timestamp = None
    else:
        if mode == "from_last_run":
            since_timestamp = get_last_successful_run_timestamp(WORKFLOW_FILENAME)
            if not since_timestamp:
                print("[INFO] No previous successful run found. "
                      "Use fresh_check or a fixed time-window mode for a first run.")
                write_summary(
                    "### Doc Sync\n"
                    "No previous successful run found. No commits to analyze. "
                    "Re-run with a time-window mode (e.g. last_1_month) or fresh_check."
                )
                return
            print(f"[INFO] Mode: from_last_run — since {since_timestamp}")
        else:
            days = MODE_DAYS[mode]
            since_dt = datetime.now(timezone.utc) - timedelta(days=days)
            since_timestamp = since_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            print(f"[INFO] Mode: {mode} — since {since_timestamp} ({days} days ago)")

        commits = get_commits_since(since_timestamp)
        if not commits:
            write_summary(
                f"### Doc Sync\n"
                f"No commits to {PRODUCT_REPO} since `{since_timestamp}`. No action taken."
            )
            return

        print(f"[INFO] Found {len(commits)} commits to analyze.")
        commit_diffs = collect_diffs(commits)
        diff_text = build_single_pass_diff(commit_diffs)
        llm_result = run_llm_analysis(diff_text, doc_map, doc_contents, commit_diffs)

    if not llm_result.get("changes_needed", False):
        since_info = f"since `{since_timestamp}`" if since_timestamp else "(full audit)"
        write_summary(
            f"### Doc Sync\n"
            f"Analyzed {len(commits)} commit(s) {since_info}. "
            f"No documentation changes needed."
        )
        return

    log_findings(llm_result, commits, since_timestamp, mode)


def main() -> None:
    valid_modes = ["fresh_check", "from_last_run"] + list(MODE_DAYS.keys())
    parser = argparse.ArgumentParser(description="Doc sync workflow script")
    parser.add_argument(
        "--mode",
        choices=valid_modes,
        default=os.environ.get("MODE", "from_last_run"),
        help="Analysis scope (default: from_last_run)",
    )
    parser.add_argument(
        "--credential-check",
        action="store_true",
        help="Only validate credentials and exit",
    )
    args = parser.parse_args()

    if args.credential_check:
        validate_product_pat()
        return

    run(mode=args.mode)


if __name__ == "__main__":
    main()
