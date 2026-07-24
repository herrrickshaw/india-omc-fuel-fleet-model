#!/usr/bin/env python3
"""India's refining economics: spends big importing crude, earns back exporting
refined products — but the model is under pressure. Anchored on DGCIS/Tradestat
(HS-27 trade, CY2024), PPAC RR (crude import / product export, FY24-25), and
market data (Argus/Platts MS crack, GRM). Pure stdlib.
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"; OUT.mkdir(parents=True, exist_ok=True)

# ── DGCIS / Tradestat, HS-27 "Mineral fuels, oils, distillation products" (US$ bn, CY) ──
# Source: DGCIS "A Quick View of India's Trade Scenario"
HS27 = {
    "exports_2023": 89.34, "exports_2024": 75.85,   # -15.1% YoY (lower oil prices)
    "imports_2023": 220.58, "imports_2024": 225.39,  # +2.2% YoY
    "total_exports_2024": 442.71, "total_imports_2024": 718.16,
    "export_share_2024": 17.13, "import_share_2024": 31.38,   # % of India's total
}

# ── PPAC RR Table 4.11 (FY24-25) — the refining arbitrage, narrower defn ──────
RR = {
    "crude_import_MMT": 243.2, "crude_import_usdbn": 137.2,
    "product_import_MMT": 50.9, "product_import_usdbn": 23.7,     # incl. LPG, naphtha, fuel oil
    "total_oil_import_MMT": 294.1, "total_oil_import_usdbn": 160.8,  # crude + products
    "product_export_MMT": 65.1, "product_export_usdbn": 44.4,
    "petrol_export_MMT": 15.8, "petrol_export_usdbn": 11.6,
    "diesel_export_MMT": 28.0, "diesel_export_usdbn": 19.1,
}
# PPAC RR Table 4.11 — net oil trade trend ($ bn): total oil import, product export
RR_TREND = {  # FY : (total_oil_import_usdbn, product_export_usdbn)
    "2020-21": (77.0, 21.4), "2021-22": (144.3, 44.4), "2022-23": (184.4, 57.3),
    "2023-24": (156.3, 47.7), "2024-25": (160.8, 44.4),
}

# ── market data (Argus/Platts/analysts, 2025-26) ─────────────────────────────
MARKET = {
    "ms_crack_sing92_brent": 24.2,     # $/bbl, Singapore Mogas 92 vs Brent (Jul-26)
    "grm_fy24": (10, 12), "grm_fy25": (4, 6), "grm_norm": (5.5, 6.0),
    "russian_share_2023": 0.375, "russian_share_jan26": 0.20,
    "eu_ban_export_drop": 0.69,        # -69% from 11 Russian-crude refineries, Feb-Apr'26
}
CAPACITY_MMT = 256                     # India refining capacity ~2024 (4th largest)
THROUGHPUT_MMT = 250                    # ~crude processed / yr
BBL_PER_T_CRUDE = 7.33

# ── petrochemical-integration GRM uplift (Digital Refining, DecarbTech, analysts) ──
PETCHEM = {
    "marginal_uplift_bbl": (1.5, 2.0),     # +$/bbl GRM from adding petchem to a fuels refinery
    "cotc_margin_bbl": (60, 80),           # full crude-to-chemicals complex margin, $/bbl
    "fuels_margin_bbl": (15, 25),          # fuels-focused refinery margin, $/bbl
    "cotc_chem_yield": 0.45,               # up to 45% crude-to-chemicals by volume (vs <15% standalone)
    "std_chem_yield": 0.15,
    "demand_cagr": (0.03, 0.04),           # petchem demand growth (~1.5x GDP)
}


def main():
    net_hs27 = HS27["imports_2024"] - HS27["exports_2024"]
    trade_deficit = HS27["total_imports_2024"] - HS27["total_exports_2024"]
    hs27_share_of_deficit = net_hs27 / trade_deficit
    crude_per_bbl = RR["crude_import_usdbn"] * 1e9 / (RR["crude_import_MMT"] * 1e6 * 7.33)   # ~7.33 bbl/t crude
    prod_per_bbl = RR["product_export_usdbn"] * 1e9 / (RR["product_export_MMT"] * 1e6 * 8.0)  # ~8 bbl/t products
    implied_valadd = prod_per_bbl - crude_per_bbl

    with (OUT / "refining_trade_summary.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["metric", "value", "unit", "source"])
        rows = [
            ("HS-27 exports CY2024", HS27["exports_2024"], "US$ bn", "DGCIS/Tradestat"),
            ("HS-27 imports CY2024", HS27["imports_2024"], "US$ bn", "DGCIS/Tradestat"),
            ("HS-27 net (deficit)", -net_hs27, "US$ bn", "derived"),
            ("HS-27 share of total trade deficit", round(hs27_share_of_deficit*100, 1), "%", "derived"),
            ("Crude import FY25", RR["crude_import_usdbn"], "US$ bn", "PPAC RR 4.11"),
            ("Product export FY25", RR["product_export_usdbn"], "US$ bn", "PPAC RR 4.11"),
            ("Crude cost", round(crude_per_bbl, 1), "US$/bbl", "derived"),
            ("Product realisation", round(prod_per_bbl, 1), "US$/bbl", "derived"),
            ("Implied gross value-add", round(implied_valadd, 1), "US$/bbl", "derived"),
            ("MS crack (Sing 92 vs Brent)", MARKET["ms_crack_sing92_brent"], "US$/bbl", "Platts/Argus Jul-26"),
        ]
        w.writerows(rows)

    L = []
    L.append("# India's refinery economics — crude-in, product-out, under pressure\n")
    L.append("India is the **world's 4th-largest refiner** (~%d MMT capacity) and a structural **net "
             "exporter of refined products**: it imports crude, refines it, sells the surplus abroad, and "
             "keeps the refining margin. But the terms of that trade are tightening. Anchored on "
             "**DGCIS/Tradestat** (HS-27 trade), **PPAC Ready Reckoner** (FY24-25), and Argus/Platts "
             "market data.\n" % CAPACITY_MMT)

    L.append("## 1. The scale — energy is half the trade deficit\n")
    L.append("HS-27 (mineral fuels), DGCIS/Tradestat, CY2024:\n")
    L.append("| | US$ bn | Share of India total |")
    L.append("|---|--:|--:|")
    L.append(f"| HS-27 **imports** | {HS27['imports_2024']:.1f} | {HS27['import_share_2024']:.1f}% of all imports |")
    L.append(f"| HS-27 **exports** | {HS27['exports_2024']:.1f} | {HS27['export_share_2024']:.1f}% of all exports |")
    L.append(f"| **Net (deficit)** | **−{net_hs27:.1f}** | — |")
    L.append("")
    L.append(f"- India spends **${HS27['imports_2024']:.0f} bn** importing energy and earns back "
             f"**${HS27['exports_2024']:.0f} bn** exporting refined products — a **net −${net_hs27:.0f} bn**.")
    L.append(f"- That single deficit is **~{hs27_share_of_deficit*100:.0f}% of India's entire "
             f"${trade_deficit:.0f} bn merchandise trade deficit** — no other commodity group comes close. "
             "The refining export book is what stops it being far worse.\n")

    L.append("## 2. The arbitrage — what a barrel earns\n")
    L.append("PPAC RR Table 4.11 (FY24-25), the narrower petroleum-products cut:\n")
    L.append("| Flow | Volume | Value | Per barrel |")
    L.append("|---|--:|--:|--:|")
    L.append(f"| Crude **imported** | {RR['crude_import_MMT']:.0f} MMT | ${RR['crude_import_usdbn']:.0f} bn | ~${crude_per_bbl:.0f}/bbl |")
    L.append(f"| Products **exported** | {RR['product_export_MMT']:.0f} MMT | ${RR['product_export_usdbn']:.0f} bn | ~${prod_per_bbl:.0f}/bbl |")
    L.append(f"| — of which diesel | {RR['diesel_export_MMT']:.0f} MMT | ${RR['diesel_export_usdbn']:.0f} bn | (top export) |")
    L.append(f"| — of which petrol | {RR['petrol_export_MMT']:.0f} MMT | ${RR['petrol_export_usdbn']:.0f} bn | |")
    L.append("")
    L.append(f"- Products leave at **~${prod_per_bbl:.0f}/bbl** vs crude in at **~${crude_per_bbl:.0f}/bbl** — an "
             f"implied **~${implied_valadd:.0f}/bbl of gross value-add**, broadly in line with reported GRMs. "
             "Diesel is the biggest export by both volume and value; petrol (the freed-by-ethanol barrels "
             "in the sibling models) is second.")
    L.append("- Top destinations (DGCIS): **Netherlands, UAE, Singapore** — i.e. Europe is the marginal, "
             "highest-value market, which is exactly what's now at risk.\n")

    L.append("## 3. PPAC view — the net oil-import bill\n")
    net_oil = RR["total_oil_import_usdbn"] - RR["product_export_usdbn"]
    export_offset = RR["product_export_usdbn"] / RR["total_oil_import_usdbn"]
    L.append("PPAC RR Table 4.11 nets the *oil* trade (crude + products), the number the government "
             "tracks as the oil-import burden:\n")
    L.append("| FY | Oil import ($ bn) | Product export ($ bn) | **Net oil bill ($ bn)** | Export offsets |")
    L.append("|---|--:|--:|--:|--:|")
    for fy, (imp, exp) in RR_TREND.items():
        L.append(f"| {fy} | {imp:.1f} | {exp:.1f} | **{imp-exp:.1f}** | {exp/imp*100:.0f}% |")
    L.append("")
    L.append(f"- FY25: India imports **${RR['total_oil_import_usdbn']:.0f} bn** of oil "
             f"(crude ${RR['crude_import_usdbn']:.0f} bn + products ${RR['product_import_usdbn']:.0f} bn) and "
             f"exports **${RR['product_export_usdbn']:.0f} bn** of products — a **net oil bill of "
             f"~${net_oil:.0f} bn**.")
    L.append(f"- **Product exports offset ~{export_offset*100:.0f}% of the gross oil-import bill** — the "
             "refining sector claws back roughly a quarter of the crude spend as export earnings, before "
             "counting the value it adds to the ~85% consumed at home.")
    L.append("- The net bill swung with oil prices (peak ~$127 bn in FY23) but sits structurally high; "
             "with self-sufficiency at ~12%, it only falls if domestic demand slows (EV/ethanol) or "
             "output rises (upstream).\n")

    L.append("## 4. Market read — cracks healthy, GRMs normalised, one big spike\n")
    lo, hi = MARKET["grm_fy25"]
    L.append(f"- **MS (gasoline) crack** — Singapore Mogas 92 vs Brent ≈ **${MARKET['ms_crack_sing92_brent']}/bbl** "
             "(Jul-26): a healthy product-vs-crude spread, well above the whole-barrel margin.")
    L.append(f"- **GRMs normalised** — Indian refiners ~**${lo}-{hi}/bbl in FY25**, down from "
             f"${MARKET['grm_fy24'][0]}-{MARKET['grm_fy24'][1]}/bbl in FY24; analysts see a normalised "
             f"${MARKET['grm_norm'][0]}-{MARKET['grm_norm'][1]}/bbl. A 2026 Mideast-conflict supply scare "
             "briefly spiked Asian margins to their highest since 2022 — a reminder the margin is "
             "geopolitically levered, not structural.")
    L.append("- **RIL Jamnagar** (world's most complex single site) and **MRPL** (now India's #2 fuel "
             "exporter) anchor the export machine; India shipped a record ~1.28 mn b/d of products in 2025.\n")

    L.append("## 5. The pressure point — the Russian-crude model is unwinding\n")
    L.append(f"India's recent GRM edge leaned heavily on **discounted Russian crude** (~"
             f"{MARKET['russian_share_2023']*100:.0f}% of imports in 2023-24). Two 2025-26 shocks hit it:\n")
    L.append("- **US sanctions** on Russian oil entities (Nov 2025) and the **EU ban on products refined "
             "from Russian crude (21 Jan 2026)** — the latter demands a 60-day 'washout' (no Russian crude "
             "at the terminal) plus refinery attestation to keep selling into Europe.")
    L.append(f"- Result: India cut Russian crude share **{MARKET['russian_share_2023']*100:.0f}% → "
             f"{MARKET['russian_share_jan26']*100:.0f}%**, and product flows from 11 Russian-crude "
             f"refineries fell **~{MARKET['eu_ban_export_drop']*100:.0f}%** (Feb-Apr 2026). The discount "
             "narrows *and* the premium European outlet closes for Russian-fed barrels at the same time — "
             "a double squeeze on the export margin.\n")

    L.append("## 6. Petrochemical integration — the GRM upside (Digital Refining)\n")
    mlo, mhi = PETCHEM["marginal_uplift_bbl"]
    bbl_yr = THROUGHPUT_MMT * 1e6 * BBL_PER_T_CRUDE
    upside_lo = bbl_yr * mlo / 1e9        # $ bn if applied system-wide
    upside_hi = bbl_yr * mhi / 1e9
    clo, chi = PETCHEM["cotc_margin_bbl"]; flo, fhi = PETCHEM["fuels_margin_bbl"]
    L.append("Per **Digital Refining** (and DecarbonisationTechnology / RI-2023), moving down the "
             "petrochemical value chain is the clearest structural lever on refining margin — and the one "
             "hedge against the fuel-demand peak:\n")
    L.append(f"- **Marginal integration** — bolting petrochemical units onto a fuels refinery lifts GRM "
             f"**+${mlo}-{mhi}/bbl of crude** (byproduct upgrading, shared utilities, lower conversion cost). "
             f"Across India's ~{THROUGHPUT_MMT} MMT throughput (~{bbl_yr/1e9:.1f} bn bbl/yr) that is "
             f"**~${upside_lo:.1f}-{upside_hi:.1f} bn/yr (~₹{round(upside_lo*86*1e3):,}-{round(upside_hi*86*1e3):,} cr)** "
             "if adopted system-wide.")
    L.append(f"- **Full crude-to-chemicals (COTC)** — a purpose-built complex converts up to "
             f"**{PETCHEM['cotc_chem_yield']*100:.0f}% of crude to chemicals** (vs <{PETCHEM['std_chem_yield']*100:.0f}% "
             f"standalone) and earns **${clo}-{chi}/bbl** vs **${flo}-{fhi}/bbl** for a fuels refinery — a "
             "step-change, capturing the whole petchem chain, but capital-heavy.")
    L.append(f"- Petrochemicals are set to be the **largest driver of oil-demand growth by 2030** (demand "
             f"~1.5× GDP, {PETCHEM['demand_cagr'][0]*100:.0f}-{PETCHEM['demand_cagr'][1]*100:.0f}% CAGR), so the "
             "value is durable even as transport fuels plateau.\n")
    L.append("**India read:** India is still broadly a *net importer* of petrochemicals (exports bulk "
             "polymers, imports specialty chemicals/feedstock), so integration fixes a deficit *and* lifts "
             "GRM at once. RIL Jamnagar already runs high chemical integration; HMEL Bathinda, ONGC-OPaL, "
             "HPCL-Barmer and BPCL/IOCL COTC plans are the pipeline. The +$1.5-2/bbl is the realistic "
             "near-term GRM prize on the existing base; COTC is the long-game re-rating.\n")

    L.append("## 7. Evaluation — strengths, risks, and where to lean\n")
    L.append("**Strengths:** scale (4th-largest, ~%d MMT, expanding toward ~450 MMT by 2030); Jamnagar-class "
             "complexity that lifts light-product yield and GRM; a proven forex-earning export machine that "
             "offsets ~a third of the crude bill; flexible crude sourcing.\n" % CAPACITY_MMT)
    L.append("**Risks:** (i) EU ban + sanctions erasing the Russian-discount edge and the premium EU outlet; "
             "(ii) GRMs normalised to mid-single digits; (iii) Asian overcapacity (China mega-refineries) "
             "compressing product cracks; (iv) domestic fuel-demand peak as EVs/ethanol scale (see sibling "
             "models) shrinking the captive base; (v) crude-import bill hostage to Brent + rupee.\n")
    L.append("**Where to lean:** diversify crude (Mideast/US/Latin America, cut Russian dependence to stay "
             "EU-compliant); pivot exports toward Africa, Mideast and Asia as Europe closes; accelerate "
             "**crude-to-chemicals / petrochem integration** to move up the value chain and hedge the fuel "
             "peak; and keep the ethanol/EV domestic shift working *for* the export book — every litre of "
             "petrol ethanol frees at home is a litre that can be exported at global cracks (~$24/bbl MS).\n")

    L.append("## 8. Bottom line\n")
    L.append(f"India's refining sector is a **strategic value-add machine bolted onto a huge energy import "
             f"bill**: it turns ~${RR['crude_import_usdbn']:.0f} bn of crude into ~${HS27['exports_2024']:.0f} bn "
             "of product exports plus the domestic supply, earning the GRM as forex and softening a deficit "
             "that is already half the country's trade gap. The machine still works — cracks are healthy — "
             "but its recent *super-normal* profits rested on cheap Russian crude and open European markets, "
             "**both of which closed in 2025-26**. The next leg of value has to come from crude "
             "diversification, new export geographies, and moving from fuels into petrochemicals.\n")

    L.append("## Sources & how to drill deeper\n")
    L.append("- **DGCIS / Tradestat** (`tradestat.commerce.gov.in`) — HS-code trade: crude HS-2709, products "
             "HS-2710, gas HS-2711; HS-27 aggregate used above. **Niryat** (`niryat.gov.in`) — commodity- & "
             "country-wise export dashboard for the same data.")
    L.append("- **PPAC Ready Reckoner** — crude import / product export (Table 4.11), GRM (4.7), capacity (4.1).")
    L.append("- **Argus / Platts** — Mogas 92 & gasoil cracks, GRM commentary; CareEdge/analysts for GRM bands.\n")
    L.append("---\n*Synthesis of official trade data + market reporting; analytical evaluation, not "
             "investment advice. HS-27/PPAC differ in scope (mineral-fuels CY vs petroleum-products FY).*\n")
    (OUT / "refining_trade_analysis.md").write_text("\n".join(L))

    print(f"HS-27 (CY2024): imports ${HS27['imports_2024']:.1f}bn | exports ${HS27['exports_2024']:.1f}bn "
          f"| net −${net_hs27:.1f}bn = {hs27_share_of_deficit*100:.0f}% of ${trade_deficit:.0f}bn trade deficit")
    print(f"Arbitrage: crude ~${crude_per_bbl:.0f}/bbl -> products ~${prod_per_bbl:.0f}/bbl "
          f"(~${implied_valadd:.0f}/bbl value-add); MS crack ${MARKET['ms_crack_sing92_brent']}/bbl")
    print(f"PPAC net oil bill FY25: import ${RR['total_oil_import_usdbn']:.0f}bn - product export "
          f"${RR['product_export_usdbn']:.0f}bn = ~${RR['total_oil_import_usdbn']-RR['product_export_usdbn']:.0f}bn "
          f"(exports offset {RR['product_export_usdbn']/RR['total_oil_import_usdbn']*100:.0f}%)")
    bbl_yr = THROUGHPUT_MMT*1e6*BBL_PER_T_CRUDE
    print(f"Petchem GRM upside (Digital Refining): +${PETCHEM['marginal_uplift_bbl'][0]}-{PETCHEM['marginal_uplift_bbl'][1]}/bbl "
          f"= ~${bbl_yr*PETCHEM['marginal_uplift_bbl'][0]/1e9:.1f}-{bbl_yr*PETCHEM['marginal_uplift_bbl'][1]/1e9:.1f}bn/yr system-wide; "
          f"full COTC ${PETCHEM['cotc_margin_bbl'][0]}-{PETCHEM['cotc_margin_bbl'][1]}/bbl vs fuels ${PETCHEM['fuels_margin_bbl'][0]}-{PETCHEM['fuels_margin_bbl'][1]}")
    print(f"Russian crude share {MARKET['russian_share_2023']*100:.0f}%->{MARKET['russian_share_jan26']*100:.0f}%; "
          f"EU-ban export drop {MARKET['eu_ban_export_drop']*100:.0f}%")
    print("Wrote outputs/refining_trade_analysis.md + refining_trade_summary.csv")


if __name__ == "__main__":
    main()
