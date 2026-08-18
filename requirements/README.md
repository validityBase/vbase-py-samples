# Python Requirements

Human-edited dependency inputs and generated hash-locked files live directly
under `requirements/` so Dependabot can update each `.in`/`.txt` pair.

Do not edit generated `.txt` files by hand. Install runtime and development
dependencies with hash checking:

```bash
python -m pip install --require-hashes -r requirements/base.txt
python -m pip install --require-hashes -r requirements/dev.txt
```

For Windows-specific dependencies use `requirements/win.txt`. Documentation
build dependencies are in `requirements/docs.txt`.

To update dependencies, edit the matching `.in` file and regenerate with the
pinned lock tooling:

```bash
python -m pip install --require-hashes -r requirements/tools.txt
pip-compile --strip-extras --no-annotate --generate-hashes \
  --output-file=requirements/base.txt requirements/base.in
```

Use the same command with the matching `.in` and `.txt` paths for `dev`,
`win`, and `docs`.
