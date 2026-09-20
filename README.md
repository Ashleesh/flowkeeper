# FlowKeeper

**A notification gatekeeper that understands when you're in flow — and never breaks it.**

FlowKeeper watches *how* you work (typing rhythm, app switching, on-screen activity)
entirely **on-device**, infers your current focus state on the Snapdragon **Hexagon NPU**,
and holds non-urgent notifications until you surface. No cloud. No keystroke logging.
Your behavioural signals never leave the laptop.

> Built for the Snapdragon® AI Lab Build & Present Challenge — designed and optimised
> for Snapdragon-powered HP PCs (Snapdragon X / X2 series).

---

## The problem nobody solves

Every notification system on your PC is dumb about *timing*. Slack, Teams, Mail and the
OS itself all interrupt you the instant a message arrives — whether you're deep in a
compile-debug loop or idly scrolling. The average knowledge worker is interrupted every
**~6 minutes**, and each context switch costs **~23 minutes** to fully recover from.

"Do Not Disturb" is the only tool we're given, and it's a blunt manual switch: you either
remember to turn it on (you don't), or you miss things that mattered. Nobody has built a
notification layer that actually *understands* whether you're focused right now.

A cloud service fundamentally **cannot** solve this — knowing your focus state means
continuously reading your screen and keystrokes, which is exactly the data you'd never
stream to someone else's server. This problem is *only* solvable on-device.

## The idea

FlowKeeper runs a tiny always-on classifier on the NPU that maps live behavioural
features to one of four states:

| State | What it means | What FlowKeeper does |
|---|---|---|
| `DEEP_FOCUS` | Steady typing, one app, no switching | **Hold & batch** everything non-urgent |
| `LIGHT_WORK` | Reading, browsing, moderate switching | Release low-priority in small batches |
| `IDLE` | At the machine but between tasks | Release everything held |
| `AWAY` | No input for a while | Hold, then summarise on return |

When you drop out of `DEEP_FOCUS`, the queue is released in one calm digest instead of a
stream of mid-task pop-ups. Genuinely urgent items (configurable senders / keywords)
always pass straight through.

## Why Snapdragon / why on-device

- **Always-on at ~zero battery cost.** The classifier is a sub-millisecond MLP quantised
  to INT8 and run on the Hexagon NPU via ONNX Runtime's **QNN Execution Provider**. It
  can sample every few seconds all day without touching the CPU or the battery — the
  exact workload NPUs exist for.
- **Private by construction.** Raw keystrokes and screen frames are reduced to anonymous
  numeric features in memory and discarded. Nothing is stored, nothing is uploaded.
- **Offline & instant.** Zero network round-trip means the gate reacts in real time, on a
  plane, in a tunnel, anywhere.

The focus model is authored and compiled through **Qualcomm AI Hub** for the target
Snapdragon device, then loaded by the QNN EP at runtime. See
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Quick start

```bash
python -m pip install -r requirements.txt

# Run against synthetic signals on any OS (great for a first look / CI):
python -m flowkeeper --simulate

# Run for real on a Snapdragon HP PC:
python -m flowkeeper --config config/default.yaml
```

On first run with no compiled model present, FlowKeeper uses a transparent heuristic
classifier so it works out of the box; drop a compiled `models/focus.onnx` in place and it
automatically switches to NPU inference. Verify which backend is active:

```bash
python -m flowkeeper --diagnose
```

## How it fits the judging criteria

- **Technical implementation** — real signal pipeline, INT8 ONNX model, QNN NPU backend
  with graceful fallback, clean modular architecture.
- **Application use case & innovation** — a category nobody has built: notifications that
  understand you, only possible on-device.
- **Deployment & accessibility** — single `pip install`, runs on any Snapdragon HP PC,
  degrades gracefully on non-NPU hardware, helps neurodivergent users who are especially
  sensitive to interruption.
- **Presentation & documentation** — this README, an architecture doc, and a pitch deck.

## Repo layout

```
flowkeeper/
├── flowkeeper/           # the package
│   ├── signals/          # keyboard cadence, active window, screen activity
│   ├── model/            # ONNX/QNN focus classifier + heuristic fallback
│   ├── gate/             # gatekeeper policy + notification capture/replay
│   ├── features.py       # signals -> feature vector
│   ├── store.py          # in-memory rolling buffer (privacy boundary)
│   └── app.py            # the always-on loop
├── scripts/export_model.py  # train/export/quantise the focus model for AI Hub + QNN
├── models/               # compiled focus.onnx goes here
├── config/default.yaml
└── docs/ARCHITECTURE.md
```

## License

MIT — see [LICENSE](LICENSE).
