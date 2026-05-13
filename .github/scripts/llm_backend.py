"""
Pluggable LLM backend for doc-sync workflow.

Supported providers (set via LLM_PROVIDER env var):
  github-models  — Azure AI inference via GITHUB_TOKEN (default)
  openai         — OpenAI API via OPENAI_API_KEY
  anthropic      — Anthropic API via ANTHROPIC_API_KEY

All providers accept the same (system_prompt, user_prompt) interface and
return a parsed dict matching the doc-sync JSON schema:
  {
    "changes_needed": bool,
    "findings": [{"docs_file": str, "current_text": str, "suggested_text": str, "reason": str}],
    "uncertain": [{"path": str, "question": str}],
    "selected_files": [str]   # only in Pass 1 metadata responses
  }
"""

from __future__ import annotations

import json
import os
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "github-models")

# Model names per provider — override via env var if needed
MODELS = {
    "github-models": os.environ.get("GITHUB_MODEL", "gpt-4o"),
    "openai": os.environ.get("OPENAI_MODEL", "gpt-4o"),
    "anthropic": os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
}

_MAX_RETRIES = 5
_BASE_BACKOFF = 10  # seconds


def _post_json(url: str, headers: dict, body: dict) -> dict:
    data = json.dumps(body).encode()
    for attempt in range(_MAX_RETRIES):
        req = Request(url, data=data, method="POST", headers=headers)
        try:
            with urlopen(req) as resp:
                return json.loads(resp.read().decode())
        except HTTPError as exc:
            if exc.code == 429:
                # Respect Retry-After header if present, else exponential backoff
                retry_after = exc.headers.get("Retry-After")
                wait = int(retry_after) if retry_after else _BASE_BACKOFF * (2 ** attempt)
                print(f"[LLM] Rate limit hit — waiting {wait}s before retry "
                      f"(attempt {attempt + 1}/{_MAX_RETRIES})...", flush=True)
                time.sleep(wait)
                continue
            body_text = exc.read().decode(errors="replace")
            print(f"[ERROR] LLM API {url} -> HTTP {exc.code}: {body_text}", file=sys.stderr)
            sys.exit(1)
        except URLError as exc:
            print(f"[ERROR] LLM API request failed: {exc.reason}", file=sys.stderr)
            sys.exit(1)
    print(f"[ERROR] LLM API {url} — exhausted {_MAX_RETRIES} retries after rate limiting.",
          file=sys.stderr)
    sys.exit(1)


def _call_github_models(system: str, user: str) -> str:
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("[ERROR] GITHUB_TOKEN is required for github-models provider.", file=sys.stderr)
        sys.exit(1)
    model = MODELS["github-models"]
    resp = _post_json(
        "https://models.inference.ai.azure.com/chat/completions",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        body={
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        },
    )
    return resp["choices"][0]["message"]["content"]


def _call_openai(system: str, user: str) -> str:
    token = os.environ.get("OPENAI_API_KEY", "")
    if not token:
        print("[ERROR] OPENAI_API_KEY is required for openai provider.", file=sys.stderr)
        sys.exit(1)
    model = MODELS["openai"]
    resp = _post_json(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        body={
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        },
    )
    return resp["choices"][0]["message"]["content"]


def _call_anthropic(system: str, user: str) -> str:
    token = os.environ.get("ANTHROPIC_API_KEY", "")
    if not token:
        print("[ERROR] ANTHROPIC_API_KEY is required for anthropic provider.", file=sys.stderr)
        sys.exit(1)
    model = MODELS["anthropic"]
    resp = _post_json(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": token,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        body={
            "model": model,
            "max_tokens": 8192,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        },
    )
    return resp["content"][0]["text"]


def call_llm(system_prompt: str, user_prompt: str) -> dict:
    """
    Call the configured LLM provider and return a parsed JSON dict.
    Exits loudly if the response cannot be parsed as JSON.
    """
    print(f"[LLM] Calling provider: {LLM_PROVIDER}")

    if LLM_PROVIDER == "github-models":
        raw = _call_github_models(system_prompt, user_prompt)
    elif LLM_PROVIDER == "openai":
        raw = _call_openai(system_prompt, user_prompt)
    elif LLM_PROVIDER == "anthropic":
        raw = _call_anthropic(system_prompt, user_prompt)
    else:
        print(f"[ERROR] Unknown LLM_PROVIDER: {LLM_PROVIDER!r}. "
              "Valid values: github-models, openai, anthropic", file=sys.stderr)
        sys.exit(1)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"[ERROR] LLM returned invalid JSON: {exc}", file=sys.stderr)
        print(f"[ERROR] Raw LLM response:\n{raw}", file=sys.stderr)
        sys.exit(1)
