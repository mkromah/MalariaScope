# MalariaScope

**AI-assisted malaria blood-cell classification with uncertainty-aware review**

[Live Streamlit app](https://malariascope-mkromah.streamlit.app/) · [AI for Medicine hackathon](https://ai-for-medicine.devpost.com/) · [Results](docs/RESULTS.md) · [Reproducibility audit](docs/REPRODUCIBILITY.md) · [Kaggle run guide](docs/KAGGLE_RUN_GUIDE.md) · [Submission draft](docs/HACKATHON_SUBMISSION.md) · [Demo video plan](docs/DEMO_VIDEO_SCRIPT.md) · [Final checks](docs/FINAL_SUBMISSION_CHECKLIST.md)

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

Outputs generated locally under `outputs/` include model weights, validation selection, and test metrics. The aggregate result JSON files in `results/` were checked against the uploaded archive. **The user subsequently uploaded the previously missing records separately.** The private patient-level manifest was audited (27,558 unique image paths; no patient overlap); public [aggregate split summary](results/split_summary.json), [audit record](results/data_audit.json), and [verified software versions](docs/REPRODUCIBILITY.md) are now published. The complete environment snapshot and patient-level manifest remain private, and an independent rerun has not yet been performed. The model weights are preserved in the user's local backup but have not been published here.

## Demo

The project author confirms that the Streamlit application has been deployed at **[malariascope-mkromah.streamlit.app](https://malariascope-mkromah.streamlit.app/).** The link was supplied by the author on 23 November 2026. Two PDF reports supplied by the author demonstrate that the deployed app produced **different model outputs and downloadable PDF reports** for two uploaded cropped-cell images (22 November 2026). The first also includes an offline manual-review worksheet. This is **user-provided functional-test evidence**, not an independently observed browser test or a clinical validation. A public access check in a separate browser session remains to be confirmed. The source interface is in [app.py](app.py). For local use, place the trained `model_best.pt` and `selection.json` under `outputs/` and run:

```bash
streamlit run app.py
```

The interface intentionally stops if those files are absent. Document where deployed weights are loaded from without exposing credentials or private files. The checkpoint is not published in this GitHub repository, which is distinct from whether the deployed app has access to it.

Next hackathon deliverables: confirm the app URL works for an unauthenticated visitor, record a short demonstration video, and complete the final Devpost submission. See the [demo video plan](docs/DEMO_VIDEO_SCRIPT.md) and [final checklist](docs/FINAL_SUBMISSION_CHECKLIST.md).

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
├── results/                  # aggregate metrics and deidentified split audit
└── docs/
    ├── RESULTS.md
    ├── REPRODUCIBILITY.md
    ├── KAGGLE_RUN_GUIDE.md
    ├── HACKATHON_SUBMISSION.md
    ├── DEMO_VIDEO_SCRIPT.md
    └── FINAL_SUBMISSION_CHECKLIST.md
```

## Responsible use and harms

False negatives could cause dangerous false reassurance; false positives could trigger unnecessary review. Staining, device, population, and site differences may significantly degrade accuracy. This project has not been assessed on full smears, in different laboratories, or with clinical readers. The review threshold is research-only and **not** a clinically validated safety threshold. See [limitations and results](docs/RESULTS.md).

## Attribution

- NIH/NLM malaria microscopy image data; follow linked dataset datasheet for the original researchers and citations.
- PyTorch, torchvision and ImageNet-pretrained MobileNetV3-Small weights; scikit-learn logistic regression; Streamlit; Pillow; NumPy.
- OpenAI ChatGPT assisted with planning, code drafting, evaluation documentation, and repository updates. Data execution and model training were conducted by the project author in Kaggle; the archived outputs were subsequently checked here.

License for original project code: under review. Do not assume an open-source license applies to NIH data or model weights.
