"""Generate paired sample notebooks from Python percent-format cells."""

import json
import re
from pathlib import Path
from typing import Dict, List

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = REPOSITORY_ROOT / "samples"
PAIRED_SAMPLE_NAMES = (
    "add_string_dataset_record",
    "add_string_dataset_record_async",
    "add_trades",
    "add_trades_parallel",
    "create_set",
    "produce_portfolio_history_csv_s3",
    "produce_portfolio_history_json_s3",
    "produce_sentiment_dataset_history_s3",
    "restore_dataset_provenance",
    "verify_portfolio_history_csv_s3",
    "verify_portfolio_history_json_s3",
    "verify_sentiment_dataset_history_s3",
)
CELL_MARKER = re.compile(r"^# %%(?: \[(markdown)\])?\s*$")


def _markdown_source(lines: List[str]) -> List[str]:
    source = []
    for line in lines:
        if line.startswith("# "):
            source.append(line[2:])
        elif line.startswith("#"):
            source.append(line[1:])
        elif not line.strip():
            source.append(line)
        else:
            raise ValueError("Markdown cells must contain comment lines only.")
    return source


def _code_source(lines: List[str]) -> List[str]:
    """Apply the small script/notebook compatibility directives."""
    source = []
    skipping_script_only = False
    for line in lines:
        stripped = line.strip()
        if stripped == "# SCRIPT_ONLY_BEGIN":
            skipping_script_only = True
            continue
        if stripped == "# SCRIPT_ONLY_END":
            skipping_script_only = False
            continue
        if skipping_script_only:
            continue
        if line.startswith("# NOTEBOOK_ONLY: "):
            source.append(line[len("# NOTEBOOK_ONLY: ") :])
            continue
        source.append(line)
    if skipping_script_only:
        raise ValueError("SCRIPT_ONLY_BEGIN is missing SCRIPT_ONLY_END.")
    return source


def build_notebook(source_text: str) -> Dict:
    """Convert percent-format Python source into a notebook dictionary."""
    cells = []
    cell_type = None
    cell_lines: List[str] = []

    def flush_cell() -> None:
        if cell_type is None:
            return
        source = (
            _markdown_source(cell_lines)
            if cell_type == "markdown"
            else _code_source(cell_lines)
        )
        cell = {
            "cell_type": cell_type,
            "metadata": {},
            "source": source,
        }
        if cell_type == "code":
            cell["execution_count"] = None
            cell["outputs"] = []
        cells.append(cell)

    for line in source_text.splitlines(keepends=True):
        marker = CELL_MARKER.match(line.rstrip("\n"))
        if marker:
            flush_cell()
            cell_type = "markdown" if marker.group(1) else "code"
            cell_lines = []
            continue
        if cell_type is None:
            if line.strip():
                raise ValueError("Python source must start with a percent cell marker.")
            continue
        cell_lines.append(line)
    flush_cell()

    if not cells:
        raise ValueError("Python source did not define any notebook cells.")

    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def render_notebook(source_path: Path) -> str:
    """Return stable JSON for a paired Python sample."""
    notebook = build_notebook(source_path.read_text(encoding="utf-8"))
    return json.dumps(notebook, indent=1, ensure_ascii=False) + "\n"


def main() -> None:
    """Regenerate every paired notebook."""
    for sample_name in PAIRED_SAMPLE_NAMES:
        source_path = SAMPLES_DIR / f"{sample_name}.py"
        notebook_path = SAMPLES_DIR / f"{sample_name}.ipynb"
        notebook_path.write_text(render_notebook(source_path), encoding="utf-8")
        print(f"Updated {notebook_path.relative_to(REPOSITORY_ROOT)}")


if __name__ == "__main__":
    main()
