# MalariaScope — Six-award readiness plan (2026-11-22)

**Competition:** AI for Medicine hackathon (Open Health AI Collective), submission deadline 2026-12-04 23:45 EST / 2026-12-05 07:45 Türkiye time.

**Purpose:** Enter all six award categories competitively, prioritizing a credible Grand Prize submission and the strongest existing research/reproducibility work. Award outcomes cannot be promised.

**Current snapshot:** `archive/hackathon-evaluated-2026-11-22` points to commit `80bfe64ce3f19e6d5c26be1395a3f94367e3b9c7`; it preserves source code and public aggregate results (not private model weights or patient-level manifest). All improvements go to `improvements/award-readiness` first and require tests before merging into `main`.

## Non-negotiable protections

1. Do **not** retrain or overwrite `model_best.pt`, change the current review margin (0.49), or edit reported evaluation outcomes for presentation purposes.
2. Do **not** use the held-out test images or test labels to tune parameters, select a new model or calibrate a threshold. Any new test-set descriptive analysis must be clearly labeled post-hoc.
3. Never push `split_manifest.csv`, patient-level IDs, raw data or copyrighted dataset images to the public repository without an explicit licensing/privacy review.
4. Do not claim a medical diagnosis, proven safety, human-in-the-loop error correction, external generalization, or clinical implementation.
5. Keep every scientific figure linked to saved results and state which images were referred but not manually adjudicated.
6. Work as a student-led project: the event is student-only, not a company submission. No fabricated customers, pilot partners, or regulatory endorsements.

## Six award categories, deliverables and acceptance tests

| Award | What success looks like | Priority |
|---|---|---|
| Grand Prize | Strong evaluation and a visibly working end-to-end public demo; accurate clinical framing; clear explanation in submission and video | Critical |
| Excellence in Research & Reproducibility | Verified patient-disjoint split, strong baseline and held-out test, code/version provenance; smoke-tested reproduction commands; appropriate uncertainty estimates if available | Critical |
| Most Promising Venture | Defined end user (e.g. microscopy lab training/research), realistic time/cost problem, documented stakeholder feedback (if obtained), adoption and governance barriers, small credible pilot plan | Medium |
| Best Logo | Original, legible, distinctive MalariaScope logo with microscope/cell/review motif; consistent use on app, repository, video, and thumbnail; no unlicensed assets | Medium |
| Best User Interface | Fast and understandable input → processed image → result → uncertainty/manual review; accessible labels; clear not-for-clinical-use warning; tested on phone and desktop | Critical |
| Best Presentation | Video shows working live product **within the first 60 seconds**, then problem, baseline, test results, limitations and what comes next; no unsupported clinical claims | Critical |

Judging criteria: Technical Depth 25%; Rigor & Reproducibility 25%; Clinical Relevance & Honesty 25%; Demo Quality 25%.

## Delivery stages (work one step at a time)

### Phase A — Protect and deploy the evaluated model (immediate)
- [x] Freeze current GitHub state on the archive branch (source and results only).
- [x] Start a separate award-readiness development branch.
- [ ] Verify checkpoint hash against original backup; safely distribute the checkpoint and `selection.json` without patient data.
- [ ] Run the existing Streamlit app against the real checkpoint; make a smoke test using a public, licensed or user-permitted sample cell.
- [ ] Deploy a public demo and test from a fresh browser session.

### Phase B — Engineering and interface
- [ ] Add unit tests for file validation, preprocessing, checkpoint loading and both sides of the review threshold; keep test images synthetic.
- [ ] Extend GitHub Actions to run appropriate unit/smoke tests.
- [ ] Build user-friendly Streamlit input → result → review decision flow, with accessible layout and visible limitations.
- [ ] Measure inference latency on specified hardware; avoid unsupported real-world speed claims.

### Phase C — Strengthen existing scientific evidence
- [ ] Preserve patient-disjoint and baseline validation evidence (already measured).
- [ ] Obtain/preserve per-image probabilities and patient group IDs privately **without rerunning model selection** if safe and needed for statistical intervals.
- [ ] If doing patient-cluster bootstrap uncertainty intervals, mark these as descriptive post-hoc analysis; do not change trained model or threshold.
- [ ] If adding evidence visualizations, generate directly from stored aggregate metrics; distinguish selective accuracy from whole-test accuracy.
- [ ] Improve instructions for reproducing exact Kaggle environment and data split; verify public repo test workflow.

### Phase D — Venture, identity and presentation
- [ ] Prepare concise, evidence-based target user and adoption hypotheses; gather genuine feedback only if available, label all plans as proposed.
- [ ] Make original logo and consistent visual identity for UI/README/demo.
- [ ] Draft concise Devpost project summary, attribution, honest harms section and meaningful one-month plan.
- [ ] Record a demo with actual functioning inference visible within first minute.
- [ ] Open the Devpost submission from a fresh browser, check all requirements and live links, and submit before the official deadline.

## What is already strong

27,558 NIH cropped images; 201 distinct patient IDs; zero cross-split patient leakage; validation baseline vs pretrained MobileNetV3-Small; frozen held-out test with 3,805 images from 31 patients; sensitivity 95.94%, specificity 96.62%, AUROC 0.9919; uncertainty-based review of 822/3,805 images, with 10 infected cells still incorrectly automatically labeled uninfected. The model is **not clinically validated**.

## Publication relationship

Post-hackathon external validation, new models, and paper writing belong to a separate research track. They must not silently alter the submitted hackathon model or re-use the existing held-out test set for optimization.

**Official rules:** https://ai-for-medicine.devpost.com/ (recheck at submission).
