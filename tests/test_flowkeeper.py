"""Fast, dependency-light tests (numpy only). Run: python -m pytest -q  (or run directly)."""
import time

from flowkeeper.store import SignalStore
from flowkeeper import features as feat
from flowkeeper.model.classifier import FocusClassifier
from flowkeeper.model.labels import DEEP_FOCUS, LIGHT_WORK, IDLE, AWAY
from flowkeeper.gate.gatekeeper import Gatekeeper, PriorityRules
from flowkeeper.gate.notifications import ConsoleSink, Notification


def _steady_typing_store(now):
    s = SignalStore(window_seconds=30)
    # steady, fast typing in a productive app -> deep focus
    for i in range(90):
        s.add_key(is_backspace=False, ts=now - 30 + i * (30 / 90))
    for _ in range(1):
        s.add_window("code", "productive", ts=now)
    s.add_screen(0.05, ts=now)
    s.mark_input(now)
    return s


def test_features_shape():
    now = time.time()
    fv = feat.extract(_steady_typing_store(now), now=now)
    assert len(fv.as_list()) == feat.N_FEATURES


def test_heuristic_detects_deep_focus():
    now = time.time()
    clf = FocusClassifier(onnx_path=None)  # heuristic
    fv = feat.extract(_steady_typing_store(now), now=now)
    pred = clf.predict(fv)
    assert pred.backend == "heuristic"
    assert pred.state == DEEP_FOCUS


def test_heuristic_detects_away():
    now = time.time()
    s = SignalStore(window_seconds=30)
    s.mark_input(now - 200)  # no input for 200s
    clf = FocusClassifier(onnx_path=None)
    pred = clf.predict(feat.extract(s, now=now))
    assert pred.state == AWAY


def test_gate_holds_in_focus_and_digests():
    sink = ConsoleSink()
    gate = Gatekeeper(sink, focus_debounce_seconds=0, summarise_on_return=True)
    gate.update_state(DEEP_FOCUS, now=100)
    gate.submit(Notification("Slack", "A", "hi", priority="normal"), now=101)
    gate.submit(Notification("Mail", "B", "news", priority="low"), now=102)
    assert gate.held_count == 2
    assert len(sink.delivered) == 0
    gate.update_state(IDLE, now=110)   # focus ends -> digest
    assert len(sink.delivered) == 2
    assert len(sink.digests) == 1


def test_urgent_always_passes():
    sink = ConsoleSink()
    rules = PriorityRules(urgent_keywords=["outage"])
    gate = Gatekeeper(sink, priority=rules, focus_debounce_seconds=0)
    gate.update_state(DEEP_FOCUS, now=100)
    gate.submit(Notification("Teams", "Ops", "payments outage!", priority="normal"), now=101)
    assert len(sink.delivered) == 1  # bypassed the gate
    assert gate.held_count == 0


if __name__ == "__main__":
    import traceback
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception:
            failed += 1
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    raise SystemExit(1 if failed else 0)
