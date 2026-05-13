"""
GitHub API client for doc-sync workflow.

Handles:
- Fetching the last successful workflow run timestamp (self-referential cursor)
- Fetching commits to the product repo since a given timestamp
- Fetching raw diffs for individual commits
- Loading the full product source tree (fresh_check mode)
"""

from __future__ import annotations

import os
import sys
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json


GITHUB_API = "https://api.github.com"
DOCS_REPO = os.environ.get("GITHUB_REPOSITORY", "")  # owner/repo of THIS repo
PRODUCT_REPO = os.environ.get("PRODUCT_REPO", "")     # owner/repo of the product
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
# PRODUCT_REPO_PAT is optional when the product repo is public.
# Falls back to GITHUB_TOKEN (authenticated, higher rate limits than anonymous).
_PAT = os.environ.get("PRODUCT_REPO_PAT", "")
PRODUCT_REPO_PAT = _PAT if _PAT else GITHUB_TOKEN


def _request(
    url: str,
    *,
    token: str,
    method: str = "GET",
    body: Optional[dict] = None,
    accept: str = "application/vnd.github+json",
    raw: bool = False,
) -> dict | list | str:
    """Make a GitHub API request. raw=True returns decoded text (for diff endpoints)."""
    data = json.dumps(body).encode() if body is not None else None
    headers = {
        "Accept": accept,
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(url, data=data, method=method, headers=headers)
    try:
        with urlopen(req) as resp:
            decoded = resp.read().decode()
            return decoded if raw else json.loads(decoded)
    except HTTPError as exc:
        body_text = exc.read().decode(errors="replace")
        print(f"[ERROR] GitHub API {method} {url} -> HTTP {exc.code}: {body_text}", file=sys.stderr)
        sys.exit(1)
    except URLError as exc:
        print(f"[ERROR] GitHub API request failed: {exc.reason}", file=sys.stderr)
        sys.exit(1)


def _paginate(url: str, *, token: str, params: str = "") -> list:
    """Fetch all pages from a GitHub list endpoint."""
    results = []
    page = 1
    while True:
        sep = "&" if params else ""
        page_url = f"{url}?{params}{sep}per_page=100&page={page}"
        batch = _request(page_url, token=token)
        if not isinstance(batch, list) or not batch:
            break
        results.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return results


# ── Credential validation ────────────────────────────────────────────────────

def validate_product_pat() -> None:
    """Verify product repo is accessible. PRODUCT_REPO_PAT is optional for public repos."""
    if not PRODUCT_REPO:
        print("[ERROR] PRODUCT_REPO env var is not set.", file=sys.stderr)
        sys.exit(1)
    using_pat = bool(os.environ.get("PRODUCT_REPO_PAT", ""))
    _request(f"{GITHUB_API}/repos/{PRODUCT_REPO}", token=PRODUCT_REPO_PAT)
    if using_pat:
        print(f"[OK] PRODUCT_REPO_PAT validated for {PRODUCT_REPO}")
    else:
        print(f"[OK] Product repo {PRODUCT_REPO} is accessible via GITHUB_TOKEN (no PAT set — OK for public repos)")


# ── Workflow run history ─────────────────────────────────────────────────────

def get_last_successful_run_timestamp(workflow_filename: str) -> Optional[str]:
    """
    Return the ISO 8601 `updated_at` timestamp of the last successful run of
    `workflow_filename` in this (docs) repo, or None if no successful run exists.
    """
    if not GITHUB_TOKEN:
        print("[ERROR] GITHUB_TOKEN is not available.", file=sys.stderr)
        sys.exit(1)

    url = f"{GITHUB_API}/repos/{DOCS_REPO}/actions/workflows/{workflow_filename}/runs"
    runs = _request(
        f"{url}?status=success&per_page=2",
        token=GITHUB_TOKEN,
    )
    workflow_runs = runs.get("workflow_runs", []) if isinstance(runs, dict) else []

    # The query is already restricted to successful runs, so the current
    # in-progress run is not returned here. GitHub returns runs newest first,
    # so the first successful candidate is the correct cursor to use.
    candidates = [r for r in workflow_runs if r.get("conclusion") == "success"]
    if candidates:
        return candidates[0]["updated_at"]
    return None


# ── Product repo commits ─────────────────────────────────────────────────────

def get_commits_since(since_iso: Optional[str]) -> list[dict]:
    """
    Return commits to the product repo's default branch since `since_iso`.
    Each entry: {"sha": ..., "message": ..., "url": ...}
    If `since_iso` is None, returns an empty list (fresh_check handles its own path).
    """
    if since_iso is None:
        return []
    raw = _paginate(
        f"{GITHUB_API}/repos/{PRODUCT_REPO}/commits",
        token=PRODUCT_REPO_PAT,
        params=f"since={since_iso}",
    )
    return [
        {
            "sha": c["sha"],
            "message": c["commit"]["message"].split("\n")[0],
            "url": c["html_url"],
        }
        for c in raw
    ]


def get_commit_diff(sha: str) -> str:
    """Return the unified diff text for a single product repo commit."""
    return _request(
        f"{GITHUB_API}/repos/{PRODUCT_REPO}/commits/{sha}",
        token=PRODUCT_REPO_PAT,
        accept="application/vnd.github.v3.diff",
        raw=True,
    )


def get_full_product_tree() -> list[dict]:
    """
    For fresh_check mode: return all Python source files in the product repo
    as a list of {"path": ..., "content": ...} dicts (decoded from base64).
    """
    import base64

    repo_info = _request(f"{GITHUB_API}/repos/{PRODUCT_REPO}", token=PRODUCT_REPO_PAT)
    default_branch = repo_info.get("default_branch", "main") if isinstance(repo_info, dict) else "main"
    tree_resp = _request(
        f"{GITHUB_API}/repos/{PRODUCT_REPO}/git/trees/{default_branch}?recursive=1",
        token=PRODUCT_REPO_PAT,
    )
    files = []
    for item in tree_resp.get("tree", []):
        if item["type"] == "blob" and item["path"].endswith(".py"):
            blob = _request(
                f"{GITHUB_API}/repos/{PRODUCT_REPO}/git/blobs/{item['sha']}",
                token=PRODUCT_REPO_PAT,
            )
            content = base64.b64decode(blob["content"]).decode(errors="replace")
            files.append({"path": item["path"], "content": content})
    return files
