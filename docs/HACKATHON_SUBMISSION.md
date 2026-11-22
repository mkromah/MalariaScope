# MalariaScope — Devpost submission draft

**Status:** Research pipeline evaluated; public demo and submission video still pending. This is a draft, not proof of clinical utility.

## Project description

**Problem:** Malaria microscopy takes trained attention. I built MalariaScope to study one limited task: classifying *already-cropped* cell images and identifying images for manual review. I intend it for research and education, not patient diagnosis.

**Method:** I used the NIH/NLM malaria microscopy dataset (27,558 cropped cells, 201 distinct patient IDs). A patient-disjoint split (seed 42) assigned 139 patients to training, 31 to validation, and 31 to held-out testing. A simple RGB-histogram Logistic Regression model served as the baseline. I trained a pretrained MobileNetV3-Small model with aspect-ratio-preserving 224×224 padding, normalization, and training-only augmentation. I selected the epoch-3 checkpoint using validation loss and chose the uncertainty margin (0.49) using validation data.

## Evaluation

The RGB-histogram baseline achieved 88.28% sensitivity, 95.34% specificity and 0.9569 AUROC on 4,459 validation images. MobileNetV3 achieved 97.83% sensitivity, 98.29% specificity and 0.9967 AUROC on that same partition.

On **3,805 cells from 31 held-out patients**, the selected MobileNetV3 model achieved **95.94% sensitivity, 96.62% specificity, 0.9919 AUROC and 0.9583 F1**, with 1,608 true positives, 2,057 true negatives, 72 false positives, and 68 false negatives.

Using the validation-selected uncertainty band, the model automatically classified **2,983 (78.4%)** of the test images, referring **822 (21.6%)** for human review. Among automatic classifications, **20 errors remained, including 10 infected cells classified as uninfected**. I did not have clinicians review the referred cells. I therefore cannot claim that the workflow corrects those errors or reduces clinical workload.

I report **individual cropped-cell results, not patient diagnosis accuracy**. They cannot establish safety for malaria screening or rule-out. Full aggregate evidence is in [RESULTS.md](RESULTS.md) and `results/`.

## Who benefits, and who could be harmed

Potential beneficiaries are researchers and laboratory educators investigating image classification and uncertainty-aware review. A false-negative prediction could create dangerous false reassurance, while a false positive could trigger additional testing. Changes in microscope, staining, specimen preparation, parasite stage and population may lead to model failures. I do not present this project as a clinically approved tool.

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
- I used OpenAI ChatGPT for planning, some code drafting, results reporting, and documentation. I ran the training and image analysis in Kaggle and checked the exported results.

## Submission checklist

- [x] Define research task and clinical limitations.
- [x] Download and examine the NIH cell images and patient mappings in Kaggle.
- [x] Create patient-disjoint train/validation/test partition.
- [x] Train baseline and MobileNet; choose one validation checkpoint.
- [x] Report held-out test metrics and an uncertainty-based referral experiment.
- [x] Publish aggregate results, split audit, and methodology in GitHub.
- [x] Verify separately uploaded private split manifest, aggregate summary, and Kaggle package versions; publish non-identifying audit.
- [x] Add the saved checkpoint to the demonstration branch.
- [x] Deploy and smoke-test the public Streamlit demo using training examples.
- [ ] Record and publish short walkthrough video.
- [ ] Add final links and submit on Devpost.
