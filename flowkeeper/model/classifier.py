"""Focus-state classifier.

Two backends behind one interface:

* **ONNX / QNN** — the real model, an INT8 MLP compiled through Qualcomm AI Hub and
  run on the Snapdragon Hexagon NPU via ONNX Runtime's QNNExecutionProvider. This is
  the always-on, battery-free path on target hardware.
* **Heuristic** — a transparent, dependency-free fallback that reproduces the model's
  intent with hand-tuned rules. Used when no compiled model is present or onnxruntime
  is unavailable, so FlowKeeper always runs.

`FocusClassifier` picks the best available backend and reports which one is active,
so the two never diverge silently.
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import List, Optional, Sequence

from flowkeeper.features import FeatureVector, N_FEATURES
from flowkeeper.model.labels import STATES, DEEP_FOCUS, LIGHT_WORK, IDLE, AWAY


@dataclass
class Prediction:
    state: str
    confidence: float
    probabilities: dict
    backend: str  # "qnn-npu" | "onnx-cpu" | "heuristic"


def _softmax(xs: Sequence[float]) -> List[float]:
    m = max(xs)
    exps = [math.exp(x - m) for x in xs]
    total = sum(exps) or 1.0
    return [e / total for e in exps]


class FocusClassifier:
    def __init__(
        self,
        onnx_path: Optional[str] = None,
        providers: Optional[Sequence[str]] = None,
        qnn_backend: str = "QnnHtp.dll",
        allow_heuristic_fallback: bool = True,
    ) -> None:
        self.allow_heuristic_fallback = allow_heuristic_fallback
        self._session = None
        self._input_name = None
        self.backend = "heuristic"

        if onnx_path and os.path.exists(onnx_path):
            self._try_load_onnx(onnx_path, providers or ["CPUExecutionProvider"], qnn_backend)

        if self._session is None and not allow_heuristic_fallback:
            raise RuntimeError(
                f"No usable ONNX model at {onnx_path!r} and heuristic fallback is disabled."
            )

    # -- ONNX / QNN backend ----------------------------------------------
    def _try_load_onnx(self, onnx_path: str, providers: Sequence[str], qnn_backend: str) -> None:
        try:
            import onnxruntime as ort  # type: ignore
        except Exception:
            return  # onnxruntime not installed -> heuristic

        available = set(ort.get_available_providers())
        # Build (provider, options) pairs, keeping only providers actually available.
        selected, opts = [], []
        for p in providers:
            if p not in available:
                continue
            selected.append(p)
            if p == "QNNExecutionProvider":
                opts.append({"backend_path": qnn_backend})
            else:
                opts.append({})
        if not selected:
            selected, opts = ["CPUExecutionProvider"], [{}]

        try:
            self._session = ort.InferenceSession(
                onnx_path, providers=selected, provider_options=opts
            )
            self._input_name = self._session.get_inputs()[0].name
            active = self._session.get_providers()[0]
            self.backend = "qnn-npu" if active == "QNNExecutionProvider" else "onnx-cpu"
        except Exception:
            self._session = None  # any failure -> heuristic

    # -- public API -------------------------------------------------------
    def predict(self, fv: FeatureVector) -> Prediction:
        if self._session is not None:
            return self._predict_onnx(fv)
        return self._predict_heuristic(fv)

    def _predict_onnx(self, fv: FeatureVector) -> Prediction:
        import numpy as np  # local import so the module loads without numpy at rest

        x = np.asarray([fv.as_list()], dtype=np.float32)
        outputs = self._session.run(None, {self._input_name: x})
        logits = np.asarray(outputs[0]).reshape(-1)[: len(STATES)]
        probs = _softmax(logits.tolist())
        idx = max(range(len(probs)), key=lambda i: probs[i])
        return Prediction(
            state=STATES[idx],
            confidence=probs[idx],
            probabilities=dict(zip(STATES, probs)),
            backend=self.backend,
        )

    def _predict_heuristic(self, fv: FeatureVector) -> Prediction:
        f = fv.named()
        idle = f["idle_seconds"]

        if idle >= 90:
            scores = {AWAY: 3.0, IDLE: 0.5, LIGHT_WORK: -1.0, DEEP_FOCUS: -2.0}
        elif idle >= 20:
            scores = {IDLE: 2.0, AWAY: 0.3, LIGHT_WORK: 0.2, DEEP_FOCUS: -1.0}
        else:
            # Actively working: distinguish deep focus from light work.
            steady = 1.0 - min(1.0, f["interkey_cv"])          # steady rhythm -> flow
            typing = min(1.0, f["keys_per_min"] / 220.0)
            settled = 1.0 - min(1.0, f["app_switches_per_min"] / 6.0)
            deep = (
                1.4 * steady
                + 1.2 * typing
                + 1.1 * settled
                + 1.0 * f["productive_ratio"]
                - 0.8 * f["backspace_ratio"]
            )
            light = (
                1.0 * f["comms_ratio"]
                + 0.8 * min(1.0, f["app_switches_per_min"] / 6.0)
                + 0.6 * min(1.0, f["screen_change_mean"] * 3.0)
                + 0.4 * (1.0 - typing)
            )
            scores = {
                DEEP_FOCUS: deep,
                LIGHT_WORK: light,
                IDLE: 0.2,
                AWAY: -2.0,
            }

        ordered = [scores[s] for s in STATES]
        probs = _softmax(ordered)
        idx = max(range(len(probs)), key=lambda i: probs[i])
        return Prediction(
            state=STATES[idx],
            confidence=probs[idx],
            probabilities=dict(zip(STATES, probs)),
            backend="heuristic",
        )
