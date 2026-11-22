# MalariaScope — Kaggle environment record

I exported `pip-freeze.txt` from Kaggle. It lists **937 packages**, many of which Kaggle preinstalled and this project does not use. I keep the complete snapshot in my research backup and list the main packages here, using the saved file rather than guessing versions from `requirements.txt`.

| Package | Recorded version |
|---|---|
| torch | 2.11.0+cu130 |
| torchvision | 0.26.0+cu130 |
| numpy | 2.1.3 |
| pandas | 2.3.3 |
| scikit-learn | 1.6.1 |
| Pillow | 11.3.0 |
| SciPy | 1.16.3 |
| matplotlib | 3.10.0 |
| Streamlit | 1.67.0 |

The exact 937-entry file has SHA-256:

`15d8b50f333e6a55731974b383d089c8773fdce60ff88462db86d060b0bf68aa`

I cannot reconstruct the full Kaggle runtime from the package list alone: it does not record all GPU driver, NVIDIA runtime, Python interpreter, and hardware details. A fresh installation of the full 937 packages is **not recommended**: the file includes Kaggle/Colab environment-specific and Git-based entries. The project's `requirements.txt` is for practical installations rather than a bit-for-bit lock file.

## Dataset split and privacy

I checked **27,558 rows** and four columns in `split_manifest.csv` (`path`, `label`, `patient_id`, `split`), **201 unique patient IDs** and no missing values. I found no duplicate image paths and **no patient overlap** between training, validation, and testing.

For machine-readable, non-identifying counts and an audit record, see [split_summary.json](../results/split_summary.json) and [data_audit.json](../results/data_audit.json). I keep the raw patient-level manifest private. I publish its SHA-256 so anyone who has the file can check its integrity.

## Reproduction notes

1. Use the official NIH/NLM malaria dataset, preserving its filenames and patient mappings.
2. Run `scripts/prepare_data.py` with seed 42 and verify its output counts against the public aggregate split summary. A seed alone cannot guarantee identical assignments if the source maps/order or script change; retain the private manifest for byte-exact comparison.
3. Use the preprocessing in `scripts/preprocessing.py`.
4. Run the baseline, 8-epoch CNN training and test evaluation separately, using validation-only model and review threshold selection.
5. Compare generated JSON files with `results/`, and do not use the test partition to choose model/threshold.

**Limitations:** I checked that the saved split manifest is internally consistent. I did not redownload the raw images or rerun the full training pipeline.
