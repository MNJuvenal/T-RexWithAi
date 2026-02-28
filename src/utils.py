import os
import random
from typing import Optional

import numpy as np


def set_seed(seed: Optional[int]) -> None:
    if seed is None:
        return
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))
