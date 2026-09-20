"""FlowKeeper command line: --simulate, --diagnose, or live run."""
from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Dict, List

from flowkeeper.app import AppConfig, FlowKeeperApp
from flowkeeper.gate.gatekeeper import PriorityRules
from flowkeeper.gate.notifications import ConsoleSink


def _load_config(path: str) -> dict:
    try:
        import yaml  # type: ignore
    except Exception:
        print("pyyaml not installed; using built-in defaults.", file=sys.stderr)
        return {}
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _build_appconfig(cfg: dict) -> AppConfig:
    sampling = cfg.get("sampling", {})
    model = cfg.get("model", {})
    gate = cfg.get("gate", {})
    prio = cfg.get("priority", {})
    return AppConfig(
        interval_seconds=sampling.get("interval_seconds", 3.0),
        feature_window_seconds=sampling.get("feature_window_seconds", 30.0),
        onnx_path=model.get("onnx_path"),
        providers=model.get("providers"),
        qnn_backend=model.get("qnn_backend", "QnnHtp.dll"),
        allow_heuristic_fallback=model.get("allow_heuristic_fallback", True),
        focus_debounce_seconds=gate.get("focus_debounce_seconds", 20.0),
        light_work_release_interval_seconds=gate.get("light_work_release_interval_seconds", 120.0),
        summarise_on_return=gate.get("summarise_on_return", True),
        priority=PriorityRules(
            always_allow_apps=prio.get("always_allow_apps", []),
            urgent_keywords=prio.get("urgent_keywords", []),
            vip_senders=prio.get("vip_senders", []),
        ),
        app_categories=cfg.get("app_categories"),
    )


def _diagnose(app: FlowKeeperApp) -> int:
    print("FlowKeeper diagnostics")
    print("=" * 40)
    print(f"Classifier backend : {app.backend}")
    if app.backend == "qnn-npu":
        print("  -> running on the Snapdragon Hexagon NPU (QNN EP). Ideal.")
    elif app.backend == "onnx-cpu":
        print("  -> ONNX model loaded but running on CPU (no QNN EP available here).")
    else:
        print("  -> heuristic fallback (no compiled model / onnxruntime). Still fully functional.")
    try:
        import onnxruntime as ort  # type: ignore
        print(f"onnxruntime EPs    : {', '.join(ort.get_available_providers())}")
    except Exception:
        print("onnxruntime        : not installed")
    print(f"Model path         : {app.config.onnx_path}")
    return 0


def _run_simulated(app: FlowKeeperApp, speed: float) -> int:
    from flowkeeper.signals.simulate import SimulatedSource

    src = SimulatedSource(app.store)
    print(f"Simulating {int(src.total_seconds)}s of activity  (backend: {app.backend})")
    print("=" * 60)
    step = app.config.interval_seconds
    t = 0.0
    last_state = None
    while t < src.total_seconds:
        wall_now = time.time()
        src.feed_interval(t, t + step, wall_now)
        for note in src.due_notifications(t, t + step):
            dec = app.submit(note, now=wall_now)
            tag = "HOLD " if dec.action == "hold" else "PASS "
            print(f"[{int(t):>3}s] NOTE {tag} {note.one_line()}  ({dec.reason})")
        res = app.step(now=wall_now)
        if res.state != last_state:
            print(f"[{int(t):>3}s] STATE -> {res.state:<11} conf={res.confidence:.2f} held={res.held}")
            last_state = res.state
        t += step
        if speed > 0:
            time.sleep(step / speed)
    app.gate.flush_now(reason="end of session")
    print("=" * 60)
    sink = app.sink
    if isinstance(sink, ConsoleSink):
        print(f"Delivered {len(sink.delivered)} notifications, "
              f"{len(sink.digests)} as batched digest(s).")
    return 0


def _run_live(app: FlowKeeperApp, cfg: dict) -> int:
    from flowkeeper.signals.keyboard import KeyboardCollector
    from flowkeeper.signals.window import WindowCollector
    from flowkeeper.signals.screen import ScreenCollector

    cats = cfg.get("app_categories", {})
    kb = KeyboardCollector(app.store)
    win = WindowCollector(app.store, cats)
    scr = ScreenCollector(app.store)

    kb_ok = kb.start()
    print(f"FlowKeeper live  (backend: {app.backend}, keyboard hook: {kb_ok})")
    print("Ctrl-C to stop.")
    step = app.config.interval_seconds
    last_state = None
    try:
        while True:
            win.poll()
            scr.poll()
            res = app.step()
            if res.state != last_state:
                print(f"STATE -> {res.state:<11} conf={res.confidence:.2f} held={res.held}")
                last_state = res.state
            time.sleep(step)
    except KeyboardInterrupt:
        app.gate.flush_now(reason="shutdown")
        kb.stop()
        print("\nStopped. All held notifications released.")
    return 0


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="flowkeeper", description=__doc__)
    ap.add_argument("--config", default="config/default.yaml", help="path to YAML config")
    ap.add_argument("--simulate", action="store_true", help="run scripted synthetic activity")
    ap.add_argument("--diagnose", action="store_true", help="print backend diagnostics and exit")
    ap.add_argument("--speed", type=float, default=60.0,
                    help="simulation speedup (0 = as fast as possible)")
    args = ap.parse_args(argv)

    cfg = _load_config(args.config)
    app = FlowKeeperApp(_build_appconfig(cfg))

    if args.diagnose:
        return _diagnose(app)
    if args.simulate:
        return _run_simulated(app, speed=args.speed)
    return _run_live(app, cfg)
