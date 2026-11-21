# Kaggle Skill for Codex

A small Codex skill for running reproducible jobs on Kaggle and retrieving their outputs.

## What it covers

- Locating the current Kaggle CLI instead of relying on a stale `PATH`
- Checking OAuth authentication without exposing credentials
- Inspecting private/public datasets and attached files
- Creating script or notebook kernels
- Requesting Kaggle GPU T4 x2 (`NvidiaTeslaT4`)
- Pushing, polling, logging, and downloading kernel output
- Diagnosing common mount, permission, GPU, and non-finite-loss failures

## Install

Copy the `kaggle` folder into your Codex skills directory, for example:

```text
C:\Users\<you>\.codex\skills\kaggle
```

The skill can also be referenced directly from this repository.

## Quick start

```powershell
python scripts/kaggle_job.py doctor
python scripts/kaggle_job.py push --folder examples/smoke-kernel --output ./smoke-output --poll 10
```

The helper locates a current Kaggle CLI (including OAuth-based CLI 2.x), verifies authentication, pushes a kernel, waits for completion, and downloads output.

## Validation

```powershell
python -m unittest discover -s tests -v
python C:\Users\<you>\.codex\skills\.system\skill-creator\scripts\quick_validate.py .
```

The smoke kernel was run successfully on Kaggle. It produced `smoke_result.json` with:

```json
{
  "status": "ok",
  "python": "3.13.18",
  "platform": "Linux-6.18.55+-x86_64-with-glibc2.39",
  "cwd": "/kaggle/working",
  "input_exists": true
}
```

## Security

- Never commit `~/.kaggle/credentials.json`.
- Never print Kaggle access tokens.
- Keep private datasets private and verify account access before attaching them.
- Write job outputs under `/kaggle/working`.
