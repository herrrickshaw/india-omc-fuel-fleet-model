#!/usr/bin/env node
/* CBG investment pitch deck. Numbers from cbg_pitch_model.py, cbg_satat_economics.py,
 * ethanol_supply_match.py and the GOBARdhan circular register (paper Annex A).
 * Structure: problem -> market -> policy moat -> model -> financials -> ask.
 * Output: docs/CBG_Investment_Pitch.pptx */
const pptxgen = require("pptxgenjs");

const P = { dark: "0E3B2E", dark2: "16523F", amber: "E3A72F", green: "2E9E6B",
  red: "C0392B", ink: "1C2B27", mute: "5C6B66", bg: "FFFFFF", card: "F2F6F4", line: "D5E0DB" };
const FONT = "Calibri", HEAD = "Cambria";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "india-omc-fuel-fleet-model";
pres.title = "Compressed Biogas — Investment Pitch";

const title = (s, t, sub, dark = false) => {
  s.addText(t, { x: 0.6, y: 0.35, w: 12.1, h: 0.75, fontFace: HEAD, fontSize: 29, bold: true,
    color: dark ? "FFFFFF" : P.dark, margin: 0 });
  if (sub) s.addText(sub, { x: 0.6, y: 1.02, w: 12.1, h: 0.4, fontFace: FONT, fontSize: 13,
    color: dark ? "CFE3DA" : P.mute, margin: 0 });
};
const card = (s, x, y, w, h, fill = P.card) =>
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: fill }, rectRadius: 0.08,
    line: { color: P.line, width: 0.75 } });
const stat = (s, x, y, w, big, label, color) => {
  card(s, x, y, w, 1.5);
  s.addText(big, { x: x + 0.12, y: y + 0.1, w: w - 0.24, h: 0.75, fontFace: HEAD, fontSize: 26,
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
s.addText("Compressed Biogas", { x: 0.9, y: 1.8, w: 11.5, h: 1.1, fontFace: HEAD, fontSize: 54,
  bold: true, color: "FFFFFF", margin: 0 });
s.addText("India's on-budget decarbonisation play — mandated demand, assured pricing, three revenue legs",
  { x: 0.9, y: 3.0, w: 11.2, h: 0.6, fontFace: FONT, fontSize: 20, color: P.amber, margin: 0 });
s.addText("Investment pitch · July 2026 · built on the Volume Dividend research stack (SATAT economics, supply match, GOBARdhan circular register, reference-plant model)",
  { x: 0.9, y: 6.4, w: 11.5, h: 0.5, fontFace: FONT, fontSize: 12, color: "9DBFB2", margin: 0 });

/* ── 2. PROBLEM ───────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "The problem: imports, wasted biomass, dishonest blends",
  "Three converging failures CBG monetises simultaneously");
[["Imported molecules", "India's CGD growth rides on spot RLNG (~$12/MMBtu, ₹0.94/MJ). Every kg of CNG demand growth is an import at the margin — price-volatile, dollar-denominated.", P.card],
 ["Wasted feedstock", "Press-mud, cattle dung, paddy straw and municipal waste are burned or dumped: stubble smoke, methane emissions, and a disposal cost — negative-value feedstock waiting for a digester.", P.card],
 ["The liquid-biofuel trap", "The ethanol route funds decarbonisation through a hidden consumer levy (−4% mileage at unchanged price = ₹22,700 cr/yr) and now faces distillery overcapacity (59% utilisation). CBG has neither problem: energy parity per kg, on-budget support.", P.dark]]
.forEach(([h, d, fill], i) => {
  const x = 0.6 + i * 4.2;
  card(s, x, 1.8, 3.95, 3.4, fill);
  const dk = fill === P.dark;
  s.addText(h, { x: x + 0.2, y: 2.0, w: 3.55, h: 0.5, fontFace: FONT, fontSize: 16, bold: true,
    color: dk ? P.amber : P.dark, margin: 0 });
  s.addText(d, { x: x + 0.2, y: 2.55, w: 3.55, h: 2.5, fontFace: FONT, fontSize: 12.5,
    color: dk ? "E8F1EC" : P.ink, margin: 0 });
});
bullets(s, 0.6, 5.6, 12.1, 1.5, [
  "CBG converts a waste liability into a gas molecule that is legally fungible with CNG (IS 16087:2025) — sold per kg at energy parity, no mileage penalty, no volumetric pass-through",
  "It undercuts imported LNG outright whenever spot runs above ~$14.8/MMBtu — the import-substitution case stands on its own",
], { size: 13.5 });

/* ── 3. MARKET ────────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "The market: demand is mandated, supply is missing",
  "CBG Blending Obligation (CBO) on city-gas distributors — demand by decree, stepping 1% → 5%");
grid(s, [
  ["", "CBO share", "CBG needed (t/yr)", "Procurement value (₹ cr/yr)"],
  ["FY25-26 (live)", "1%", "66,700", "378"],
  ["FY28-29", "~5%", "333,500", "1,891"],
], 0, 1.75, [0.6, 3.1, 5.0, 8.0], [2.5, 1.9, 3.0, 3.4], 0.6);
s.addText("…on the 6.67-MMT CNG(T) pool alone — PNG (domestic) obligations add further demand on top",
  { x: 0.6, y: 3.7, w: 8.0, h: 0.4, fontFace: FONT, fontSize: 11.5, italic: true, color: P.mute, margin: 0 });
card(s, 0.6, 4.3, 5.9, 2.6);
s.addText("Supply is nowhere near", { x: 0.85, y: 4.5, w: 5.4, h: 0.4, fontFace: FONT, fontSize: 14,
  bold: true, color: P.dark, margin: 0 });
bullets(s, 0.85, 4.95, 5.4, 1.9, [
  "SATAT envisioned 5,000 plants; a few hundred are commissioned — the obligation ramp outruns the build-out",
  "Each 12-TPD plant supplies ~4,000 t/yr: the 5% CBO alone needs ~85 such plants' output",
], { size: 12.5 });
card(s, 6.8, 4.3, 5.95, 2.6, P.dark);
s.addText("Price floor + import ceiling", { x: 7.05, y: 4.5, w: 5.4, h: 0.4, fontFace: FONT,
  fontSize: 14, bold: true, color: P.amber, margin: 0 });
bullets(s, 7.05, 4.95, 5.45, 1.9, [
  "SATAT assures ₹54/kg ex-plant (+5% GST); synchronization scheme injects straight into the CGD grid",
  "Renewable energy at ₹1.16/MJ vs ethanol's ₹2.94 — CBG is the CHEAPEST renewable molecule India buys",
], { size: 12.5, color: "E8F1EC" });

/* ── 4. POLICY MOAT ───────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "The policy moat: 70 circulars de-risk every leg",
  "GOBARdhan register, ~half dated 2025-26 — the cadence is accelerating, all support on-budget and ex-plant");
const moat = [
  ["Offtake", "SATAT ₹54/kg assured · CBO mandate · CGD grid injection"],
  ["Capital", "MNRE CFA (up to ₹10 cr/plant) · SBM 2.0 VGF · SASCI state capital"],
  ["Evacuation", "DPI scheme funds the plant-to-grid pipeline"],
  ["Feedstock", "Biomass machinery assistance · crop-residue channelling"],
  ["Digestate", "FCO Schedule VIII fertiliser status · bulk-sale rights · MDA ~₹1,500/t"],
  ["Debt", "RBI priority-sector lending · AIF · AHIDF"],
  ["Tax & carbon", "5% GST · excise exemption on blended CNG · carbon-credit eligibility"],
  ["States", "7 state policies + MoPNG model template (2026)"],
];
moat.forEach(([h, d], i) => {
  const col = i % 2, row = Math.floor(i / 2);
  const x = 0.6 + col * 6.2, y = 1.75 + row * 1.24;
  card(s, x, y, 5.95, 1.12);
  s.addText(h, { x: x + 0.18, y: y + 0.08, w: 1.65, h: 0.9, fontFace: FONT, fontSize: 13.5,
    bold: true, color: P.dark, valign: "middle", margin: 0 });
  s.addText(d, { x: x + 1.9, y: y + 0.08, w: 3.9, h: 0.96, fontFace: FONT, fontSize: 11,
    color: P.mute, valign: "middle", margin: 0 });
});
card(s, 0.6, 6.8, 12.15, 0.55, P.dark);
s.addText("No other Indian infrastructure class has assured price + mandated demand + subsidised capex + priority debt + a regulated second product — simultaneously.",
  { x: 0.85, y: 6.82, w: 11.7, h: 0.5, fontFace: FONT, fontSize: 12, bold: true, color: "FFFFFF",
    valign: "middle", margin: 0 });

/* ── 5. BUSINESS MODEL ────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Business model: one digester, three revenue legs",
  "Reference plant: 12 TPD CBG · 250 TPD multi-feedstock (press-mud + agri-residue) · 330 days · 90% steady utilisation");
const legs = [
  ["GAS — ₹19.2 cr/yr (77%)", "3,564 t CBG @ SATAT ₹54/kg, injected into the CGD grid (DPI pipeline). CBO makes the buyer's demand mandatory.", P.dark],
  ["FERTILISER — ₹2.2 cr/yr (9%)", "14,850 t FOM under FCO Schedule VIII @ ₹1,500/t net (incl. MDA). Bulk-sale rights direct to farmers.", P.card],
  ["CARBON — ₹0.7 cr/yr (3%)", "~8,900 credits/yr @ ₹800 (2.5 tCO2e/t CBG). MoEFCC-recognised eligibility; upside under CCTS.", P.card],
];
legs.forEach(([h, d, fill], i) => {
  const x = 0.6 + i * 4.2;
  card(s, x, 1.85, 3.95, 2.6, fill);
  const dk = fill === P.dark;
  s.addText(h, { x: x + 0.2, y: 2.02, w: 3.55, h: 0.55, fontFace: FONT, fontSize: 14.5, bold: true,
    color: dk ? P.amber : P.dark, margin: 0 });
  s.addText(d, { x: x + 0.2, y: 2.6, w: 3.55, h: 1.7, fontFace: FONT, fontSize: 12,
    color: dk ? "E8F1EC" : P.ink, margin: 0 });
});
bullets(s, 0.6, 4.85, 12.1, 2.1, [
  "Opex ₹10.1 cr/yr (feedstock ₹700/t delivered + ₹5 cr O&M/power/manpower) → steady EBITDA ₹12.0 cr, ~54% margin",
  "The fertiliser leg is load-bearing: without FOM+MDA, project IRR falls 20.6% → 16.1% — digestate discipline is a core operating competency, not an afterthought",
  "Feedstock strategy: anchor on sugar-mill press-mud (contracted, dense, cheap) + agri-residue swing — the cooperative-mill partnership angle below",
], { size: 13 });

/* ── 6. FINANCIALS ────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Financials: 20%+ project IRR with a policy floor under revenue",
  "₹60 cr capex − ₹10 cr MNRE assistance = ₹50 cr net · 70:30 debt:equity @ 9.5% (priority sector) · 15-yr life");
stat(s, 0.6, 1.75, 2.35, "20.6%", "Project IRR", P.dark);
stat(s, 3.1, 1.75, 2.35, "32.0%", "Equity IRR (levered)", P.dark);
stat(s, 5.6, 1.75, 2.35, "₹26.6 cr", "NPV @ 12%", P.green);
stat(s, 8.1, 1.75, 2.35, "Year 5", "Payback", P.amber);
stat(s, 10.6, 1.75, 2.15, "1.85×", "Steady DSCR", P.amber);
s.addText("Sensitivity — project IRR (%): SATAT price × delivered feedstock cost",
  { x: 0.6, y: 3.6, w: 8.0, h: 0.4, fontFace: FONT, fontSize: 13.5, bold: true, color: P.dark, margin: 0 });
grid(s, [
  ["CBG price", "Feed ₹525/t (−25%)", "₹700/t (base)", "₹875/t (+25%)"],
  ["₹48/kg", "18.9", "16.3", "13.5"],
  ["₹54/kg (SATAT)", "23.1", "20.6", "18.0"],
  ["₹60/kg", "27.1", "24.7", "22.2"],
], 0, 4.05, [0.6, 2.7, 5.1, 7.5], [2.1, 2.4, 2.4, 2.4], 0.56);
card(s, 10.2, 3.6, 2.55, 2.75, P.dark);
s.addText("Worst cell still 13.5% — the SATAT floor + PSL debt keep the downside financeable",
  { x: 10.4, y: 3.8, w: 2.15, h: 2.4, fontFace: FONT, fontSize: 12, color: "E8F1EC", margin: 0 });
bullets(s, 0.6, 6.45, 12.1, 0.9, [
  "Model discipline: ramp year at 60%; carbon priced conservatively (₹800/credit); no terminal value; all levers editable in cbg_pitch_model.py",
], { size: 12.5 });

/* ── 7. RISKS ─────────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Risks and mitigants", "What actually kills CBG plants — and how the structure answers it");
grid(s, [
  ["Risk", "Reality", "Mitigant"],
  ["Feedstock supply", "The #1 failure mode — plants starve, not drown", "Anchor press-mud contracts with sugar mills; multi-feed digester; BAM-funded collection machinery"],
  ["Digestate offtake", "FOM piles up without marketing muscle", "Bulk-sale authorisation + MDA ₹1,500/t + ICAR practice guide; co-marketing with fertiliser distributors"],
  ["Price revision", "SATAT methodology changed May-2025", "Floor has only moved UP since 2018 (₹46→₹54); CBO demand decouples volume risk from price risk"],
  ["Evacuation", "Trucking kills margins", "DPI-funded pipeline to CGD grid; site selection ≤10 km from network"],
  ["Execution/EPC", "Commissioning delays burn the interest clock", "Proven-technology EPC (fixed-price), staged drawdown, MNRE CFA milestone-linked"],
], 0, 1.7, [0.6, 2.6, 6.3], [2.0, 3.7, 6.45], 0.8);
bullets(s, 0.6, 6.62, 12.1, 0.7, [
  "Deliberately NOT relying on: the NCDC coop-mill scheme as capital (96.5% goes to working capital), or carbon prices above ₹800",
], { size: 11.5 });

/* ── 8. LANDSCAPE ─────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.bg };
title(s, "Landscape: majors, IPOs, and a fragmented middle",
  "The capital markets are already pricing this theme");
[["Majors committed", "Reliance (target ~100 CBG plants), Adani TotalEnergies, GAIL, IOCL/BPCL/HPCL joint ventures — strategic buyers of both gas and, eventually, platforms", P.card],
 ["IPO pipeline live", "TruAlt Bioenergy and Godavari Biorefineries listings establish public-market comps for bioenergy platforms; Praj Industries anchors the EPC value chain", P.card],
 ["Fragmented middle = the opportunity", "Hundreds of single-plant developers with LOIs but no capital or digestate muscle — a roll-up / platform play with shared EPC, O&M and FOM marketing beats one-off plants", P.dark]]
.forEach(([h, d, fill], i) => {
  const x = 0.6 + i * 4.2;
  card(s, x, 1.85, 3.95, 3.3, fill);
  const dk = fill === P.dark;
  s.addText(h, { x: x + 0.2, y: 2.02, w: 3.55, h: 0.8, fontFace: FONT, fontSize: 15, bold: true,
    color: dk ? P.amber : P.dark, margin: 0 });
  s.addText(d, { x: x + 0.2, y: 2.85, w: 3.55, h: 2.2, fontFace: FONT, fontSize: 12.5,
    color: dk ? "E8F1EC" : P.ink, margin: 0 });
});
bullets(s, 0.6, 5.5, 12.1, 1.6, [
  "Cooperative sugar mills are the underexploited entry: 229 functional CSMs hold the press-mud and the land, NCDC keeps them liquid, but only ₹251 cr of the ₹10,005 cr scheme went to ethanol/energy assets — they need a capital + execution partner, not another loan",
  "Structures that fit: BOT/BOOT on mill land, feedstock-for-equity JVs, or O&M-plus-offtake partnerships — mill gets waste disposal + lease income, platform gets contracted feedstock",
], { size: 13 });

/* ── 9. ASK ───────────────────────────────────────────────────────────── */
s = pres.addSlide(); s.background = { color: P.dark };
title(s, "The ask: seed a 10-plant CBG platform", null, true);
stat(s, 0.9, 1.7, 2.7, "₹150 cr", "equity for 10 × 12-TPD plants", P.dark);
stat(s, 3.8, 1.7, 2.7, "₹120 cr", "EBITDA/yr at steady state", P.dark);
stat(s, 6.7, 1.7, 2.7, "32%", "levered equity IRR per plant", P.dark);
stat(s, 9.6, 1.7, 2.7, "~40 kt/yr", "CBG = 12% of the FY29 CBO gap", P.dark);
bullets(s, 0.9, 3.7, 11.5, 3.0, [
  "Phase 1 (18 months): 3 plants on contracted sugar-mill press-mud in UP/Maharashtra — sites within 10 km of CGD networks, MNRE CFA + PSL debt term sheets in hand",
  "Phase 2: 7 plants replicating the template; shared EPC frame contract, central O&M, one FOM marketing organisation across the fleet",
  "Exit paths: strategic sale to a major building CBG portfolios, CGD backward-integration, or the public-market route the current IPO window is validating",
  "Every revenue leg sits on a government floor (SATAT, CBO, MDA) and every cost leg on a subsidy (CFA, DPI, PSL) — the pitch is not a technology bet, it is disciplined execution against a policy stack that is accelerating",
], { size: 15, color: "FFFFFF", gap: 14 });
s.addText("Model, sensitivity and sources: cbg_pitch_model.py · Annex A of The Volume Dividend · github.com/herrrickshaw/india-omc-fuel-fleet-model",
  { x: 0.9, y: 6.85, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 11.5, color: "9DBFB2", margin: 0 });

pres.writeFile({ fileName: "docs/CBG_Investment_Pitch.pptx" })
  .then(() => console.log("wrote docs/CBG_Investment_Pitch.pptx"));
