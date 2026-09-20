/*
 * Regenerate the Brief Project Description as a .docx.
 * Requires Node with the `docx` package:  npm install docx
 * Run:  node build/build_docx.js   ->  FlowKeeper_Project_Description.docx
 */
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
} = require("docx");

const INK = "1C1C22", PURPLE = "2A1B57", MUTE = "5B4A86";
const h1 = (t) => new Paragraph({ children: [new TextRun({ text: t, bold: true, size: 48, color: PURPLE })], spacing: { after: 60 } });
const sub = (t) => new Paragraph({ children: [new TextRun({ text: t, bold: true, size: 26, color: MUTE })], spacing: { after: 40 } });
const meta = (t) => new Paragraph({ children: [new TextRun({ text: t, size: 18, color: "666666" })], spacing: { after: 220 } });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, bold: true, size: 27, color: PURPLE })], spacing: { before: 220, after: 100 } });
const p = (runs) => new Paragraph({ children: runs, spacing: { after: 140 } });
const t = (text, opts = {}) => new TextRun({ text, size: 23, color: INK, ...opts });
const bullet = (text) => new Paragraph({ bullet: { level: 0 }, children: [t(text)], spacing: { after: 60 } });

function cell(text, { header = false, w } = {}) {
  return new TableCell({
    width: { size: w, type: WidthType.DXA },
    shading: header ? { type: ShadingType.CLEAR, fill: "F4F0FE" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ children: [new TextRun({ text, bold: header, size: 20, color: header ? PURPLE : INK })] })],
  });
}
function stateTable() {
  const cols = [1500, 3400, 4380];
  const rows = [["State", "Meaning", "FlowKeeper's response"],
    ["DEEP_FOCUS", "Steady typing, one app, little switching", "Hold and batch everything non-urgent"],
    ["LIGHT_WORK", "Reading or browsing, moderate switching", "Deliver normal items; batch low-priority"],
    ["IDLE", "At the machine, between tasks", "Release everything held"],
    ["AWAY", "No input for a while", "Hold, then deliver one digest on return"]];
  return new Table({
    columnWidths: cols, width: { size: 9280, type: WidthType.DXA },
    rows: rows.map((r, i) => new TableRow({ children: r.map((c, j) => cell(c, { header: i === 0, w: cols[j] })) })),
  });
}

const doc = new Document({
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    children: [
      h1("FlowKeeper"),
      sub("Notifications That Understand Your Focus"),
      p([t("An on-device, attention-aware notification gatekeeper, designed and optimized for Snapdragon-powered HP PCs.", { size: 24, color: "33324A" })]),
      meta("Author: Ashlesh  ·  Submission: Snapdragon® AI Lab — Build & Present Challenge (Qualcomm)  ·  2026"),

      h2("The problem"),
      p([t("Knowledge workers are interrupted roughly every six minutes, and each context switch costs about 23 minutes to fully recover from. Yet every notification system on a PC — Slack, Teams, Mail, and the operating system itself — interrupts the instant a message arrives, with no regard for whether you are in the middle of a deep-work session or idly scrolling. The only control we are given is “Do Not Disturb”: a blunt, manual switch that people forget to turn on, and that hides things which actually mattered when they do. No product today makes notifications genuinely understand the user’s current focus.")]),

      h2("Why nobody solves it — and why it must be on-device"),
      p([t("Understanding someone’s focus state means continuously observing how they work: their typing rhythm and their on-screen activity. That is precisely the kind of data a person would never agree to stream to a third-party cloud server. As a result, an attention-aware notification layer is only solvable with private, on-device AI — which is exactly the workload the Snapdragon NPU is built for.")]),

      h2("The solution"),
      p([t("FlowKeeper runs a tiny, always-on classifier that maps live behavioural signals to one of four focus states and gates notifications accordingly:")]),
      stateTable(),
      p([t("When you drop out of deep focus, the held queue is released as a single calm digest instead of a stream of mid-task pop-ups. Genuinely urgent items — VIP senders, keywords such as “outage” or “P0”, and allow-listed apps — always bypass the gate in every state.")]),

      h2("How it works"),
      p([t("Three lightweight collectors feed an in-memory rolling window. Each is deliberately minimal to protect privacy: the keyboard collector records only typing cadence and a backspace flag, never keycodes; the window collector records only the foreground process name and category, never window titles; the screen collector downsamples each frame to a 32×32 grayscale grid, computes a single change ratio, and discards it — no screenshot is ever stored.")]),
      p([t("Those signals reduce to an eight-dimensional, fully anonymous feature vector: keystrokes per minute, inter-key rhythm steadiness, backspace ratio, application switches per minute, productive-app ratio, communication-app ratio, mean screen change, and idle seconds. An 8→16→4 multilayer perceptron classifies the current state, and a rule-based Gatekeeper applies the hold, batch, and digest policy.")]),

      h2("Why Snapdragon"),
      p([t("The classifier is an INT8-quantized MLP of fewer than 50,000 parameters. It is authored and compiled through Qualcomm AI Hub for the target device and executed on the Hexagon NPU via ONNX Runtime’s QNN Execution Provider. Inference is sub-millisecond and effectively free in battery terms, which is what makes always-on sampling — every few seconds, all day — practical on a laptop. FlowKeeper is therefore private by construction, fully offline, and instant. A graceful fallback chain — QNN NPU → CPU Execution Provider → transparent heuristic — means it is correct on any machine and optimal on Snapdragon HP PCs (X and X2 series).")]),

      h2("Current status"),
      p([t("FlowKeeper is a runnable Python package, not a slides-only concept. A --simulate mode plays a scripted work-day and shows the gate holding, batching, and releasing a digest as the focus state changes. The heuristic classifier works out of the box, and dropping a compiled models/focus.onnx into place automatically switches inference to the NPU. A --diagnose command reports which backend is active. The included scripts/export_model.py trains and exports the ONNX graph and can submit it to Qualcomm AI Hub for NPU compilation. Unit tests cover feature extraction, state classification, and the gate policy.")]),

      h2("Deployment & accessibility"),
      p([t("Installation is a single pip install followed by python -m flowkeeper. Beyond general productivity, FlowKeeper is a meaningful accessibility tool: neurodivergent users, including those with ADHD or autism, are especially sensitive to interruption, and an attention-aware gate acts as an assistive layer rather than another source of noise.")]),

      h2("Roadmap"),
      bullet("Per-user personalization — learn each person’s individual flow signature, entirely on-device."),
      bullet("Calendar-awareness — automatically protect scheduled focus blocks and relax the gate around meetings."),
      bullet("Deeper Slack / Teams integration — richer urgency and VIP detection."),
      bullet("Focus dashboard — a private, on-device history of when you do your best work."),

      h2("Mapping to the judging criteria"),
      p([t("Technical implementation: a real signal-to-decision pipeline with an INT8 ONNX model, a QNN NPU backend, and graceful fallback. Application use case & innovation: a category nobody has built — notifications that understand you — only possible on-device. Deployment & accessibility: one-line install, runs on any Snapdragon HP PC, and directly helps interruption-sensitive users. Presentation & documentation: a documented repository, an architecture overview, and an accompanying pitch deck.")]),
    ],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("FlowKeeper_Project_Description.docx", buf);
  console.log("wrote FlowKeeper_Project_Description.docx");
});
