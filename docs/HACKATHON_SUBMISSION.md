# Hackathon submission draft — MalariaScope

**Status:** In development. **Do not submit this as if results have been measured.** Replace the bracketed placeholders only after reproducing the analysis.

## The problem and who has it

Manual examination of thin blood smears requires training and attention. MalariaScope investigates whether a lightweight image classifier can separate cropped parasitized and uninfected red blood cells and refer uncertain cases to a microscopy professional. Its intended audience is researchers and laboratory training teams exploring computer-assisted microscopy, **not patients seeking diagnosis**.

## What we built

The repository implements official NIH malaria cell-image retrieval, patient-to-image mapping, patient-disjoint dataset partitions, a simple RGB histogram logistic regression baseline, a MobileNetV3-Small training pipeline, validation-only selection of a review margin, held-out test metrics, and a Streamlit research interface. Training and clinical performance are **not yet demonstrated**.

## Evaluation — fill after executing

- Training/validation/test split: patient-disjoint using seed 42; report [N] patients and [N] images in each split.
- Baseline (validation): [AUROC], [sensitivity], [specificity].
- Final test set (frozen model): [AUROC], [sensitivity], [specificity], [TP, FP, TN, FN].
- Review threshold set solely on validation: [margin]; referrals [n/N] (%).
- Missed infected cells after deferral: [n] of [all infected test cells].
- Deployment and inference time: [measured hardware and latency].
- Caveats: the outcome is **cell-label accuracy**, not patient-level malaria screening accuracy.

All reported results must point to exact saved output files, scripts, model-weight provenance, environment versions, dataset hashes, and the specific commit used. Do not state target performance as actual performance.

## Who benefits, and who could be harmed

Potential beneficiaries are researchers studying microscopy-aided screening and laboratory educators evaluating uncertainty-aware classification. A false negative could incorrectly reassure a clinician or patient and delay diagnosis; a false positive could cause needless concern or review. Domain shift in microscopes, staining, parasite stages, and collection sites may cause unpredictable failure. Referrals based on an unvalidated threshold must not be treated as safe clinical triage.

## Limitations

- Trained only on cropped individual red cells, not entire clinical blood smears.
- Labels and patient mapping may not capture external-site and microscope variability.
- Noninfected cells are not equivalent to confirmed malaria-negative patients.
- Validation-selected confidence bands cannot guarantee clinical sensitivity.
- Intended only for controlled research demonstration; no real-world diagnostic claims.

## What we would do with another month

Test on images from a separate acquisition site and additional smear conditions; measure calibration and referral workload; add quality-control checks; undertake a blinded laboratory-reader comparison subject to appropriate clinical oversight.

## Full attribution

NIH/NLM malaria microscopy image dataset and original research listed in the [official dataset datasheet](https://lhncbc.nlm.nih.gov/LHC-research/LHC-projects/image-processing/malaria-datasheet.html); PyTorch/torchvision pretrained MobileNetV3 weights if used; scikit-learn; Streamlit; Python packages recorded in requirements. OpenAI ChatGPT assisted with code drafting, workflow design and documentation; outputs require review and verification.

## Before submitting

- [ ] Obtain patient mapping and download the images
- [ ] Verify data integrity and record dataset hashes
- [ ] Run and inspect data split and sample image quality
- [ ] Train baseline and MobileNet with frozen seed/config
- [ ] Select one final model from validation data
- [ ] Run exactly one held-out test evaluation for reporting
- [ ] Review numerical results and avoid clinical overclaims
- [ ] Publish reproducible trained weights or a reliable retrieval method
- [ ] Deploy and manually verify demo
- [ ] Capture working demo video and include repository/live links
