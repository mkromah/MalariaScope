"""Validate the new NIH + Makerere audit notebook without accessing network data."""
import ast
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "MalariaScope_Uncropped_Audit.ipynb"


class UncroppedNotebookChecks(unittest.TestCase):
    def test_notebook_is_valid_json_and_python(self):
        book = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
        self.assertEqual(book["nbformat"], 4)
        self.assertGreaterEqual(len(book["cells"]), 12)
        for i, cell in enumerate(book["cells"], start=1):
            self.assertIn(cell["cell_type"], {"code", "markdown"})
            if cell["cell_type"] == "code":
                code = "".join(cell["source"])
                with self.subTest(cell=i):
                    ast.parse(code, filename=f"notebook-cell-{i}")

    def test_audit_only_has_no_training_execution(self):
        book = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
        code = "\n".join("".join(c["source"]) for c in book["cells"]
                         if c["cell_type"] == "code")
        self.assertIn("MAKERERE_DOI", code)
        self.assertIn("NIH_POLY", code)
        self.assertIn("NIH_POINT", code)
        self.assertNotIn("torch.load(", code)
        self.assertNotIn("train.py", code)


if __name__ == "__main__":
    unittest.main()
