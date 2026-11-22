# Running MalariaScope on Kaggle (GPU)

I keep the code in GitHub and run data processing and training in Kaggle. I download the NIH dataset into the Kaggle working directory and do not commit it to GitHub.

1. Open a new Kaggle notebook, enable **Internet** (if available) and the GPU accelerator.
2. In a notebook cell run:

```bash
!git clone https://github.com/mkromah/MalariaScope.git
%cd MalariaScope
!python -m pip install -r requirements.txt
!python scripts/download_data.py --extract
!python scripts/prepare_data.py
```

3. Review `data/processed/manifest.summary.json`. Every split must include infected and uninfected images, and no patient may occur across splits.
4. Run these **in order**:

```bash
!python scripts/baseline.py
!python scripts/train.py --epochs 8 --batch-size 64
!python scripts/evaluate.py
```

5. I save `outputs/baseline_validation.json`, `outputs/selection.json`, `outputs/test_metrics.json`, and `outputs/model_best.pt` as Kaggle notebook outputs. Record package versions (`!python -m pip freeze`). **The raw NIH dataset stays out of GitHub. I publish model weights only in the demonstration branch where needed.** Do not report results until you have read the files and validated the full run.

Kaggle can interrupt a notebook or change compute quotas. GPU, Internet and dataset downloads must be available in the actual Kaggle session. If `download_data.py` fails, inspect the NIH URL and Kaggle network settings rather than swapping datasets without documenting the change.

Deployment requires model weights distributed through a separate, reliable and properly licensed mechanism, or a repo release if size and terms permit. The current Streamlit app intentionally declines to predict until its weights exist.
