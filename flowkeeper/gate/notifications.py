"""Notification model and delivery sinks.

A `NotificationSink` is where held notifications are eventually delivered. The
`ConsoleSink` is used for --simulate and tests; a real Windows build would add a
sink backed by Windows.UI.Notifications (toast) and a shim that intercepts
incoming toasts so FlowKeeper can queue them. Capturing incoming notifications on
Windows requires the UserNotificationListener API (see docs/ARCHITECTURE.md).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Protocol


@dataclass
class Notification:
    app: str
    title: str
    body: str
    ts: float = field(default_factory=time.time)
    priority: str = "normal"   # "urgent" | "normal" | "low"

    def one_line(self) -> str:
        return f"[{self.app}] {self.title}: {self.body}".strip()


class NotificationSink(Protocol):
    def deliver(self, note: Notification) -> None: ...
    def deliver_digest(self, notes: List[Notification], reason: str) -> None: ...


class ConsoleSink:
    """Prints delivered notifications; handy for demos, CI, and tests."""

    def __init__(self) -> None:
        self.delivered: List[Notification] = []
        self.digests: List[List[Notification]] = []

    def deliver(self, note: Notification) -> None:
        self.delivered.append(note)
        print(f"  -> DELIVER  {note.one_line()}")

    def deliver_digest(self, notes: List[Notification], reason: str) -> None:
        if not notes:
            return
        self.digests.append(list(notes))
        self.delivered.extend(notes)
        print(f"  -> DIGEST ({reason}) — {len(notes)} held item(s):")
        for n in notes:
            print(f"       - {n.one_line()}")
