# MalariaScope — Devpost submission draft

**Status (23 November 2026):** Research pipeline evaluated. The project author confirms the Streamlit app has been deployed; its public URL and live behavior have not yet been independently verified or documented in this repository. Demonstration video and final Devpost submission remain unconfirmed. This draft is not proof of clinical utility.

## Project description

**Problem and who has it:** Reviewing malaria blood smears requires trained human attention. MalariaScope studies a narrow research task: classifying *already-cropped* individual cell images and flagging uncertain results for human review. It is intended for researchers and educational demonstrations, not patients or clinical diagnoses.

**Method:** The project used the NIH/NLM malaria microscopy dataset (27,558 cropped cells, 201 distinct patient IDs). A patient-disjoint split (seed 42) assigned 139 patients to training, 31 to validation, and 31 to held-out testing. A simple RGB-histogram Logistic Regression model served as the baseline. A pretrained MobileNetV3-Small classifier was trained using aspect-ratio-preserving 224×224 padding, normalization and training-only augmentation. The best checkpoint was selected at epoch 3 by validation loss. A separate symmetric uncertainty band (margin 0.49) was chosen using validation data.

## Evaluation

The RGB-histogram baseline achieved 88.28% sensitivity, 95.34% specificity and 0.9569 AUROC on 4,459 validation images. MobileNetV3 achieved 97.83% sensitivity, 98.29% specificity and 0.9967 AUROC on that same partition.

On **3,805 cells from 31 held-out patients**, the selected MobileNetV3 model achieved **95.94% sensitivity, 96.62% specificity, 0.9919 AUROC and 0.9583 F1**, with 1,608 true positives, 2,057 true negatives, 72 false positives, and 68 false negatives.

Using the validation-selected uncertainty band, the model automatically classified **2,983 (78.4%)** of the test images, referring **822 (21.6%)** for human review. Among automatic classifications, **20 errors remained, including 10 infected cells classified as uninfected**. The referred images were not reviewed by humans in this study, so their eventual correctness and any clinical workload savings are unknown.

These figures are **individual cropped-cell results, not patient diagnosis accuracy**. They cannot establish safety for malaria screening or rule-out. Full aggregate evidence is in [RESULTS.md](RESULTS.md) and `results/`.

## Who benefits, and who could be harmed

Potential beneficiaries are researchers and laboratory educators investigating image classification and uncertainty-aware review. A false-negative prediction could create dangerous false reassurance, while a false positive could trigger additional testing. Changes in microscope, staining, specimen preparation, parasite stage and population may lead to model failures. This project is not approved for clinical use.

## Limitations

- Pre-cropped individual cells; no validation on full thin smears, thick smears, or patients.
- Test images from the original dataset only; no independent acquisition-site validation.
- A selected subset's conditional accuracy cannot be interpreted as overall clinical sensitivity.
- No human review experiment, cost study, calibration study or prospective clinical assessment.
- Patient-correlated images mean naïve image-level confidence intervals would be misleading.
- The uploaded manifest was audited for patient overlap and counts, and key Kaggle package versions were captured. Independent end-to-end retraining, GPU hardware provenance, and external-site evaluation remain outstanding.

## If we had another month

Test an independent microscopy dataset, quantify patient-cluster uncertainty and image quality failures, evaluate review burden with laboratory professionals, and validate inference speed on low-cost hardware.

## Attribution

- Dataset and linked original research: [NIH/NLM malaria imaging datasheet](https://lhncbc.nlm.nih.gov/LHC-research/LHC-projects/image-processing/malaria-datasheet.html).
- MobileNetV3 pretrained weights: torchvision / PyTorch and associated sources.
- Logistic Regression: scikit-learn. App: Streamlit. Image handling: Pillow.
- OpenAI ChatGPT helped with research planning, drafting code, results reporting, and documentation. Model training and image analysis were performed in Kaggle by the author; uploaded artifacts were examined for consistency.

## Submission checklist

- [x] Define research task and clinical limitations.
- [x] Download and examine the NIH cell images and patient mappings in Kaggle.
- [x] Create patient-disjoint train/validation/test partition.
- [x] Train baseline and MobileNet; choose one validation checkpoint.
- [x] Report held-out test metrics and an uncertainty-based referral experiment.
- [x] Publish aggregate results, split audit, and methodology in GitHub.
- [x] Verify separately uploaded private split manifest, aggregate summary, and Kaggle package versions; publish non-identifying audit.
- [x] Implement Streamlit app and deploy it (completion reported by project author).
- [ ] Add the exact public Streamlit URL to the README and Devpost entry after confirming the link works.
- [ ] Verify the deployed demo loads model weights and gives an understandable output for a sample cropped-cell image.
- [ ] Document how the deployed app accesses the trained checkpoint without exposing private assets or credentials.
- [ ] Record and publish a short walkthrough video (see [demo-video plan](DEMO_VIDEO_SCRIPT.md)).
- [ ] Add final repository, live-demo, and video links; then submit to Devpost.
