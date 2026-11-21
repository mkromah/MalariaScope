#!/usr/bin/env python3
"""Download and verify the official NIH/NLM malaria cell-image dataset.

Usage:
    python scripts/download_data.py --mappings-only
    python scripts/download_data.py --extract

Raw dataset files are kept under data/raw/ and must NOT be committed to GitHub.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

BASE_URL = "https://data.lhncbc.nlm.nih.gov/public/Malaria"
ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "data" / "raw"

# Checksums independently pinned by the stable-datasets project (not NIH-issued).
# https://galilai-group.github.io/stable-datasets/stable_datasets.images/
SHA256 = {
    "cell_images.zip": "0a949556b2414159b5100192609805376654c4266d8d187be9b1922fad43c668",
    "patientid_cellmapping_parasitized.csv": "d0367e513397404e980baee2a641bce9ce329a22e62ea9007962dfca2f8418d3",
    "patientid_cellmapping_uninfected.csv": "a8577b21e7154724f4bbd18326218e2c63a99b22ab372b79a7530d36df6dab78",
}


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def download(name: str) -> Path:
    DESTINATION.mkdir(parents=True, exist_ok=True)
    target = DESTINATION / name
    expected = SHA256[name]
    if target.is_file() and digest(target) == expected:
        print(f"[OK] Already verified: {target}")
        return target

    temporary = target.with_name(target.name + ".partial")
    temporary.unlink(missing_ok=True)
    print(f"[DOWNLOAD] {BASE_URL}/{name}", flush=True)
    request = urllib.request.Request(
        f"{BASE_URL}/{name}", headers={"User-Agent": "MalariaScope-research/0.1"}
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response, temporary.open("wb") as out:
            shutil.copyfileobj(response, out, length=1024 * 1024)
        actual = digest(temporary)
        if actual != expected:
            raise ValueError(f"SHA-256 mismatch for {name}: got {actual}, expected {expected}")
        temporary.replace(target)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    print(f"[OK] Verified {name} ({target.stat().st_size:,} bytes)")
    return target


def extract_images(archive: Path) -> None:
    # Avoid path traversal, symlinks, or writing outside the data directory.
    destination_root = DESTINATION.resolve()
    with zipfile.ZipFile(archive) as zf:
        members = [m for m in zf.infolist() if not m.is_dir()]
        for member in members:
            resolved = (destination_root / member.filename).resolve()
            if not resolved.is_relative_to(destination_root):
                raise ValueError(f"Unsafe path in archive: {member.filename}")
            if (member.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError(f"Symlink in archive: {member.filename}")
        print(f"[EXTRACT] Extracting {len(members):,} files ...", flush=True)
        zf.extractall(DESTINATION)
    png_count = len(list(DESTINATION.rglob("*.png")))
    print(f"[OK] Found {png_count:,} PNG images after extraction.")
    if png_count != 27558:
        raise ValueError("Expected 27,558 PNG cell images; check the extraction.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mappings-only", action="store_true", help="Download only patient-mapping CSVs")
    parser.add_argument("--extract", action="store_true", help="Extract the image archive after download")
    args = parser.parse_args()
    if args.mappings_only and args.extract:
        parser.error("--extract cannot be combined with --mappings-only")

    names = list(SHA256) if not args.mappings_only else list(SHA256)[1:]
    for name in names:
        download(name)
    if args.extract:
        extract_images(DESTINATION / "cell_images.zip")
    print("[DONE] Files are in data/raw/. Do not commit raw images or mapping files.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)
