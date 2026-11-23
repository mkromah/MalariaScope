# MalariaScope

**AI-assisted malaria blood-cell classification with uncertainty-aware review**

[Live demo](https://malariascope-mkromah.streamlit.app/) · [AI for Medicine hackathon](https://ai-for-medicine.devpost.com/) · [Results](docs/RESULTS.md) · [Reproducibility audit](docs/REPRODUCIBILITY.md) · [Kaggle run guide](docs/KAGGLE_RUN_GUIDE.md) · [Submission draft](docs/HACKATHON_SUBMISSION.md)

> **Research prototype — not a clinical diagnostic tool.** MalariaScope classifies cropped individual blood-cell images, not patient blood smears or patient infection status. A negative model output must not be used to rule out malaria.

## Why this project?

I built MalariaScope to explore how a lightweight model distinguishes infected and uninfected **cropped cell images** and when it should ask for manual review. I do not use it to diagnose malaria.

## Verified research results

I trained and evaluated the model in Kaggle, then checked the saved metrics against the confusion matrix. I have **not** independently retrained the model or tested it on an external dataset.

| Metric | RGB-histogram Logistic Regression (validation) | MobileNetV3-Small (validation) | MobileNetV3-Small (held-out test) |
|---|---:|---:|---:|
| Images | 4,459 | 4,459 | 3,805 |
| Sensitivity | 88.28% | 97.83% | 95.94% |
| Specificity | 95.34% | 98.29% | 96.62% |
| AUROC | 0.9569 | 0.9967 | 0.9919 |
| False negatives | 276 | 51 | 68 |

I evaluated 3,805 images from **31 held-out patients**. The classifier produced TP 1,608; TN 2,057; FP 72; FN 68.

I selected the **uncertainty review margin** (0.49) on validation data. On the held-out test images, it referred 822/3,805 (21.60%) cells for review. Of the remaining 2,983 automatic decisions, 20 were incorrect, including **10 infected cells predicted as uninfected**. I do **not** count the 822 referred cells as correctly classified. Full counts and limitations: [Results](docs/RESULTS.md).

## Dataset

NIH/NLM [Malaria Cell Images](https://lhncbc.nlm.nih.gov/LHC-research/LHC-projects/image-processing/malaria-datasheet.html): 27,558 cropped individual blood-cell images (13,779 parasitized; 13,779 uninfected). I checked **201 distinct patient IDs** across both mapping files (some patients appear in both label categories). I split patients, rather than images, into the three partitions using seed 42.

| Split | Patients | Images | Parasitized | Uninfected |
|---|---:|---:|---:|---:|
| Train | 139 | 19,294 | 9,749 | 9,545 |
| Validation | 31 | 4,459 | 2,354 | 2,105 |
| Test | 31 | 3,805 | 1,676 | 2,129 |

I do **not** publish raw images, patient-level manifests, or patient mapping files here. Respect the provider's terms and original publication attribution.

## Reproduce the research

Python 3.10+ recommended, GPU optional for training. Internet needed for NIH data and pretrained torchvision weights.

```bash
python -m pip install -r requirements.txt
python scripts/download_data.py --extract
python scripts/prepare_data.py --seed 42
python -m unittest discover -s tests -v
python scripts/baseline.py
python scripts/train.py --epochs 8 --batch-size 64
python scripts/evaluate.py
```

See the [Kaggle notebook](notebooks/MalariaScope_Kaggle.ipynb) and [run guide](docs/KAGGLE_RUN_GUIDE.md) for staged execution. I resize and pad each image to 224 × 224 without stretching it, use ImageNet normalization, and apply random horizontal/vertical flips only during training.

I keep model weights, validation settings, and evaluation metrics in `outputs/` during training. I checked the aggregate metrics and audited the private split manifest: 27,558 unique image paths and no shared patients across partitions. I publish the [split summary](results/split_summary.json), [audit](results/data_audit.json), and [software versions](docs/REPRODUCIBILITY.md), but keep the patient-level manifest and full environment snapshot private. I have not independently rerun the entire training pipeline.

## Demo

I run the research-only [Streamlit dashboard](https://malariascope-mkromah.streamlit.app/) from [app.py](app.py). The dashboard uses a responsive branded theme in [assets/theme.css](assets/theme.css); both PDF exports use the MalariaScope vector logo, color-coded model output, and a prominent research-only warning. These changes do **not** retrain or alter the frozen classifier. The public demo runs from the [`improvements/award-readiness`](https://github.com/mkromah/MalariaScope/tree/improvements/award-readiness) branch, where I keep the trained checkpoint and branding. To run it locally, add `model_best.pt` and `selection.json` under `outputs/` and use:

```bash
streamlit run app.py
```

The app stops with a clear message if either file is missing. For a separately evaluated future experiment with larger uncropped microscopy fields, see the [uncropped-image pilot plan](docs/UNCROPPED_IMAGE_PILOT.md); no new model performance is claimed.

## Structure

```text
├── app.py
├── assets/ (MalariaScope SVG logo/banner and theme.css)
├── notebooks/MalariaScope_Kaggle.ipynb
├── scripts/
│   ├── download_data.py
│   ├── prepare_data.py
│   ├── preprocessing.py
│   ├── baseline.py
│   ├── dashboard_logic.py
│   ├── reporting.py
│   ├── train.py
│   └── evaluate.py
├── tests/ (data preparation, dashboard logic and PDF exports)
├── results/                  # aggregate metrics and deidentified split audit
└── docs/
    ├── RESULTS.md
    ├── REPRODUCIBILITY.md
    ├── KAGGLE_RUN_GUIDE.md
    ├── UNCROPPED_IMAGE_PILOT.md
    └── HACKATHON_SUBMISSION.md
```

## Responsible use and harms

False negatives could cause dangerous false reassurance; false positives could trigger unnecessary review. Staining, device, population, and site differences may significantly degrade accuracy. I have not tested the model on full blood smears, at other laboratories, or with clinical readers. I use the review threshold for research only; **no clinical validation supports it**. See [limitations and results](docs/RESULTS.md).

## Attribution

- NIH/NLM malaria microscopy image data; follow linked dataset datasheet for the original researchers and citations.
- PyTorch, torchvision and ImageNet-pretrained MobileNetV3-Small weights; scikit-learn logistic regression; Streamlit; Pillow; NumPy.
- I used OpenAI ChatGPT to help plan the workflow, draft parts of the code, review results, and edit documentation. I ran model training and evaluation in Kaggle, then checked the saved outputs.

I have not yet assigned a licence to the original project code. Do not assume that NIH data or pretrained model weights share that licence.
