"""Screen-activity collector.

Computes a single scalar — the fraction of the (heavily downscaled) screen that
changed since the last sample. PRIVACY: the frame is downscaled to a tiny
grayscale grid and immediately discarded; no screenshot is ever stored, and the
grid is far too coarse to reconstruct content.
"""
from __future__ import annotations

from typing import Optional

from flowkeeper.store import SignalStore

_GRID = 32  # downscale to 32x32 grayscale before diffing


class ScreenCollector:
    def __init__(self, store: SignalStore, change_threshold: float = 0.08) -> None:
        self.store = store
        self.change_threshold = change_threshold
        self._prev = None

    def _grab_downscaled(self):
        """Return a small numpy grayscale array, or None if capture unavailable."""
        try:
            import numpy as np  # type: ignore
            import mss  # type: ignore
        except Exception:
            return None
        try:
            with mss.mss() as sct:
                shot = sct.grab(sct.monitors[0])
            arr = np.asarray(shot)[:, :, :3].mean(axis=2)  # to grayscale
            h, w = arr.shape
            gh, gw = max(1, h // _GRID), max(1, w // _GRID)
            small = arr[::gh, ::gw][:_GRID, :_GRID]
            return small.astype("float32") / 255.0
        except Exception:
            return None

    def poll(self) -> None:
        import_ok = self._grab_downscaled()
        if import_ok is None:
            return
        cur = import_ok
        if self._prev is not None and self._prev.shape == cur.shape:
            import numpy as np  # type: ignore
            changed = float((np.abs(cur - self._prev) > self.change_threshold).mean())
            self.store.add_screen(change_ratio=changed)
        self._prev = cur
