#!/usr/bin/env node
/* Isobutanol blending pitch. Numbers from isobutanol_pitch_model.py,
 * energy_blend_comparison.py, ethanol_supply_match.py.
 * Structure: problem -> the molecule -> policy gap (the ask) -> market ->
 * model -> financials -> risks -> landscape -> ask.
 * Output: docs/Isobutanol_Blending_Pitch.pptx */
const pptxgen = require("pptxgenjs");

const P = { dark: "0E3B2E", dark2: "16523F", amber: "E3A72F", green: "2E9E6B",
  red: "C0392B", ink: "1C2B27", mute: "5C6B66", bg: "FFFFFF", card: "F2F6F4", line: "D5E0DB" };
const FONT = "Calibri", HEAD = "Cambria";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "india-omc-fuel-fleet-model";
pres.title = "Bio-Isobutanol Blending — Investment Pitch";

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
s.addText("The Better Molecule", { x: 0.9, y: 1.8, w: 11.5, h: 1.1, fontFace: HEAD, fontSize: 50,
  bold: true, color: "FFFFFF", margin: 0 });
s.addText("Bio-isobutanol for petrol blending and aviation fuel — half of ethanol's mileage penalty, 25% more jet per tonne",
  { x: 0.9, y: 3.0, w: 11.3, h: 0.7, fontFace: FONT, fontSize: 19, color: P.amber, margin: 0 });
s.addText("Investment pitch · July 2026 · built on the Volume Dividend energy analysis, ICAO ATJ conversion factors and the DFPD/CareEdge capacity picture",
  { x: 0.9, y: 6.4, w: 11.5, h: 0.5, fontFace: FONT, fontSize: 12, color: "9DBFB2", margin: 0 });

/* ── 2. PROBLEM ───────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Two problems ethanol cannot solve",
  "India's blending programme is hitting a molecule limit, not a capacity limit");
[["The mileage wall", "Ethanol's −34%/L energy deficit is the whole Volume Dividend: E20 already costs drivers ₹22,700 cr/yr in extra litres, and E30 doubles it. Engines are calibrated for E20 — the octane offset is spent. Every further ethanol point is a bigger hidden levy.", P.card],
 ["The overcapacity trap", "~2,000 cr L of distillery capacity chasing ~1,100 cr L of E20 demand; only ~60% of offered ethanol absorbed; utilisation stuck at 65–75% for three years (CareEdge). More ethanol capacity is the last thing India needs.", P.card],
 ["And a third: aviation has no ethanol answer", "SAF mandates arrive from 2027. Ethanol-to-jet wastes carbon: 0.60 t distillate per tonne. The alcohol India has surplus of is the wrong alcohol for the market that is about to be created.", P.dark]]
.forEach(([h, d, fill], i) => {
  const x = 0.6 + i * 4.2;
  card(s, x, 1.8, 3.95, 3.9, fill);
  const dk = fill === P.dark;
  s.addText(h, { x: x + 0.2, y: 2.0, w: 3.55, h: 0.8, fontFace: FONT, fontSize: 15, bold: true,
    color: dk ? P.amber : P.dark, margin: 0 });
  s.addText(d, { x: x + 0.2, y: 2.85, w: 3.55, h: 2.7, fontFace: FONT, fontSize: 12,
    color: dk ? "E8F1EC" : P.ink, margin: 0 });
});
bullets(s, 0.6, 6.05, 12.1, 1.0, [
  "The same fermentation assets can make a different, better molecule — that is the entire thesis",
], { size: 13.5 });

/* ── 3. THE MOLECULE ──────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Isobutanol: a C4 alcohol that behaves like petrol",
  "Same sugar, same fermenters, different organism — and materially better fuel properties");
grid(s, [
  ["Property", "Ethanol", "Isobutanol", "Why it matters"],
  ["Energy, MJ/L", "21.1", "26.5", "+26% per litre"],
  ["Blend dilution at 20%", "−6.9%", "−3.5%", "HALF the mileage penalty"],
  ["ATJ / SAF yield (t per t)", "0.60", "0.75", "+25% more jet fuel"],
  ["Water miscible?", "yes", "no", "pipeline-shippable, no phase separation"],
  ["Blending vapour pressure", "raises RVP", "neutral / lowers", "easier summer-grade compliance"],
], 0, 1.7, [0.6, 3.5, 5.3, 7.1], [2.9, 1.8, 1.8, 5.65], 0.62, 3);
card(s, 0.6, 5.6, 5.9, 1.6, P.dark);
s.addText("IB20 delivers the same 20% renewable volume at 3.5% dilution instead of 6.9% — the consumer keeps half the energy ethanol takes away",
  { x: 0.85, y: 5.8, w: 5.4, h: 1.2, fontFace: FONT, fontSize: 13, color: "E8F1EC", margin: 0 });
card(s, 6.8, 5.6, 5.95, 1.6);
s.addText("Not a lab curiosity: Gevo and Butamax have run commercial retrofits abroad; the chemistry, the ASTM D7566 ATJ pathway and the engine data all exist. India has none.",
  { x: 7.05, y: 5.8, w: 5.45, h: 1.2, fontFace: FONT, fontSize: 13, color: P.ink, margin: 0 });

/* ── 4. THE POLICY GAP = THE ASK ──────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "The gap that stops everything: no price, no standard",
  "Ethanol has six administered slabs and a BIS blending standard. Isobutanol has neither.");
grid(s, [
  ["", "Ethanol", "Isobutanol"],
  ["Administered OMC price", "6 feedstock slabs (₹57.97 – ₹71.86/L)", "NONE"],
  ["BIS blending standard", "IS 15464 / IS 2796", "NONE"],
  ["Interest subvention (DFPD ISS)", "6%, 1,212 projects sanctioned", "NOT eligible"],
  ["Result", "1,970 cr L built", "zero litres"],
], 0, 1.7, [0.6, 4.2, 8.2], [3.6, 4.0, 4.55], 0.62, 4);
card(s, 0.6, 4.62, 5.9, 2.25, P.dark);
s.addText("The ask to policy", { x: 0.85, y: 4.78, w: 5.4, h: 0.4, fontFace: FONT, fontSize: 14,
  bold: true, color: P.amber, margin: 0 });
bullets(s, 0.85, 5.2, 5.4, 1.55, [
  "Price isobutanol on ENERGY, not litres: parity with the maize ethanol slab = ₹90.3/L. We ask ₹88 — below parity, so the OMC buys renewable energy cheaper than it does today",
], { size: 12.5, color: "E8F1EC" });
card(s, 6.8, 4.62, 5.95, 2.25, P.card);
s.addText("Why per-litre pricing kills it", { x: 7.05, y: 4.78, w: 5.4, h: 0.4, fontFace: FONT,
  fontSize: 14, bold: true, color: P.red, margin: 0 });
bullets(s, 7.05, 5.2, 5.45, 1.55, [
  "Isobutanol yields ~280 L/t of maize vs ethanol's ~400. Paid at ethanol's per-LITRE slab the margin is −₹9.58/L — a guaranteed loss. Energy-basis pricing is not a subsidy; it is the correct unit.",
], { size: 12.5 });

/* ── 5. BUSINESS MODEL ────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Business model: retrofit idle ethanol capacity",
  "100-KLPD grain distillery → 70 KLPD isobutanol · ₹80 cr retrofit · the overcapacity IS the opportunity");
const steps = [
  ["Idle ethanol asset", "utilisation 60–75%; allocation-starved"],
  ["Engineered organism", "C4 pathway in existing fermenters"],
  ["Decanter separation", "isobutanol splits from water — no azeotrope distillation"],
  ["Two markets", "petrol blending + ATJ/SAF offtake"],
];
steps.forEach(([h, d], i) => {
  const x = 0.6 + i * 3.15;
  card(s, x, 1.85, 2.9, 1.9, i === 3 ? P.dark : P.card);
  const dk = i === 3;
  s.addText(h, { x: x + 0.15, y: 2.02, w: 2.6, h: 0.6, fontFace: FONT, fontSize: 13.5, bold: true,
    color: dk ? P.amber : P.dark, margin: 0 });
  s.addText(d, { x: x + 0.15, y: 2.65, w: 2.6, h: 1.0, fontFace: FONT, fontSize: 11,
    color: dk ? "E8F1EC" : P.mute, margin: 0 });
  if (i < 3) s.addText("→", { x: x + 2.87, y: 2.4, w: 0.3, h: 0.5, fontFace: FONT, fontSize: 20,
    bold: true, color: P.amber, align: "center", margin: 0 });
});
card(s, 0.6, 4.15, 5.9, 2.75);
s.addText("Per-litre economics (₹/L)", { x: 0.85, y: 4.35, w: 5.4, h: 0.4, fontFace: FONT,
  fontSize: 14, bold: true, color: P.dark, margin: 0 });
bullets(s, 0.85, 4.8, 5.4, 2.0, [
  "Realisation 88.00 − maize 82.14 (₹23,000/t ÷ 280 L/t) + DDGS 18.70 − conversion 18.00",
  "= ₹6.56/L margin → EBITDA ₹13.6 cr on blending alone",
  "Conversion cost is higher than ethanol's (₹18 vs ₹13): separation is the price of a non-azeotropic alcohol",
], { size: 12 });
card(s, 6.8, 4.15, 5.95, 2.75, P.dark);
s.addText("…and then the SAF leg", { x: 7.05, y: 4.35, w: 5.4, h: 0.4, fontFace: FONT,
  fontSize: 14, bold: true, color: P.amber, margin: 0 });
bullets(s, 7.05, 4.8, 5.45, 2.0, [
  "Routing 30% of output to an ATJ offtaker at ₹115/L lifts blended realisation to ₹96/L",
  "Margin ₹14.66/L, EBITDA ₹30.5 cr — the same plant, a different customer",
  "India's SAF mandate (1–2% from 2027) creates the captive buyer",
], { size: 12, color: "E8F1EC" });

/* ── 6. FINANCIALS ────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Financials: blending alone is marginal — SAF makes it a business",
  "₹80 cr retrofit · 70:30 @ 9.5% · NO subvention assumed (isobutanol is not ISS-eligible)");
grid(s, [
  ["Output routed to ATJ/SAF", "Blended realisation ₹/L", "Margin ₹/L", "EBITDA ₹ cr", "Project IRR"],
  ["0% — blending only", "88.0", "6.56", "13.6", "13.8%"],
  ["30% — base case", "96.1", "14.66", "30.5", "33.9%"],
  ["50% — SAF-led", "101.5", "20.06", "41.7", "45.6%"],
], 0, 1.75, [0.6, 4.2, 6.6, 8.4, 10.2], [3.6, 2.4, 1.8, 1.8, 2.15], 0.62, 2);
s.addText("Sensitivity — project IRR (%): maize price × isobutanol realisation (blending only, no SAF)",
  { x: 0.6, y: 4.35, w: 9.0, h: 0.4, fontFace: FONT, fontSize: 13, bold: true, color: P.dark, margin: 0 });
grid(s, [
  ["Maize ₹/t", "₹80/L", "₹88/L (ask)", "₹96/L"],
  ["20,000", "21.1", "39.6", "56.4"],
  ["23,000 (base)", "loss", "13.8", "33.6"],
  ["26,000", "loss", "loss", "5.0"],
], 0, 4.8, [0.6, 2.9, 5.2, 7.5], [2.3, 2.3, 2.3, 2.3], 0.52);
card(s, 10.2, 4.35, 2.55, 2.5, P.dark);
s.addText("Read the 'loss' cells honestly: without energy-basis pricing AND cheap grain, blending-only isobutanol does not work. The SAF leg is what carries it.",
  { x: 10.4, y: 4.55, w: 2.15, h: 2.15, fontFace: FONT, fontSize: 11.5, color: "E8F1EC", margin: 0 });

/* ── 7. RISKS ─────────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Risks and mitigants", "This is a technology-and-policy bet — we say so plainly");
grid(s, [
  ["Risk", "Reality", "Mitigant"],
  ["Technology (the big one)", "No Indian bio-isobutanol plant operates; yield 280 L/t and ₹18/L conversion are the least certain numbers here", "Licence a proven organism (Gevo/Butamax-class); pilot train before full retrofit; capex staged on demonstrated yield"],
  ["No price slab", "Sold at ethanol's per-litre slab the margin is −₹9.58/L", "Energy-basis pricing is the pre-condition, not a hope: no notification, no capex"],
  ["No BIS standard", "IS 15464 covers ethanol only", "Standards ask filed alongside the price ask; ASTM D7566 + global engine data support it"],
  ["SAF timing", "The 1–2% mandate lands 2027; ATJ offtakes are nascent", "Blending-only case still positive (13.8%) at base — SAF is upside, not survival"],
  ["Feedstock", "Same maize exposure as any grain distillery", "Multi-feed front end retained; DDGS credit larger per litre than ethanol's"],
], 0, 1.7, [0.6, 2.5, 5.9], [1.9, 3.4, 6.85], 0.82);
bullets(s, 0.6, 6.65, 12.1, 0.6, [
  "Not claiming: ISS eligibility, carbon credits, or that this is as bankable as a molasses-to-grain conversion (it is not — it is the higher-return, higher-risk sibling)",
], { size: 11.5 });

/* ── 8. LANDSCAPE ─────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Landscape: proven abroad, absent in India",
  "The window is the gap between India's SAF mandate and its ethanol glut");
[["Technology holders", "Gevo (US) and Butamax (BP/DuPont JV) have operated commercial isobutanol retrofits of corn-ethanol plants — the exact play proposed here. Licensing, not invention, is the route in.", P.card],
 ["Indian adjacency", "Praj has an ATJ/SAF programme and builds the distilleries; IOCL and Indian Oil–LanzaJet activity signals OMC appetite for alcohol-to-jet; the 2027 SAF mandate is the demand anchor.", P.card],
 ["The opening", "India has 900+ cr L of idle distillery capacity, a maize-slab price that already tolerates ₹71.86/L alcohol, and no isobutanol at all. First mover sets the standard and the slab.", P.dark]]
.forEach(([h, d, fill], i) => {
  const x = 0.6 + i * 4.2;
  card(s, x, 1.8, 3.95, 3.7, fill);
  const dk = fill === P.dark;
  s.addText(h, { x: x + 0.2, y: 2.0, w: 3.55, h: 0.5, fontFace: FONT, fontSize: 15, bold: true,
    color: dk ? P.amber : P.dark, margin: 0 });
  s.addText(d, { x: x + 0.2, y: 2.55, w: 3.55, h: 2.8, fontFace: FONT, fontSize: 12,
    color: dk ? "E8F1EC" : P.ink, margin: 0 });
});
bullets(s, 0.6, 5.85, 12.1, 1.2, [
  "Fits the platform logic of the other pitches: CBG monetises waste carbon, multi-feed conversion monetises seasonality — isobutanol monetises the ethanol glut by turning surplus fermentation into a higher-value molecule",
], { size: 13 });

/* ── 9. ASK ───────────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.dark };
title(s, "The ask: one licensed pilot, gated on policy", null, true);
stat(s, 0.9, 1.7, 2.7, "₹80 cr", "retrofit (₹24 cr equity)", P.dark);
stat(s, 3.8, 1.7, 2.7, "23 kt/yr", "isobutanol from idle capacity", P.dark);
stat(s, 6.7, 1.7, 2.7, "33.9%", "project IRR at 30% SAF routing", P.dark);
stat(s, 9.6, 1.7, 2.7, "2 asks", "energy-basis slab + BIS standard", P.dark);
bullets(s, 0.9, 3.7, 11.5, 3.0, [
  "Gate 1 (policy): an energy-basis OMC price notification for isobutanol (₹88/L against the ₹90.3 parity) and a BIS blending specification — no notification, no capex. This is the pitch's honest precondition, and the reason nothing exists today",
  "Gate 2 (technology): licence a proven organism and demonstrate ≥280 L/t on Indian maize in a pilot train before the full ₹80 cr retrofit is drawn",
  "Then: one ATJ/SAF offtake for 30% of output; replicate across the idle grain-distillery fleet — the same 900+ cr L of stranded capacity the ethanol overcapacity analysis identifies",
  "Why back the harder molecule: it is the only route that raises blending WITHOUT raising the consumer's hidden levy, and the only alcohol that gives aviation 25% more fuel per tonne of Indian carbon",
], { size: 14.5, color: "FFFFFF", gap: 12 });
s.addText("Model & sensitivity: isobutanol_pitch_model.py · energy analysis: energy_blend_comparison.py · The Volume Dividend · github.com/herrrickshaw/india-omc-fuel-fleet-model",
  { x: 0.9, y: 6.9, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 11.5, color: "9DBFB2", margin: 0 });

pres.writeFile({ fileName: "docs/Isobutanol_Blending_Pitch.pptx" })
  .then(() => console.log("wrote docs/Isobutanol_Blending_Pitch.pptx"));
