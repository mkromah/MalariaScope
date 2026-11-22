# MalariaScope — measured research results

**Scope:** Evaluation on cropped individual-cell images from the NIH/NLM malaria dataset. **Not a clinical validation or patient-level diagnostic study.**

**Evidence inspected:** Two identical seven-file ZIP archives uploaded in the current conversation, containing `model_best.pt`, `baseline_validation.json`, `selection.json`, `test_metrics.json`, and three PNG figures. ZIP integrity tests passed. JSON arithmetic was checked, and the checkpoint metadata reports MobileNetV3-Small, seed 42, and best epoch 3. Training was done by the project author in Kaggle, not independently rerun during repository documentation.

## 1. Data and evaluation protocol

The author reported 27,558 images belonging to 201 unique patient IDs. Patients, not individual cells, were allocated into disjoint sets using seed 42:

| Split | Patient IDs | Images | Infected | Uninfected |
|---|---:|---:|---:|---:|
| Train | 139 | 19,294 | 9,749 | 9,545 |
| Validation | 31 | 4,459 | 2,354 | 2,105 |
| Test | 31 | 3,805 | 1,676 | 2,129 |

Baseline: RGB histograms + Logistic Regression. Candidate: pretrained MobileNetV3-Small with black-padding resize to 224×224 and ImageNet normalization. Train with augmentation; validate without augmentation. Trained for up to eight epochs, learning rate 0.0003, batch size 64; selected best checkpoint by lowest validation loss at epoch 3. The symmetric review margin (0.49) was chosen on validation data and frozen before test evaluation.

## 2. Validation comparison

| Metric | Logistic Regression | MobileNetV3 |
|---|---:|---:|
| Sensitivity | 88.28% | 97.83% |
| Specificity | 95.34% | 98.29% |
| AUROC | 0.9569 | 0.9967 |
| False negatives | 276 | 51 |
| False positives | 98 | 36 |

These figures support selection of the neural model over the simple color histogram baseline **on the validation partition**. They are not evidence of a benefit in clinical workflows.

## 3. Frozen held-out test results

| Measure | Value |
|---|---:|
| Held-out patients | 31 |
| Individual cells | 3,805 |
| Parasitized / uninfected | 1,676 / 2,129 |
| True positives (TP) | 1,608 |
| True negatives (TN) | 2,057 |
| False positives (FP) | 72 |
| False negatives (FN) | 68 |
| Sensitivity | 95.94% |
| Specificity | 96.62% |
| F1 | 0.9583 |
| AUROC | 0.9919 |
| Average precision | 0.9897 |

**Confusion matrix (actual rows × predicted columns):**

| Actual \ Predicted | Uninfected | Parasitized |
|---|---:|---:|
| Uninfected | 2,057 | 72 |
| Parasitized | 68 | 1,608 |

No claims about per-patient accuracy, smear interpretation, or malaria prevalence can be inferred from these cell-level metrics. The test performance is lower than validation performance, emphasizing the importance of separate evaluation.

## 4. Uncertainty-based referral

A validation-selected review band of 0.01–0.99 (endpoints included for referral) was used for research-only selective classification.

| Outcome | Parasitized cells | Uninfected cells | Total |
|---|---:|---:|---:|
| Correctly classified automatically | 1,286 | 1,677 | 2,963 |
| Incorrectly classified automatically | 10 | 10 | 20 |
| Referred for manual review | 380 | 442 | 822 |
| Total | 1,676 | 2,129 | 3,805 |

- Automatic classifications: **2,983 / 3,805 (78.40%)**.
- Referrals: **822 / 3,805 (21.60%)**.
- False negatives remaining among automatic decisions: **10**.
- Infected cells referred to humans: **380 / 1,676 (22.67%)**.
- Uninfected cells referred to humans: **442 / 2,129 (20.76%)**.
- Sensitivity calculated **only among automatically classified infected cells**: 99.23% (1,286 / 1,296). This is **conditional on selection** and should never be presented as whole-population sensitivity.
- The study did **not** evaluate whether a human correctly classifies the referred cells, the time required for review, or the actual cost reduction.

Selecting a high-confidence subset can make conditional performance appear high. The 822 referrals are unresolved, not automatically corrected predictions. Neither this band nor softmax confidence is clinically validated.

## 5. Evidence, files and reproducibility gaps

Aggregate results (without patient identifiers) are published in `results/baseline_validation.json`, `results/selection.json`, and `results/test_metrics.json`. The uploaded checkpoint's SHA-256 was:

`99fb60ab181c1fc666ce45706068a31d5be5d6a2e4bb6ceff7eab8d528d2d88c`

The user also generated PNG plots in Kaggle: held-out confusion matrix, uncertainty-based outcomes, and review outcomes per class. These were inspected against the supplied counts but are not yet stored as binary assets in this repository. The local checkpoint and figures remain in the user's backup.

**Reproducibility update (22 November 2026):** The author subsequently uploaded all three previously missing records separately. The private `split_manifest.csv` was audited: 27,558 unique image paths, 201 patients, no missing values, zero patient overlap among partitions, and exact agreement with `split_summary.json`. Non-identifying counts and audit checks are now published in [`results/split_summary.json`](../results/split_summary.json) and [`results/data_audit.json`](../results/data_audit.json); core software versions are in [`docs/REPRODUCIBILITY.md`](REPRODUCIBILITY.md). The manifest, which contains patient-to-cell associations, **has not been uploaded publicly**. The full 937-package environment snapshot is retained privately; the repository documents key versions and its SHA-256.

**Still outstanding:** decide how to distribute the trained checkpoint; verify a fresh end-to-end reproduction or document platform/hardware deviations; and deploy/test a public demo. No external laboratory validation or patient-cluster confidence intervals have been calculated.

## 6. Limitations and potential harms

This dataset comprises pre-cropped images; it is not representative of entire blood smear workflows or routine patients. Repeated cells from the same patient are correlated. Class balance is imposed by the dataset and not reflective of clinical prevalence. Real-world variation in staining, microscope hardware, and preparation could reduce performance. A missed infected cell, particularly an unflagged false negative, could foster dangerous reassurance. No clinical deployment or treatment decision is warranted.

## 7. Next studies

Add patient-cluster bootstrap uncertainty intervals; evaluate on independently sourced microscopy slides; measure image-quality failure and detection of out-of-distribution inputs; involve skilled readers to estimate referral burden and error correction; measure inference latency on deployment hardware. These are **proposed**, not completed.

**Dataset:** [NIH/NLM malaria image resource](https://lhncbc.nlm.nih.gov/LHC-research/LHC-projects/image-processing/malaria-datasheet.html). **Source code:** this repository. **Development assistance:** OpenAI ChatGPT helped plan, draft and review code and docs.
