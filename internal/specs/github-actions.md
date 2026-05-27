# GitHub Actions

## Policy
- Third-party actions are pinned by full commit SHA for reproducibility.
- Shared vBase-owned actions and reusable workflows use `validityBase/vbase-github-actions` with reviewed release tags such as `@v1`.
- Workflow permissions are declared explicitly and kept minimal.
- Secrets must come from GitHub Secrets or deployment configuration, never from committed files, notebooks, screenshots, or logs.

## Workflows

### `.github/workflows/doc-sync.yml`
- Runs manually with a required analysis scope input.
- Validates cross-repository credentials before running documentation analysis.
- Uses pinned `actions/checkout` and `actions/setup-python` actions with Python 3.11.
- Runs `.github/scripts/main.py` through `python -m scripts.main`.
- Uses repository variables and GitHub Secrets for product repository and LLM provider configuration.

### `.github/workflows/update-main-docs.yml`
- Runs on pushes to `main` and manual dispatch.
- Delegates to `validityBase/vbase-github-actions/.github/workflows/publish-docs.yml@v1`.
- Installs `docs/requirements.txt` with Python 3.11 and pip hash checking enabled.
- Builds Sphinx Markdown docs into `docs/_build/markdown`.
- Publishes `docs/_build/markdown` to the `main` branch of the central docs repository.
- Passes `vbase-py-samples` and `vbase-py-tools` to absolute-link rewriting.
- Uses `DOCS_REPO_ACCESS_TOKEN` for the central docs repository.

### `.github/workflows/python-dependency-locks.yml`
- Runs on pull requests that modify Python dependency inputs or generated locks.
- Uses `validityBase/vbase-github-actions/.github/actions/setup-python-deps@v1`.
- Regenerates runtime, development, Windows, docs, and lock-tooling requirement locks with hashes.
- Installs generated locks with `require-hashes: "true"` and checks package metadata with `pip check`.
