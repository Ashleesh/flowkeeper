"""Turn recent raw signals into a fixed feature vector for the classifier.

The vector is intentionally small (8 dims) and fully anonymous — it captures the
*shape* of your activity, not its content. This is the only representation that
reaches the model.
"""
from __future__ import annotations

import statistics
import time
from dataclasses import dataclass
from typing import List

from flowkeeper.store import SignalStore

# Order matters: the ONNX model is trained against exactly this layout.
FEATURE_NAMES: List[str] = [
    "keys_per_min",          # typing volume
    "interkey_cv",           # coefficient of variation of gaps (low = steady rhythm)
    "backspace_ratio",       # error/correction rate
    "app_switches_per_min",  # context switching
    "productive_ratio",      # fraction of window time in a productive app
    "comms_ratio",           # fraction in a communication app
    "screen_change_mean",    # mean on-screen motion (0..1)
    "idle_seconds",          # seconds since last input
]
N_FEATURES = len(FEATURE_NAMES)


@dataclass
class FeatureVector:
    values: List[float]

    def as_list(self) -> List[float]:
        return self.values

    def named(self) -> dict:
        return dict(zip(FEATURE_NAMES, self.values))


def _safe_cv(gaps: List[float]) -> float:
    if len(gaps) < 2:
        return 0.0
    mean = statistics.fmean(gaps)
    if mean <= 0:
        return 0.0
    return statistics.pstdev(gaps) / mean


def extract(store: SignalStore, now: float | None = None) -> FeatureVector:
    now = now if now is not None else time.time()
    store.prune(now)
    window = max(1.0, store.window_seconds)
    minutes = window / 60.0

    keys = store.keys()
    n_keys = len(keys)
    keys_per_min = n_keys / minutes

    gaps = [b.ts - a.ts for a, b in zip(keys, keys[1:])]
    interkey_cv = _safe_cv(gaps)

    n_back = sum(1 for k in keys if k.is_backspace)
    backspace_ratio = (n_back / n_keys) if n_keys else 0.0

    windows = store.windows()
    switches = sum(
        1 for a, b in zip(windows, windows[1:]) if a.process != b.process
    )
    app_switches_per_min = switches / minutes

    if windows:
        productive_ratio = sum(1 for w in windows if w.category == "productive") / len(windows)
        comms_ratio = sum(1 for w in windows if w.category == "communication") / len(windows)
    else:
        productive_ratio = comms_ratio = 0.0

    screens = store.screens()
    screen_change_mean = statistics.fmean(s.change_ratio for s in screens) if screens else 0.0

    idle_seconds = store.idle_seconds(now)

    return FeatureVector([
        float(keys_per_min),
        float(interkey_cv),
        float(backspace_ratio),
        float(app_switches_per_min),
        float(productive_ratio),
        float(comms_ratio),
        float(screen_change_mean),
        float(idle_seconds),
    ])
