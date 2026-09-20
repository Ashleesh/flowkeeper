"""Active-window collector.

Records only the foreground *process name* and its category — never the window
title text. Poll-based so it costs almost nothing.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from flowkeeper.signals.categorize import categorize_process
from flowkeeper.store import SignalStore


class WindowCollector:
    def __init__(self, store: SignalStore, categories: Dict[str, List[str]]) -> None:
        self.store = store
        self.categories = categories
        self._last_process: Optional[str] = None

    def _foreground_process(self) -> Optional[str]:
        """Windows implementation via win32; None if unavailable."""
        try:
            import win32gui  # type: ignore
            import win32process  # type: ignore
            import psutil  # type: ignore
        except Exception:
            return None
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return psutil.Process(pid).name()
        except Exception:
            return None

    def poll(self) -> None:
        proc = self._foreground_process()
        if not proc:
            return
        cat = categorize_process(proc, self.categories)
        self.store.add_window(process=proc.lower().replace(".exe", ""), category=cat)
        self.store.mark_input()  # a foreground app implies presence
        self._last_process = proc
