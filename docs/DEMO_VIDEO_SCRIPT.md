# MalariaScope — final demo video plan

**Status:** Script and recording plan prepared; a recorded video has not yet been confirmed. Author-provided Streamlit app link: https://malariascope-mkromah.streamlit.app/ (independent live smoke test pending).

**Target length:** About 90 seconds. Show the live application and its real output in the **first 60 seconds**. Use the actual deployed Streamlit app, not a simulated prediction. Capture the whole browser window or app clearly enough for a judge to follow.

## 0:00–0:12 — The problem and the live app
**On screen:** Open the deployed MalariaScope Streamlit page, with its research-only warning visible.

**Say:** "MalariaScope explores whether AI can help identify malaria-infected red blood cells in microscope images. This is a research demonstration, not a medical diagnosis tool."

## 0:12–0:40 — Show it working
**On screen:** Upload an authorized example of a single, cropped blood-cell image. Show the prediction and model score. If a suitable example is available, also show an uncertain result that is referred for manual review.

**Say:** "I upload one cropped cell image. The model analyzes it and shows a classification or flags it for manual review when its score falls in the uncertainty range."

Do not state that a predicted label is correct unless you also show the ground-truth label. Do not show patient identifiers.

## 0:40–1:07 — Explain the evaluation
**On screen:** Show the held-out test results table or confusion matrix already documented in `docs/RESULTS.md`.

**Say:** "We trained a MobileNetV3 model using the NIH malaria image dataset and tested it on 3,805 cell images from 31 held-out patients. It achieved 95.94% sensitivity and 96.62% specificity. Our uncertainty rule referred 21.6% of test images for review. Ten infected cells were still incorrectly classified among the automatic decisions."

Use readable on-screen labels: **cell-level test**, **31 held-out patients**, **not patient-level diagnostic accuracy**.

## 1:07–1:30 — Limits and reproducibility
**On screen:** Show the GitHub README and its evaluation/attribution links.

**Say:** "This study uses cropped cells from one dataset, not complete blood smears, and we have not tested it in clinics or on new microscopes. The code, evaluation results, and methods are documented in our public GitHub repository."

## Recording checklist

- [ ] Live app URL opens in an incognito/private browsing window.
- [ ] Upload a test image and show the actual model output; no artificial or fabricated results.
- [ ] Ensure the demo clearly shows the review warning and medical-use disclaimer.
- [ ] Record at a readable resolution with clear narration.
- [ ] Check that any figures/labels agree with `docs/RESULTS.md`.
- [ ] Remove personal data, credentials, patient identifiers, API keys, or access tokens.
- [ ] Publish the final video via a shareable URL, then add it to Devpost.
- [ ] Run a final playback check with audio before submitting.

**Required final links:** GitHub repository; public Streamlit app; demo video. The app URL is documented; live functioning and the video URL remain to be verified/recorded.
