# FlowKeeper architecture

```
 ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
 │  Keyboard    │   │ Active window│   │   Screen     │
 │  cadence     │   │  (process +  │   │  activity    │
 │ (no content) │   │  category)   │   │ (32x32 diff) │
 └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
        │                  │                  │
        └────────┬─────────┴─────────┬────────┘
                 ▼                    ▼
          ┌───────────────────────────────┐
          │        SignalStore            │  in-memory rolling window
          │   (privacy boundary — raw     │  (default 30s), nothing persisted
          │    events age out, no disk)   │
          └───────────────┬───────────────┘
                          ▼
                  ┌────────────────┐
                  │  features.py   │  8-dim anonymous vector
                  └───────┬────────┘
                          ▼
              ┌───────────────────────────┐
              │      FocusClassifier      │
              │  QNN NPU  ▸  CPU  ▸  rules │  ← Hexagon NPU via ONNX Runtime
              └───────────┬───────────────┘
                          ▼  DEEP_FOCUS / LIGHT_WORK / IDLE / AWAY
                  ┌────────────────┐        ┌───────────────────┐
   incoming  ───▶ │   Gatekeeper   │  ────▶ │ NotificationSink  │
   notifications  │  hold / batch  │        │ (toast / digest)  │
                  └────────────────┘        └───────────────────┘
```

## The 8 features

`keys_per_min`, `interkey_cv` (rhythm steadiness), `backspace_ratio`,
`app_switches_per_min`, `productive_ratio`, `comms_ratio`, `screen_change_mean`,
`idle_seconds`. See `flowkeeper/features.py` — the order is fixed because the ONNX
model is trained against exactly this layout.

## On-device model & Snapdragon path

The classifier is an 8→16→4 MLP (<50k params). It is exported to ONNX by
`scripts/export_model.py`, then compiled and INT8-quantised through **Qualcomm AI
Hub** for the target Snapdragon device. At runtime `FocusClassifier` requests the
`QNNExecutionProvider` first (Hexagon Tensor Processor), then `CPUExecutionProvider`,
then a rule-based fallback — so FlowKeeper is correct everywhere and *optimal* on
Snapdragon. Inference is sub-millisecond and effectively free on the NPU, which is
what makes always-on sampling (every 3s, all day) viable on battery.

## Privacy model

- Keyboard collector records only *timing* and a backspace flag — never keycodes.
- Window collector records only the foreground *process name* + category — never
  the window title or its contents.
- Screen collector downsamples to a 32×32 grayscale grid, computes one change
  ratio, and discards the frame — no screenshot is retained.
- All of the above live in `SignalStore` for the length of the feature window and
  then age out. Nothing is written to disk (unless `keep_state_timeline` is on,
  which stores only `(state, timestamp)` pairs), and nothing leaves the device.

## Gate policy

| State | Incoming non-urgent | Held queue |
|---|---|---|
| `DEEP_FOCUS` | hold (after debounce) | released as one digest when focus ends |
| `LIGHT_WORK` | deliver normal; hold low | low batched every N seconds |
| `IDLE` | deliver | flushed immediately |
| `AWAY` | hold | one digest on return |

Urgent items (VIP senders, urgent keywords, always-allow apps) bypass the gate in
every state.

## Windows integration notes

Capturing *incoming* OS/app notifications so they can be queued uses the
`Windows.UI.Notifications.Management.UserNotificationListener` API (requires the
user to grant notification-access). Re-emitting held items uses toast
notifications via `Windows.UI.Notifications`. The `ConsoleSink` stands in for both
during `--simulate` and tests.
```
