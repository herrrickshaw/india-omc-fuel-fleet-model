#!/usr/bin/env node
/* DME blending pitch — "DME, done right". Numbers from dme_pitch_model.py and
 * dme_lpg_blending.py (LERC basis). Structure: problem -> guardrails-as-strategy
 * -> market wedge -> business model -> financials -> risks -> landscape -> ask.
 * Output: docs/DME_Blending_Pitch.pptx */
const pptxgen = require("pptxgenjs");

const P = { dark: "0E3B2E", dark2: "16523F", amber: "E3A72F", green: "2E9E6B",
  red: "C0392B", ink: "1C2B27", mute: "5C6B66", bg: "FFFFFF", card: "F2F6F4", line: "D5E0DB" };
const FONT = "Calibri", HEAD = "Cambria";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "india-omc-fuel-fleet-model";
pres.title = "DME Blending — Investment Pitch";

const title = (s, t, sub, dark = false) => {
  s.addText(t, { x: 0.6, y: 0.35, w: 12.1, h: 0.75, fontFace: HEAD, fontSize: 28, bold: true,
    color: dark ? "FFFFFF" : P.dark, margin: 0 });
  if (sub) s.addText(sub, { x: 0.6, y: 1.02, w: 12.1, h: 0.4, fontFace: FONT, fontSize: 13,
    color: dark ? "CFE3DA" : P.mute, margin: 0 });
};
const card = (s, x, y, w, h, fill = P.card) =>
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: fill }, rectRadius: 0.08,
    line: { color: P.line, width: 0.75 } });
const stat = (s, x, y, w, big, label, color) => {
  card(s, x, y, w, 1.5);
  s.addText(big, { x: x + 0.12, y: y + 0.1, w: w - 0.24, h: 0.75, fontFace: HEAD, fontSize: 25,
    bold: true, color, align: "center", margin: 0 });
  s.addText(label, { x: x + 0.12, y: y + 0.86, w: w - 0.24, h: 0.56, fontFace: FONT,
    fontSize: 11, color: P.mute, align: "center", margin: 0 });
};
const bullets = (s, x, y, w, h, items, opts = {}) =>
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: { code: "2022", indent: 14 },
    breakLine: i < items.length - 1, paraSpaceAfter: opts.gap ?? 8 } })),
    { x, y, w, h, fontFace: FONT, fontSize: opts.size ?? 13.5, color: opts.color ?? P.ink,
      valign: "top", margin: 0 });
const grid = (s, rows, x, y, colX, colW, rowH = 0.55, hotRow = -1) => rows.forEach((r, i) => {
  const yy = y + i * rowH, head = i === 0, hot = i === hotRow;
  r.forEach((t, j) => {
    s.addShape(pres.ShapeType.rect, { x: colX[j], y: yy, w: colW[j], h: rowH - 0.02,
      fill: { color: head ? P.dark : hot ? P.dark2 : i % 2 ? P.card : "FFFFFF" },
      line: { color: P.line, width: 0.75 } });
    s.addText(t, { x: colX[j] + 0.08, y: yy, w: colW[j] - 0.16, h: rowH - 0.02, fontFace: FONT,
      fontSize: head ? 11.5 : 12.5, bold: head || j === 0, color: (head || hot) ? "FFFFFF" : P.ink,
      valign: "middle", align: j === 0 ? "left" : "center", margin: 0 });
  });
});

/* ── 1. TITLE ─────────────────────────────────────────────────────────── */
let s = pres.addSlide(); s.background = { color: P.dark };
s.addText("DME, Done Right", { x: 0.9, y: 1.8, w: 11.5, h: 1.1, fontFace: HEAD, fontSize: 52,
  bold: true, color: "FFFFFF", margin: 0 });
s.addText("Domestic dimethyl ether for LPG blending — commercial segment first, energy-parity pricing always",
  { x: 0.9, y: 3.0, w: 11.3, h: 0.6, fontFace: FONT, fontSize: 20, color: P.amber, margin: 0 });
s.addText("Investment pitch · July 2026 · built on the Volume Dividend fourth-quadrant analysis, LERC engineering evidence and BIS IS 18698:2024",
  { x: 0.9, y: 6.4, w: 11.5, h: 0.5, fontFace: FONT, fontSize: 12, color: "9DBFB2", margin: 0 });

/* ── 2. PROBLEM ───────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "The setup: a huge import bill and a freshly opened standard",
  "…and a trap that will kill naive DME programmes");
[["₹90,000+ cr of LPG imports", "India imports ~62% of its 29.7-MMT LPG pool — propane/butane priced off the Saudi CP, dollar-denominated, geopolitically exposed. Every blending programme starts from this bill.", P.card],
 ["The door is open", "BIS IS 18698:2024 permits up to 20% DME in LPG. LERC (LPG Equipment Research Centre, Bengaluru) has cleared 20% material compatibility and run stable flex-burner trials — the engineering is done.", P.card],
 ["The trap (our own analysis)", "DME carries 37% less energy per kg. On subsidised domestic cylinders at unchanged prices, DME20 bills households +₹312/yr AND adds ₹1,201 cr/yr of PMUY subsidy — a programme designed that way dies politically. The pitch is built NOT to be that programme.", P.dark]]
.forEach(([h, d, fill], i) => {
  const x = 0.6 + i * 4.2;
  card(s, x, 1.8, 3.95, 3.9, fill);
  const dk = fill === P.dark;
  s.addText(h, { x: x + 0.2, y: 2.0, w: 3.55, h: 0.75, fontFace: FONT, fontSize: 15, bold: true,
    color: dk ? P.amber : P.dark, margin: 0 });
  s.addText(d, { x: x + 0.2, y: 2.8, w: 3.55, h: 2.75, fontFace: FONT, fontSize: 12,
    color: dk ? "E8F1EC" : P.ink, margin: 0 });
});
bullets(s, 0.6, 6.05, 12.1, 1.0, [
  "LERC's measured thermal-efficiency drop at DME20 is −5.26% (IS 4246) — real but manageable IF the pricing is honest; the venture's entire design flows from that condition",
], { size: 13 });

/* ── 3. GUARDRAILS = STRATEGY ─────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "The guardrails ARE the strategy", "Three self-imposed conditions that make the venture durable where naive DME dies");
[["1 · Energy-parity pricing, always", "DME sells at LPG price × 28.8/45.8 (~0.63× per kg). The buyer pays for energy, not kilograms. This forgoes the ₹34.7/kg 'temptation margin' — which is precisely the consumer's hidden loss and the programme's political poison.", P.dark],
 ["2 · Commercial LPG first", "The 19-kg commercial cylinder is price-DEREGULATED and unsubsidised: parity pricing is a private negotiation, not a subsidy fight. The PMUY inversion never arises. Domestic kitchens only after parity cylinder pricing is regulated in.", P.card],
 ["3 · Domestic carbon only", "Imported-methanol DME earns ₹1.9/kg at honest pricing — it fails, and merely re-denominates the import bill. The venture runs on domestic coal-gasification / bio-methanol under long-term contract, or it does not run.", P.card]]
.forEach(([h, d, fill], i) => {
  const x = 0.6 + i * 4.2;
  card(s, x, 1.8, 3.95, 4.1, fill);
  const dk = fill === P.dark;
  s.addText(h, { x: x + 0.2, y: 2.0, w: 3.55, h: 0.8, fontFace: FONT, fontSize: 14.5, bold: true,
    color: dk ? P.amber : P.dark, margin: 0 });
  s.addText(d, { x: x + 0.2, y: 2.85, w: 3.55, h: 2.9, fontFace: FONT, fontSize: 12,
    color: dk ? "E8F1EC" : P.ink, margin: 0 });
});
bullets(s, 0.6, 6.25, 12.1, 0.9, [
  "Honesty as moat: a venture that cannot be accused of the fourth-quadrant harm is the one regulators let scale — the same durability logic as CBG's on-budget stack",
], { size: 13 });

/* ── 4. MARKET WEDGE ──────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "The wedge: commercial & industrial LPG",
  "Unsubsidised, deregulated, price-sensitive buyers — hotels, restaurants, industry");
grid(s, [
  ["Segment", "Pool (MMT/yr)", "DME20 ceiling (kt DME)", "Why it works"],
  ["Commercial (19-kg) + industrial", "~4.5", "~900", "deregulated; parity = commercial discount"],
  ["Auto-LPG", "~0.3", "~60", "niche; elastomer retrofit known"],
  ["Domestic (14.2-kg, PMUY)", "~25", "—", "EXCLUDED until parity pricing is regulated"],
], 0, 1.75, [0.6, 4.3, 6.3, 8.7], [3.7, 2.0, 2.4, 4.05], 0.62, 3);
card(s, 0.6, 4.5, 5.9, 2.4);
s.addText("The commercial buyer's math", { x: 0.85, y: 4.7, w: 5.4, h: 0.4, fontFace: FONT,
  fontSize: 14, bold: true, color: P.dark, margin: 0 });
bullets(s, 0.85, 5.15, 5.4, 1.6, [
  "DME20 at energy parity cuts the effective ₹/MJ of a hotel's fuel bill ~2–3% (blender passes part of the DME discount)",
  "Same burners; elastomer swap per LERC compatibility list",
], { size: 12.5 });
card(s, 6.8, 4.5, 5.95, 2.4, P.dark);
s.addText("Ceiling with today's standard", { x: 7.05, y: 4.7, w: 5.4, h: 0.4, fontFace: FONT,
  fontSize: 14, bold: true, color: P.amber, margin: 0 });
bullets(s, 7.05, 5.15, 5.45, 1.6, [
  "C&I DME20 ceiling ≈ 0.9–1.1 MMT DME/yr = 27–33 plants of the reference size — years of runway before the domestic segment is even needed",
], { size: 12.5, color: "E8F1EC" });

/* ── 5. BUSINESS MODEL ────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Business model: the simple step in the chain",
  "100-TPD methanol-to-DME dehydration plant, co-located with domestic methanol capacity");
const steps = [
  ["Domestic methanol", "coal-gasification / bio-methanol, long-term contract ₹15–17/kg"],
  ["Dehydration unit", "catalytic (alumina) — proven, simple; the ₹120 cr asset"],
  ["DME storage & loading", "LPG-like handling; pressurised spheres"],
  ["Blender / marketer", "OMC & parallel marketers blend ≤20% per IS 18698"],
  ["C&I customer", "19-kg cylinders & bulk — energy-parity billed"],
];
steps.forEach(([h, d], i) => {
  const x = 0.6 + i * 2.5;
  card(s, x, 1.85, 2.3, 2.05, i === 1 ? P.dark : P.card);
  const dk = i === 1;
  s.addText(h, { x: x + 0.12, y: 2.0, w: 2.06, h: 0.6, fontFace: FONT, fontSize: 12.5, bold: true,
    color: dk ? P.amber : P.dark, margin: 0 });
  s.addText(d, { x: x + 0.12, y: 2.62, w: 2.06, h: 1.2, fontFace: FONT, fontSize: 10.5,
    color: dk ? "E8F1EC" : P.mute, margin: 0 });
  if (i < 4) s.addText("→", { x: x + 2.26, y: 2.5, w: 0.3, h: 0.5, fontFace: FONT, fontSize: 18,
    bold: true, color: P.amber, align: "center", margin: 0 });
});
card(s, 0.6, 4.3, 12.15, 2.5);
s.addText("Per-kg economics at the three postures (₹/kg)", { x: 0.85, y: 4.5, w: 11.5, h: 0.4,
  fontFace: FONT, fontSize: 14, bold: true, color: P.dark, margin: 0 });
grid(s, [
  ["", "Realisation", "Methanol feed (1.4×)", "Conversion", "Margin"],
  ["Base: domestic methanol, parity", "39.0", "(23.8)", "(3.5)", "11.7"],
  ["Imported methanol (fails)", "39.0", "(33.6)", "(3.5)", "1.9"],
  ["kg-parity pricing (refused)", "62.0", "(23.8)", "(3.5)", "34.7"],
], 0, 4.95, [0.85, 4.6, 6.4, 8.6, 10.3], [3.75, 1.8, 2.2, 1.7, 2.0], 0.46, 3);

/* ── 6. FINANCIALS ────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Financials: honest pricing still clears 26%",
  "₹120 cr capex · 70:30 @ 10% (no subvention assumed) · 29.7 kt DME/yr · energy-parity realisation ₹39/kg");
stat(s, 0.6, 1.75, 2.35, "26.0%", "Project IRR", P.dark);
stat(s, 3.1, 1.75, 2.35, "42.1%", "Equity IRR", P.dark);
stat(s, 5.6, 1.75, 2.35, "₹106 cr", "NPV @ 12%", P.green);
stat(s, 8.1, 1.75, 2.35, "Year 4", "Payback", P.amber);
stat(s, 10.6, 1.75, 2.15, "1.94×", "Steady DSCR", P.amber);
s.addText("Sensitivity — project IRR (%): methanol price × DME realisation",
  { x: 0.6, y: 3.6, w: 8.0, h: 0.4, fontFace: FONT, fontSize: 13.5, bold: true, color: P.dark, margin: 0 });
grid(s, [
  ["Methanol ₹/kg", "₹36/kg", "₹39/kg (parity, base)", "₹42/kg"],
  ["15,000/t", "25.6", "32.4", "39.0"],
  ["17,000/t (base)", "18.8", "26.0", "32.9"],
  ["20,000/t", "6.7", "15.6", "23.2"],
], 0, 4.05, [0.6, 2.9, 5.2, 7.5], [2.3, 2.3, 2.3, 2.3], 0.56);
card(s, 10.2, 3.6, 2.55, 2.75, P.dark);
s.addText("The whole model rides on the methanol contract: ₹20/kg methanol compresses IRR to 15.6% — the feed contract IS the investment decision",
  { x: 10.4, y: 3.8, w: 2.15, h: 2.4, fontFace: FONT, fontSize: 11.5, color: "E8F1EC", margin: 0 });
bullets(s, 0.6, 6.45, 12.1, 0.9, [
  "No subvention assumed — a DME-specific interest-subvention analogue (the ethanol ISS template) is pure upside; EBITDA ₹34.7 cr/yr at base",
], { size: 12.5 });

/* ── 7. RISKS ─────────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Risks and mitigants", "Named in our own fourth-quadrant analysis — answered structurally");
grid(s, [
  ["Risk", "Reality", "Mitigant"],
  ["Methanol supply", "Domestic coal/bio-methanol capacity is nascent; market methanol is imported ₹24", "Co-location + take-or-pay with Coal India/BHEL-route projects; venture gated on the contract, not built ahead of it"],
  ["Elastomer retrofit", "DME attacks conventional seals beyond ~20%", "Stay ≤20% per IS 18698; LERC compatibility list is the binding spec; retrofit kits funded at blender"],
  ["Demand adoption", "C&I buyers must accept a blended product", "Energy-parity billing makes the buyer strictly better off; pilot with 2 parallel marketers"],
  ["Policy drift", "Pressure to push into subsidised domestic LPG at kg prices", "Charter commitment: domestic segment only under regulated parity pricing — the refusal is contractual"],
  ["Saudi CP swings", "Parity realisation moves with LPG", "Margin is methanol-linked, not CP-linked, at ~63% pass-through; hedge on the spread"],
], 0, 1.7, [0.6, 2.6, 6.0], [2.0, 3.4, 6.75], 0.8);
bullets(s, 0.6, 6.65, 12.1, 0.6, [
  "Not relying on: subvention, carbon credits, domestic-kitchen volumes, or any pricing above energy parity",
], { size: 11.5 });

/* ── 8. LANDSCAPE ─────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Landscape: technology proven, field empty",
  "China blends DME-LPG at scale; India has the standard but no supply");
[["Global precedent", "China has blended DME into LPG at multi-MMT scale for two decades (the cautionary tales are all kg-parity mis-selling — our guardrail #1 exists because of them). Korea/Japan ran fleet and burner programmes.", P.card],
 ["Indian building blocks", "NCL Pune has demonstrated DME synthesis; IOCL R&D active; Assam Petrochemicals and GNFC hold methanol capacity; Coal India–BHEL coal-to-methanol projects are the feed pipeline. Nobody has assembled the chain.", P.card],
 ["First-mover reality", "India has a 20% standard (IS 18698:2024), LERC-cleared equipment evidence, a ₹90,000-cr import bill — and zero commercial DME blending. The venture IS the market at inception.", P.dark]]
.forEach(([h, d, fill], i) => {
  const x = 0.6 + i * 4.2;
  card(s, x, 1.8, 3.95, 3.9, fill);
  const dk = fill === P.dark;
  s.addText(h, { x: x + 0.2, y: 2.0, w: 3.55, h: 0.55, fontFace: FONT, fontSize: 15, bold: true,
    color: dk ? P.amber : P.dark, margin: 0 });
  s.addText(d, { x: x + 0.2, y: 2.6, w: 3.55, h: 2.95, fontFace: FONT, fontSize: 12,
    color: dk ? "E8F1EC" : P.ink, margin: 0 });
});
bullets(s, 0.6, 6.05, 12.1, 1.0, [
  "Synergy with the bioenergy platform: bio-methanol/bio-DME from CBG-adjacent syngas is the long-run domestic-carbon route — same feedstock ecosystems, same partners",
], { size: 13 });

/* ── 9. ASK ───────────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.dark };
title(s, "The ask: one gated pilot, then replicate", null, true);
stat(s, 0.9, 1.7, 2.7, "₹120 cr", "pilot plant (₹36 cr equity)", P.dark);
stat(s, 3.8, 1.7, 2.7, "29.7 kt/yr", "DME = ~150 kt DME20 comm. LPG", P.dark);
stat(s, 6.7, 1.7, 2.7, "26% / 42%", "project / equity IRR at parity", P.dark);
stat(s, 9.6, 1.7, 2.7, "27–33×", "replication ceiling in C&I alone", P.dark);
bullets(s, 0.9, 3.7, 11.5, 3.0, [
  "Gate 1 (pre-capex): 10-yr take-or-pay domestic methanol contract at ≤₹17/kg — no contract, no build; site co-located with the methanol plant",
  "Gate 2: blending MoU with two parallel marketers / one OMC for C&I DME20 at energy-parity transfer pricing; LERC-listed retrofit kits at the bottling plant",
  "Build (15 months) → prove the honest-pricing P&L publicly → replicate toward the ~30-plant C&I ceiling; domestic kitchens only when parity cylinder pricing is regulated",
  "Why fund the constrained version: the unconstrained margin (₹34.7/kg at kg-parity) is exactly what makes naive DME uninvestable — this structure is the one that survives scrutiny, scale and time",
], { size: 15, color: "FFFFFF", gap: 14 });
s.addText("Model & sensitivity: dme_pitch_model.py · analysis: dme_lpg_blending.py (LERC basis) · The Volume Dividend §10 · github.com/herrrickshaw/india-omc-fuel-fleet-model",
  { x: 0.9, y: 6.85, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 11.5, color: "9DBFB2", margin: 0 });

pres.writeFile({ fileName: "docs/DME_Blending_Pitch.pptx" })
  .then(() => console.log("wrote docs/DME_Blending_Pitch.pptx"));
