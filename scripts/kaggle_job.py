#!/usr/bin/env python3
"""Small, dependency-free wrapper around the Kaggle CLI."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path


def find_cli() -> str:
    explicit = os.environ.get("KAGGLE_CLI")
    if explicit and Path(explicit).is_file():
        return explicit
    found = shutil.which("kaggle")
    if found:
        return found
    roots = []
    if os.name == "nt":
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            roots.append(Path(appdata) / "Python")
            roots.extend(sorted((Path(appdata) / "Python").glob("Python*"), reverse=True))
        roots += [Path("C:/Program Files/Kaggle"), Path("C:/ProgramData/chocolatey/bin")]
    else:
        roots += [Path.home() / ".local/bin", Path("/usr/local/bin"), Path("/usr/bin")]
    for root in roots:
        if not root.exists():
            continue
        candidates = [root / "kaggle"] if root.is_file() else [root / "kaggle", root / "Scripts/kaggle", root / "Scripts/kaggle.exe"]
        for candidate in candidates:
            if candidate.is_file():
                return str(candidate)
    raise FileNotFoundError("Kaggle CLI not found. Set KAGGLE_CLI or install the current Kaggle CLI.")


def run(cli: str, args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run([cli, *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if check and proc.returncode != 0:
        raise RuntimeError(f"Kaggle CLI failed ({proc.returncode}):\n{proc.stdout}")
    return proc


def cmd_doctor(_args: argparse.Namespace) -> int:
    cli = find_cli()
    version = run(cli, ["--version"], check=False).stdout.strip()
    auth = run(cli, ["datasets", "list", "-m", "--page-size", "1"], check=False)
    print(f"CLI: {cli}")
    print(f"Version: {version}")
    print("Authentication:", "OK" if auth.returncode == 0 else "NOT AVAILABLE")
    if auth.returncode != 0:
        print(auth.stdout.strip())
        return 2
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    cli = find_cli()
    proc = run(cli, ["kernels", "status", args.kernel], check=False)
    print(proc.stdout.strip())
    return proc.returncode


def cmd_logs(args: argparse.Namespace) -> int:
    cli = find_cli()
    proc = run(cli, ["kernels", "logs", args.kernel], check=False)
    print(proc.stdout)
    return proc.returncode


def cmd_download(args: argparse.Namespace) -> int:
    cli = find_cli()
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    proc = run(cli, ["kernels", "output", args.kernel, "-p", str(out)], check=False)
    print(proc.stdout)
    return proc.returncode


def parse_kernel_ref(output: str, fallback: str) -> str:
    match = re.search(r"https://www\.kaggle\.com/code/([^\s/]+/[^\s]+)", output)
    return match.group(1).rstrip(".,)") if match else fallback


def cmd_push(args: argparse.Namespace) -> int:
    cli = find_cli()
    folder = Path(args.folder).resolve()
    meta_path = folder / "kernel-metadata.json"
    if not meta_path.is_file():
        raise FileNotFoundError(f"Missing {meta_path}")
    meta = json.loads(meta_path.read_text(encoding="utf-8-sig"))
    fallback = str(meta.get("id", "")).strip()
    cmd = ["kernels", "push", "-p", str(folder)]
    if args.accelerator:
        cmd += ["--accelerator", args.accelerator]
    pushed = run(cli, cmd, check=False)
    print(pushed.stdout)
    if pushed.returncode != 0:
        return pushed.returncode
    kernel = parse_kernel_ref(pushed.stdout, fallback)
    print(f"Kernel: {kernel}")
    if args.no_wait:
        return 0
    deadline = time.time() + args.timeout
    last = None
    while time.time() < deadline:
        status = run(cli, ["kernels", "status", kernel], check=False).stdout.strip()
        if status != last:
            print(status, flush=True)
            last = status
        upper = status.upper()
        if "COMPLETE" in upper:
            output_dir = Path(args.output).resolve()
            output_dir.mkdir(parents=True, exist_ok=True)
            proc = run(cli, ["kernels", "output", kernel, "-p", str(output_dir)], check=False)
            print(proc.stdout)
            return proc.returncode
        if "ERROR" in upper or "FAILED" in upper:
            print(run(cli, ["kernels", "logs", kernel], check=False).stdout)
            return 1
        time.sleep(max(5, args.poll))
    print("Timed out waiting for the Kaggle kernel.", file=sys.stderr)
    return 3


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor", help="Find the CLI and test authentication")
    doctor.set_defaults(func=cmd_doctor)

    status = sub.add_parser("status", help="Show kernel status")
    status.add_argument("kernel")
    status.set_defaults(func=cmd_status)

    logs = sub.add_parser("logs", help="Print kernel logs")
    logs.add_argument("kernel")
    logs.set_defaults(func=cmd_logs)

    download = sub.add_parser("download", help="Download kernel output")
    download.add_argument("kernel")
    download.add_argument("--output", required=True)
    download.set_defaults(func=cmd_download)

    push = sub.add_parser("push", help="Push and optionally wait for a kernel")
    push.add_argument("--folder", required=True)
    push.add_argument("--accelerator", default=None)
    push.add_argument("--output", default="./kaggle-output")
    push.add_argument("--poll", type=int, default=60)
    push.add_argument("--timeout", type=int, default=12 * 60 * 60)
    push.add_argument("--no-wait", action="store_true")
    push.set_defaults(func=cmd_push)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
