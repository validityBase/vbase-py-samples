# Python Dependency Hashes

Python dependencies use pip-tools input files plus generated hash-locked output
files.

## Pattern

- Human-edited inputs live in `requirements/src/*.in` files.
- Generated locks live in matching `requirements/lock/*.txt` files and include
  `--hash` entries.
- Install generated locks with `python -m pip install --require-hashes -r <file>`.
- Do not edit generated lock files by hand.
- The public vBase SDK dependency is `vbase==1.0.0`.

`setup.py` reads package runtime dependencies from `requirements/src/base.in`,
not from the generated `requirements/lock/base.txt` lock file. This avoids
passing hash-lock syntax to `install_requires`.

## Files

- `requirements/src/base.in` -> `requirements/lock/base.txt`: runtime sample dependencies.
- `requirements/src/dev.in` -> `requirements/lock/dev.txt`: development tooling.
- `requirements/src/win.in` -> `requirements/lock/win.txt`: Windows install lock.
- `docs/requirements/src/base.in` -> `docs/requirements/lock/base.txt`: Sphinx docs build.
- `requirements/src/tools.in` -> `requirements/lock/tools.txt`: pinned pip-tools setup.

## Regeneration

Use the pinned lock tooling:

```bash
python -m pip install --require-hashes -r requirements/lock/tools.txt
```

Regenerate locks with the Python version used by
`.github/workflows/python-dependency-locks.yml`:

```bash
pip-compile --strip-extras --no-annotate --generate-hashes -o requirements/lock/base.txt requirements/src/base.in
pip-compile --strip-extras --no-annotate --allow-unsafe --generate-hashes -o requirements/lock/dev.txt requirements/src/dev.in
pip-compile --strip-extras --no-annotate --generate-hashes -o requirements/lock/win.txt requirements/src/win.in
pip-compile --strip-extras --no-annotate --generate-hashes -o docs/requirements/lock/base.txt docs/requirements/src/base.in
pip-compile --strip-extras --no-annotate --allow-unsafe --generate-hashes -o requirements/lock/tools.txt requirements/src/tools.in
```
