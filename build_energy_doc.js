#!/usr/bin/env node
/* Word-document build for the energy/blend-dilution analysis.
 * Numbers come from energy_blend_comparison.py (rerun it first if levers change).
 * Output: docs/Energy_Blend_Volume_Dividend.docx */
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType, LevelFormat,
} = require("docx");

const OUT = path.join(__dirname, "docs", "Energy_Blend_Volume_Dividend.docx");

const INK = "1a1a2e", ACCENT = "0f4c81", MUTE = "5a5a6e", HEAD_BG = "0f4c81", ALT_BG = "eef3f8";

const p = (text, opts = {}) =>
  new Paragraph({
    spacing: { after: opts.after ?? 160, before: opts.before ?? 0 },
    alignment: opts.align,
    children: [new TextRun({ text, size: opts.size ?? 21, color: opts.color ?? INK,
      bold: opts.bold, italics: opts.italics, font: "Calibri" })],
  });

const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 320, after: 160 },
  children: [new TextRun({ text: t, size: 28, bold: true, color: ACCENT, font: "Calibri" })] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 },
  children: [new TextRun({ text: t, size: 24, bold: true, color: INK, font: "Calibri" })] });

const bullet = (t) => new Paragraph({
  numbering: { reference: "bullets", level: 0 }, spacing: { after: 100 },
  children: [new TextRun({ text: t, size: 21, color: INK, font: "Calibri" })] });

function table(headers, rows, widths) {
  const total = widths.reduce((a, b) => a + b, 0);
  const mk = (text, i, isHead, alt) => new TableCell({
    width: { size: widths[i], type: WidthType.DXA },
    shading: { type: ShadingType.CLEAR, fill: isHead ? HEAD_BG : alt ? ALT_BG : "ffffff" },
    margins: { top: 70, bottom: 70, left: 110, right: 110 },
    children: [new Paragraph({
      alignment: i === 0 ? AlignmentType.LEFT : AlignmentType.RIGHT,
      children: [new TextRun({ text: String(text), size: 19, font: "Calibri",
        bold: isHead, color: isHead ? "ffffff" : INK })],
    })],
  });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    borders: Object.fromEntries(["top","bottom","left","right","insideHorizontal","insideVertical"]
      .map(k => [k, { style: BorderStyle.SINGLE, size: 2, color: "c8d2dc" }])),
    rows: [
      new TableRow({ tableHeader: true, children: headers.map((t, i) => mk(t, i, true, false)) }),
      ...rows.map((r, ri) => new TableRow({ children: r.map((t, i) => mk(t, i, false, ri % 2 === 1)) })),
    ],
  });
}
const spacer = () => p("", { after: 120 });

const doc = new Document({
  numbering: { config: [{ reference: "bullets",
    levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
      style: { paragraph: { indent: { left: 360, hanging: 200 } } } }] }] },
  styles: { default: { document: { run: { font: "Calibri", size: 21, color: INK } } } },
  sections: [{
    properties: { page: { margin: { top: 1080, bottom: 1080, left: 1180, right: 1180 } } },
    children: [
      // ── title ──
      new Paragraph({ spacing: { before: 200, after: 80 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "The Volume Dividend", size: 48, bold: true, color: ACCENT, font: "Calibri" })] }),
      p("Energy density, blend dilution, and who profits per extra litre — ethanol and isobutanol in petrol, biodiesel in diesel, versus compressed biogas in CNG",
        { align: AlignmentType.CENTER, size: 24, color: MUTE, after: 60 }),
      p("India, FY 2024-25 volume basis · July 2026 prices · companion to the OMC retail-profitability model",
        { align: AlignmentType.CENTER, size: 18, color: MUTE, after: 300, italics: true }),

      h1("Executive summary"),
      p("Ethanol carries 34% less energy per litre than petrol. Blending it dilutes every litre sold, cutting km-per-litre — yet the pump price per litre is unchanged, so the consumer silently buys more litres for the same distance. Because central excise, state VAT (in effect), dealer commission and OMC marketing margin are all levied per litre, every stakeholder in the fuel chain collects on the extra volume. At E20 on India's 54-billion-litre petrol pool, the volume effect alone moves ≈₹22,700 crore per year of extra consumer spend: ≈₹8,500 crore to the exchequer, ≈₹886 crore to retail-outlet dealers, ≈₹757 crore to OMC marketing margin. Walking the blend to E30 roughly doubles this."),
      p("Compressed biogas (CBG) is the structural exception: purified to IS 16087 spec it matches or exceeds pipeline CNG in energy per kilogram, and CNG is retailed per kg — so blending CBG into the gas stream substitutes imports without any hidden dilution levy on the consumer. It is, fiscally, the honest blend."),

      h1("1. Energy content of the fuels (lower heating value)"),
      table(
        ["Fuel", "MJ/kg", "MJ/litre", "Sold by", "vs base"],
        [
          ["Petrol (E0)", "43.4", "32.1", "litre", "—"],
          ["Ethanol (anhydrous)", "26.8", "21.1", "litre", "−34%"],
          ["Isobutanol", "33.1", "26.5", "litre", "−17%"],
          ["Diesel (B0)", "43.0", "35.7", "litre", "—"],
          ["Biodiesel (FAME)", "37.2", "32.7", "litre", "−8%"],
          ["HVO renewable diesel", "44.0", "34.3", "litre", "−4% (drop-in)"],
          ["CNG (pipeline gas)", "47.5", "n/a (gas)", "kg", "—"],
          ["CBG (IS 16087, CH₄ ≥90%)", "46.5", "n/a (gas)", "kg", "≈ CNG parity"],
          ["Pure methane (CBG ceiling)", "50.0", "n/a (gas)", "kg", "+5% vs CNG"],
        ],
        [2900, 1100, 1300, 1100, 1900]),
      spacer(),
      p("The oxygenates that policy favours for petrol are exactly the ones with the deepest energy deficit. Isobutanol — denser, less oxygenated — halves ethanol's penalty per unit of renewable content. On the gas side the ordering flips: well-purified biogas sits at or above fossil CNG."),

      h1("2. Blend dilution → extra litres for the same distance"),
      table(
        ["Blend", "MJ/L", "Energy vs base", "Extra litres (energy basis)", "Real-world drop"],
        [
          ["E10", "31.02", "−3.4%", "+3.5%", "~2%"],
          ["E20 (today)", "29.92", "−6.8%", "+7.3%", "4% (SIAM 2–6%)"],
          ["E25", "29.37", "−8.5%", "+9.3%", "~5.5%"],
          ["E30", "28.82", "−10.3%", "+11.4%", "~7%"],
          ["IB16 isobutanol", "31.22", "−2.8%", "+2.9%", "no India data"],
          ["IB24 isobutanol", "30.78", "−4.2%", "+4.3%", "no India data"],
          ["B7 biodiesel", "35.48", "−0.6%", "+0.6%", "≈ energy basis"],
          ["B10 biodiesel", "35.39", "−0.8%", "+0.8%", "≈ energy basis"],
          ["B15 biodiesel", "35.25", "−1.2%", "+1.3%", "≈ energy basis"],
          ["B20 biodiesel", "35.10", "−1.7%", "+1.7%", "≈ energy basis"],
          ["CBG in CNG (any %)", "per kg", "0%", "0%", "0% — sold per kg"],
        ],
        [2300, 1100, 1500, 2300, 2100]),
      spacer(),
      p("Real-world E20 loss (4%) runs below the pure energy math (6.8%) because E20-calibrated engines claw back part of it through octane and combustion gains; older vehicles lose up to ~12%. Diesel has no equivalent recovery mechanism, so biodiesel's real-world drop tracks the energy arithmetic."),

      h1("3. What the dilution costs a petrol owner"),
      p("Hatchback, 20 km/L on E0, 10,000 km/yr, pump ₹105/L. The price board shows the same ₹/litre for E0 and E20 — the energy cut is invisible at the point of sale:"),
      table(
        ["Blend", "Extra litres / yr", "Extra ₹ / yr", "Hidden levy on every km"],
        [
          ["E20", "+21 L", "₹2,188", "4.2%"],
          ["E25", "+29 L", "₹3,056", "5.8%"],
          ["E30", "+38 L", "₹3,952", "7.5%"],
        ],
        [1600, 2000, 1900, 2400]),

      h1("4. National petrol pool: where the extra litres' money goes"),
      p("Base: FY24-25 petrol pool 54.1 bn L (40 MMT), distance demand held at its E0-equivalent, dispensed through 99,281 retail outlets. Per-litre stakes: excise ₹19.90, effective state VAT ≈₹19.5, dealer commission ₹4.1, OMC margin ₹3.5. All figures ₹ crore per year:"),
      table(
        ["Blend", "Extra bn L", "Consumer pays", "Central excise", "State VAT", "Dealer comm.", "OMC margin"],
        [
          ["E20", "2.16", "22,703", "4,303", "4,216", "886", "757"],
          ["E25", "3.02", "31,712", "6,010", "5,889", "1,238", "1,057"],
          ["E30", "3.91", "41,011", "7,773", "7,616", "1,601", "1,367"],
          ["IB16*", "1.49", "15,696", "2,975", "2,915", "613", "523"],
          ["IB24*", "2.22", "23,295", "4,415", "4,326", "910", "776"],
        ],
        [1300, 1200, 1600, 1600, 1400, 1400, 1400]),
      p("*Isobutanol rows are energy-basis (no Indian fleet-trial data). The OMC-margin column reconciles exactly with the OMC retail-profitability model (₹757 / 1,057 / 1,367 crore).", { size: 18, color: MUTE, italics: true }),

      h2("4a. The E20 → E30 walk: what each next step adds"),
      p("India is already at ~E20, so the live policy question is the increment. Deltas below are each blend's take beyond what E20 already extracts:"),
      table(
        ["Step (vs E20)", "Δ bn L", "Δ Consumer", "Δ Excise", "Δ VAT", "Δ Dealer", "Δ OMC"],
        [
          ["E25", "+0.86", "+9,009", "+1,707", "+1,673", "+352", "+301"],
          ["E27", "+1.30", "+13,621", "+2,581", "+2,530", "+532", "+454"],
          ["E30", "+1.75", "+18,308", "+3,470", "+3,400", "+715", "+610"],
        ],
        [1700, 1100, 1500, 1400, 1400, 1300, 1300]),
      spacer(),
      p("The walk from E20 to E30 roughly doubles the volume-effect take. The increments are also qualitatively worse than the first 20%: today's engines are calibrated for E20, so the octane-recovery offset that softened E20's real-world drop has little left to give at E25–E30 — each further step passes through closer to the raw energy loss."),

      h2("4b. Diesel pool: B7 → B20 biodiesel walk"),
      p("Diesel is the bigger prize by volume — 110 bn L/yr (91.4 MMT), twice the petrol pool. FAME dilutes far less per litre, but the base is enormous. Per-litre stakes: pump ₹92, excise ₹15.80, effective VAT ≈₹12.3, dealer ₹3.1, OMC ₹2.5:"),
      table(
        ["Blend", "Mileage drop", "Extra bn L", "Consumer pays", "Excise", "VAT", "Dealer", "OMC"],
        [
          ["B7", "−0.6%", "0.64", "5,904", "1,014", "786", "199", "160"],
          ["B10", "−0.8%", "0.92", "8,455", "1,452", "1,126", "285", "230"],
          ["B15", "−1.2%", "1.38", "12,736", "2,187", "1,696", "429", "346"],
          ["B20", "−1.7%", "1.85", "17,053", "2,929", "2,271", "575", "463"],
        ],
        [1000, 1400, 1200, 1600, 1200, 1100, 1100, 1100]),
      spacer(),
      p("B20 pulls nearly as many extra litres as E20 does on petrol, though the per-km burden is far gentler (−1.7% vs −4%). The incidence differs too: diesel is freight-dominated, so the extra cost cascades into logistics and inflation rather than household fuel budgets. Feasibility check: actual biodiesel blending was under 1% in FY24-25 and the National Biofuel Policy targets only B5 by 2030 — B15/B20 are a what-if ceiling, and OEM warranties beyond B7 remain unresolved."),

      h1("5. The CBG contrast: same decarbonisation, no hidden levy"),
      bullet("Petrol + ethanol — energy dilution is real; pump ₹/L unchanged; consumer buys ~4% more litres at E20; centre, state, dealer and OMC all collect per-litre on the extra volume."),
      bullet("Diesel + FAME — the same mechanism, mild per litre but material in aggregate because the pool is 2× petrol's."),
      bullet("CNG + CBG — retailed per kilogram at methane-grade energy (46.5 MJ/kg spec floor vs 47.5 pipeline; pure methane 50). Substituting CBG changes sourcing — domestic agricultural and municipal waste instead of imported LNG — without changing the kilograms bought per kilometre. Zero dilution, zero volumetric pass-through."),
      p("Both routes substitute imports. Only the liquid route monetises an energy haircut through per-litre levies. CBG delivers the import substitution without taxing the consumer through the fuel gauge — and its SATAT procurement pricing keeps the subsidy explicit and on-budget rather than hidden in mileage.", { before: 100 }),

      h1("6. Price-adjustment scenarios: what would neutralise the mileage loss"),
      p("If blended petrol were priced for honest cost-per-km, its pump price would carry a discount equal to the mileage it takes away: P(blend) = P(E0) × (1 − drop). At a ₹105 pump, that means:"),
      table(
        ["Blend", "Mileage drop", "Parity discount", "Parity pump price", "National cost (₹ cr/yr)"],
        [
          ["E20", "4.0%", "₹4.20/L", "₹100.80", "22,703"],
          ["E25", "5.5%", "₹5.78/L", "₹99.22", "31,712"],
          ["E30", "7.0%", "₹7.35/L", "₹97.65", "41,011"],
        ],
        [1300, 1500, 1700, 1900, 1900]),
      spacer(),
      p("Note the FY23 budget's ₹2/L penalty on unblended petrol is a stick pointing the other way — it widens the per-km gap instead of closing it. Four funding routes, tested against the ethanol-procurement, grain-price and taxation numbers from the companion models:"),

      h2("S1 — pass through the tax break already embedded (works, 1.3–1.5× coverage)"),
      p("From the Bang-for-Your-Buck tax analysis: the ethanol molecule escapes both central excise (₹19.90/L) and state VAT (~₹19.5/L), bearing only 5% GST (~₹3.1/L on ₹62 ethanol) — but because E20 sells at the unblended price, that saving is retained in the price build-up rather than rebated. Netting off ethanol's cost premium over refinery petrol (₹62 vs ₹58):"),
      table(
        ["Blend", "Embedded headroom (₹/L)", "Parity needs (₹/L)", "Coverage"],
        [
          ["E20", "6.46", "4.20", "1.54×"],
          ["E25", "8.07", "5.78", "1.40×"],
          ["E30", "9.69", "7.35", "1.32×"],
        ],
        [1400, 2400, 2200, 1500]),
      spacer(),
      p("The embedded tax break more than funds parity at every blend level. Passing it through prices E20 honestly with ~₹2/L still left in the chain — no new subsidy and no new revenue loss versus an unblended counterfactual. What it does end is the windfall from the volume effect: that gain is, litre for litre, the consumer's loss."),

      h2("S2 / S3 — centre or states fund it via duty cuts (possible, costly)"),
      p("An excise cut of the full parity discount leaves ₹15.70/L (E20) falling to ₹12.55/L (E30) and costs the centre ₹22,700–41,000 crore/yr; the state-VAT route is symmetrical. Either is politically the mirror image of today's arrangement — which is precisely why neither has happened."),

      h2("S4 — fund it from cheaper ethanol (fails on grain economics)"),
      p("Parity funded from procurement alone needs ethanol at ₹41/L (E20) down to ₹37.5/L (E30) — far below every ESY 2024-25 feedstock slab:"),
      table(
        ["Feedstock", "OMC procurement (₹/L)"],
        [
          ["C-heavy molasses", "57.97"],
          ["FCI surplus rice", "58.50"],
          ["B-heavy molasses", "60.73"],
          ["Damaged food grains", "64.00"],
          ["Sugarcane juice / syrup", "65.61"],
          ["Maize", "71.86"],
        ],
        [3200, 2600]),
      spacer(),
      p("Grain and cane mandi prices set these floors — and maize, the marginal feedstock the E30 walk leans on, is the most expensive slab, pushing average procurement up, not down. Squeezing procurement to the cheapest slab funds only ₹0.81/L of E20's ₹4.20 need (~19%). Ethanol economics cannot pay for parity; only the tax side can. CBG needs no such scenario at all — its energy parity per kilogram is physical, not fiscal."),

      h1("7. Caveats and sources"),
      bullet("Volumes: PPAC Ready Reckoner FY2025-26 (H1), Table 6.1 (MS 40.0 MMT, HSD 91.4 MMT FY24-25); outlets Table 6.6/6.7 (99,281); dealer commission Table 8.10."),
      bullet("Mileage drops: SIAM/ARAI central figures (E20 4%, band 2–6%; up to ~12% for older vehicles); E25/E30 scaled on ethanol's calorific deficit; isobutanol and biodiesel rows are energy-basis."),
      bullet("Per-litre levies are editable levers shared with omc_model.py and statewise_tax_impact.py: excise ₹19.90/L petrol, ₹15.80/L diesel; VAT 25% on ₹78/L petrol base, 17.5% on ₹70/L diesel base; OMC margins ₹3.5/₹2.5."),
      bullet("This volume effect is distinct from — and additive to — the tax-differential effect (states forgo VAT on the ethanol fraction, ~₹9,000 cr/yr at E20): states lose on substitution while every per-litre stakeholder gains on volume."),
      bullet("Generated by build_energy_doc.js from energy_blend_comparison.py outputs; do not hand-edit. Repository: github.com/herrrickshaw/india-omc-fuel-fleet-model."),
    ],
  }],
});

fs.mkdirSync(path.join(__dirname, "docs"), { recursive: true });
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log("wrote", OUT, buf.length, "bytes"); });
