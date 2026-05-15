# GitHub Actions

## Policy
- Third-party actions are pinned by full commit SHA for reproducibility.
- Shared vBase-owned actions and reusable workflows use `validityBase/vbase-github-actions` with reviewed release tags such as `@v1`.
- Workflow permissions are declared explicitly and kept minimal.
- Secrets must come from GitHub Secrets or deployment configuration, never from committed files, notebooks, screenshots, or logs.

## Workflows

### `.github/workflows/update-main-docs.yml`
- Runs on pushes to `main` and manual dispatch.
- Delegates to `validityBase/vbase-github-actions/.github/workflows/publish-docs.yml@v1`.
- Installs `docs/requirements.txt` with Python 3.11.
- Builds Sphinx Markdown docs into `docs/_build/markdown`.
- Publishes `docs/_build/markdown` to the `main` branch of the central docs repository.
- Passes `vbase-py-tools` to absolute-link rewriting.
- Uses `DOCS_REPO_ACCESS_TOKEN` for the central docs repository.
