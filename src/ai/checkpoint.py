import json
import os
from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class TrainState:
    step: int
    epsilon: float
    best_score: float


def save_state(path_dir: str, state: TrainState) -> None:
    os.makedirs(path_dir, exist_ok=True)
    with open(os.path.join(path_dir, "state.json"), "w", encoding="utf-8") as f:
        json.dump(asdict(state), f, ensure_ascii=False, indent=2)


def load_state(path_dir: str) -> Optional[TrainState]:
    path = os.path.join(path_dir, "state.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    return TrainState(step=int(d.get("step", 0)), epsilon=float(d.get("epsilon", 1.0)), best_score=float(d.get("best_score", 0.0)))
