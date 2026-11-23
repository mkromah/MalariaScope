# MalariaScope — Uncropped Microscopy Validation and Detection Pilot

**Status (23 November 2026):** Project design only. **No full-field model training, external test results, or improvement claim yet.** Preserve the frozen cell-level MobileNetV3 and reported 3,805-cell test results as the existing validated research benchmark.

## Next session — 24 November 2026 (agreed plan)

**Use both uncropped microscopy datasets in complementary, separate research experiments:**

- **NIH/NLM full-field thin-smear microscopy**: audit licensing, annotation format, patient identities and overlap with the original NIH cropped-cell training dataset; develop or pilot cell localization. Do not call this an independent external test until overlap has been ruled out.
- **Makerere University (Uganda) full-field thin smears**: audit access, complete cell-label coverage and patient/slide identifiers; use as the preferred candidate for independent generalization testing of the frozen MobileNetV3 on expert-annotated cell crops, then assess automated detection + classification separately if feasible.

**Tomorrow's first action:** Start by auditing the download/access, metadata and labels for **both** datasets, with a clean numbered notebook. Keep NIH and Uganda results separate, avoid train/test leakage, and **do not retrain or change the currently deployed model yet**. Only propose training a detector or fine-tuning after confirming annotation quality and evaluation splits.

This is a note for the next work session, not a completed experiment or a scheduled reminder.

## Research question

Can the existing cell-image classifier retain useful performance when cells come from realistic, *uncropped thin-smear microscopy fields*, and can a separate cell detector locate candidate cells accurately enough for an end-to-end, uncertainty-aware pipeline?

*Reliability is measured, not assumed. A new detection stage can introduce additional false negatives.*

## Data sources and key caution

1. **NIH/NLM Thin Blood Smears Pf**: https://data.lhncbc.nlm.nih.gov/public/Malaria/NIH-NLM-ThinBloodSmearsPf/index.html
   - Provider README: https://data.lhncbc.nlm.nih.gov/public/Malaria/NIH-NLM-ThinBloodSmearsPf/ReadMe.pdf
   - 193 patients, 5 full-field images per patient; 5312 x 2988 resolution. Polygon and point subsets have annotations for parasitized/uninfected cells and WBCs.
   - The full-field NIH images and our 27,558 cropped NIH cell images trace to the **same original malaria research program/hospital**. Patient and image overlap is plausible; **this dataset must not be described as independent external validation unless overlap is ruled out explicitly**. Use for annotation-format exploration and developing a cell detection baseline with strictly separated patient identifiers and provenance checks.
   - The index includes a separate *Data License Agreement.docx*. Review it before redistribution, republication or training reuse. Archive is about 690 MB.

2. **Makerere University / Lacuna malaria dataset (Uganda)**:
   - Data paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC11719325/
   - Harvard Dataverse: https://dataverse.harvard.edu/dataverse/airlab_lacuna_mal
   - 1,000 thin-smear fields and 3,000 thick-smear fields, with image annotations. Thin-smear labels include parasitized cells, trophozoites, WBCs and artifacts. Check each available annotation class and whether *all uninfected cells are annotated* before specifying denominators for cell-level specificity.
   - Different hospital/equipment setting; appropriate *candidate* for a domain-shift benchmark. Check access, rights, origin, slide IDs, image quality and train/test provenance first.
   - **Do not mix thick- and thin-smear tasks.** The current classifier expects a cropped red blood cell from a thin smear.

## Three distinct experiments (in order)

### Experiment A — Audit (no training)
- Download/acquire dataset metadata and a small set of representative full-field images in Kaggle.
- Audit image size, file quality, annotation formats, class completeness, patient/slide identifiers, license and overlap.
- Record dataset version/hash and whether the source can support evaluation of both infected and uninfected cells.
- Stop if annotations are insufficient for the proposed metric.

### Experiment B — Isolate model generalization
- For regions with reliable expert annotations, crop cells **using reference coordinates** solely as a *classifier-only diagnostic test*.
- Run the **frozen** MobileNetV3 checkpoint without retraining.
- Evaluate per-cell sensitivity and (only where confirmed complete negative labels exist) specificity, confusion matrix, abstention/review fraction and false negatives.
- This experiment does **not** represent automated full-field performance because a human/ground truth supplied the crops.
- Use a different acquisition site if possible; account for patient/slide clustering.

### Experiment C — Full-field pipeline
- Split by patient/slide before patch generation or augmentation.
- Train or adapt a *cell locator* (e.g. a small object detector), using a thin-field dataset with valid cell locations.
- Evaluate detection recall/precision and cell-localization error at specified IoU or centroid tolerance.
- Then pass predicted crops through the frozen classifier. Evaluate **end to end** against full-field annotations: missed infected cells, spurious alerts per field, count of undecidable/referred regions, throughput and runtime.
- Compare automated detected crops against expert-provided crops and explain failures. Unannotated or overlapping cells should not be silently counted as correct negatives.

## Release decision

- Keep existing cropped-cell app and documented metrics unchanged.
- Promote a new 'Full-field experimental' tab only if (1) annotations are trustworthy, (2) held-out end-to-end metrics can be reproduced, and (3) warning text clearly states that this is **not** an entire-smear or patient diagnosis.
- Otherwise include this work as a clearly labeled pilot/future research direction.

## Suggested timeboxed order before 5 December 2026

1. **One session:** audit Uganda thin-smear labels and compare NIH field annotation structure; check license/provenance.
2. **Next session:** run the frozen model on reference-cropped, separately sourced annotated cells **if valid labels are available**; document any performance shift.
3. **Only if feasible:** add and benchmark cell localization; don't sacrifice the evaluated primary submission.
4. Freeze new experiments and finish the demonstration video/Devpost by 4 December.

No result should be described as 'improved' until quantitative held-out evidence is available.
