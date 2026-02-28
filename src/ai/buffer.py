from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Tuple

import numpy as np


@dataclass
class Transition:
    s: np.ndarray
    a: int
    r: float
    s2: np.ndarray
    d: bool


class ReplayBuffer:
    def __init__(self, capacity: int):
        self.buf: Deque[Transition] = deque(maxlen=int(capacity))

    def __len__(self) -> int:
        return len(self.buf)

    def add(self, s: np.ndarray, a: int, r: float, s2: np.ndarray, d: bool) -> None:
        self.buf.append(Transition(s, int(a), float(r), s2, bool(d)))

    def sample(self, batch_size: int) -> Transition:
        batch = random.sample(self.buf, k=min(batch_size, len(self.buf)))
        s = np.stack([t.s for t in batch], axis=0)
        a = np.array([t.a for t in batch], dtype=np.int64)
        r = np.array([t.r for t in batch], dtype=np.float32)
        s2 = np.stack([t.s2 for t in batch], axis=0)
        d = np.array([t.d for t in batch], dtype=np.float32)
        return Transition(s, a, r, s2, d)
