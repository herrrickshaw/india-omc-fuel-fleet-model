#!/usr/bin/env node
/* Distillery multi-feed conversion pitch. Numbers from distillery_conversion_model.py,
 * ethanol_supply_match.py, price_parity_scenarios.py (slabs), digital-twin layer 24d.
 * Structure: problem -> opportunity -> moat -> the conversion -> financials -> risks
 * -> landscape -> ask. Output: docs/Distillery_MultiFeed_Pitch.pptx */
const pptxgen = require("pptxgenjs");

const P = { dark: "0E3B2E", dark2: "16523F", amber: "E3A72F", green: "2E9E6B",
  red: "C0392B", ink: "1C2B27", mute: "5C6B66", bg: "FFFFFF", card: "F2F6F4", line: "D5E0DB" };
const FONT = "Calibri", HEAD = "Cambria";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "india-omc-fuel-fleet-model";
pres.title = "Multi-Feed Distillery Conversion — Investment Pitch";

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
const grid = (s, rows, x, y, colX, colW, rowH = 0.55) => rows.forEach((r, i) => {
  const yy = y + i * rowH, head = i === 0;
  r.forEach((t, j) => {
    s.addShape(pres.ShapeType.rect, { x: colX[j], y: yy, w: colW[j], h: rowH - 0.02,
      fill: { color: head ? P.dark : i % 2 ? P.card : "FFFFFF" }, line: { color: P.line, width: 0.75 } });
    s.addText(t, { x: colX[j] + 0.08, y: yy, w: colW[j] - 0.16, h: rowH - 0.02, fontFace: FONT,
      fontSize: head ? 11.5 : 12.5, bold: head || j === 0, color: head ? "FFFFFF" : P.ink,
      valign: "middle", align: j === 0 ? "left" : "center", margin: 0 });
  });
});

/* ── 1. TITLE ─────────────────────────────────────────────────────────── */
let s = pres.addSlide(); s.background = { color: P.dark };
s.addText("From Molasses to Multi-Feed", { x: 0.9, y: 1.8, w: 11.5, h: 1.1, fontFace: HEAD,
  fontSize: 48, bold: true, color: "FFFFFF", margin: 0 });
s.addText("Converting seasonal sugar-mill distilleries into 330-day multi-feedstock ethanol plants — the highest-IRR brownfield play in Indian bioenergy",
  { x: 0.9, y: 3.0, w: 11.3, h: 0.9, fontFace: FONT, fontSize: 19, color: P.amber, margin: 0 });
s.addText("Investment pitch · July 2026 · built on the Volume Dividend research stack (supply match, OMC price slabs, DFPD register, UP capacity mapping)",
  { x: 0.9, y: 6.4, w: 11.5, h: 0.5, fontFace: FONT, fontSize: 12, color: "9DBFB2", margin: 0 });

/* ── 2. PROBLEM ───────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "The single-feed trap", "Why molasses-only distilleries are the casualties of the consolidation phase");
[["Seasonal by design", "A molasses distillery runs on the cane crush: ~180 days of feedstock. Half the year the fermenters sit idle while debt service runs 365 days.", P.card],
 ["Overcapacity punishes the inflexible", "OMCs absorb only ~60% of offered ethanol (CareEdge). Utilisation stuck at 65–75% for 3 years hits single-feedstock plants first — they cannot chase the slab or the season.", P.card],
 ["Concentration risk everywhere", "One feedstock = one price (cane politics set molasses), one policy lever (sugar-diversion caps), one failure mode. The Jul-2023 FCI rice suspension showed how fast a feedstock leg can vanish.", P.dark]]
.forEach(([h, d, fill], i) => {
  const x = 0.6 + i * 4.2;
  card(s, x, 1.8, 3.95, 3.5, fill);
  const dk = fill === P.dark;
  s.addText(h, { x: x + 0.2, y: 2.0, w: 3.55, h: 0.75, fontFace: FONT, fontSize: 15.5, bold: true,
    color: dk ? P.amber : P.dark, margin: 0 });
  s.addText(d, { x: x + 0.2, y: 2.8, w: 3.55, h: 2.3, fontFace: FONT, fontSize: 12.5,
    color: dk ? "E8F1EC" : P.ink, margin: 0 });
});
bullets(s, 0.6, 5.7, 12.1, 1.3, [
  "India's 229 functional cooperative sugar mills are the extreme case: molasses-bound, working-capital-starved (NCDC's ₹10,005 cr scheme is 96.5% working capital), and structurally unable to fund conversion themselves",
], { size: 13.5 });

/* ── 3. OPPORTUNITY ───────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "The opportunity: the slab ladder pays for flexibility",
  "Administered ESY 2024-25 procurement prices — grain campaigns price ₹11–14/L above molasses");
grid(s, [
  ["Feedstock slab", "OMC price (₹/L)", "Season"],
  ["C-heavy molasses", "57.97", "cane crush only"],
  ["FCI surplus rice", "58.50", "allocation-dependent"],
  ["B-heavy molasses", "60.73", "cane crush only"],
  ["Damaged food grains", "64.00", "year-round"],
  ["Sugarcane juice/syrup", "65.61", "cane crush only"],
  ["Maize", "71.86", "year-round — the E30 marginal slab"],
], 0, 1.7, [0.6, 4.0, 6.4], [3.4, 2.4, 3.6], 0.52);
card(s, 10.3, 1.7, 2.45, 3.6, P.dark);
s.addText("+770", { x: 10.5, y: 1.95, w: 2.05, h: 0.7, fontFace: HEAD, fontSize: 34, bold: true,
  color: P.amber, margin: 0 });
s.addText("of the 1,212 DFPD-approved projects came in the grain + dual-feed windows (2021-22) — the register already shows the pivot",
  { x: 10.5, y: 2.7, w: 2.05, h: 2.4, fontFace: FONT, fontSize: 11.5, color: "E8F1EC", margin: 0 });
bullets(s, 0.6, 5.6, 12.1, 1.5, [
  "The E20→E27/E30 walk adds 400–600 cr L of fuel-ethanol demand (supply-match analysis) — and its marginal litre is grain: conversions capture the increment without greenfield risk",
  "Multi-feed = slab arbitrage: crush molasses in season, run maize/damaged grain off-season, switch legs as administered prices and allocations move",
], { size: 13 });

/* ── 4. POLICY MOAT ───────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "The policy moat: conversion is the scheme's intended outcome",
  "Every instrument points the same way — flexible, year-round, grain-capable capacity");
[["DFPD Interest Subvention", "6% subvention on project loans (grain/dual windows) — debt at ~4.75% effective. ₹1,17,362 cr of loans already recommended across the register."],
 ["Administered slab ladder", "DA&FW/OMC prices fixed per feedstock per ESY — the maize premium is policy, deliberately steering capacity toward grain."],
 ["FCI grain leg", "72 LMT rice allocation ESY25-26 at ₹2,320/qtl + damaged-grain channel — a second grain feedstock when maize runs hot."],
 ["Long-term offtake", "OMC LTOAs + 5% GST + excise-free ethanol molecule; allocation cycles favour plants that can bid multiple slabs."],
 ["Cooperative rescue money", "NCDC ₹10,005 cr keeps CSMs alive (working capital) — but only ₹251 cr reached ethanol assets: the conversion capital gap IS the entry."],
 ["State layering", "UP/Bihar/MP bioenergy policies add capital subsidy and single-window clearances on top (UP added ~50 cr L capacity in 2025 alone)."]]
.forEach(([h, d], i) => {
  const col = i % 2, row = Math.floor(i / 2);
  const x = 0.6 + col * 6.2, y = 1.75 + row * 1.64;
  card(s, x, y, 5.95, 1.52);
  s.addText(h, { x: x + 0.18, y: y + 0.1, w: 5.6, h: 0.38, fontFace: FONT, fontSize: 13.5,
    bold: true, color: P.dark, margin: 0 });
  s.addText(d, { x: x + 0.18, y: y + 0.5, w: 5.6, h: 0.95, fontFace: FONT, fontSize: 11,
    color: P.mute, margin: 0 });
});

/* ── 5. THE CONVERSION ────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "What actually gets built: ₹50 cr on a live plant",
  "100 KLPD molasses distillery → dual-feed · fermentation and distillation columns stay · ~12-month execution, season-synchronised");
const steps = [
  ["Grain intake & silos", "maize / damaged-grain storage, cleaning"],
  ["Milling + liquefaction", "hammer mills, slurry, jet cooker, enzymes"],
  ["Fermentation tweaks", "yeast strain + cascade re-piping (existing vessels)"],
  ["Distillation unchanged", "same columns, same ENA/RS quality"],
  ["DDGS dryer + boiler mods", "co-product line; multi-fuel boiler flexibility"],
];
steps.forEach(([h, d], i) => {
  const x = 0.6 + i * 2.5;
  card(s, x, 1.85, 2.3, 1.9, i === 4 ? P.dark : P.card);
  const dk = i === 4;
  s.addText(h, { x: x + 0.12, y: 2.0, w: 2.06, h: 0.75, fontFace: FONT, fontSize: 12.5, bold: true,
    color: dk ? P.amber : P.dark, margin: 0 });
  s.addText(d, { x: x + 0.12, y: 2.8, w: 2.06, h: 0.85, fontFace: FONT, fontSize: 10.5,
    color: dk ? "E8F1EC" : P.mute, margin: 0 });
  if (i < 4) s.addText("→", { x: x + 2.26, y: 2.4, w: 0.3, h: 0.5, fontFace: FONT, fontSize: 18,
    bold: true, color: P.amber, align: "center", margin: 0 });
});
card(s, 0.6, 4.15, 5.9, 2.5);
s.addText("Operating days: 180 → 330", { x: 0.85, y: 4.35, w: 5.4, h: 0.45, fontFace: HEAD,
  fontSize: 20, bold: true, color: P.dark, margin: 0 });
bullets(s, 0.85, 4.9, 5.4, 1.7, [
  "+150 grain days × 100 KLPD = +1.5 cr L/yr incremental ethanol",
  "Same licence, same LTOA counterparty, same tank farm and ETP headroom",
], { size: 12.5 });
card(s, 6.8, 4.15, 5.95, 2.5, P.dark);
s.addText("Per-litre grain economics (₹/L)", { x: 7.05, y: 4.35, w: 5.4, h: 0.4, fontFace: FONT,
  fontSize: 14, bold: true, color: P.amber, margin: 0 });
bullets(s, 7.05, 4.8, 5.45, 1.8, [
  "Maize slab 71.86 − maize 57.50 (₹23,000/t ÷ 400 L/t) + DDGS credit 13.18 − conversion cost 13.00",
  "= ₹14.5/L EBITDA — vs ₹8–11/L typical on molasses legs",
], { size: 12.5, color: "E8F1EC" });

/* ── 6. FINANCIALS ────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Financials: brownfield returns greenfield cannot touch",
  "₹50 cr conversion · 70:30 debt:equity · DFPD subvention → 3.5% effective debt · 15-yr life · incremental cash flows only");
stat(s, 0.6, 1.75, 2.35, "38.4%", "Project IRR", P.dark);
stat(s, 3.1, 1.75, 2.35, "81%", "Equity IRR (subvented)", P.dark);
stat(s, 5.6, 1.75, 2.35, "₹90.7 cr", "NPV @ 12%", P.green);
stat(s, 8.1, 1.75, 2.35, "Year 3", "Payback", P.amber);
stat(s, 10.6, 1.75, 2.15, "3.74×", "Steady DSCR", P.amber);
s.addText("Sensitivity — project IRR (%): maize price × grain-campaign days",
  { x: 0.6, y: 3.6, w: 8.0, h: 0.4, fontFace: FONT, fontSize: 13.5, bold: true, color: P.dark, margin: 0 });
grid(s, [
  ["Maize ₹/t", "100 days", "150 days (base)", "200 days"],
  ["20,000", "38.8", "56.5", "73.2"],
  ["23,000 (base)", "25.8", "38.4", "50.2"],
  ["26,000", "10.3", "18.1", "24.9"],
], 0, 4.05, [0.6, 2.9, 5.2, 7.5], [2.3, 2.3, 2.3, 2.3], 0.56);
card(s, 10.2, 3.6, 2.55, 2.75, P.dark);
s.addText("Honest stress: if grain litres price at the damaged-grain slab (₹64) instead of maize, IRR is still 17.0% — above the 12% hurdle",
  { x: 10.4, y: 3.8, w: 2.15, h: 2.4, fontFace: FONT, fontSize: 11.5, color: "E8F1EC", margin: 0 });
bullets(s, 0.6, 6.45, 12.1, 0.9, [
  "The slab premium is ADMINISTERED, not market — the biggest lever and the biggest risk; the ₹26,000-maize row and the ₹64-slab stress are the honest downside reading",
], { size: 12.5 });

/* ── 7. RISKS ─────────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Risks and mitigants", "The model's own caveats, answered structurally");
grid(s, [
  ["Risk", "Reality", "Mitigant"],
  ["Slab revision", "Maize premium is a policy choice, revised every ESY", "Multi-feed = switch legs; DFG-slab stress still clears hurdle (17%); slabs have only risen since 2018"],
  ["OMC allocation", "Only ~60% of offered ethanol absorbed today", "E27/E30 walk absorbs the glut (utilisation 76–83%); flexible plants win allocation cycles"],
  ["Maize price", "₹26,000/t compresses IRR to 10–25%", "DFG + FCI rice as alternate grain legs; forward contracts with FPOs; DDGS hedge (feed prices co-move)"],
  ["Execution on a live plant", "Conversion during crush season kills a year", "12-month build synchronised to off-season; proven EPC (Praj-class); fixed-price contract"],
  ["DDGS market", "Credit is ₹13/L of the margin", "Poultry-belt siting; take-or-pay feed offtakes; model works at DDGS −30% (IRR ~29%)"],
], 0, 1.7, [0.6, 2.6, 6.0], [2.0, 3.4, 6.75], 0.8);
bullets(s, 0.6, 6.62, 12.1, 0.7, [
  "Not relying on: E30 arriving on schedule, carbon revenue, or any slab premium widening — base case is today's published prices",
], { size: 11.5 });

/* ── 8. LANDSCAPE ─────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Landscape: the listed players are already converting",
  "The playbook is proven — the gap is the cooperative and mid-tier private mills");
[["Proof it works", "Bajaj Hindusthan: 570 KLD new multi-feed (group >1,200 KLPD). Dalmia Bharat Sugar: ₹400 cr grain distillery + two 100-KL units. Balrampur, Triveni, Dhampur all running dual-feed. UP added ~50 cr L in 2025; Gorakhpur GIDA is the grain-ethanol cluster.", P.card],
 ["EPC capacity exists", "Praj Industries anchors multi-feed conversion EPC with standard packages; 12-month brownfield timelines are routine. The DFPD register (1,212 projects) means DPRs, vendors and lenders all know the template.", P.card],
 ["The gap = the deal flow", "229 cooperative mills + dozens of mid-tier private molasses plants have the site, licence, ETP and LTOA — but not the ₹50 cr or the grain-operations capability. NCDC keeps them solvent, not strategic.", P.dark]]
.forEach(([h, d, fill], i) => {
  const x = 0.6 + i * 4.2;
  card(s, x, 1.8, 3.95, 3.9, fill);
  const dk = fill === P.dark;
  s.addText(h, { x: x + 0.2, y: 2.0, w: 3.55, h: 0.5, fontFace: FONT, fontSize: 15.5, bold: true,
    color: dk ? P.amber : P.dark, margin: 0 });
  s.addText(d, { x: x + 0.2, y: 2.55, w: 3.55, h: 3.0, fontFace: FONT, fontSize: 11.5,
    color: dk ? "E8F1EC" : P.ink, margin: 0 });
});
bullets(s, 0.6, 6.1, 12.1, 1.0, [
  "Synergy with the CBG platform pitch: the same mills' press-mud feeds CBG digesters — one partnership, two energy assets, shared site services",
], { size: 13 });

/* ── 9. ASK ───────────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.dark };
title(s, "The ask: a 5-mill conversion programme", null, true);
stat(s, 0.9, 1.7, 2.7, "₹250 cr", "5 × 100-KLPD conversions (₹75 cr equity)", P.dark);
stat(s, 3.8, 1.7, 2.7, "+7.5 cr L", "incremental grain ethanol/yr", P.dark);
stat(s, 6.7, 1.7, 2.7, "₹109 cr", "incremental EBITDA/yr at base", P.dark);
stat(s, 9.6, 1.7, 2.7, "Year 3", "programme payback", P.dark);
bullets(s, 0.9, 3.7, 11.5, 3.0, [
  "Structure per mill: BOT/lease or JV on the existing distillery — mill contributes plant, licence and molasses leg; programme funds and operates the grain conversion; revenue share aligned to slabs actually realised",
  "Phase 1: 2 UP mills (grain belt, GIDA vendor ecosystem, state policy top-up) + 1 Maharashtra cooperative; Phase 2: replicate ×2 with the shared grain-procurement and DDGS-marketing organisation",
  "Downside protection: DFPD-subvented debt at ~3.5% effective, DFG/FCI-rice alternate slabs, and the molasses leg keeps servicing debt even if the grain campaign pauses",
  "Exit: sale to a listed sugar-ethanol consolidator, or the mills buy back the conversion at a pre-agreed multiple once cash flows season",
], { size: 15, color: "FFFFFF", gap: 14 });
s.addText("Model, sensitivity and sources: distillery_conversion_model.py · ethanol_supply_match.py · The Volume Dividend · github.com/herrrickshaw/india-omc-fuel-fleet-model",
  { x: 0.9, y: 6.85, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 11.5, color: "9DBFB2", margin: 0 });

pres.writeFile({ fileName: "docs/Distillery_MultiFeed_Pitch.pptx" })
  .then(() => console.log("wrote docs/Distillery_MultiFeed_Pitch.pptx"));
