# CLAUDE.md

This repository contains runnable examples and documentation for the vBase
Python SDK.

## Core Standards

- Keep sample code small, readable, and focused on demonstrating SDK usage.
- Do not commit secrets, private keys, API tokens, `.env` files, or notebook
  outputs containing credentials.
- Runtime dependencies are declared in `requirements.in`; generated lock files
  are committed with hashes and must not be edited by hand.
- Documentation published externally lives in `docs/`.
- Internal specs, guides, and agent memory live in `internal/`.

## Internal Documentation

- Agent memory: [internal/agents/memory/MEMORY.md](internal/agents/memory/MEMORY.md)
- GitHub Actions: [internal/specs/github-actions.md](internal/specs/github-actions.md)
- Python dependency hashes: [internal/specs/python-dependency-hashes.md](internal/specs/python-dependency-hashes.md)
