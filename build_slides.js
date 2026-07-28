#!/usr/bin/env node
/* Slide deck for the Volume Dividend analysis — scenarios, proposed consumer
 * prices, government taxes, blend-more + SGST opportunity, CBG alternative.
 * Numbers from energy_blend_comparison.py, price_parity_scenarios.py,
 * cbg_satat_economics.py, ethanol_sgst_sweetspot.py.
 * Output: docs/Volume_Dividend_Slides.pptx */
const pptxgen = require("pptxgenjs");

const P = {                       // palette: petrol-green + grain amber + CBG green
  dark: "0E3B2E",                 // deep petrol green (dominant)
  dark2: "16523F",
  amber: "E3A72F",                // ethanol / grain
  green: "2E9E6B",                // CBG accent
  red: "C0392B",                  // consumer cost
  ink: "1C2B27",
  mute: "5C6B66",
  bg: "FFFFFF",
  card: "F2F6F4",
  line: "D5E0DB",
};
const FONT = "Calibri", HEAD = "Cambria";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";      // 13.33 x 7.5
pres.author = "india-omc-fuel-fleet-model";
pres.title = "The Volume Dividend";

const title = (s, t, sub, dark = false) => {
  s.addText(t, { x: 0.6, y: 0.35, w: 12.1, h: 0.75, fontFace: HEAD, fontSize: 30, bold: true,
    color: dark ? "FFFFFF" : P.dark, margin: 0 });
  if (sub) s.addText(sub, { x: 0.6, y: 1.02, w: 12.1, h: 0.4, fontFace: FONT, fontSize: 13,
    color: dark ? "CFE3DA" : P.mute, margin: 0 });
};
const card = (s, x, y, w, h, fill = P.card) =>
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: fill }, rectRadius: 0.08,
    line: { color: P.line, width: 0.75 } });
const stat = (s, x, y, w, big, label, color, small) => {
  card(s, x, y, w, 1.55);
  s.addText(big, { x: x + 0.15, y: y + 0.12, w: w - 0.3, h: 0.75, fontFace: HEAD, fontSize: 27,
    bold: true, color, align: "center", margin: 0 });
  s.addText(label, { x: x + 0.15, y: y + 0.88, w: w - 0.3, h: 0.58, fontFace: FONT,
    fontSize: small || 11.5, color: P.mute, align: "center", margin: 0 });
};
const bullets = (s, x, y, w, h, items, opts = {}) =>
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: { code: "2022", indent: 14 },
    breakLine: i < items.length - 1, paraSpaceAfter: opts.gap ?? 8 } })),
    { x, y, w, h, fontFace: FONT, fontSize: opts.size ?? 14, color: opts.color ?? P.ink,
      valign: "top", margin: 0 });

/* ── 1. TITLE ─────────────────────────────────────────────────────────── */
let s = pres.addSlide();
s.background = { color: P.dark };
s.addText("The Volume Dividend", { x: 0.9, y: 2.0, w: 11.5, h: 1.2, fontFace: HEAD,
  fontSize: 54, bold: true, color: "FFFFFF", margin: 0 });
s.addText("Ethanol & biodiesel blending, honest pump prices, state taxation — and the CBG alternative",
  { x: 0.9, y: 3.25, w: 11.0, h: 0.6, fontFace: FONT, fontSize: 20, color: P.amber, margin: 0 });
s.addText("India · FY 2024-25 volumes · July 2026 prices · SIAM/ARAI FE anchor  |  repos: india-omc-fuel-fleet-model · vehicle_fuel_mileage",
  { x: 0.9, y: 6.4, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 12, color: "9DBFB2", margin: 0 });

/* ── 2. THE PHYSICS ───────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "The physics: a litre is not a litre", "Lower heating value per litre (liquids) and per kg (gases)");
s.addChart(pres.ChartType.bar, [{
  name: "MJ per litre",
  labels: ["Diesel", "B20", "Petrol E0", "E10", "E20", "E30", "Isobutanol", "Ethanol"],
  values: [35.7, 35.1, 32.1, 31.0, 29.9, 28.8, 26.5, 21.1],
}], {
  x: 0.6, y: 1.65, w: 7.6, h: 5.3, barDir: "col",
  chartColors: [P.dark2], showLegend: false, showTitle: false,
  showValue: true, dataLabelPosition: "outEnd", dataLabelColor: P.ink, dataLabelFontSize: 11,
  catAxisLabelColor: P.ink, catAxisLabelFontSize: 11, valAxisLabelColor: P.mute,
  valAxisMaxVal: 40, valGridLine: { color: P.line, size: 0.5 }, catGridLine: { style: "none" },
});
card(s, 8.5, 1.65, 4.25, 5.3, P.card);
s.addText("Sold per kilogram", { x: 8.75, y: 1.9, w: 3.8, h: 0.35, fontFace: FONT, fontSize: 13,
  bold: true, color: P.mute, margin: 0 });
s.addText("CNG  47.5 MJ/kg", { x: 8.75, y: 2.3, w: 3.8, h: 0.5, fontFace: HEAD, fontSize: 22,
  bold: true, color: P.dark, margin: 0 });
s.addText("CBG  46.5 MJ/kg", { x: 8.75, y: 2.85, w: 3.8, h: 0.5, fontFace: HEAD, fontSize: 22,
  bold: true, color: P.green, margin: 0 });
bullets(s, 8.75, 3.6, 3.8, 3.2, [
  "Ethanol carries 34% less energy per litre than petrol; isobutanol only 17% less",
  "Every ethanol blend step dilutes the litre the customer pays for",
  "CBG at IS 16087 spec is at CNG parity per kg — pure methane is above it (50 MJ/kg)",
], { size: 13 });

/* ── 3. THE MECHANISM ─────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "The mechanism: dilution becomes revenue", "Why every per-litre stakeholder quietly gains from blending");
const steps = [
  ["Blend 20% ethanol", "energy/litre −6.8%"],
  ["Mileage falls", "−4% real-world (SIAM/ARAI)"],
  ["Same km, more litres", "+4.2% volume through pumps"],
  ["Per-litre levies collect", "excise ₹19.90 · VAT ~₹19.5 · dealer ₹4.1 · OMC ₹3.5"],
];
steps.forEach(([h, d], i) => {
  const x = 0.6 + i * 3.15;
  card(s, x, 1.9, 2.85, 1.7, i === 3 ? P.dark : P.card);
  s.addText(h, { x: x + 0.15, y: 2.02, w: 2.55, h: 0.6, fontFace: FONT, fontSize: 15, bold: true,
    color: i === 3 ? "FFFFFF" : P.dark, margin: 0 });
  s.addText(d, { x: x + 0.15, y: 2.62, w: 2.55, h: 0.85, fontFace: FONT, fontSize: 12,
    color: i === 3 ? "CFE3DA" : P.mute, margin: 0 });
  if (i < 3) s.addText("→", { x: x + 2.82, y: 2.35, w: 0.4, h: 0.6, fontFace: FONT, fontSize: 24,
    bold: true, color: P.amber, align: "center", margin: 0 });
});
s.addText("₹22,703 cr", { x: 0.6, y: 4.15, w: 6.0, h: 1.1, fontFace: HEAD, fontSize: 56, bold: true,
  color: P.red, margin: 0 });
s.addText("extra consumer fuel spend per year at E20 from the volume effect alone —\nat an unchanged price per litre. The pump board never shows it.",
  { x: 0.6, y: 5.3, w: 6.2, h: 0.9, fontFace: FONT, fontSize: 14, color: P.ink, margin: 0 });
card(s, 7.3, 4.15, 5.45, 2.35);
bullets(s, 7.55, 4.4, 5.0, 2.0, [
  "A 20 km/L hatchback buys +21 L/yr ≈ ₹2,188/yr extra on E20",
  "Hidden levy of 4.2% on every km driven — regressive, invisible",
  "The FY23 ₹2/L penalty on unblended petrol widens the gap further",
], { size: 13.5 });

/* ── 4. WHO COLLECTS TODAY ────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Who collects the E20 volume dividend today", "₹ crore per year on the 54-billion-litre petrol pool (2.16 bn extra litres)");
stat(s, 0.6, 1.8, 2.85, "₹4,303 cr", "Centre — excise ₹19.90/L", P.dark);
stat(s, 3.65, 1.8, 2.85, "₹4,216 cr", "States — VAT ~₹19.5/L", P.dark);
stat(s, 6.7, 1.8, 2.85, "₹886 cr", "Dealers — commission ₹4.1/L", P.amber);
stat(s, 9.75, 1.8, 2.85, "₹757 cr", "OMCs — margin ₹3.5/L", P.amber);
card(s, 0.6, 3.75, 12.0, 1.5, P.dark);
s.addText("Paid entirely by the consumer:  ₹22,703 cr/yr", { x: 0.9, y: 3.95, w: 11.4, h: 0.6,
  fontFace: HEAD, fontSize: 24, bold: true, color: "FFFFFF", margin: 0 });
s.addText("The exchequer + trade gain IS the consumer's loss, litre for litre. This is additive to the separate substitution effect (states forgo VAT on the ethanol fraction).",
  { x: 0.9, y: 4.55, w: 11.4, h: 0.5, fontFace: FONT, fontSize: 13, color: "CFE3DA", margin: 0 });
bullets(s, 0.6, 5.6, 12.0, 1.5, [
  "Dealer commission and OMC margin are volume-linked — network economics quietly improve as blends rise (per-RO throughput has been falling on network dilution; blending offsets it)",
  "OMC-margin figure reconciles exactly with the OMC retail-profitability model (₹757 cr at E20)",
], { size: 13.5 });

/* ── 5. BLEND MORE: THE WALK ──────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Blending more: E25/E30 and diesel B10–B20", "Extra litres pulled through pumps for the same distance (bn L/yr)");
s.addChart(pres.ChartType.bar, [{
  name: "Extra bn L/yr",
  labels: ["E20", "E25", "E30", "B7", "B10", "B15", "B20"],
  values: [2.16, 3.02, 3.91, 0.64, 0.92, 1.38, 1.85],
}], {
  x: 0.6, y: 1.65, w: 7.4, h: 5.3, barDir: "col",
  chartColors: [P.amber], showLegend: false, showTitle: false,
  showValue: true, dataLabelPosition: "outEnd", dataLabelColor: P.ink, dataLabelFontSize: 12,
  catAxisLabelColor: P.ink, valAxisLabelColor: P.mute,
  valGridLine: { color: P.line, size: 0.5 }, catGridLine: { style: "none" },
});
card(s, 8.3, 1.65, 4.45, 5.3);
s.addText("The E20→E30 walk (vs today)", { x: 8.55, y: 1.9, w: 4.0, h: 0.4, fontFace: FONT,
  fontSize: 14, bold: true, color: P.dark, margin: 0 });
bullets(s, 8.55, 2.35, 3.95, 4.5, [
  "E30 adds +1.75 bn L/yr beyond E20: +₹18,300 cr consumer, +₹6,900 cr excise+VAT, +₹715 cr dealer commission",
  "Engines are calibrated for E20 — the octane-recovery offset is spent; E25–E30 pass through closer to raw energy loss",
  "Diesel pool is 2× petrol: B20 pulls 1.85 bn L despite only −1.7% dilution; cost lands on freight & inflation",
  "Reality check: biodiesel was <1% in FY24-25; NBP targets B5 by 2030",
], { size: 12.5, gap: 10 });

/* ── 6. CONSUMER: PROPOSED PRICES ─────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "For the consumer: parity prices that give the mileage back",
  "Honest pricing rule  P(blend) = P(E0) × (1 − mileage drop)   ·   petrol at ₹105/L today");
[["E20", "₹100.80", "−₹4.20/L", "4.0% drop"], ["E25", "₹99.22", "−₹5.78/L", "5.5% drop"],
 ["E27", "₹98.44", "−₹6.56/L", "6.25% drop"], ["E30", "₹97.65", "−₹7.35/L", "7.0% drop"]]
.forEach(([b, pr, d, dr], i) => {
  const x = 0.6 + i * 3.15;
  card(s, x, 1.85, 2.85, 2.5, i === 2 ? P.dark : P.card);
  const fg = i === 2 ? "FFFFFF" : P.dark, sub = i === 2 ? "CFE3DA" : P.mute;
  s.addText(b, { x: x + 0.15, y: 2.0, w: 2.55, h: 0.45, fontFace: FONT, fontSize: 17, bold: true,
    color: i === 2 ? P.amber : P.amber, margin: 0 });
  s.addText(pr, { x: x + 0.15, y: 2.45, w: 2.55, h: 0.8, fontFace: HEAD, fontSize: 33, bold: true,
    color: fg, margin: 0 });
  s.addText(`${d} · ${dr}`, { x: x + 0.15, y: 3.3, w: 2.55, h: 0.4, fontFace: FONT, fontSize: 12.5,
    color: sub, margin: 0 });
  if (i === 2) s.addText("proposed sweet spot", { x: x + 0.15, y: 3.75, w: 2.55, h: 0.4,
    fontFace: FONT, fontSize: 11.5, italic: true, color: P.amber, margin: 0 });
});
bullets(s, 0.6, 4.8, 12.0, 2.3, [
  "A parity-priced blend makes cost-per-km identical to unblended petrol — the consumer is made whole, the pump board tells the truth",
  "Restores the consumer's ₹22,700–41,000 cr/yr; the hatchback owner gets the ₹2,188/yr back",
  "E27 mirrors Brazil's ceiling for non-flex engines — the highest blend today's fleet tolerates as E20+ vehicles diffuse",
], { size: 14, gap: 10 });

/* ── 7. GOVERNMENT: THE FUNDING TEST ──────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "For the government: parity is already funded", "₹/L per blended litre — tax break embedded in the blend vs the discount parity needs");
s.addChart(pres.ChartType.bar, [
  { name: "Embedded tax headroom", labels: ["E20", "E25", "E27", "E30"], values: [6.46, 8.07, 8.72, 9.69] },
  { name: "Parity discount needed", labels: ["E20", "E25", "E27", "E30"], values: [4.20, 5.78, 6.56, 7.35] },
], {
  x: 0.6, y: 1.65, w: 7.4, h: 5.3, barDir: "col", barGapWidthPct: 60,
  chartColors: [P.dark2, P.amber], showLegend: true, legendPos: "b", legendColor: P.ink,
  showTitle: false, showValue: true, dataLabelPosition: "outEnd", dataLabelColor: P.ink,
  dataLabelFontSize: 11, catAxisLabelColor: P.ink, valAxisLabelColor: P.mute,
  valGridLine: { color: P.line, size: 0.5 }, catGridLine: { style: "none" },
});
card(s, 8.3, 1.65, 4.45, 5.3);
s.addText("Four scenarios tested", { x: 8.55, y: 1.9, w: 4.0, h: 0.4, fontFace: FONT, fontSize: 14,
  bold: true, color: P.dark, margin: 0 });
bullets(s, 8.55, 2.35, 3.95, 4.5, [
  "S1 pass-through (works, 1.3–1.5×): the ethanol molecule escapes excise + VAT, pays only 5% GST — ₹6.5–9.7/L already sits in the price build-up",
  "S2/S3 duty cuts: possible but costs centre/states ₹22,700–41,000 cr/yr",
  "S4 cheaper ethanol: FAILS — needs ₹37–41/L vs ₹57.97 cheapest feedstock slab; grain mandi prices set the floor (maize slab ₹71.86 is the E30 marginal source)",
  "No new subsidy in S1 — it only stops a windfall the blend walk creates",
], { size: 12.5, gap: 10 });

/* ── 8. INTRODUCE SGST ────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Introduce a state SGST on ethanol — price-neutral new revenue",
  "States lose petrol VAT on every ethanol litre; a 1–5% ethanol SGST claws it back inside the fiscal space");
s.addChart(pres.ChartType.bar, [{
  name: "5% ethanol SGST revenue (₹ cr/yr)",
  labels: ["E20", "E22", "E25", "E27", "E30"],
  values: [3243, 3662, 4324, 4787, 5513],
}], {
  x: 0.6, y: 1.75, w: 7.4, h: 5.1, barDir: "col",
  chartColors: [P.green], showLegend: false, showTitle: false,
  showValue: true, dataLabelPosition: "outEnd", dataLabelColor: P.ink, dataLabelFontSize: 12,
  catAxisLabelColor: P.ink, valAxisLabelColor: P.mute,
  valGridLine: { color: P.line, size: 0.5 }, catGridLine: { style: "none" },
});
card(s, 8.3, 1.75, 4.45, 5.1);
bullets(s, 8.55, 2.0, 3.95, 4.6, [
  "Rate sets the recovery %, blend sets the ₹: 5% recovers ~18% of foregone petrol-VAT at any blend",
  "A 5% levy costs ₹3.0–3.4/L of ethanol — fits inside the ₹7–15/L fiscal space at every blend, so the pump price never moves",
  "Revenue rises on both axes: E20→E30 grows the ethanol base 50%",
  "Sweet spot: E27 @ 5% ≈ ₹4,787 cr/yr of new state revenue at zero consumer cost",
], { size: 13, gap: 10 });

/* ── 9. THE GRAND BARGAIN + CBG ───────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "The grand bargain: blend more, charge less, tax smarter",
  "E27 with parity pricing + 5% ethanol SGST — everyone still fits inside the embedded headroom (₹/L of blended petrol)");
card(s, 0.6, 1.8, 7.6, 3.3, P.card);
const bars = [["Embedded headroom at E27", 8.72, P.dark2], ["Consumer parity discount", -6.56, P.red],
              ["States: 5% ethanol SGST", -0.89, P.green], ["Slack remaining", 1.27, P.amber]];
bars.forEach(([l, v, c], i) => {
  const y = 2.05 + i * 0.75;
  s.addText(l, { x: 0.85, y, w: 3.1, h: 0.5, fontFace: FONT, fontSize: 13, color: P.ink,
    valign: "middle", margin: 0 });
  const w = Math.abs(v) * 0.42;
  s.addShape(pres.ShapeType.rect, { x: 4.05, y: y + 0.06, w, h: 0.38, fill: { color: c } });
  s.addText(`${v > 0 ? "+" : "−"}₹${Math.abs(v).toFixed(2)}`, { x: 4.05 + w + 0.1, y, w: 1.2, h: 0.5,
    fontFace: FONT, fontSize: 13, bold: true, color: c, valign: "middle", margin: 0 });
});
bullets(s, 0.85, 5.35, 7.2, 1.7, [
  "Consumer: ₹98.44/L and honest cost-per-km  ·  States: +₹4,787 cr/yr SGST  ·  Centre: keeps full excise on a bigger blended pool  ·  Farmers: 35% more ethanol offtake",
], { size: 13.5 });
card(s, 8.5, 1.8, 4.25, 5.25, P.dark);
s.addText("…and let CBG do the gas side", { x: 8.75, y: 2.0, w: 3.8, h: 0.45, fontFace: FONT,
  fontSize: 15, bold: true, color: P.amber, margin: 0 });
bullets(s, 8.75, 2.5, 3.75, 4.4, [
  "Renewable MJ via SATAT CBG: ₹1.16 vs ethanol's ₹2.94 — 2.5× cheaper",
  "Sold per kg at CNG parity: zero mileage loss, zero hidden levy",
  "CBO at 5% moves the CNG pump just ₹0.59/kg (~0.8%), mileage −0.1%",
  "Undercuts imported LNG above ~$14.8/MMBtu; subsidy sits on-budget (SATAT + GOBARdhan), not in the fuel gauge",
], { size: 12.5, color: "E8F1EC", gap: 10 });

/* ── 10. SUPPLY CHECK ─────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Supply check: higher blends CURE the distillery overcapacity",
  "Capacity utilisation = (fuel + non-fuel ethanol demand) ÷ capacity · CareEdge Ratings May-2026 supply data");
s.addChart(pres.ChartType.bar, [
  { name: "Utilisation on 2,000 cr L (today)", labels: ["E20", "E25", "E27", "E30"], values: [70, 85, 91, 100] },
  { name: "On 2,400 cr L (FY27)", labels: ["E20", "E25", "E27", "E30"], values: [59, 71, 76, 83] },
], {
  x: 0.6, y: 1.65, w: 7.4, h: 5.3, barDir: "col", barGapWidthPct: 60,
  chartColors: [P.dark2, P.green], showLegend: true, legendPos: "b", legendColor: P.ink,
  showTitle: false, showValue: true, dataLabelPosition: "outEnd", dataLabelColor: P.ink,
  dataLabelFontSize: 11, catAxisLabelColor: P.ink, valAxisLabelColor: P.mute, valAxisMaxVal: 110,
  valGridLine: { color: P.line, size: 0.5 }, catGridLine: { style: "none" },
});
card(s, 8.3, 1.65, 4.45, 5.3);
bullets(s, 8.55, 1.9, 3.95, 4.9, [
  "Installed ~2,000 cr L (+400 by FY27); at E20 only ~60% of offered ethanol is absorbed — CareEdge sees 65–75% utilisation for 3 years",
  "E27 lifts utilisation to 76% — top of the band, absorbs Maharashtra's +277 cr L surplus, zero new construction",
  "Coop-mill scheme ≠ capacity: of ₹10,005 cr NCDC gave 56 mills, 96.5% is working capital; the ₹251 cr ethanol tranche ≈ 9.7 cr L/yr (0.5% of installed)",
  "FCI rice leg ~211 cr L (3.9 blend pts, Jul-2023 suspension risk) — the E27/E30 increment rides on open-market maize, the dearest slab",
  "Demand-grown E30 (FY31, 2,173 cr L) hits ~104% — only then does the 4,530 cr L DFPD sanction register need to build",
], { size: 11.5, gap: 8 });

/* ── 11. RON95 ────────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "The RON95 dividend: octane the consumer never sees",
  "RON = knock resistance (regular petrol 91, premium 95) · ethanol blending RON ~112 · BOB = the petrol base before blending");
const ronRows = [["Blend", "BOB needed if pump stays RON 91", "Pump RON if BOB stays 91", "Octane credit ₹/L*"],
  ["E10", "88.7", "93.1", "4.7"], ["E20", "85.7", "95.2", "9.5"],
  ["E25", "84.0", "96.2", "11.8"], ["E27", "83.2", "96.7", "12.8"], ["E30", "82.0", "97.3", "14.2"]];
ronRows.forEach((r, i) => {
  const y = 1.75 + i * 0.62, head = i === 0;
  r.forEach((t, j) => {
    const x = [0.6, 1.9, 5.0, 8.1][j], w = [1.2, 3.0, 3.0, 1.7][j];
    s.addShape(pres.ShapeType.rect, { x, y, w, h: 0.56,
      fill: { color: head ? P.dark : i % 2 ? P.card : "FFFFFF" }, line: { color: P.line, width: 0.75 } });
    s.addText(t, { x: x + 0.08, y, w: w - 0.16, h: 0.56, fontFace: FONT, fontSize: head ? 11.5 : 13,
      bold: head || j === 0, color: head ? "FFFFFF" : P.ink, valign: "middle",
      align: j === 0 ? "left" : "center", margin: 0 });
  });
});
s.addText("*valued at the retail XP95 spread (~₹2.25/RON point) — a willingness-to-pay ceiling; refining cost is lower (₹0.3–0.8/L per 4–5 points)",
  { x: 0.6, y: 5.6, w: 9.2, h: 0.4, fontFace: FONT, fontSize: 10.5, italic: true, color: P.mute, margin: 0 });
card(s, 10.1, 1.75, 2.65, 3.7, P.dark);
s.addText("net E20 penalty on a RON95-calibrated engine", { x: 10.3, y: 1.95, w: 2.25, h: 0.85,
  fontFace: FONT, fontSize: 11.5, color: "CFE3DA", margin: 0 });
s.addText("−1.8%", { x: 10.3, y: 2.8, w: 2.25, h: 0.9, fontFace: HEAD, fontSize: 40, bold: true,
  color: P.amber, margin: 0 });
s.addText("−4% energy +2.2% from CR 10.5→12", { x: 10.3, y: 3.75, w: 2.25, h: 0.8, fontFace: FONT,
  fontSize: 11, color: "CFE3DA", margin: 0 });
bullets(s, 0.6, 6.15, 12.1, 1.2, [
  "Today India blends to pump RON 91 → refiners quietly drop the blendstock to 85.7 and keep the saving. Holding the blendstock at 91 instead makes E20 a FREE national RON95 fuel — Brazil's E27 playbook: parity pricing compensates today's fleet, RON95 + high-compression E20+ engines erase the penalty as the fleet turns over (~2.9 cr new vehicles/yr)",
], { size: 12.5 });

/* ── 12. CBG INCENTIVE STACK ──────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "The CBG incentive stack: every leg de-risked, all on-budget",
  "GOBARdhan important-circulars register (70 circulars, ~half dated 2025-26) · full detail in the paper's Annex A");
const stack = [
  ["Offtake & pricing", "SATAT assured ₹54/kg ex-plant (2022, rev. 2025) · CGD synchronization (2021→2026) · CBO mandate 1%→5% (2024)"],
  ["Capital support", "MNRE Waste-to-Energy CFA (2022, rev. 2025) · SBM 2.0 bio-methanation VGF (2025) · SASCI state capital assistance (2026)"],
  ["Infrastructure & feedstock", "DPI pipeline-connectivity scheme (2024→2026) · biomass aggregation machinery (2024-25) · crop-residue channelling (2023-24)"],
  ["Fertiliser (digestate) leg", "FCO Schedule VIII 'Organic Carbon Enhancer' (2025, gazette-verified) · Bulk Sale Notifications I–VII · MDA ~₹1,500/t · ICAR practice guide"],
  ["Finance access", "RBI Priority Sector Lending (2020) · Agriculture Infrastructure Fund (2020/23) · AHIDF (2022)"],
  ["Tax & carbon", "5% GST · excise exemption on CBG-blended CNG (2023) · carbon-credit eligibility (MoEFCC 2023)"],
  ["Standards & easing", "IS 16087:2025 (= legal CNG fungibility) · MoRTH bio-CNG fuel notification (2015) · CPCB re-categorisation (2021/25)"],
  ["State layer", "UP · Bihar · Rajasthan · AP · Assam · MP · Chhattisgarh (Jul-2026) + MoPNG Model State CBG Policy (Apr-2026)"],
];
stack.forEach(([h, d], i) => {
  const col = i % 2, row = Math.floor(i / 2);
  const x = 0.6 + col * 6.2, y = 1.7 + row * 1.28;
  card(s, x, y, 5.95, 1.16, row === 1 && col === 1 ? P.dark : P.card);
  const hl = row === 1 && col === 1;
  s.addText(h, { x: x + 0.18, y: y + 0.07, w: 5.6, h: 0.34, fontFace: FONT, fontSize: 13, bold: true,
    color: hl ? P.amber : P.dark, margin: 0 });
  s.addText(d, { x: x + 0.18, y: y + 0.42, w: 5.6, h: 0.7, fontFace: FONT, fontSize: 10.5,
    color: hl ? "E8F1EC" : P.mute, margin: 0 });
});
card(s, 0.6, 6.8, 12.15, 0.6, P.dark);
s.addText("Feedstock, capex, debt, gas revenue, digestate revenue, carbon revenue — all supported ON-BUDGET and ex-plant: the structural opposite of ethanol's consumer-funded volume dividend.",
  { x: 0.85, y: 6.83, w: 11.7, h: 0.54, fontFace: FONT, fontSize: 12, bold: true, color: "FFFFFF",
    valign: "middle", margin: 0 });

/* ── 13. DME IN LPG ───────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "DME in LPG: the fourth quadrant — the dividend inverts",
  "DME 28.8 vs LPG 45.8 MJ/kg (−37%) · LERC-measured −5.26% at DME20 (IS 4246) · BIS IS 18698:2024 caps blends at 20%");
const quad = [["Blend", "Dilution", "Fiscal status", "Volume effect lands on"],
  ["Ethanol in petrol", "−34% /L", "heavily taxed", "consumer pays; exchequer + trade collect"],
  ["Biodiesel in diesel", "−8% /L", "taxed", "mild; cascades into freight"],
  ["CBG in CNG", "~0% /kg", "lightly taxed", "nobody — the honest blend"],
  ["DME in LPG", "−37% /kg", "SUBSIDISED", "consumer AND exchequer pay"]];
quad.forEach((r, i) => {
  const y = 1.75 + i * 0.72, head = i === 0, hot = i === 4;
  r.forEach((t, j) => {
    const x = [0.6, 2.9, 4.4, 6.4][j], w = [2.3, 1.5, 2.0, 3.3][j];
    s.addShape(pres.ShapeType.rect, { x, y, w, h: 0.66,
      fill: { color: head ? P.dark : hot ? P.dark2 : i % 2 ? P.card : "FFFFFF" },
      line: { color: P.line, width: 0.75 } });
    s.addText(t, { x: x + 0.08, y, w: w - 0.16, h: 0.66, fontFace: FONT, fontSize: head ? 11.5 : 12,
      bold: head || j === 0, color: (head || hot) ? "FFFFFF" : P.ink, valign: "middle",
      align: j === 0 ? "left" : "center", margin: 0 });
  });
});
card(s, 10.1, 1.75, 2.65, 3.55, P.dark);
s.addText("DME20 at unchanged cylinder price", { x: 10.3, y: 1.95, w: 2.25, h: 0.7, fontFace: FONT,
  fontSize: 11.5, color: "CFE3DA", margin: 0 });
s.addText("+₹312/yr", { x: 10.3, y: 2.65, w: 2.25, h: 0.7, fontFace: HEAD, fontSize: 30, bold: true,
  color: P.red, margin: 0 });
s.addText("per household — plus ₹1,201 cr/yr extra PMUY subsidy. Parity cylinder = ₹761 vs ₹803",
  { x: 10.3, y: 3.4, w: 2.25, h: 1.7, fontFace: FONT, fontSize: 11, color: "CFE3DA", margin: 0 });
bullets(s, 0.6, 5.6, 12.1, 1.7, [
  "Ethanol's dilution EARNS the exchequer excise; DME's dilution BILLS it — a hidden levy on the Ujjwala merit good with the subsidy bill co-paying (₹9,325 cr consumer + ₹1,201 cr PMUY at DME20 on the full pool)",
  "Economics don't clear: energy-neutral DME must price ≤₹32.7/kg but methanol-route feedstock alone is ₹33.6/kg — import substitution is honest only on coal/bio-DME, and DME20 needs 6.3 MMT/yr (~6× India's methanol output)",
  "Guardrails if pursued: energy-parity cylinder pricing + domestic-carbon DME only",
], { size: 12, gap: 8 });

/* ── 14. CLOSING ──────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.dark };
title(s, "What honest blending policy looks like", null, true);
bullets(s, 0.9, 1.6, 11.5, 4.6, [
  "Price blends for parity: E20 at ₹100.80, stepping to ₹98.44 at E27 — funded by passing through the tax break already embedded (1.3–1.5× coverage; no new subsidy)",
  "Give states a 1–5% SGST on ethanol — up to ₹4,787 cr/yr at E27, price-neutral, ending their structural objection to higher blends",
  "Walk the blend E20 → E27 with the fleet, not ahead of it (Brazil precedent); label pumps with energy content, not just blend %",
  "Label E20+ as RON95 (hold the blendstock at 91) — the free octane lets high-compression engines shrink the mileage penalty to ~−1.8% as the fleet turns over",
  "Keep diesel at B5–B7 until supply and OEM warranties mature — the pool is too big for silent dilution",
  "Scale CBG on the gas side: CNG-parity energy per kg means decarbonisation with no volume dividend to hide — the fiscally honest blend",
], { size: 17, color: "FFFFFF", gap: 16 });
s.addText("Full paper: The Volume Dividend (docx/pdf) · github.com/herrrickshaw/india-omc-fuel-fleet-model · vehicle_fuel_mileage",
  { x: 0.9, y: 6.6, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 12, color: "9DBFB2", margin: 0 });

pres.writeFile({ fileName: "docs/Volume_Dividend_Slides.pptx" })
  .then(() => console.log("wrote docs/Volume_Dividend_Slides.pptx"));
