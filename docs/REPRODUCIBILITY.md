# MalariaScope — Kaggle environment record

The author uploaded `pip-freeze.txt` from the Kaggle runtime. It contains **937 package entries**, many preinstalled by Kaggle and unrelated to this study. The complete snapshot is kept in the author's private research backup; key direct dependencies used by this project are listed below. These versions were extracted from the uploaded file, **not inferred from `requirements.txt`**.

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

Kaggle GPU drivers, NVIDIA runtime, Python interpreter and hardware version have not all been established by this uploaded `pip freeze`; the exact execution environment cannot be reconstructed from the package list alone. A fresh installation of the full 937 packages is **not recommended**: the file includes Kaggle/Colab environment-specific and Git-based entries. The project's `requirements.txt` is for practical installations rather than a bit-for-bit lock file.

## Dataset split and privacy

The uploaded `split_manifest.csv` contained **27,558 rows**, four columns (`path`, `label`, `patient_id`, `split`), **201 unique patient IDs** and no missing values. Zero duplicate image paths and **zero patient overlap** were found among train, validation and test.

For machine-readable, non-identifying counts and an audit record, see [split_summary.json](../results/split_summary.json) and [data_audit.json](../results/data_audit.json). The raw patient-level manifest was **not published**; the public audit includes its SHA-256, allowing a user holding the private file to check it has not changed.

## Reproduction notes

1. Use the official NIH/NLM malaria dataset, preserving its filenames and patient mappings.
2. Run `scripts/prepare_data.py` with seed 42 and verify its output counts against the public aggregate split summary. A seed alone cannot guarantee identical assignments if the source maps/order or script change; retain the private manifest for byte-exact comparison.
3. Use the preprocessing in `scripts/preprocessing.py`.
4. Run the baseline, 8-epoch CNN training and test evaluation separately, using validation-only model and review threshold selection.
5. Compare generated JSON files with `results/`, and do not use the test partition to choose model/threshold.

**Limitations:** The verification performed here checked the uploaded split manifest's consistency. It did not redownload raw images or independently rerun the training code.
