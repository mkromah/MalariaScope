# MalariaScope — pilot plan for uncropped microscopy fields

**Status:** Proposed extension, **not trained or evaluated**. The existing, frozen MobileNetV3 model and reported 3,805-cell test results remain unchanged.

## Why uncropped images are a different task

MalariaScope currently classifies already-cropped, individual cell images. A full microscopy field contains background, overlapping cells, artifacts, and multiple potential parasites. Feeding an entire field directly into the cropped-cell model would not produce a scientifically valid smear-level result.

A suitable extension has **two stages**:

1. **Locate candidate cells or parasites** in a larger image, with a detector or annotated segmentation model.
2. **Classify appropriately cropped candidates** with the existing frozen classifier; preserve a separate reject/review option and show detections overlaid on the original field.

The two-stage pipeline must be assessed **end to end**. Cropping from reference bounding boxes for evaluation would overstate real-world performance because it bypasses detection errors.

## Public data candidates to audit

- [NIH/NLM thin blood smear full-field images and cell annotations](https://data.lhncbc.nlm.nih.gov/public/Malaria/NIH-NLM-ThinBloodSmearsPf/ReadMe.pdf): field images with polygon/point annotations; confirm downloaded structure, licensing and mapping metadata before use.
- [Makerere University annotated microscopy datasets](https://air.ug/microscopy/): includes thick smear images with parasite bounding-box annotations. Thick smears should be evaluated **separately** from thin-cell classification; never treat this as the same label task.

## Minimal exploration without new clinical claims

- [ ] Audit license, annotation scheme, patient/site metadata and image resolution.
- [ ] Decide **thin-smear cell localization** versus **thick-smear parasite detection**; don't merge these tasks.
- [ ] Partition by slide/patient/acquisition site **before** augmentation or patch generation.
- [ ] Establish annotation coverage and ground-truth labels on full fields.
- [ ] Train a baseline detector; evaluate detections with recall and precision at stated localization tolerance or IoU.
- [ ] Evaluate combined detector + classifier with end-to-end missed-parasite counts and review workload.
- [ ] Use a new untouched test partition; measure failures on blur, stain change, overlaps, and difficult backgrounds.
- [ ] Label all examples as research data, with no diagnosis or parasitemia output.

## Hackathon decision

The current cropped-cell model has measured held-out performance. Do **not** quietly replace those results with full-field claims. Treat any uncropped-image result as a separate exploratory experiment until it has its own evaluation and limitations. The UI and PDF redesign does not alter the frozen model.
