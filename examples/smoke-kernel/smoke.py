import json
import os
import platform
from pathlib import Path

result = {
    "status": "ok",
    "python": platform.python_version(),
    "platform": platform.platform(),
    "cwd": os.getcwd(),
    "input_exists": Path("/kaggle/input").exists(),
}
Path("/kaggle/working/smoke_result.json").write_text(
    json.dumps(result, indent=2), encoding="utf-8"
)
print(json.dumps(result, indent=2))
