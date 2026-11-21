# Kernel Metadata Templates

## Script kernel with dual T4

```json
{
  "id": "YOUR_USERNAME/KERNEL_SLUG",
  "title": "KERNEL TITLE",
  "code_file": "job.py",
  "language": "python",
  "kernel_type": "script",
  "is_private": "true",
  "enable_gpu": "true",
  "enable_tpu": "false",
  "enable_internet": "true",
  "machine_shape": "NvidiaTeslaT4",
  "dataset_sources": ["OWNER/DATASET_SLUG"],
  "competition_sources": [],
  "kernel_sources": [],
  "model_sources": []
}
```

`NvidiaTeslaT4` requests Kaggle's **GPU T4 x2** accelerator. The job must still print `torch.cuda.device_count()` to verify what was allocated.

## Notebook kernel

Use `"kernel_type": "notebook"` and set `"code_file": "job.ipynb"`.

## Dataset attachment

`dataset_sources` uses dataset references such as:

```json
["kagglejackyang/evbattery"]
```

The mount directory can vary. Search under `/kaggle/input` rather than hard-coding `/kaggle/input/<slug>/<file>`.

## Accelerator selection

- CPU: omit `machine_shape` and set `"enable_gpu": "false"`.
- Single/default GPU: `"enable_gpu": "true"` with an appropriate accelerator setting.
- GPU T4 x2: add `"machine_shape": "NvidiaTeslaT4"`.
- TPU: use `"enable_tpu": "true"` and the corresponding TPU shape.

For CLI pushes, `--accelerator NvidiaTeslaT4` overrides the requested accelerator for that push.
