# Python Dependency Hashes

Python dependencies use pip-tools input files plus generated hash-locked output
files.

## Pattern

- Human-edited inputs live in `requirements.in` files.
- Generated locks live in matching `requirements.txt` files and include
  `--hash` entries.
- Install generated locks with `python -m pip install --require-hashes -r <file>`.
- Do not edit generated lock files by hand.
- The public vBase SDK dependency is `vbase==1.0.0`.

`setup.py` reads package runtime dependencies from `requirements.in`, not from
the generated `requirements.txt` lock file. This avoids passing hash-lock syntax
to `install_requires`.

## Files

- `requirements.in` -> `requirements.txt`: runtime sample dependencies.
- `requirements-dev.in` -> `requirements-dev.txt`: development tooling.
- `requirements-win.in` -> `requirements-win.txt`: Windows install lock.
- `docs/requirements.in` -> `docs/requirements.txt`: Sphinx docs build.
- `requirements-lock.in` -> `requirements-lock.txt`: pinned pip-tools setup.

## Regeneration

Use the pinned lock tooling:

```bash
python -m pip install --require-hashes -r requirements-lock.txt
```

Regenerate locks with the Python version used by
`.github/workflows/python-dependency-locks.yml`:

```bash
pip-compile --strip-extras --no-annotate --generate-hashes -o requirements.txt requirements.in
pip-compile --strip-extras --no-annotate --allow-unsafe --generate-hashes -o requirements-dev.txt requirements-dev.in
pip-compile --strip-extras --no-annotate --generate-hashes -o requirements-win.txt requirements-win.in
pip-compile --strip-extras --no-annotate --generate-hashes -o docs/requirements.txt docs/requirements.in
pip-compile --strip-extras --no-annotate --allow-unsafe --generate-hashes -o requirements-lock.txt requirements-lock.in
```
