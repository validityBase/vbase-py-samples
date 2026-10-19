"""Structural, syntax, and public-content checks for the samples."""

import ast
import json
import re
import unittest
from pathlib import Path

from scripts.sync_notebooks import PAIRED_SAMPLE_NAMES, render_notebook

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = REPOSITORY_ROOT / "samples"
NOTEBOOKS = sorted(SAMPLES_DIR.glob("*.ipynb"))
PYTHON_SAMPLES = sorted(SAMPLES_DIR.glob("*.py"))
S3_STAMP_SAMPLE_NAMES = (
    "produce_portfolio_history_csv_s3.py",
    "produce_portfolio_history_json_s3.py",
    "produce_sentiment_dataset_history_s3.py",
    "restore_dataset_provenance.py",
    "stamp_alpaca_portfolio.py",
    "stamp_interactive_brokers_portfolio.py",
)
EXPECTED_NOTEBOOK_NAMES = {
    f"{sample_name}.ipynb" for sample_name in PAIRED_SAMPLE_NAMES
}
PUBLIC_CONTENT_FILES = (
    [REPOSITORY_ROOT / "README.md", REPOSITORY_ROOT / "doc-map.json"]
    + sorted((REPOSITORY_ROOT / "docs").glob("*.md"))
    + PYTHON_SAMPLES
    + NOTEBOOKS
)
LEGACY_MARKERS = (
    "from vbase import",
    "ForwarderCommitmentService",
    "VBASE_FORWARDER_URL",
    "VBASE_COMMITMENT_SERVICE_PRIVATE_KEY",
    "VBaseDataset",
    "VBaseStringObject",
    "VBaseJsonObject",
    "VBaseIntObject",
)


class PublicSamplesTests(unittest.TestCase):
    """Keep scripts, notebooks, dependencies, and public wording aligned."""

    def test_all_python_samples_compile(self):
        for sample_path in PYTHON_SAMPLES:
            with self.subTest(sample=sample_path.name):
                compile(
                    sample_path.read_text(encoding="utf-8"),
                    str(sample_path),
                    "exec",
                )

    def test_expected_notebooks_are_present(self):
        self.assertEqual({path.name for path in NOTEBOOKS}, EXPECTED_NOTEBOOK_NAMES)

    def test_notebooks_match_paired_python_sources(self):
        for sample_name in PAIRED_SAMPLE_NAMES:
            source_path = SAMPLES_DIR / f"{sample_name}.py"
            notebook_path = SAMPLES_DIR / f"{sample_name}.ipynb"
            with self.subTest(notebook=notebook_path.name):
                self.assertEqual(
                    notebook_path.read_text(encoding="utf-8"),
                    render_notebook(source_path),
                )

    def test_notebook_code_cells_compile(self):
        for notebook_path in NOTEBOOKS:
            notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
            for cell_number, cell in enumerate(notebook["cells"], start=1):
                if cell["cell_type"] != "code":
                    continue
                with self.subTest(
                    notebook=notebook_path.name,
                    cell=cell_number,
                ):
                    compile(
                        "".join(cell["source"]),
                        f"{notebook_path.name}:cell-{cell_number}",
                        "exec",
                        flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
                    )

    def test_notebooks_have_no_saved_execution_state(self):
        for notebook_path in NOTEBOOKS:
            notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
            for cell in notebook["cells"]:
                if cell["cell_type"] != "code":
                    continue
                with self.subTest(notebook=notebook_path.name):
                    self.assertIsNone(cell.get("execution_count"))
                    self.assertEqual(cell.get("outputs", []), [])

    def test_public_content_has_no_legacy_configuration_or_internal_task_ids(self):
        private_key_assignment = re.compile(
            r"(?i)(?:private_key|\bpk\b)[^\n=]*=\s*[\"']0x[0-9a-f]{64}"
        )
        task_id = re.compile(r"\bVI-\d+\b")

        for content_path in PUBLIC_CONTENT_FILES:
            content = content_path.read_text(encoding="utf-8")
            with self.subTest(path=content_path.relative_to(REPOSITORY_ROOT)):
                for marker in LEGACY_MARKERS:
                    self.assertNotIn(marker, content)
                self.assertIsNone(private_key_assignment.search(content))
                self.assertIsNone(task_id.search(content))

    def test_runtime_dependencies_use_vbase_api(self):
        requirements = [
            line.strip()
            for line in (REPOSITORY_ROOT / "requirements.txt")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip() and not line.startswith("#")
        ]
        self.assertTrue(
            any(requirement.startswith("vbase-api") for requirement in requirements)
        )
        self.assertNotIn("vbase", requirements)

    def test_s3_samples_store_records_before_stamping(self):
        for sample_name in S3_STAMP_SAMPLE_NAMES:
            sample_path = SAMPLES_DIR / sample_name
            tree = ast.parse(
                sample_path.read_text(encoding="utf-8"),
                filename=str(sample_path),
            )
            write_lines = []
            stamp_lines = []
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                if (
                    isinstance(node.func, ast.Name)
                    and node.func.id == "write_s3_object"
                ):
                    write_lines.append(node.lineno)
                if (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "create_stamp"
                ):
                    stamp_lines.append(node.lineno)

            with self.subTest(sample=sample_name):
                self.assertEqual(len(write_lines), 1)
                self.assertEqual(len(stamp_lines), 1)
                self.assertLess(write_lines[0], stamp_lines[0])


if __name__ == "__main__":
    unittest.main()
