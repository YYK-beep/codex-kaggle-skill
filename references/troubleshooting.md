# Kaggle Troubleshooting

## CLI not found

Use `where.exe kaggle` and `%APPDATA%\Python\Python*\Scripts\kaggle.exe`. Do not confuse the older `kaggle.json` client with the newer OAuth CLI.

## Authentication required or 401

Run:

```powershell
kaggle auth login
kaggle datasets list -m --page-size 5
```

Never print `~/.kaggle/credentials.json`.

## 403 on dataset files

The active account may lack access to a private dataset. Confirm the dataset reference and account. Do not rename the dataset or guess a replacement.

## Dataset file not found inside a kernel

List the actual mount:

```python
from pathlib import Path
for p in Path("/kaggle/input").rglob("*"):
    print(p)
```

or choose the largest attached CSV:

```python
candidates = sorted(Path("/kaggle/input").rglob("*.csv"), key=lambda p: p.stat().st_size, reverse=True)
```

## Kernel runs on CPU despite requesting GPU

Check the metadata and the push command, then print inside the job:

```python
import torch
print(torch.cuda.is_available(), torch.cuda.device_count())
print([torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())])
```

## Kernel ERROR

Download logs with:

```powershell
kaggle kernels logs OWNER/KERNEL
```

Fix the cause and push a new version. Do not treat a failed log as a model result.

## Output files missing

A kernel must write files under `/kaggle/working`. After status is `COMPLETE`, download with:

```powershell
kaggle kernels output OWNER/KERNEL -p ./output
```

## Long-running job

Poll status rather than re-pushing. Stop at `COMPLETE` or `ERROR/FAILED`. Use a bounded timeout and report elapsed time.

## Two-GPU numerical failures

Some model packages are not safe when multiple instances share CUDA in separate threads. Prefer sequential per-GPU runs unless the package explicitly supports distributed execution. Verify finite losses on the first batch before committing to a long run.
