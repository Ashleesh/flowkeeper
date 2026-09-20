/*
 * Regenerate the pitch deck as a .pptx.
 * Requires Node with pptxgenjs:  npm install pptxgenjs
 * Run:  node build/build_deck.js   ->  FlowKeeper_Pitch.pptx
 * Then convert to PDF with LibreOffice:  soffice --headless --convert-to pdf FlowKeeper_Pitch.pptx
 */
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pres.defineLayout({ name: "W", width: 13.33, height: 7.5 });

const C = {
  bg: "160E2E", bg2: "1F1440", panel: "241851", line: "3A2A6B",
  ink: "F3EEFF", muted: "B7A9E0", teal: "2EE6C5", amber: "FFB454",
  violet: "8A6BFF", pink: "FF7A9C", lightbg: "F5F2FF", darktext: "20143F",
};
const F = "Calibri";

function base(dark = true) {
  const s = pres.addSlide();
  s.background = { color: dark ? C.bg : C.lightbg };
  return s;
}
function kicker(s, text, dark = true) {
  s.addText(text.toUpperCase(), { x: 0.7, y: 0.55, w: 11.9, h: 0.4, isTextBox: true,
    fontFace: F, fontSize: 13, bold: true, charSpacing: 3, color: dark ? C.teal : "6B45FF" });
}
function title(s, text, dark = true, y = 1.0, size = 34) {
  s.addText(text, { x: 0.7, y, w: 11.9, h: 1.1, isTextBox: true, fontFace: F,
    fontSize: size, bold: true, color: dark ? C.ink : C.darktext });
}
function foot(s, n, dark = true) {
  const col = dark ? C.muted : "5A4D86";
  s.addText("FlowKeeper", { x: 0.7, y: 7.0, w: 6, h: 0.3, isTextBox: true, fontFace: F, fontSize: 11, color: col });
  s.addText(String(n), { x: 12.4, y: 7.0, w: 0.6, h: 0.3, isTextBox: true, fontFace: F, fontSize: 11, color: col, align: "right" });
}
function card(s, x, y, w, h, dark = true) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.12,
    fill: { color: dark ? C.panel : "FFFFFF" }, line: { color: dark ? C.line : "E2DBFF", width: 1 } });
}
function circ(s, x, y, color) {
  s.addShape(pres.ShapeType.ellipse, { x, y, w: 0.75, h: 0.75, fill: { color: C.panel },
    line: { color, width: 1.5 } });
}

// 1 TITLE
let s = base(true);
kicker(s, "Snapdragon® AI Lab · Build & Present Challenge");
s.addText("FlowKeeper", { x: 0.7, y: 1.4, w: 11.9, h: 1.6, isTextBox: true, fontFace: F, fontSize: 66, bold: true, color: C.ink });
s.addText("Notifications that understand your focus — and never break it.",
  { x: 0.7, y: 3.1, w: 11.5, h: 0.7, isTextBox: true, fontFace: F, fontSize: 24, color: C.muted });
s.addText("On-device attention-aware notification gatekeeper, built for Snapdragon-powered HP PCs.",
  { x: 0.7, y: 3.8, w: 11.5, h: 0.6, isTextBox: true, fontFace: F, fontSize: 18, color: C.muted });
s.addText("Runs entirely on the NPU   ·   100% private · offline",
  { x: 0.7, y: 5.6, w: 11.5, h: 0.5, isTextBox: true, fontFace: F, fontSize: 16, color: C.teal });
s.addText("Ashlesh · 2026", { x: 12.0, y: 7.0, w: 1.0, h: 0.3, isTextBox: true, fontFace: F, fontSize: 11, color: C.muted, align: "right" });

// 2 PROBLEM
s = base(true);
kicker(s, "The problem");
title(s, "Every notifier on your PC is dumb about timing.");
const stats = [["~6 min", C.teal, "Average gap between interruptions for a knowledge worker."],
  ["~23 min", C.amber, "To fully recover focus after one context switch."],
  ["1", C.violet, "Tool we're given: “Do Not Disturb” — a blunt manual switch nobody remembers to flip."]];
stats.forEach(([n, col, lbl], i) => {
  const x = 0.7 + i * 4.05;
  card(s, x, 2.3, 3.75, 2.5);
  s.addText(n, { x: x + 0.3, y: 2.55, w: 3.2, h: 1.0, isTextBox: true, fontFace: F, fontSize: 46, bold: true, color: col });
  s.addText(lbl, { x: x + 0.3, y: 3.6, w: 3.2, h: 1.1, isTextBox: true, fontFace: F, fontSize: 15, color: C.muted });
});
s.addText([{ text: "Slack, Teams, Mail and the OS all interrupt the instant a message arrives. ", options: {} },
  { text: "Nobody has built a notification layer that understands whether you're focused right now.", options: { color: C.teal, bold: true } }],
  { x: 0.7, y: 5.1, w: 11.9, h: 1.2, isTextBox: true, fontFace: F, fontSize: 20, color: C.ink });
foot(s, 2);

// 3 WHY UNSOLVED
s = base(true);
kicker(s, "Why nobody solves it");
title(s, "The cloud fundamentally can't do this.");
s.addText([
  { text: "Knowing your focus state means continuously reading your typing rhythm and screen activity.\n", options: {} },
  { text: "That is exactly the data you would never stream to someone else's server.\n\n", options: {} },
  { text: "So this problem is only solvable on-device — where Snapdragon's NPU shines.", options: { color: C.amber, bold: true } },
], { x: 0.7, y: 2.3, w: 6.6, h: 3.5, isTextBox: true, fontFace: F, fontSize: 22, color: C.ink, lineSpacingMultiple: 1.2 });
card(s, 7.7, 2.3, 4.9, 3.3);
s.addText("Keystrokes + screen", { x: 7.9, y: 2.7, w: 4.5, h: 0.5, isTextBox: true, fontFace: F, fontSize: 18, color: C.muted, align: "center" });
s.addText("↓  stay on your laptop  ↓", { x: 7.9, y: 3.4, w: 4.5, h: 0.6, isTextBox: true, fontFace: F, fontSize: 22, color: C.teal, align: "center", bold: true });
s.addText("Focus state", { x: 7.9, y: 4.1, w: 4.5, h: 0.5, isTextBox: true, fontFace: F, fontSize: 18, color: C.muted, align: "center" });
s.addText("Nothing uploaded. Nothing stored.", { x: 7.9, y: 4.9, w: 4.5, h: 0.4, isTextBox: true, fontFace: F, fontSize: 15, color: C.amber, align: "center" });
foot(s, 3);

// 4 THE IDEA
s = base(true);
kicker(s, "The idea");
title(s, "Four focus states. One calm gate.");
const rows = [["State", "What it means", "What FlowKeeper does"],
  ["DEEP_FOCUS", "Steady typing, one app, no switching", "Hold & batch everything non-urgent"],
  ["LIGHT_WORK", "Reading / browsing, moderate switching", "Deliver normal, batch low-priority"],
  ["IDLE", "At the machine, between tasks", "Release everything held"],
  ["AWAY", "No input for a while", "Hold, then one digest on return"]];
const stateColors = [null, C.teal, C.violet, C.amber, C.pink];
const tRows = rows.map((r, i) => r.map((c, j) => ({
  text: c,
  options: {
    fontFace: F, fontSize: i === 0 ? 13 : 16, bold: i === 0 || j === 0,
    color: i === 0 ? C.teal : (j === 0 ? (stateColors[i] || C.ink) : C.ink),
    fill: { color: i === 0 ? C.bg2 : C.panel }, valign: "middle", margin: 6,
  },
})));
s.addTable(tRows, { x: 0.7, y: 2.1, w: 11.9, colW: [2.6, 4.9, 4.4], rowH: 0.62,
  border: { type: "solid", color: C.line, pt: 1 } });
s.addText([{ text: "Drop out of focus and the queue arrives as one digest, not a stream of pop-ups. ", options: {} },
  { text: "Urgent items always pass straight through.", options: { color: C.amber, bold: true } }],
  { x: 0.7, y: 5.7, w: 11.9, h: 0.8, isTextBox: true, fontFace: F, fontSize: 18, color: C.muted });
foot(s, 4);

// 5 HOW IT WORKS (light)
s = base(false);
kicker(s, "How it works", false);
title(s, "Signals → features → on-device model → gate.", false);
const steps = [["Signals", "Typing cadence (never keycodes), app category (never titles), 32×32 screen motion (never a screenshot)."],
  ["8 features", "Anonymous vector: rhythm steadiness, keys/min, app-switches/min, productive ratio, idle seconds…"],
  ["NPU classifier", "Tiny INT8 MLP infers the focus state in <1 ms on the Hexagon NPU."],
  ["Gatekeeper", "Holds, batches, or delivers — one digest when you surface."]];
steps.forEach(([h, d], i) => {
  const x = 0.7 + i * 3.05;
  s.addShape(pres.ShapeType.roundRect, { x, y: 2.2, w: 2.75, h: 2.0, rectRadius: 0.1, fill: { color: "FFFFFF" }, line: { color: "E2DBFF", width: 1 } });
  s.addText(h, { x: x + 0.2, y: 2.35, w: 2.4, h: 0.5, isTextBox: true, fontFace: F, fontSize: 18, bold: true, color: "6B45FF" });
  s.addText(d, { x: x + 0.2, y: 2.85, w: 2.4, h: 1.25, isTextBox: true, fontFace: F, fontSize: 12.5, color: "5A4D86" });
  if (i < 3) s.addText("→", { x: x + 2.7, y: 2.9, w: 0.4, h: 0.6, isTextBox: true, fontFace: F, fontSize: 26, bold: true, color: "6B45FF", align: "center" });
});
s.addShape(pres.ShapeType.roundRect, { x: 0.7, y: 4.7, w: 11.9, h: 1.5, rectRadius: 0.1, fill: { color: "FFFFFF" }, line: { color: "E2DBFF", width: 1 } });
s.addText([{ text: "Privacy by construction:  ", options: { bold: true, color: "6B45FF" } },
  { text: "raw signals live in memory for a 30-second window, reduce to anonymous numbers, then age out. Nothing is written to disk. Nothing leaves the device.", options: {} }],
  { x: 1.0, y: 4.95, w: 11.3, h: 1.0, isTextBox: true, fontFace: F, fontSize: 18, color: C.darktext });
foot(s, 5, false);

// 6 WHY SNAPDRAGON
s = base(true);
kicker(s, "Why Snapdragon");
title(s, "An always-on job that only the NPU makes free.");
const pil = [["⚡", C.teal, "Always-on, ~zero battery", "A sub-ms INT8 MLP on the Hexagon NPU via ONNX Runtime's QNN Execution Provider. Sample every few seconds, all day."],
  ["🔒", C.amber, "Private by construction", "Behavioural signals never leave the laptop and are never stored — the architecture cloud AI can't match."],
  ["✈", C.violet, "Offline & instant", "Zero network round-trip: the gate reacts in real time — on a plane, in a tunnel, anywhere."]];
pil.forEach(([ic, col, h, d], i) => {
  const x = 0.7 + i * 4.05;
  card(s, x, 2.2, 3.75, 3.1);
  circ(s, x + 0.3, 2.45, col);
  s.addText(ic, { x: x + 0.3, y: 2.5, w: 0.75, h: 0.65, isTextBox: true, fontFace: F, fontSize: 24, color: col, align: "center" });
  s.addText(h, { x: x + 0.3, y: 3.35, w: 3.2, h: 0.6, isTextBox: true, fontFace: F, fontSize: 19, bold: true, color: C.ink });
  s.addText(d, { x: x + 0.3, y: 3.95, w: 3.2, h: 1.25, isTextBox: true, fontFace: F, fontSize: 13.5, color: C.muted });
});
s.addText([{ text: "Model compiled through Qualcomm AI Hub. Fallback: ", options: {} },
  { text: "QNN NPU → CPU → heuristic", options: { color: C.teal, bold: true } },
  { text: " — correct everywhere, optimal on Snapdragon.", options: {} }],
  { x: 0.7, y: 5.6, w: 11.9, h: 0.7, isTextBox: true, fontFace: F, fontSize: 17, color: C.muted });
foot(s, 6);

// 7 IT WORKS TODAY
s = base(true);
kicker(s, "It works today");
title(s, "A running prototype, not a slide-only idea.");
card(s, 0.7, 2.2, 5.9, 3.6);
s.addText("Simulated day → the gate in action", { x: 1.0, y: 2.4, w: 5.4, h: 0.5, isTextBox: true, fontFace: F, fontSize: 17, bold: true, color: C.teal });
s.addText([
  { text: "[ 20s] NOTE HOLD  [Slack] Priya: review my PR?\n", options: {} },
  { text: "[ 45s] NOTE HOLD  [Mail] Newsletter\n", options: {} },
  { text: "[ 70s] NOTE PASS  [Teams] P0 outage — bridge\n", options: { color: C.teal } },
  { text: "[120s] STATE → IDLE\n", options: {} },
  { text: "   → DIGEST (focus ended) — 3 held items", options: { color: C.amber } },
], { x: 1.0, y: 3.0, w: 5.4, h: 2.6, isTextBox: true, fontFace: "Courier New", fontSize: 13.5, color: "D8CEFF", lineSpacingMultiple: 1.3 });
card(s, 6.9, 2.2, 5.7, 3.6);
s.addText("Interruptions: without vs. with FlowKeeper", { x: 7.2, y: 2.4, w: 5.2, h: 0.5, isTextBox: true, fontFace: F, fontSize: 17, bold: true, color: C.amber });
s.addChart(pres.ChartType.bar, [{ name: "Interruptions", labels: ["Without", "With FlowKeeper"], values: [18, 4] }],
  { x: 7.1, y: 3.0, w: 5.3, h: 2.7, barDir: "bar", showTitle: false, showLegend: false,
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: C.ink, dataLabelFontSize: 12,
    chartColors: [C.teal], catAxisLabelColor: C.muted, valAxisLabelColor: C.muted,
    valGridLine: { color: C.line, size: 1 }, catGridLine: { style: "none" }, valAxisHidden: true });
foot(s, 7);

// 8 IMPACT (light)
s = base(false);
kicker(s, "Impact & accessibility", false);
title(s, "Reclaim the deep-work block.", false);
const imp = [["◎", "6B45FF", "Every knowledge worker", "Protects your longest, most valuable stretches of concentration from death-by-a-thousand-pings."],
  ["♥", "E07B1F", "A real accessibility win", "Neurodivergent users (ADHD, autism) are especially interruption-sensitive — this is an assistive layer, not a nag."],
  ["⇩", "7A45FF", "Deploys in one line", "pip install → python -m flowkeeper. Runs on any Snapdragon HP PC; degrades gracefully elsewhere."]];
imp.forEach(([ic, col, h, d], i) => {
  const x = 0.7 + i * 4.05;
  s.addShape(pres.ShapeType.roundRect, { x, y: 2.3, w: 3.75, h: 3.0, rectRadius: 0.12, fill: { color: "FFFFFF" }, line: { color: "E2DBFF", width: 1 } });
  s.addText(ic, { x: x + 0.3, y: 2.55, w: 0.9, h: 0.7, isTextBox: true, fontFace: F, fontSize: 26, color: col });
  s.addText(h, { x: x + 0.3, y: 3.35, w: 3.2, h: 0.6, isTextBox: true, fontFace: F, fontSize: 19, bold: true, color: C.darktext });
  s.addText(d, { x: x + 0.3, y: 3.95, w: 3.2, h: 1.3, isTextBox: true, fontFace: F, fontSize: 14, color: "5A4D86" });
});
foot(s, 8, false);

// 9 ROADMAP + ASK
s = base(true);
kicker(s, "Roadmap & the ask");
title(s, "From a smart gate to a focus companion.");
const road = ["Per-user personalization — learn each person's flow signature, on-device.",
  "Calendar-aware — auto-protect focus blocks, open the gate around meetings.",
  "Deeper Slack / Teams hooks — smarter urgency and VIP detection.",
  "Focus dashboard — private, on-device history of your best hours."];
s.addText(road.map((t, i) => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, paraSpaceAfter: 10 } })),
  { x: 0.7, y: 2.3, w: 6.7, h: 3.4, isTextBox: true, fontFace: F, fontSize: 18, color: C.ink });
card(s, 7.7, 2.3, 4.9, 2.9);
s.addText("The ask", { x: 8.0, y: 2.55, w: 4.3, h: 0.5, isTextBox: true, fontFace: F, fontSize: 19, bold: true, color: C.amber });
s.addText("A category nobody has built, only possible on-device, running today on Snapdragon.",
  { x: 8.0, y: 3.15, w: 4.3, h: 1.1, isTextBox: true, fontFace: F, fontSize: 18, color: C.ink });
s.addText("Let's put attention-aware notifications on every Snapdragon PC.",
  { x: 8.0, y: 4.25, w: 4.3, h: 0.9, isTextBox: true, fontFace: F, fontSize: 18, bold: true, color: C.teal });
foot(s, 9);

pres.writeFile({ fileName: "FlowKeeper_Pitch.pptx" }).then((f) => console.log("wrote " + f));
