"""Keyboard cadence collector.

PRIVACY: we never record which keys are pressed — only *that* a key was pressed
and whether it was backspace. There is no keylogging; the content of what you
type never enters FlowKeeper.
"""
from __future__ import annotations

from typing import Optional

from flowkeeper.store import SignalStore


class KeyboardCollector:
    def __init__(self, store: SignalStore) -> None:
        self.store = store
        self._listener = None

    def start(self) -> bool:
        """Start listening. Returns False if pynput is unavailable."""
        try:
            from pynput import keyboard  # type: ignore
        except Exception:
            return False

        backspace = keyboard.Key.backspace

        def on_press(key) -> None:
            self.store.add_key(is_backspace=(key == backspace))

        self._listener = keyboard.Listener(on_press=on_press)
        self._listener.daemon = True
        self._listener.start()
        return True

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
