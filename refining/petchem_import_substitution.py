#!/usr/bin/env python3
"""Which petrochemical imports India can substitute with domestic petroleum-
feedstock (naphtha + reformate aromatics) — the crude-to-chemicals import-
substitution prize. Values from Ministry of Chemicals 'Statistics at a Glance',
DGCIS/Tradestat and industry reporting (2023-25). Pure stdlib.

The petrol link: naphtha (co-produced with petrol) is the steam-cracker feedstock
for ethylene/propylene; catalytic reformate (a petrol octane component) is the
aromatics source (benzene->styrene, paraxylene->PET). Diverting these petrol-range
streams into petrochemicals — and ethanol blending frees exactly this material —
substitutes the imports below.
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"; OUT.mkdir(parents=True, exist_ok=True)

# context (Ministry of Chemicals & Petrochemicals)
TOTAL_CHEM_IMPORT_CR = 631898          # FY24-25 chem+petchem imports (excl pharma, fert), ₹ cr (~$74bn)
PLASTICS_IMPORT_USDBN = 22.0           # 2025 (HS-39)

# product, import_dependence, approx import value ₹cr, feedstock, petrol-linkage
# (values approximate: MoC Statistics-at-a-Glance / DGCIS / industry 2023-25)
PRODUCTS = [
    ("PVC (poly-vinyl chloride)", "~55-75%", 19000, "ethylene (naphtha) + chlorine → EDC/VCM", "High", "Biggest single polymer gap; capacity set to rise ~2.5x by FY30"),
    ("Polyethylene (HDPE/LLDPE/LDPE)", "~20%", 13000, "ethylene ← naphtha/ethane cracking", "High", "~1.4 MT imported of ~7 MT demand"),
    ("Polypropylene (PP)", "~20% (closing)", 11000, "propylene ← refinery FCC / naphtha", "High", "1.2 MT+ imported (2025, record); capacity 1.7-1.8x by FY30 could end imports"),
    ("Styrene monomer (SM)", "~100%", 10150, "benzene (reformate) + ethylene", "High", "No domestic SM plant historically — near-fully imported"),
    ("Mono-ethylene glycol (MEG)", "high", 6666, "ethylene → ethylene-oxide → MEG", "High", "Polyester/PET chain"),
    ("Methanol", "~90%", 7524, "syngas (gas / petcoke gasification)", "Low-Med", "Mostly gas-based — petrol link only via petcoke/COTC"),
    ("PTA / paraxylene / PET", "partial", 5000, "paraxylene ← catalytic reformate aromatics", "High", "India has PX/PTA (RIL) but still net-imports some grades"),
    ("ABS / SAN / polystyrene / others", "partial", 8000, "styrene + butadiene/acrylonitrile", "Med", "Engineering-plastic gap"),
]
CR = 1e7; USD_INR = 86.0


def main():
    petrol_linked = [p for p in PRODUCTS if p[4] in ("High", "Med")]
    sub_cr = sum(p[2] for p in petrol_linked)
    high_cr = sum(p[2] for p in PRODUCTS if p[4] == "High")

    with (OUT / "petchem_import_substitution.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["product", "import_dependence", "import_value_cr", "import_value_usdbn",
                    "feedstock", "petrol_linkage", "note"])
        for name, dep, cr, feed, link, note in PRODUCTS:
            w.writerow([name, dep, cr, round(cr*CR/USD_INR/1e9, 2), feed, link, note])

    L = []
    L.append("# Petrochemical imports India can substitute with domestic petrol/naphtha feedstock\n")
    L.append("India imports **₹%s cr (~$%.0f bn) of chemicals & petrochemicals** a year (excl. pharma/"
             "fertilizer; MoC) and **~$%.0f bn of plastics** (HS-39, 2025). Much of it is polymers and "
             "intermediates whose feedstock is exactly what India's refineries make: **naphtha** "
             "(co-produced with petrol; the steam-cracker feed for ethylene/propylene) and **reformate "
             "aromatics** (a petrol octane component; the source of benzene→styrene and paraxylene→PET). "
             "Redirecting those petrol-range streams into petrochemicals — crude-to-chemicals — substitutes "
             "the imports below.\n" % (f"{TOTAL_CHEM_IMPORT_CR:,}", TOTAL_CHEM_IMPORT_CR*CR/USD_INR/1e9, PLASTICS_IMPORT_USDBN))

    L.append("## 1. The major substitutable imports\n")
    L.append("| Product | Import dependence | Import value | Feedstock (petrol-linked) | Link |")
    L.append("|---|---|--:|---|:--:|")
    for name, dep, cr, feed, link, note in sorted(PRODUCTS, key=lambda p: -p[2]):
        L.append(f"| **{name}** | {dep} | ₹{cr:,} cr (${cr*CR/USD_INR/1e9:.1f} bn) | {feed} | {link} |")
    L.append("")
    L.append(f"- **Directly petroleum-feedstock-linked imports ≈ ₹{sub_cr:,} cr (~${sub_cr*CR/USD_INR/1e9:.0f} bn/yr)** "
             f"— of which the high-linkage core (PVC, PE, PP, styrene, MEG, PX/PET) is ≈ ₹{high_cr:,} cr.")
    L.append("- **PVC is the single biggest gap** (~55-75% imported): ethylene + chlorine, a clear domestic "
             "cracker + chlor-alkali opportunity. **Styrene is ~fully imported** — India has essentially no "
             "styrene-monomer capacity, yet benzene (its feedstock) sits in the petrol reformate pool.\n")

    L.append("## 2. The feedstock loop — petrol → petrochemicals\n")
    L.append("| Petrol-range refinery stream | Cracks/reforms to | Substitutes import of |")
    L.append("|---|---|---|")
    L.append("| Naphtha (steam cracker) | ethylene, propylene | PE, PP, PVC (via EDC), MEG |")
    L.append("| Reformate / aromatics (BTX) | benzene, paraxylene | styrene, PTA→PET, ABS |")
    L.append("| Refinery propylene (FCC) | propylene | polypropylene directly |")
    L.append("")
    L.append("This is the same molecule India currently either **burns as petrol** or **exports as fuel** at "
             "~$85/bbl. Cracked into polymers it fetches the petrochemical premium instead (Digital Refining: "
             "+$1.5-2/bbl GRM marginal, $60-80/bbl full COTC) **and** erases an import — a double win.\n")

    L.append("## 3. The strategic loop with ethanol & the fuel peak\n")
    L.append("The pieces connect: **ethanol blending frees petrol-range volume** (E20 ≈ 10.8 bn L, E30 ≈ 16 "
             "bn L in the sibling models); as EVs and ethanol cap domestic fuel demand, that freed naphtha/"
             "reformate is better **cracked into import-substituting petrochemicals** than exported as low-"
             "margin fuel. It turns three problems into one answer — a fuel-demand peak, a ~$74 bn chem "
             "import bill, and a normalised refining margin — via **crude-to-chemicals**.\n")

    L.append("## 4. Reality check\n")
    L.append("- Capacity is already responding: **PP capacity ~1.7-1.8x by FY30** (could end PP imports), "
             "**PVC ~2.5x** — the substitution is underway but demand grows too, so imports persist near-term.")
    L.append("- Not all imports are petrol-substitutable: **methanol** is largely gas/syngas-based (low petrol "
             "link); some specialty/engineering chemicals need dedicated units, not just a cracker.")
    L.append("- Import values are approximate (MoC Statistics-at-a-Glance / DGCIS / industry, 2023-25; "
             "product-level figures move with price). Use Tradestat HS-39 (plastics) and HS-29 (organic "
             "chemicals) for exact product×year values. ₹→$ at ₹86.\n")
    L.append("---\n*Import-substitution scan from official chem-trade data + feedstock chemistry; indicative, "
             "not a project plan.*\n")
    (OUT / "petchem_import_substitution.md").write_text("\n".join(L))

    print(f"Total chem+petchem import ₹{TOTAL_CHEM_IMPORT_CR:,} cr (~${TOTAL_CHEM_IMPORT_CR*CR/USD_INR/1e9:.0f} bn); plastics ~${PLASTICS_IMPORT_USDBN} bn")
    print(f"Petroleum-feedstock-linked substitutable imports ≈ ₹{sub_cr:,} cr (~${sub_cr*CR/USD_INR/1e9:.0f} bn); high-link core ₹{high_cr:,} cr")
    print("Top substitutable (by value):")
    for name, dep, cr, feed, link, note in sorted(PRODUCTS, key=lambda p: -p[2])[:5]:
        print(f"  {name:34s} dep {dep:14s} ₹{cr:>6,} cr  [{link}]")
    print("Wrote outputs/petchem_import_substitution.md + .csv")


if __name__ == "__main__":
    main()
