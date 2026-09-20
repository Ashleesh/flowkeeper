"""Synthetic signal source for demos, CI, and non-Snapdragon development.

Plays a scripted day: deep-focus coding, a Slack-heavy light-work stretch, an
idle gap, and stepping away — so you can watch the gatekeeper behave without any
platform hooks. Notifications are injected on a timeline too.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from flowkeeper.gate.notifications import Notification
from flowkeeper.store import SignalStore


@dataclass
class Phase:
    name: str
    seconds: float
    keys_per_sec: float
    interkey_jitter: float     # 0 steady .. 1 erratic
    backspace_rate: float
    app: str
    app_category: str
    switch_every: float        # seconds between app switches (large = settled)
    screen_change: float
    idle: bool = False


DEFAULT_SCRIPT: List[Phase] = [
    Phase("Deep coding",   90, 3.2, 0.10, 0.05, "code",    "productive",    45, 0.05),
    Phase("Slack triage",  60, 1.2, 0.55, 0.15, "slack",   "communication",  6, 0.30),
    Phase("Idle at desk",  30, 0.0, 0.00, 0.00, "chrome",  "browsing",      20, 0.02, idle=True),
    Phase("Stepped away",  40, 0.0, 0.00, 0.00, "chrome",  "browsing",      99, 0.00, idle=True),
    Phase("Back to coding",60, 3.0, 0.12, 0.06, "code",    "productive",    40, 0.05),
]

# (offset_seconds, Notification)
DEFAULT_NOTIFICATIONS: List[Tuple[float, Notification]] = [
    (20,  Notification("Slack", "Priya", "can you review my PR when free?", priority="normal")),
    (45,  Notification("Mail", "Newsletter", "This week in AI", priority="low")),
    (70,  Notification("Teams", "Ops", "P0 outage on payments — join bridge", priority="normal")),
    (105, Notification("Slack", "Dev", "lunch?", priority="low")),
    (135, Notification("Mail", "HR", "Timesheet reminder", priority="low")),
    (200, Notification("Slack", "Priya", "thanks!", priority="normal")),
]


class SimulatedSource:
    def __init__(
        self,
        store: SignalStore,
        script: Optional[List[Phase]] = None,
        notifications: Optional[List[Tuple[float, Notification]]] = None,
        seed: int = 7,
    ) -> None:
        self.store = store
        self.script = script or DEFAULT_SCRIPT
        self.notifications = list(notifications or DEFAULT_NOTIFICATIONS)
        self._rng = random.Random(seed)
        self.total_seconds = sum(p.seconds for p in self.script)

    def phase_at(self, t: float) -> Phase:
        acc = 0.0
        for p in self.script:
            acc += p.seconds
            if t < acc:
                return p
        return self.script[-1]

    def feed_interval(self, t0: float, t1: float, wall_now: float) -> None:
        """Populate the store with signals for the virtual window [t0, t1)."""
        p = self.phase_at(t0)
        dt = t1 - t0
        # keystrokes
        n_keys = int(p.keys_per_sec * dt)
        base_gap = 1.0 / p.keys_per_sec if p.keys_per_sec > 0 else 0
        for i in range(n_keys):
            jitter = 1.0 + self._rng.uniform(-p.interkey_jitter, p.interkey_jitter)
            ts = wall_now - dt + (i * base_gap * jitter)
            self.store.add_key(
                is_backspace=(self._rng.random() < p.backspace_rate), ts=ts
            )
        # window samples (one per switch interval)
        n_win = max(1, int(dt / max(1.0, p.switch_every)))
        for i in range(n_win):
            self.store.add_window(process=p.app, category=p.app_category, ts=wall_now)
        # screen samples
        self.store.add_screen(change_ratio=p.screen_change, ts=wall_now)
        # presence
        if not p.idle:
            self.store.mark_input(ts=wall_now)

    def due_notifications(self, t0: float, t1: float) -> List[Notification]:
        due = [n for (off, n) in self.notifications if t0 <= off < t1]
        self.notifications = [(off, n) for (off, n) in self.notifications if not (t0 <= off < t1)]
        return due
