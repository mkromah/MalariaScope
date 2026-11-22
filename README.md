# MalariaScope

**AI-assisted malaria blood-cell classification with uncertainty-aware review**

[AI for Medicine hackathon](https://ai-for-medicine.devpost.com/) · [Results](docs/RESULTS.md) · [Kaggle run guide](docs/KAGGLE_RUN_GUIDE.md) · [Submission draft](docs/HACKATHON_SUBMISSION.md)

> **Research prototype — not a clinical diagnostic tool.** MalariaScope classifies cropped individual blood-cell images, not patient blood smears or patient infection status. A negative model output must not be used to rule out malaria.

## Why this project?

Manual malaria microscopy requires trained attention. MalariaScope studies whether a lightweight model can distinguish infected and uninfected **cropped cell images** while referring some uncertain images for manual review.

## Verified research results

The developer inspected the user-provided Kaggle model checkpoint and results archive. Reported metrics are mathematically consistent with the saved confusion matrix; this **does not** constitute independent retraining or external validation.

| Metric | RGB-histogram Logistic Regression (validation) | MobileNetV3-Small (validation) | MobileNetV3-Small (held-out test) |
|---|---:|---:|---:|
| Images | 4,459 | 4,459 | 3,805 |
| Sensitivity | 88.28% | 97.83% | 95.94% |
| Specificity | 95.34% | 98.29% | 96.62% |
| AUROC | 0.9569 | 0.9967 | 0.9919 |
| False negatives | 276 | 51 | 68 |

The test set consists of 3,805 images from **31 held-out patients**. The plain classifier produced TP 1,608; TN 2,057; FP 72; FN 68.

The **validation-selected uncertainty policy** (symmetric probability margin 0.49) referred 822/3,805 (21.60%) test images to manual review. Of the remaining 2,983 automatic decisions, 20 were incorrect, including **10 infected cells predicted as uninfected**. The 822 referred cells are **not** assumed to be correctly classified. Full counts and limitations: [Results](docs/RESULTS.md).

## Dataset

NIH/NLM [Malaria Cell Images](https://lhncbc.nlm.nih.gov/LHC-research/LHC-projects/image-processing/malaria-datasheet.html): 27,558 cropped individual blood-cell images (13,779 parasitized; 13,779 uninfected). The user verified **201 distinct patients** across both mapping files (many patients appear in both label categories). Patient assignments were made exclusively at the patient level, with seed 42.

| Split | Patients | Images | Parasitized | Uninfected |
|---|---:|---:|---:|---:|
| Train | 139 | 19,294 | 9,749 | 9,545 |
| Validation | 31 | 4,459 | 2,354 | 2,105 |
| Test | 31 | 3,805 | 1,676 | 2,129 |

Raw datasets, patient-specific manifest, and patient mappings are **not** distributed here. Respect the provider's terms and original publication attribution.

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

See the [Kaggle notebook](notebooks/MalariaScope_Kaggle.ipynb) and [run guide](docs/KAGGLE_RUN_GUIDE.md) for staged execution. The model uses aspect-ratio-preserving 224 × 224 padding with black borders, ImageNet normalization, and random horizontal/vertical flips on training images only.

Outputs generated locally under `outputs/` include model weights, validation selection, and test metrics. The aggregate result JSON files in `results/` were checked against the uploaded archive. **Exact package versions and patient-level split manifest are still missing from the uploaded archives** and therefore cannot yet be independently reproduced byte-for-byte. The model weights are preserved in the user's local backup but have not been published here.

## Demo

The Streamlit interface is implemented in [app.py](app.py), but **no public live demo or downloadable checkpoint is yet deployed**. To run it, place the trained `model_best.pt` and `selection.json` under `outputs/` and run:

```bash
streamlit run app.py
```

The interface intentionally stops if those files are absent.

## Structure

```text
├── app.py
├── notebooks/MalariaScope_Kaggle.ipynb
├── scripts/
│   ├── download_data.py
│   ├── prepare_data.py
│   ├── preprocessing.py
│   ├── baseline.py
│   ├── train.py
│   └── evaluate.py
├── tests/test_prepare_data.py
├── results/                  # aggregate, non-patient-level metrics
└── docs/
    ├── RESULTS.md
    ├── KAGGLE_RUN_GUIDE.md
    └── HACKATHON_SUBMISSION.md
```

## Responsible use and harms

False negatives could cause dangerous false reassurance; false positives could trigger unnecessary review. Staining, device, population, and site differences may significantly degrade accuracy. This project has not been assessed on full smears, in different laboratories, or with clinical readers. The review threshold is research-only and **not** a clinically validated safety threshold. See [limitations and results](docs/RESULTS.md).

## Attribution

- NIH/NLM malaria microscopy image data; follow linked dataset datasheet for the original researchers and citations.
- PyTorch, torchvision and ImageNet-pretrained MobileNetV3-Small weights; scikit-learn logistic regression; Streamlit; Pillow; NumPy.
- OpenAI ChatGPT assisted with planning, code drafting, evaluation documentation, and repository updates. Data execution and model training were conducted by the project author in Kaggle; the archived outputs were subsequently checked here.

License for original project code: under review. Do not assume an open-source license applies to NIH data or model weights.
