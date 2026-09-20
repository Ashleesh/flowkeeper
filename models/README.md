# models/

Drop the compiled focus classifier here as `focus.onnx`.

FlowKeeper works with no model present (transparent heuristic fallback). To enable
NPU inference:

```bash
# 1. Train + export the ONNX graph
python scripts/export_model.py --out models/focus.onnx

# 2. (on a machine with the Qualcomm AI Hub SDK configured) compile for the NPU
python scripts/export_model.py --out models/focus.onnx --ai-hub \
    --device "Snapdragon X Elite CRD"
```

At runtime FlowKeeper loads the model through ONNX Runtime's
`QNNExecutionProvider` (Hexagon NPU), falling back to the CPU EP and then the
heuristic if the NPU path is unavailable. Confirm with `python -m flowkeeper --diagnose`.

Compiled `.onnx` artifacts are git-ignored — regenerate them per device.
