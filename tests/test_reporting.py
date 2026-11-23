"""Basic smoke checks for PDF report generation; synthetic images only."""
import io
import unittest
from pypdf import PdfReader
from PIL import Image
from scripts.reporting import generate_pdf


class ReportTests(unittest.TestCase):
    def test_research_and_handoff_exports(self):
        sample = Image.new("RGB", (32, 42), (154, 82, 120))
        data = io.BytesIO()
        sample.save(data, format="PNG")
        current = {
            "index": 2, "score": 0.94,
            "category": "parasitized",
            "label": "Parasite-like features detected - verification required",
            "width": 32, "height": 42,
            "timestamp": "2026-11-23 10:00 UTC",
        }
        previous = {"index": 1, "score": 0.02, "category": "uninfected"}
        for handoff in (False, True):
            with self.subTest(handoff=handoff):
                result = generate_pdf(
                    current, previous, data.getvalue(), 0.49, handoff=handoff
                )
                self.assertTrue(result.startswith(b"%PDF-"))
                self.assertGreater(len(result), 2000)
                pages = len(PdfReader(io.BytesIO(result)).pages)
                self.assertEqual(pages, 2 if handoff else 1)


if __name__ == "__main__":
    unittest.main()
