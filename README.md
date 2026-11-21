# MalariaScope

**AI-assisted malaria blood-cell classification with uncertainty-aware review**

MalariaScope is an educational research prototype for the [AI for Medicine hackathon](https://ai-for-medicine.devpost.com/). It aims to classify **individual cropped red-blood-cell microscopy images** as parasitized or uninfected and flag uncertain cases for manual review.

> **Not for clinical use.** This project does not diagnose malaria in a patient, quantify parasitemia, replace examination of a full blood smear, or recommend treatment. Its performance has not yet been established.

## Project status — 22 November 2026

- [x] Initialize public repository and dataset-download utility
- [ ] Verify downloaded dataset, patient mapping, and image integrity
- [ ] Create a reproducible **patient-disjoint** train / validation / test split
- [ ] Train and compare baseline and transfer-learning models
- [ ] Set review thresholds on validation data only
- [ ] Evaluate once on untouched patient-held-out test data
- [ ] Add Streamlit demo and a short demonstration video

**No trained model or evaluation results are claimed at this stage.**

## Data

Source: National Library of Medicine (NLM), [Malaria Cell Images](https://lhncbc.nlm.nih.gov/LHC-research/LHC-projects/image-processing/malaria-datasheet.html). The public resource contains approximately 27,558 labeled cell images and companion patient-to-cell mapping CSVs. Raw images and mapping CSVs are intentionally **not** tracked in this repository.

### Download

Requirements: Python 3.10+; internet connection; disk space for the archive and extracted images (allow at least 1 GB).

```bash
python scripts/download_data.py --mappings-only
python scripts/download_data.py --extract
```

The first command downloads the patient mapping CSVs. The second downloads and extracts the image archive (and skips already downloaded files). Files are stored under `data/raw/`. The script prints SHA-256 hashes of downloaded files to help record the exact data version; these hashes are **not independently authenticated against an official checksum list**. Inspect the file structure before modeling.

**Data access and reuse:** Follow the dataset provider's stated terms and cite the original research. Do not redistribute the downloaded dataset through this repository.

## Planned evaluation

1. Inspect patient identifiers and labels; separate patients across train, validation, and test.
2. Compare a basic baseline with a pretrained lightweight CNN (e.g. MobileNetV3).
3. Select model, hyperparameters, calibration strategy, and uncertainty/review thresholds **using training and validation patients only**.
4. On the held-out test patients, report sensitivity for infected cells, specificity, false-negative counts, AUROC, F1, confusion matrix, and intervals (where feasible).
5. Evaluate selective classification: review fraction versus sensitivity on the automatically classified subset, with false-negative counts. Report low-quality-image performance separately.
6. Save deterministic seeds, split manifest, package versions, trained weights (or a documented retrieval method), and reproducible commands.

A **patient-level malaria diagnostic accuracy** claim would be inappropriate because these are cropped individual-cell images, not complete patient examinations. Generalization to new microscopes, laboratories, regions, and real clinical workflows remains untested.

## Responsible use and potential harms

The main risk is a false negative that falsely reassures a patient or clinician, alongside false positives causing avoidable further testing. Image-quality shifts, unfamiliar parasite stages, staining variability, class imbalance, and population shifts can worsen results. The demo will always display a research-only warning, and uncertain inputs will be referred for professional review.

## Project structure

```text
MalariaScope/
├── README.md
├── requirements.txt
├── scripts/
│   └── download_data.py
└── data/                  # generated locally; excluded from version control
```

## Attribution

- Dataset: U.S. National Library of Medicine malaria image research resource. Details and original study links: https://lhncbc.nlm.nih.gov/LHC-research/LHC-projects/image-processing/malaria-datasheet.html
- Frameworks and pretrained model weights (to be used): PyTorch/torchvision; exact versions and citations will be added once selected.
- Development assistance: OpenAI ChatGPT was used to assist with planning, code drafting, and documentation. All generated code requires review and testing before results are reported.

License for original project code: **to be selected after reviewing dependencies and intended reuse terms**.
