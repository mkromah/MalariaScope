#!/usr/bin/env python3
"""Create a strict patient-disjoint train/validation/test manifest from NIH files.

Requires only Python standard library. Examples:
    python scripts/download_data.py --extract
    python scripts/prepare_data.py

Never split individual cell images at random: multiple cells come from the same
patient and can leak near-identical stain/imaging characteristics into the test set.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
LABELS = {"Parasitized": 1, "Uninfected": 0}
MAPPING = {
    1: "patientid_cellmapping_parasitized.csv",
    0: "patientid_cellmapping_uninfected.csv",
}


def read_mapping(file: Path) -> dict[str, str]:
    """Load NIH patient mapping in long (one cell/row) or wide CSV format.

    Recognizes optional header columns and strips BOM/extra empty fields.
    Every image filename must map to exactly one patient ID.
    """
    lookup: dict[str, str] = {}
    with file.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.reader(stream)
        first = next(reader, None)
        if first is None:
            raise ValueError(f"Empty CSV file: {file}")
        first = [value.strip() for value in first]
        norm = [name.lower().replace(" ", "").replace("_", "") for name in first]
        has_header = any(
            value in ("patientid", "patient", "cellname", "filename",
                      "imagename", "image", "cellimage") for value in norm
        )
        patient_idx = next((i for i, value in enumerate(norm)
                            if value in ("patientid", "patient")), 0)
        image_indices = [i for i, value in enumerate(norm)
                         if value in ("cellname", "filename", "imagename",
                                      "image", "cellimage")]
        def add(row: list[str], line: int) -> None:
            if len(row) <= patient_idx:
                return
            patient = row[patient_idx].strip()
            if not patient:
                return
            entries = (
                [row[i] for i in image_indices if i < len(row)]
                if has_header and image_indices
                else [value for i, value in enumerate(row) if i != patient_idx]
            )
            for item in entries:
                name = Path(item.strip().replace("\\\\", "/")).name
                if not name.lower().endswith(".png"):
                    continue
                if name in lookup and lookup[name] != patient:
                    raise ValueError(
                        f"{file}:{line}: {name} maps to multiple patients"
                    )
                lookup[name] = patient

        if not has_header:
            add(first, 1)
        for line, row in enumerate(reader, 2):
            add(row, line)
    if not lookup:
        raise ValueError(f"No PNG filenames parsed from {file}")
    return lookup


def patient_splits(rows: list[dict[str, str]], seed: int) -> dict[str, str]:
    patient_class: dict[str, set[int]] = collections.defaultdict(set)
    for row in rows:
        patient_class[row["patient_id"]].add(int(row["label"]))
    # Stratify patients by whether they supply any infected cells; no patient
    # can appear across multiple partitions even when supplying both classes.
    groups: dict[int, list[str]] = {0: [], 1: []}
    for patient, classes in patient_class.items():
        groups[max(classes)].append(patient)

    rng = random.Random(seed)
    result: dict[str, str] = {}
    for group in groups.values():
        rng.shuffle(group)
        if len(group) < 7:
            raise ValueError("Too few patients in one group for stratified splitting")
        n_test = max(1, round(len(group) * 0.15))
        n_val = max(1, round(len(group) * 0.15))
        for index, patient in enumerate(group):
            result[patient] = (
                "test" if index < n_test
                else "val" if index < n_test + n_val
                else "train"
            )
    return result


def create_manifest(raw: Path, output: Path, seed: int) -> dict:
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for folder_name, label in LABELS.items():
        folder = raw / "cell_images" / folder_name
        if not folder.is_dir():
            raise FileNotFoundError(f"Missing image directory: {folder}")
        mapping_path = raw / MAPPING[label]
        if not mapping_path.is_file():
            raise FileNotFoundError(f"Missing patient mapping: {mapping_path}")
        mapping = read_mapping(mapping_path)
        images = sorted(folder.glob("*.png"))
        if not images:
            raise ValueError(f"No PNG images in {folder}")
        missing = []
        for image in images:
            if image.name in seen:
                raise ValueError(f"Duplicate image name: {image.name}")
            seen.add(image.name)
            patient = mapping.get(image.name)
            if patient is None:
                missing.append(image.name)
            else:
                rows.append({
                    "path": str(image.relative_to(raw).as_posix()),
                    "label": str(label),
                    "patient_id": patient,
                })
        if missing:
            raise ValueError(
                f"Refusing to split: {len(missing)} unmapped images in {folder_name}; "
                f"examples: {missing[:4]}"
            )
        extra = set(mapping) - {p.name for p in images}
        if extra:
            raise ValueError(
                f"Refusing to split: {len(extra)} mapped images not present in "
                f"{folder_name}; examples: {sorted(extra)[:4]}"
            )

    partitions = patient_splits(rows, seed)
    for row in rows:
        row["split"] = partitions[row["patient_id"]]

    patients_per_split = {
        split: {r["patient_id"] for r in rows if r["split"] == split}
        for split in ("train", "val", "test")
    }
    if any(
        patients_per_split[a] & patients_per_split[b]
        for a, b in (("train", "val"), ("train", "test"), ("val", "test"))
    ):
        raise AssertionError("Patient leakage across splits")
    for split in patients_per_split:
        if {int(r["label"]) for r in rows if r["split"] == split} != {0, 1}:
            raise ValueError(f"Missing a class in {split} split")

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=["path", "label", "patient_id", "split"]
        )
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "seed": seed,
        "total_images": len(rows),
        "total_patients": len(partitions),
        "splits": {
            split: {
                "images": sum(r["split"] == split for r in rows),
                "patients": len(patients_per_split[split]),
                "infected_cells": sum(
                    r["split"] == split and r["label"] == "1" for r in rows
                ),
                "uninfected_cells": sum(
                    r["split"] == split and r["label"] == "0" for r in rows
                ),
            }
            for split in ("train", "val", "test")
        },
    }
    with output.with_suffix(".summary.json").open("w", encoding="utf-8") as stream:
        json.dump(summary, stream, indent=2)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=RAW)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "data" / "processed" / "manifest.csv"
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    print(json.dumps(create_manifest(args.raw, args.output, args.seed), indent=2))


if __name__ == "__main__":
    main()
