#!/usr/bin/env python3
"""Which petrochemical products India imports that could be substituted with
domestic petroleum feedstock (naphtha + reformate aromatics). Product tree from
the ICIS Petrochemicals Flowchart (crude -> building blocks -> end products);
import dependence/values from Ministry of Chemicals 'Statistics at a Glance',
DGCIS/Tradestat and industry reporting (2023-25). Pure stdlib.

Petrol link: naphtha (co-produced with petrol) steam-cracks to ethylene/propylene/
C4/pygas; catalytic reformate (a petrol octane stream) is the BTX-aromatics source
(benzene, toluene, xylenes). Every block below traces to those petrol-range cuts.
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"; OUT.mkdir(parents=True, exist_ok=True)
TOTAL_CHEM_IMPORT_CR = 631898          # FY24-25 chem+petchem imports (excl pharma/fert), ₹ cr
USD_INR = 86.0; CR = 1e7

# building block  -> feedstock root (all petrol-range unless noted)
BLOCKS = {
    "Ethylene":  "naphtha / ethane (steam cracker)",
    "Propylene": "naphtha crack / FCC / PDH",
    "C4 (butadiene/isobutylene)": "naphtha crack C4 stream",
    "Benzene":   "reformate / pygas aromatics",
    "Toluene":   "reformate aromatics",
    "Xylenes":   "reformate aromatics",
    "Methanol":  "syngas (gas/coal) — weak petrol link",
}

# product, block, import_dependence, approx import value ₹cr (None=indicative),
# petrol_link, note, primary 8-digit ITC-HS code(s) (verify on Tradestat/DGFT ITC-HS 2022)
PRODUCTS = [
    # ── Ethylene chain ──
    ("Polyethylene (LDPE/HDPE/LLDPE)", "Ethylene", "~25-40%", 22000, "High", "3.1 MT imported 2024 — India = world's #2 PE importer", "3901 10 10 / 3901 20 00 / 3901 40 00"),
    ("PVC resin (via EDC/VCM + chlorine)", "Ethylene", "~55-75%", 19000, "High", "Biggest polymer gap; capacity ~2.5x by FY30", "3904 10 10 / 3904 21 90 / 3904 22 90"),
    ("Mono-ethylene glycol (MEG)", "Ethylene", "high", 6666, "High", "Polyester/PET chain", "2905 31 00"),
    ("Styrene monomer (via ethylbenzene + benzene)", "Ethylene", "~100%", 10150, "High", "≈ no domestic SM capacity", "2902 50 00 (→ PS 3903 19 90)"),
    ("Vinyl acetate monomer (VAM)", "Ethylene", "high", 2000, "High", "Adhesives, EVA, films — largely imported", "2915 32 00 (→ EVA 3901 30 00)"),
    ("Ethanolamines (MEA/DEA/TEA)", "Ethylene", "partial", None, "Med", "Gas treating, surfactants", "2922 11 00 / 2922 12 00 / 2922 15 00"),
    # ── Propylene chain ──
    ("Polypropylene (PP)", "Propylene", "~20-25%", 13000, "High", "1.6 MT imported 2024 (#3 globally); capacity 1.7-1.8x by FY30", "3902 10 00"),
    ("Acrylonitrile (ACN)", "Propylene", "~100%", 3000, "High", "For ABS, acrylic fibre, NBR — no domestic ACN", "2926 10 00"),
    ("Phenol + Acetone (via cumene)", "Propylene", "high", 4000, "High", "Cumene ← benzene + propylene", "2907 11 10 (phenol) / 2914 11 00 (acetone)"),
    ("Polyols → Polyurethane", "Propylene", "high", 4000, "High", "Propylene-oxide route; PU foams", "3907 20 10 (polyols) / 3909 50 00 (PU)"),
    ("Oxo-alcohols (2-EH, n-butanol)", "Propylene", "high", 4000, "High", "Plasticiser alcohols — largely imported", "2905 16 20 (2-EH) / 2905 13 00 (n-BuOH)"),
    ("Acrylic acid → superabsorbents (SAP)", "Propylene", "high", 2500, "High", "Diapers/hygiene — imported", "2916 11 10 (acid) / 3906 90 90 (SAP)"),
    ("PMMA / MMA (acrylic)", "Propylene", "high", 1500, "Med", "Optical/acrylic sheet", "2916 14 10 (MMA) / 3906 10 10 (PMMA)"),
    ("Isopropanol (IPA)", "Propylene", "partial", None, "Med", "Solvent", "2905 12 20"),
    # ── C4 chain ──
    ("Butadiene → SBR/PBR/NBR rubber", "C4 (butadiene/isobutylene)", "high", 6000, "High", "Synthetic rubber — big import", "2901 24 10 (BD) / 4002 19 / 4002 20 00 (PBR)"),
    ("BDO → PBT / spandex", "C4 (butadiene/isobutylene)", "high", 2000, "Med", "Engineering plastic/fibre", "2905 39 20 (BDO) / 3907 99 90 (PBT)"),
    # ── Benzene chain (reformate) ──
    ("Bisphenol-A → Polycarbonate (PC)", "Benzene", "~90-100%", 5000, "High", "Engineering plastic — near-fully imported", "2907 23 00 (BPA) / 3907 40 00 (PC)"),
    ("Epoxy resins (via BPA)", "Benzene", "high", 4000, "High", "Coatings, composites", "3907 30 00"),
    ("Caprolactam → Nylon-6 / Adipic → Nylon-6,6", "Benzene", "high", 4000, "High", "Via cyclohexane; nylon/fibre", "2933 71 00 (capro) / 3908 10 10 (nylon-6)"),
    ("Aniline → MDI (polyurethane)", "Benzene", "~85-90%", 5000, "High", "Rigid PU foam — largely imported", "2921 41 90 (aniline) / 2929 10 20 (MDI)"),
    ("LAB (alkylbenzene) → surfactants", "Benzene", "partial", None, "Med", "Detergents — India fairly self-sufficient", "3817 00 11 (LAB) / 3402 xx (surfactants)"),
    # ── Toluene chain ──
    ("TDI (toluene di-isocyanate)", "Toluene", "~85-90%", 4000, "High", "Flexible PU foam — largely imported", "2929 10 10"),
    # ── Xylenes chain (reformate) ──
    ("Paraxylene → PTA/DMT → PET/polyester", "Xylenes", "partial", 5000, "High", "India strong (RIL) but net-imports some grades", "2902 43 00 (PX) / 2917 36 00 (PTA) / 3907 61 00 (PET)"),
    ("Orthoxylene → Phthalic anhydride → plasticisers/UPR", "Xylenes", "partial", 2000, "High", "Plasticisers, unsat. polyester resin", "2917 35 00 (PAN) / 3907 91 00 (UPR)"),
    # ── Methanol chain (weak petrol link) ──
    ("Methanol → formaldehyde/acetic acid/MTBE", "Methanol", "~90%", 7524, "Low", "Gas/coal-based — petrol link only via petcoke COTC", "2905 11 00 (MeOH) / 2915 21 00 (acetic acid)"),
]


def main():
    firm = [p for p in PRODUCTS if p[3] is not None]
    high = [p for p in PRODUCTS if p[4] == "High"]
    high_petrol_val = sum(p[3] for p in PRODUCTS if p[4] == "High" and p[3])
    all_val = sum(p[3] for p in PRODUCTS if p[3])

    with (OUT / "petchem_import_substitution.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["product", "hsn_8digit", "building_block", "feedstock_root", "import_dependence",
                    "import_value_cr", "import_value_usdbn", "petrol_link", "note"])
        for name, blk, dep, cr, link, note, hsn in PRODUCTS:
            w.writerow([name, hsn, blk, BLOCKS[blk], dep, cr or "",
                        round(cr*CR/USD_INR/1e9, 2) if cr else "", link, note])

    L = []
    L.append("# Petrochemical imports India can substitute from petrol/naphtha — the full ICIS tree\n")
    L.append("Product tree from the **ICIS Petrochemicals Flowchart** (crude → building blocks → end "
             "products), scored for India's import dependence. India imports **₹%s cr (~$%.0f bn)** of "
             "chemicals & petrochemicals a year; the list below is the slice whose feedstock is the "
             "**petrol-range refinery streams** India already makes — naphtha (→ ethylene/propylene/C4) and "
             "reformate aromatics (→ benzene/toluene/xylenes).\n"
             % (f"{TOTAL_CHEM_IMPORT_CR:,}", TOTAL_CHEM_IMPORT_CR*CR/USD_INR/1e9))
    L.append(f"**{len(PRODUCTS)} import-relevant products across 7 building blocks** — expanded from the "
             "headline polymers using the flowchart's full downstream chain.\n")

    # group by block
    for blk, feed in BLOCKS.items():
        rows = [p for p in PRODUCTS if p[1] == blk]
        L.append(f"## {blk}  ←  {feed}\n")
        L.append("| Product | HSN (8-digit ITC-HS) | Import dep. | Import value | Link |")
        L.append("|---|---|---|--:|:--:|")
        for name, _, dep, cr, link, note, hsn in sorted(rows, key=lambda p: -(p[3] or 0)):
            val = f"₹{cr:,} cr (${cr*CR/USD_INR/1e9:.1f} bn)" if cr else "*indic.*"
            L.append(f"| {name} | `{hsn}` | {dep} | {val} | {link} |")
        L.append("")

    L.append("## The petrol → petrochemicals substitution prize\n")
    L.append(f"- **High-petrol-link substitutable imports quantified ≈ ₹{high_petrol_val:,} cr "
             f"(~${high_petrol_val*CR/USD_INR/1e9:.0f} bn/yr)**; with the indicative long-tail, the "
             "petroleum-feedstock-linked chemical import bill is well into double-digit $ bn.")
    L.append("- **Newly surfaced via the flowchart (missed by a headline-polymer view):** polycarbonate, "
             "MDI & TDI (isocyanates → polyurethane), caprolactam/nylon, phenol/bisphenol-A, acrylonitrile, "
             "butadiene & synthetic rubber, oxo-alcohols/2-EH, VAM, epoxy, PBT/BDO — most **~85-100% "
             "imported** and all rooted in benzene/propylene/C4 from naphtha & reformate.")
    L.append("- **The engineering-plastics & PU cluster** (PC, nylon, MDI/TDI, epoxy, ABS, PBT) is India's "
             "deepest, highest-value gap — exactly the higher-margin end of the ICIS tree, and the natural "
             "target for crude-to-chemicals.\n")

    L.append("## Why it ties back to fuel\n")
    L.append("Every block above starts from **naphtha or reformate** — the same petrol-range material India "
             "**burns as petrol** or **exports as fuel** at ~$85/bbl. As ethanol/EV cap fuel demand and free "
             "that volume (E20 ≈ 10.8 bn L, E30 ≈ 16 bn L in the sibling models), redirecting it into these "
             "products **erases imports and captures the petrochemical premium** (Digital Refining: +$1.5-2/"
             "bbl marginal GRM, $60-80/bbl full COTC) instead of a thin fuel margin.\n")

    L.append("## Caveats\n")
    L.append("- **HSN codes are 8-digit ITC-HS** (India's tariff schedule) — the primary code per product; "
             "polymers sit in **Ch 39**, monomers/intermediates in **Ch 29**, synthetic rubber in **Ch 40**. "
             "Verify the exact current subheading on **Tradestat / DGFT ITC-HS 2022** (last two digits are "
             "revised periodically, and grades split across sub-codes) before pulling values.")
    L.append("- Import values are approximate (MoC Statistics-at-a-Glance / DGCIS / industry, 2023-25); the "
             "long-tail (*indic.*) rows are directional. Query the HSN codes above on Tradestat/Niryat for "
             "exact product×year import value & origin; the ICIS flowchart gives the chain, not the tonnage.")
    L.append("- Methanol and some surfactants are gas-based (weak petrol link). Substitution also needs "
             "downstream units (crackers, aromatics, chlor-alkali, isocyanate plants), not just feedstock. "
             "₹→$ at ₹86.\n")
    L.append("---\n*Import-substitution map from the ICIS petrochemicals tree + official trade data; "
             "indicative, not a project plan.*\n")
    (OUT / "petchem_import_substitution.md").write_text("\n".join(L))

    print(f"{len(PRODUCTS)} products across {len(BLOCKS)} building blocks (ICIS flowchart-derived)")
    print(f"High-petrol-link quantified substitutable imports ≈ ₹{high_petrol_val:,} cr (~${high_petrol_val*CR/USD_INR/1e9:.0f} bn/yr)")
    print("Product / HSN (8-digit) / dependence / value:")
    for name, blk, dep, cr, link, note, hsn in PRODUCTS:
        if link == "High":
            print(f"  {name[:40]:40s} {hsn:42s} {dep:14s} {('₹'+format(cr,',')+' cr') if cr else 'indic.'}")
    print("Wrote outputs/petchem_import_substitution.md + .csv")


if __name__ == "__main__":
    main()
