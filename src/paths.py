import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class RunPaths:
    run_id: str
    models_run_dir: str
    logs_run_dir: str
    latest_dir: str
    best_dir: str


def _timestamp_id() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")


def prepare_run_dirs(models_root: str, logs_root: str, run_name: Optional[str], resume: Optional[str]) -> RunPaths:
    os.makedirs(models_root, exist_ok=True)
    os.makedirs(logs_root, exist_ok=True)

    if resume:
        # resume points to .../latest
        latest_dir = resume
        models_run_dir = os.path.dirname(latest_dir)
        run_id = os.path.basename(models_run_dir)
        logs_run_dir = os.path.join(logs_root, "runs", run_id)
        best_dir = os.path.join(models_run_dir, "best")
        os.makedirs(latest_dir, exist_ok=True)
        os.makedirs(best_dir, exist_ok=True)
        os.makedirs(logs_run_dir, exist_ok=True)
        return RunPaths(run_id, models_run_dir, logs_run_dir, latest_dir, best_dir)

    run_id = run_name or _timestamp_id()
    models_run_dir = os.path.join(models_root, "runs", run_id)
    logs_run_dir = os.path.join(logs_root, "runs", run_id)
    latest_dir = os.path.join(models_run_dir, "latest")
    best_dir = os.path.join(models_run_dir, "best")

    os.makedirs(latest_dir, exist_ok=True)
    os.makedirs(best_dir, exist_ok=True)
    os.makedirs(logs_run_dir, exist_ok=True)

    return RunPaths(run_id, models_run_dir, logs_run_dir, latest_dir, best_dir)


def save_args(logs_run_dir: str, args) -> None:
    path = os.path.join(logs_run_dir, "args.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(vars(args), f, ensure_ascii=False, indent=2)
