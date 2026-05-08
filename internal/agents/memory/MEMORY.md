# Agent Memory

## GitHub Actions
- Third-party GitHub Actions are pinned to full commit SHAs.
- vBase-owned shared actions and reusable workflows use reviewed `validityBase/vbase-github-actions` version tags.
- Documentation publishing delegates to `validityBase/vbase-github-actions/.github/workflows/publish-docs.yml@v1`.
- Docs publishing installs only `docs/requirements.txt`, matching the previous workflow behavior.
- Docs publishing builds Sphinx Markdown into `docs/_build/markdown`, rewrites absolute links for `vbase-py-tools`, and publishes to the `main` branch of the central docs repository.
