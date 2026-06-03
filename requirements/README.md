# Python Requirements

Human-edited dependency inputs live in `requirements/src/`.
Generated hash-locked files live in `requirements/lock/`.

Do not edit generated files in `requirements/lock/` by hand. Regenerate locks
with `pip-compile --generate-hashes`.

From the repository root:

```bash
python -m pip install --require-hashes -r requirements/lock/tools.txt
pip-compile --strip-extras --no-annotate --allow-unsafe --generate-hashes -o requirements/lock/tools.txt requirements/src/tools.in
python -m pip install --require-hashes -r requirements/lock/tools.txt
pip-compile --strip-extras --no-annotate --generate-hashes -o requirements/lock/base.txt requirements/src/base.in
pip-compile --strip-extras --no-annotate --allow-unsafe --generate-hashes -o requirements/lock/dev.txt requirements/src/dev.in
pip-compile --strip-extras --no-annotate --generate-hashes -o requirements/lock/win.txt requirements/src/win.in
```

Docs dependencies follow the same source/lock layout under `docs/requirements/`:

```bash
pip-compile --strip-extras --no-annotate --generate-hashes -o docs/requirements/lock/base.txt docs/requirements/src/base.in
```
