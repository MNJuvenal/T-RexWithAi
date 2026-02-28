import csv
import os
from dataclasses import dataclass
from typing import Optional


class CSVLogger:
    def __init__(self, logs_dir: str):
        os.makedirs(logs_dir, exist_ok=True)
        self.path = os.path.join(logs_dir, "metrics.csv")
        self._init_file()

    def _init_file(self) -> None:
        if os.path.exists(self.path):
            return
        with open(self.path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["episode", "score", "total_reward", "steps", "epsilon", "loss_avg"])

    def log(self, episode: int, score: float, total_reward: float, steps: int, epsilon: float, loss_avg: Optional[float]):
        with open(self.path, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([episode, int(score), float(total_reward), int(steps), float(epsilon), "" if loss_avg is None else float(loss_avg)])
