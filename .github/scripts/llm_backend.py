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
    "openai": os.environ.get("OPENAI_MODEL", "gpt-5.4"),
    "anthropic": os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
}

_MAX_RETRIES = 5
_BASE_BACKOFF = 10  # seconds


def _header_snapshot(headers: object) -> dict[str, str]:
    if headers is None:
        return {}
    return {str(key): str(value) for key, value in headers.items()}


def _interesting_headers(headers: object) -> dict[str, str]:
    snapshot = _header_snapshot(headers)
    interesting: dict[str, str] = {}
    for key, value in snapshot.items():
        lower = key.lower()
        if "ratelimit" in lower or "retry-after" == lower or "request-id" in lower:
            interesting[key] = value
    return interesting


def _message_char_count(messages: list[dict]) -> int:
    total = 0
    for message in messages:
        content = message.get("content", "")
        if isinstance(content, str):
            total += len(content)
    return total


def _request_prompt_char_count(body: dict) -> int:
    total = 0
    system = body.get("system", "")
    if isinstance(system, str):
        total += len(system)
    messages = body.get("messages", [])
    if isinstance(messages, list):
        total += _message_char_count(messages)
    return total


def _estimate_tokens(char_count: int) -> int:
    return max(1, (char_count + 3) // 4) if char_count else 0


def _post_json(url: str, headers: dict, body: dict, provider: str, model: str) -> dict:
    data = json.dumps(body).encode()
    messages = body.get("messages", [])
    prompt_chars = _request_prompt_char_count(body)
    print(
        f"[LLM] Request provider={provider} model={model} url={url} "
        f"payload_bytes={len(data)} prompt_chars={prompt_chars} "
        f"message_chars={_message_char_count(messages)} "
        f"estimated_prompt_tokens={_estimate_tokens(prompt_chars)}",
        flush=True,
    )
    for attempt in range(_MAX_RETRIES):
        req = Request(url, data=data, method="POST", headers=headers)
        try:
            with urlopen(req) as resp:
                return json.loads(resp.read().decode())
        except HTTPError as exc:
            response_headers = _interesting_headers(exc.headers)
            body_text = exc.read().decode(errors="replace")
            if exc.code == 429:
                # Respect Retry-After header if present, else exponential backoff
                retry_after = exc.headers.get("Retry-After")
                wait = int(retry_after) if retry_after else _BASE_BACKOFF * (2 ** attempt)
                print(
                    f"[LLM] Rate limit hit provider={provider} model={model} "
                    f"attempt={attempt + 1}/{_MAX_RETRIES} wait={wait}s "
                    f"headers={json.dumps(response_headers, sort_keys=True)}",
                    flush=True,
                )
                if body_text:
                    print(
                        f"[LLM] Rate limit response body: {body_text[:1000]}",
                        flush=True,
                    )
                time.sleep(wait)
                continue
            print(f"[ERROR] LLM API {url} -> HTTP {exc.code}: {body_text}", file=sys.stderr)
            if response_headers:
                print(
                    f"[ERROR] LLM response headers: {json.dumps(response_headers, sort_keys=True)}",
                    file=sys.stderr,
                )
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
        provider="github-models",
        model=model,
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
        provider="openai",
        model=model,
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
        provider="anthropic",
        model=model,
    )
    return resp["content"][0]["text"]


def call_llm(system_prompt: str, user_prompt: str) -> dict:
    """
    Call the configured LLM provider and return a parsed JSON dict.
    Exits loudly if the response cannot be parsed as JSON.
    """
    model = MODELS.get(LLM_PROVIDER, "(unknown)")
    print(
        f"[LLM] Calling provider={LLM_PROVIDER} model={model} "
        f"system_chars={len(system_prompt)} user_chars={len(user_prompt)}",
        flush=True,
    )

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
