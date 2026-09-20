"""In-memory rolling buffers. This module is FlowKeeper's privacy boundary.

Raw events (key timestamps, window titles, screen-diff ratios) live here only for
the length of the feature window, then age out. Nothing is written to disk and no
raw text (keystrokes, window titles beyond their process name) is ever retained.
"""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, List, Optional


@dataclass
class KeyEvent:
    ts: float
    is_backspace: bool = False


@dataclass
class WindowSample:
    ts: float
    process: str          # process name only, lower-cased (e.g. "code")
    category: str         # productive | communication | browsing | other


@dataclass
class ScreenSample:
    ts: float
    change_ratio: float   # 0..1 fraction of the frame that changed vs previous


class SignalStore:
    """Thread-friendly rolling store of recent behavioural signals."""

    def __init__(self, window_seconds: float = 30.0) -> None:
        self.window_seconds = window_seconds
        self._keys: Deque[KeyEvent] = deque()
        self._windows: Deque[WindowSample] = deque()
        self._screens: Deque[ScreenSample] = deque()
        self._last_input_ts: float = time.time()

    # -- ingest -----------------------------------------------------------
    def add_key(self, is_backspace: bool = False, ts: Optional[float] = None) -> None:
        ts = ts if ts is not None else time.time()
        self._keys.append(KeyEvent(ts=ts, is_backspace=is_backspace))
        self._last_input_ts = ts

    def add_window(self, process: str, category: str, ts: Optional[float] = None) -> None:
        ts = ts if ts is not None else time.time()
        self._windows.append(WindowSample(ts=ts, process=process, category=category))

    def add_screen(self, change_ratio: float, ts: Optional[float] = None) -> None:
        ts = ts if ts is not None else time.time()
        self._screens.append(ScreenSample(ts=ts, change_ratio=change_ratio))

    def mark_input(self, ts: Optional[float] = None) -> None:
        """Register any input (mouse move/click) to reset the idle timer."""
        self._last_input_ts = ts if ts is not None else time.time()

    # -- query ------------------------------------------------------------
    def prune(self, now: Optional[float] = None) -> None:
        now = now if now is not None else time.time()
        cutoff = now - self.window_seconds
        for dq in (self._keys, self._windows, self._screens):
            while dq and dq[0].ts < cutoff:
                dq.popleft()

    def keys(self) -> List[KeyEvent]:
        return list(self._keys)

    def windows(self) -> List[WindowSample]:
        return list(self._windows)

    def screens(self) -> List[ScreenSample]:
        return list(self._screens)

    def idle_seconds(self, now: Optional[float] = None) -> float:
        now = now if now is not None else time.time()
        return max(0.0, now - self._last_input_ts)
