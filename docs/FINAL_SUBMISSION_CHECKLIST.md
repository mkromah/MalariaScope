# MalariaScope — final Devpost submission checklist

**Target deadline:** **5 December 2026, 07:45 Türkiye time (UTC+3)**. Aim to complete checks and submit on 4 December to leave room for problems.

This checklist reflects the project author's confirmation that Streamlit deployment is complete. Items requiring a public URL or live verification remain unchecked until that evidence is recorded. Do **not** repeat completed Kaggle training merely to tick boxes.

## Completed research work
- [x] Public GitHub repository with README and attribution.
- [x] NIH malaria dataset ingestion, integrity review, and patient-disjoint split.
- [x] Logistic Regression baseline and MobileNetV3 training.
- [x] Held-out test results and uncertainty-policy evaluation.
- [x] Reproducibility audit and aggregate metrics documented.
- [x] Streamlit app implemented and reportedly deployed by the project author.

## Final checks (only what remains to confirm)
- [ ] Add **public Streamlit app URL** to README and Devpost entry. The repo does not yet contain the exact URL.
- [ ] Open the deployed site without developer credentials; confirm a cropped-cell image produces a real prediction or manual-review referral.
- [ ] Confirm the deployed application can access its trained checkpoint, and document that mechanism without sharing secrets or private patient mappings.
- [ ] Check that the app's prominent warning explains that this is **not clinical diagnosis**.
- [ ] Record and publish the [90-second demo video](DEMO_VIDEO_SCRIPT.md) with the app visibly working within the first 60 seconds.
- [ ] Check project description includes the **Evaluation** section, who benefits/could be harmed, limitations, and what would be done with another month.
- [ ] Ensure model, dataset, framework, code assistance, and any reused resources are attributed.
- [ ] Add public GitHub URL, live app URL, and video URL to Devpost; confirm no fields remain incomplete.
- [ ] Submit and save the confirmation page/receipt.

## Measured evidence to quote accurately
- Held-out test: **3,805 cell images**, **31 patients**.
- Sensitivity **95.94%**, specificity **96.62%**, AUROC **0.9919**.
- Review referrals **822/3,805 (21.6%)**; the remaining automatic decisions included **10 false-negative infected cells**.
- These results describe **cropped individual blood cells** only. They do not measure whole-smear or patient-level diagnosis. Manual reviews were *not* carried out for the referred cells.

**Source of record:** [results](RESULTS.md), [reproducibility audit](REPRODUCIBILITY.md), [Devpost text](HACKATHON_SUBMISSION.md).

## Final links (record after verification)

- Public repository: https://github.com/mkromah/MalariaScope
- Live Streamlit application: *URL not yet recorded in this repository*
- Video demonstration: *URL not yet recorded*
- Final Devpost submission: *not yet confirmed*
