"""The always-on loop that ties signals -> features -> classifier -> gate together."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from flowkeeper import features as feat
from flowkeeper.gate.gatekeeper import Gatekeeper, PriorityRules
from flowkeeper.gate.notifications import ConsoleSink, Notification, NotificationSink
from flowkeeper.model.classifier import FocusClassifier
from flowkeeper.store import SignalStore


@dataclass
class AppConfig:
    interval_seconds: float = 3.0
    feature_window_seconds: float = 30.0
    onnx_path: Optional[str] = None
    providers: Optional[List[str]] = None
    qnn_backend: str = "QnnHtp.dll"
    allow_heuristic_fallback: bool = True
    focus_debounce_seconds: float = 20.0
    light_work_release_interval_seconds: float = 120.0
    summarise_on_return: bool = True
    priority: Optional[PriorityRules] = None
    app_categories: Optional[Dict[str, List[str]]] = None


class FlowKeeperApp:
    def __init__(self, config: AppConfig, sink: Optional[NotificationSink] = None) -> None:
        self.config = config
        self.store = SignalStore(window_seconds=config.feature_window_seconds)
        self.classifier = FocusClassifier(
            onnx_path=config.onnx_path,
            providers=config.providers,
            qnn_backend=config.qnn_backend,
            allow_heuristic_fallback=config.allow_heuristic_fallback,
        )
        self.sink = sink or ConsoleSink()
        self.gate = Gatekeeper(
            sink=self.sink,
            priority=config.priority or PriorityRules(),
            focus_debounce_seconds=config.focus_debounce_seconds,
            light_work_release_interval_seconds=config.light_work_release_interval_seconds,
            summarise_on_return=config.summarise_on_return,
        )

    @property
    def backend(self) -> str:
        return self.classifier.backend

    def step(self, now: Optional[float] = None) -> "StepResult":
        now = now if now is not None else time.time()
        fv = feat.extract(self.store, now=now)
        pred = self.classifier.predict(fv)
        self.gate.update_state(pred.state, now=now)
        return StepResult(
            state=pred.state,
            confidence=pred.confidence,
            backend=pred.backend,
            held=self.gate.held_count,
            features=fv.named(),
        )

    def submit(self, note: Notification, now: Optional[float] = None):
        return self.gate.submit(note, now=now)


@dataclass
class StepResult:
    state: str
    confidence: float
    backend: str
    held: int
    features: Dict[str, float]
