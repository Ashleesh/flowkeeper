"""Train and export the FlowKeeper focus classifier to ONNX, then hand off to
Qualcomm AI Hub for compilation to the Snapdragon Hexagon NPU.

Pipeline
--------
1. Generate/label feature vectors for the four focus states (here we synthesise
   from the same generative model the simulator uses; in production you'd collect
   a small on-device labelled set from the user with explicit consent).
2. Train a tiny MLP (8 -> 16 -> 4). It stays well under 50k params so it runs in
   well under a millisecond on the NPU.
3. Export to ONNX (opset 17) with a fixed [1, 8] float input named "features".
4. (On a machine with the qai-hub SDK) submit the ONNX to Qualcomm AI Hub to
   compile + quantise (INT8) a .bin/.onnx for the target Snapdragon device; the
   QNN Execution Provider then loads it at runtime.

Run:  python scripts/export_model.py --out models/focus.onnx
"""
from __future__ import annotations

import argparse

FEATURE_DIM = 8
CLASSES = ["DEEP_FOCUS", "LIGHT_WORK", "IDLE", "AWAY"]


def synth_dataset(n=6000, seed=0):
    import numpy as np
    rng = np.random.default_rng(seed)
    X, y = [], []
    for _ in range(n):
        label = rng.integers(0, 4)
        if label == 0:      # DEEP_FOCUS
            f = [rng.normal(180, 40), rng.uniform(0.05, 0.25), rng.uniform(0, 0.1),
                 rng.uniform(0, 1.5), rng.uniform(0.7, 1.0), rng.uniform(0, 0.2),
                 rng.uniform(0.02, 0.1), rng.uniform(0, 8)]
        elif label == 1:    # LIGHT_WORK
            f = [rng.normal(70, 30), rng.uniform(0.4, 0.9), rng.uniform(0.1, 0.3),
                 rng.uniform(3, 8), rng.uniform(0.1, 0.5), rng.uniform(0.3, 0.8),
                 rng.uniform(0.2, 0.6), rng.uniform(0, 12)]
        elif label == 2:    # IDLE
            f = [rng.uniform(0, 15), rng.uniform(0, 0.3), rng.uniform(0, 0.1),
                 rng.uniform(0, 2), rng.uniform(0, 0.4), rng.uniform(0, 0.4),
                 rng.uniform(0, 0.05), rng.uniform(20, 80)]
        else:               # AWAY
            f = [0, 0, 0, 0, rng.uniform(0, 0.3), rng.uniform(0, 0.3),
                 rng.uniform(0, 0.02), rng.uniform(95, 300)]
        X.append([max(0.0, v) for v in f])
        y.append(int(label))
    return np.asarray(X, dtype="float32"), np.asarray(y)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="models/focus.onnx")
    ap.add_argument("--ai-hub", action="store_true",
                    help="after export, submit to Qualcomm AI Hub for NPU compilation")
    ap.add_argument("--device", default="Snapdragon X Elite CRD")
    args = ap.parse_args()

    import numpy as np
    from sklearn.neural_network import MLPClassifier
    from skl2onnx import to_onnx
    from skl2onnx.common.data_types import FloatTensorType

    X, y = synth_dataset()
    clf = MLPClassifier(hidden_layer_sizes=(16,), max_iter=400, random_state=0)
    clf.fit(X, y)
    print(f"train accuracy: {clf.score(X, y):.3f}")

    onx = to_onnx(
        clf, X[:1],
        initial_types=[("features", FloatTensorType([1, FEATURE_DIM]))],
        target_opset=17,
        options={id(clf): {"zipmap": False}},  # plain float array output, not a dict
    )
    import os
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "wb") as fh:
        fh.write(onx.SerializeToString())
    print(f"wrote {args.out}")

    if args.ai_hub:
        # Requires: pip install qai-hub  and  qai-hub configure --api-token ...
        import qai_hub as hub  # type: ignore
        job = hub.submit_compile_job(
            model=args.out,
            device=hub.Device(args.device),
            options="--target_runtime qnn_context_binary",
        )
        print(f"submitted AI Hub compile job: {job.job_id}")
        print("download the compiled context binary and load it via the QNN EP.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
