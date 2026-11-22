"""Lightweight unit tests; no real NIH data or GPU required."""
import csv
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from prepare_data import create_manifest, read_mapping, patient_splits


class MappingTests(unittest.TestCase):
    def test_headerless_wide_mapping(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "mapping.csv"
            p.write_text("P1,a.png,b.png,\nP2,c.png,\n", encoding="utf-8")
            self.assertEqual(read_mapping(p), {"a.png": "P1", "b.png": "P1", "c.png": "P2"})

    def test_headered_long_mapping(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "mapping.csv"
            p.write_text("patient_id,cell_name\nP1,a.png\nP2,b.png\n", encoding="utf-8")
            self.assertEqual(read_mapping(p), {"a.png": "P1", "b.png": "P2"})

    def test_duplicate_mapping_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "mapping.csv"
            p.write_text("P1,a.png\nP2,a.png\n")
            with self.assertRaises(ValueError):
                read_mapping(p)

    def test_patient_disjoint(self):
        records = []
        for i in range(30):
            for j in range(3):
                records.append({
                    "path": f"P{i}_{j}.png",
                    "patient_id": f"P{i}",
                    "label": str(int(i % 2 == 0)),
                })
        split = patient_splits(records, 42)
        self.assertEqual(len(split), 30)
        for group in ("train", "val", "test"):
            self.assertTrue(any(split[r["patient_id"]] == group and r["label"] == "1" for r in records))
            self.assertTrue(any(split[r["patient_id"]] == group and r["label"] == "0" for r in records))
        self.assertEqual(split, patient_splits(records, 42))

    def test_manifest_raises_on_missing_patient_mapping(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "cell_images/Parasitized").mkdir(parents=True)
            (root / "cell_images/Uninfected").mkdir(parents=True)
            (root / "patientid_cellmapping_parasitized.csv").write_text("P1,one.png\n")
            (root / "patientid_cellmapping_uninfected.csv").write_text("P2,two.png\n")
            (root / "cell_images/Parasitized/not-in-map.png").write_bytes(b"x")
            (root / "cell_images/Uninfected/two.png").write_bytes(b"x")
            with self.assertRaises(ValueError):
                create_manifest(root, root / "manifest.csv", 42)


if __name__ == "__main__":
    unittest.main()
