---
name: kaggle
description: "Run and manage Kaggle jobs from the local workspace: authenticate the Kaggle CLI, inspect datasets, attach data, push script or notebook kernels, request CPU/GPU/TPU accelerators, monitor execution, and download outputs. Use when the user asks to run code on Kaggle, use Kaggle GPUs, manage Kaggle datasets/kernels, or retrieve Kaggle job results."
---

# Kaggle

Use Kaggle as a remote execution service when local compute is unsuitable or the user explicitly requests Kaggle. Prefer the Kaggle CLI over browser automation.

## 1. Locate the CLI

Do not assume `kaggle` is on `PATH`. Check, in order:

```powershell
where.exe kaggle
Get-ChildItem "$env:APPDATA\Python\Python*\Scripts\kaggle.exe"
```

On this machine the current CLI is typically:

```text
%APPDATA%\Python\Python312\Scripts\kaggle.exe
```

Use the executable path directly if `PATH` is stale. The bundled helper can locate it:

```powershell
python scripts/kaggle_job.py doctor
```

The helper is in `scripts/kaggle_job.py`; use `--help` for all commands.

## 2. Verify authentication first

```powershell
kaggle --version
kaggle datasets list -m --page-size 5
kaggle auth login
```

Newer Kaggle CLI versions use OAuth credentials in `~/.kaggle/credentials.json`. Never print credential values. If a command returns `401`/`403` or says authentication is required, stop and ask the user to complete `kaggle auth login`; do not silently switch to an older CLI.

## 3. Inspect the dataset

```powershell
kaggle datasets list -m --page-size 50
kaggle datasets files <owner>/<dataset-slug> --page-size 100
kaggle datasets metadata <owner>/<dataset-slug>
```

For private datasets, verify the active Kaggle account has access. A `403` on a private dataset is not a code bug.

## 4. Create a kernel folder

Required layout:

```text
job-folder/
|-- kernel-metadata.json
`-- job.py            # or job.ipynb
```

Metadata for a script kernel:

```json
{
  "id": "<username>/<kernel-slug>",
  "title": "<human title>",
  "code_file": "job.py",
  "language": "python",
  "kernel_type": "script",
  "is_private": "true",
  "enable_gpu": "true",
  "enable_tpu": "false",
  "enable_internet": "true",
  "machine_shape": "NvidiaTeslaT4",
  "dataset_sources": ["<owner>/<dataset-slug>"],
  "competition_sources": [],
  "kernel_sources": [],
  "model_sources": []
}
```

Use `"machine_shape": "NvidiaTeslaT4"` for Kaggle's **GPU T4 x2**. Verify the runtime count inside the job:

```python
import torch
print(torch.cuda.device_count())
print([torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())])
```

Do not claim two GPUs merely because the metadata requests them; verify the job logs.

## 5. Make the job portable

- Write outputs to `/kaggle/working`.
- Discover attached files instead of hard-coding one mount path:

```python
from pathlib import Path
candidates = sorted(Path("/kaggle/input").rglob("*.csv"), key=lambda p: p.stat().st_size, reverse=True)
data_path = candidates[0]
```

- Set `enable_internet` only when the job needs package downloads or network access.
- Avoid embedding tokens, credentials, or private data in the source file.
- Print dataset path, row counts, device count, and output paths early in the log.

## 6. Push and monitor

```powershell
kaggle kernels push -p <job-folder> --accelerator NvidiaTeslaT4
kaggle kernels status <owner>/<kernel-slug>
kaggle kernels logs <owner>/<kernel-slug>
kaggle kernels output <owner>/<kernel-slug> -p <output-folder>
```

The helper wraps the full cycle:

```powershell
python scripts/kaggle_job.py push --folder <job-folder> --accelerator NvidiaTeslaT4 --output <output-folder> --poll 60
python scripts/kaggle_job.py status <owner>/<kernel-slug>
python scripts/kaggle_job.py download <owner>/<kernel-slug> --output <output-folder>
```

When polling, stop on `COMPLETE` or `ERROR/FAILED`; do not repeatedly re-push a job while a previous version is running.

## 7. Diagnose failures from logs

- Dataset path not found: list `/kaggle/input` or search for large CSV files.
- `401`/`403`: re-authenticate or confirm private dataset access.
- GPU unavailable: check `torch.cuda.is_available()` and the requested accelerator.
- Non-finite loss: inspect the first batch, input finite values, clipping, and package/GPU compatibility before changing the model.
- Missing output: confirm files were written to `/kaggle/working` and download after completion.

See `references/kernel-metadata.md` and `references/troubleshooting.md` for templates and detailed diagnostics.


## 8. Smoke test

Use `examples/smoke-kernel` to verify the complete path without a dataset or GPU:

```powershell
python scripts/kaggle_job.py push --folder examples/smoke-kernel --output ./smoke-output --poll 10
```

A successful run writes `smoke_result.json` and exits with a `COMPLETE` status. Use this before debugging a larger job.
