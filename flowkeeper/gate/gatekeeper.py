"""The gate policy: given the current focus state, decide what to do with each
incoming notification and when to release what's been held.

Policy summary:
  DEEP_FOCUS  -> hold everything except urgent (after a short debounce)
  LIGHT_WORK  -> release urgent + normal now, batch low every N seconds
  IDLE        -> release everything held
  AWAY        -> hold; on return to any active state, deliver one digest
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional

from flowkeeper.gate.notifications import Notification, NotificationSink
from flowkeeper.model.labels import DEEP_FOCUS, LIGHT_WORK, IDLE, AWAY


@dataclass
class GateDecision:
    action: str            # "deliver" | "hold"
    reason: str


@dataclass
class PriorityRules:
    always_allow_apps: List[str] = field(default_factory=list)
    urgent_keywords: List[str] = field(default_factory=list)
    vip_senders: List[str] = field(default_factory=list)

    def classify(self, note: Notification) -> str:
        text = f"{note.title} {note.body}".lower()
        if note.app in self.always_allow_apps:
            return "urgent"
        if any(v.lower() in text for v in self.vip_senders):
            return "urgent"
        if any(k.lower() in text for k in self.urgent_keywords):
            return "urgent"
        return note.priority


class Gatekeeper:
    def __init__(
        self,
        sink: NotificationSink,
        priority: Optional[PriorityRules] = None,
        focus_debounce_seconds: float = 20.0,
        light_work_release_interval_seconds: float = 120.0,
        summarise_on_return: bool = True,
    ) -> None:
        self.sink = sink
        self.priority = priority or PriorityRules()
        self.focus_debounce_seconds = focus_debounce_seconds
        self.light_work_release_interval_seconds = light_work_release_interval_seconds
        self.summarise_on_return = summarise_on_return

        self._held: List[Notification] = []
        self._state: str = IDLE
        self._state_since: float = time.time()
        self._last_light_release: float = 0.0

    @property
    def held_count(self) -> int:
        return len(self._held)

    @property
    def state(self) -> str:
        return self._state

    # -- state transitions ------------------------------------------------
    def update_state(self, state: str, now: Optional[float] = None) -> None:
        now = now if now is not None else time.time()
        if state != self._state:
            leaving = self._state
            self._state = state
            self._state_since = now
            # Coming back from AWAY -> deliver a single digest of what we held.
            if leaving == AWAY and state in (IDLE, LIGHT_WORK, DEEP_FOCUS):
                self._flush(reason="back from away", now=now)
            # Dropping out of focus into idle -> release the batch.
            elif leaving == DEEP_FOCUS and state == IDLE:
                self._flush(reason="focus ended", now=now)
        # periodic housekeeping for the current state
        self._tick(now)

    def _tick(self, now: float) -> None:
        if self._state == IDLE and self._held:
            self._flush(reason="idle", now=now)
        elif self._state == LIGHT_WORK and self._held:
            if now - self._last_light_release >= self.light_work_release_interval_seconds:
                self._flush(reason="light-work batch", now=now)
                self._last_light_release = now

    # -- incoming notifications ------------------------------------------
    def submit(self, note: Notification, now: Optional[float] = None) -> GateDecision:
        now = now if now is not None else time.time()
        prio = self.priority.classify(note)
        note.priority = prio

        if prio == "urgent":
            self.sink.deliver(note)
            return GateDecision("deliver", "urgent — always pass")

        if self._state == DEEP_FOCUS:
            if now - self._state_since < self.focus_debounce_seconds:
                # Just entered focus; don't start hoarding on a hair trigger.
                self.sink.deliver(note)
                return GateDecision("deliver", "focus debounce window")
            self._held.append(note)
            return GateDecision("hold", "deep focus — batched")

        if self._state == AWAY:
            self._held.append(note)
            return GateDecision("hold", "away — will summarise on return")

        if self._state == LIGHT_WORK:
            if prio == "low":
                self._held.append(note)
                return GateDecision("hold", "light work — low priority batched")
            self.sink.deliver(note)
            return GateDecision("deliver", "light work — normal priority")

        # IDLE
        self.sink.deliver(note)
        return GateDecision("deliver", "idle — deliver immediately")

    # -- release ----------------------------------------------------------
    def _flush(self, reason: str, now: Optional[float] = None) -> None:
        if not self._held:
            return
        batch, self._held = self._held, []
        if self.summarise_on_return and len(batch) > 1:
            self.sink.deliver_digest(batch, reason)
        else:
            for n in batch:
                self.sink.deliver(n)

    def flush_now(self, reason: str = "manual") -> None:
        self._flush(reason=reason)
