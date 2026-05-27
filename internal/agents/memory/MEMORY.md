# Agent Memory

## GitHub Actions
- Third-party GitHub Actions are pinned to full commit SHAs.
- vBase-owned shared actions and reusable workflows use reviewed `validityBase/vbase-github-actions` version tags.
- Documentation publishing delegates to `validityBase/vbase-github-actions/.github/workflows/publish-docs.yml@v1`.
- Docs publishing installs only `docs/requirements.txt` with pip hash checking enabled.
- Docs publishing builds Sphinx Markdown into `docs/_build/markdown`, rewrites absolute links for `vbase-py-samples` and `vbase-py-tools`, and publishes to the `main` branch of the central docs repository.

## Python Dependencies
- Runtime dependencies are declared in `requirements.in`; `setup.py` reads this input file instead of the generated hash-locked `requirements.txt`.
- Generated lock files include hashes and are installed with `python -m pip install --require-hashes -r <file>`.
- `requirements-lock.txt` pins pip-tools for lock regeneration.
