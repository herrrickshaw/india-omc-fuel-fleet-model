#!/usr/bin/env python3
"""India's forex spend on essential imports, and the case for a PLI for chemicals.

Import data: DGCIS/Tradestat (HS-27 CY2024) + PPAC RR (FY25) + trade reporting.
PLI context: PIB / FM statements / Ministry of Chemicals. The argument: energy,
chemicals, edible oil and fertiliser are India's essential dollar drains, each
with an import-substitution lever — and chemicals is the only large one still
outside the PLI umbrella. Pure stdlib.
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"; OUT.mkdir(parents=True, exist_ok=True)
TOTAL_IMPORTS_USDBN = 718.16       # India total imports CY2024 (DGCIS)

# category, US$ bn, essential?, substitution lever, has_PLI
IMPORTS = [
    ("Crude oil", 137, True, "Ethanol/EV demand cap · domestic E&P (deepwater/Andaman)", "no (ethanol EBP)"),
    ("Electronics (HS-85)", 90, False, "PLI electronics/semiconductors — working", "YES"),
    ("Gold & precious stones", 60, False, "Discretionary — duty/financialisation, not substitutable", "n/a"),
    ("Chemicals (organic HS-29 + plastics HS-39)", 47, True, "Crude-to-chemicals + freed ethanol feedstock", "NO — the gap"),
    ("Coal & coke", 32, True, "Domestic coal · renewables · CBG", "no"),
    ("LNG + LPG (petroleum gases)", 30, True, "Domestic gas · CBG (SATAT)", "no"),
    ("Edible / vegetable oils", 17, True, "National Mission on Edible Oils / oilseeds", "no (mission)"),
    ("Fertilisers", 11, True, "Domestic urea/nano-urea · Nutrient-based", "no (subsidy)"),
]

# existing PLI programme (PIB)
PLI_SECTORS = 14
PLI_OUTLAY_CR = 197291             # ₹ ~1.97 lakh cr (2021, 14 sectors)
USD_INR = 86.0; CR = 1e7

# proposed chemicals PLI (Ministry of Chemicals, per reporting)
CHEM_PLI = {
    "incentive_pct": "4-6%", "focus": "import substitution of key intermediates",
    "substitutable_petchem_cr": 125000,   # from petchem_import_substitution (~$15bn)
    "moc_chem_import_cr": 631898,          # MoC total chem+petchem import FY25 (~$74bn)
}


def main():
    ess = [r for r in IMPORTS if r[2]]
    ess_total = sum(r[1] for r in ess)
    energy = sum(r[1] for r in IMPORTS if r[0] in ("Crude oil", "Coal & coke", "LNG + LPG (petroleum gases)"))

    with (OUT / "forex_essentials.csv").open("w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["category", "usd_bn", "share_of_imports_pct", "essential", "substitution_lever", "has_pli"])
        for name, v, essflag, lever, pli in IMPORTS:
            w.writerow([name, v, round(100*v/TOTAL_IMPORTS_USDBN, 1), essflag, lever, pli])

    L = []
    L.append("# India's forex on essentials — and the missing lever: a PLI for chemicals\n")
    L.append(f"India spent **${TOTAL_IMPORTS_USDBN:.0f} bn on imports (CY2024, DGCIS)**. Strip out gold and "
             "electronics and what remains is a bill of *essentials* the economy cannot switch off — energy, "
             "chemicals, edible oil, fertiliser — each a structural dollar drain with an import-substitution "
             "lever. This sizes that bill and argues the one big gap: **chemicals has no PLI.**\n")

    L.append("## 1. The forex bill — where the dollars go\n")
    L.append("| Import (CY2024) | US$ bn | % of imports | Essential? | Substitution lever | Under PLI? |")
    L.append("|---|--:|--:|:--:|---|:--:|")
    for name, v, essflag, lever, pli in IMPORTS:
        L.append(f"| {name} | {v} | {100*v/TOTAL_IMPORTS_USDBN:.0f}% | {'✅' if essflag else '—'} | {lever} | {pli} |")
    L.append("")
    L.append(f"- **Essential-import forex ≈ ${ess_total} bn/yr** (~{100*ess_total/TOTAL_IMPORTS_USDBN:.0f}% of all "
             f"imports) — of which **energy is ${energy} bn** (crude + coal + gas) and **chemicals ${47} bn**.")
    L.append("- Energy, edible oil and fertiliser each already have a substitution push (ethanol/EV, edible-oil "
             "mission, domestic fertiliser). **Chemicals — the 4th-largest essential drain and the fastest-"
             "growing — is the only one without a Production-Linked Incentive.**\n")

    L.append("## 2. The chemicals gap\n")
    L.append(f"- India's **14-sector PLI programme (₹{PLI_OUTLAY_CR:,} cr / ~${PLI_OUTLAY_CR*CR/USD_INR/1e9:.0f} bn)** "
             "covers electronics, pharma, autos, solar, textiles, food, telecom, steel and more — **chemicals & "
             "petrochemicals are not among them.**")
    L.append(f"- Yet India's chemical import bill is **₹{CHEM_PLI['moc_chem_import_cr']:,} cr (~$74 bn, MoC FY25)**, "
             f"with **~₹{CHEM_PLI['substitutable_petchem_cr']:,} cr (~$15 bn) of it petroleum-feedstock-substitutable** "
             "(PVC, PE, PP, styrene, polycarbonate, MDI/TDI, acrylonitrile, MEG — see the HSN-coded import tree).")
    L.append("- The template works: the **electronics PLI turned India from a mobile importer into a net "
             "exporter** in ~4 years. The same instrument, pointed at the chemical import list, is the obvious "
             "next move.\n")

    L.append("## 3. The case for a chemicals PLI (official intent)\n")
    L.append("- **FM Nirmala Sitharaman** has stated the government **\"will consider a PLI scheme for chemicals "
             "and petrochemicals\"** — the intent is on record.")
    L.append("- The **Ministry of Chemicals & Fertilizers is formulating** a scheme focused on **import "
             f"substitution of key intermediates**, with a likely **{CHEM_PLI['incentive_pct']} incentive on "
             "incremental production** (per industry reporting).")
    L.append("- **PIB** records the government redrafting the Petroleum, Chemicals & Petrochemicals policy; "
             "**PCPIRs** (Petroleum, Chemicals & Petrochemicals Investment Regions) already provide the "
             "industrial-cluster backbone a PLI can plug into.")
    L.append("- **Specialty chemicals grow ~12% CAGR** — a PLI would capture that value at home instead of "
             "importing it.\n")

    L.append("## 4. Proposed design (grounded in this analysis)\n")
    L.append("| Lever | Proposal |")
    L.append("|---|---|")
    L.append("| **Target list** | The HSN-coded, high-import-dependence products: PVC `3904`, PE `3901`, PP `3902`, styrene `2902 50`, polycarbonate `3907 40`, MDI/TDI `2929 10`, acrylonitrile `2926 10`, MEG `2905 31`, epoxy `3907 30`, nylon `3908 10` |")
    L.append("| **Priority** | The ~85-100%-imported cluster first — polycarbonate, MDI/TDI, styrene, ACN — engineering plastics & polyurethanes (deepest gap, highest value) |")
    L.append(f"| **Incentive** | {CHEM_PLI['incentive_pct']} on incremental production, tapering as capacity matures |")
    L.append("| **Feedstock link** | Tie to crude-to-chemicals / naphtha crackers and the ethanol-freed petrol pool — rupee feedstock displacing dollar polymers |")
    L.append("| **Cluster** | Anchor in PCPIRs; single-window + duty rationalisation alongside |")
    L.append("")
    sub = CHEM_PLI["substitutable_petchem_cr"]
    L.append(f"**The prize.** Substituting even half of the **~₹{sub:,} cr (~$15 bn)** petroleum-linked "
             f"chemical imports saves **~$7-8 bn/yr of forex** — comparable to the entire ethanol programme's "
             "freed-petrol value, and permanent. A 4-6% PLI on that incremental output is a fraction of the "
             "forex it protects.\n")

    L.append("## 5. The through-line\n")
    L.append("India's essential-import forex bill is ~$274 bn, and the levers are being pulled everywhere except "
             "the chemical drain. **Ethanol frees petrol → the freed naphtha cracks into the very chemicals "
             "India imports → a PLI makes that domestic production bankable.** Rupee feedstock, rupee incentive, "
             "dollar imports substituted — the same rupee-vs-dollar logic as ethanol, applied one link "
             "downstream. Chemicals is the missing piece of a coherent import-substitution stack.\n")

    L.append("## Sources\n")
    L.append("- **DGCIS / Tradestat** — HS-27 & import basket (CY2024); **PPAC RR** — crude import (FY25); "
             "**MoC Statistics-at-a-Glance** — chemical imports ₹6.32 lakh cr.")
    L.append("- **PIB** — Petroleum/Chemicals policy redraft (PRID 1863754); **FM Nirmala Sitharaman** — "
             "'will consider PLI for chemicals & petrochemicals'; Ministry of Chemicals scheme formulation "
             "(industry reporting, 4-6% incentive); Invest India — chemicals sector.\n")
    L.append("---\n*Policy analysis from official trade data + public statements; indicative figures mix CY/FY "
             "and HS scopes — verify on Tradestat/PIB before citing exact values.*\n")
    (OUT / "forex_essentials_pli_case.md").write_text("\n".join(L))

    print(f"Total imports ${TOTAL_IMPORTS_USDBN:.0f} bn (CY2024)")
    print(f"Essential-import forex ≈ ${ess_total} bn ({100*ess_total/TOTAL_IMPORTS_USDBN:.0f}%); energy ${energy} bn; chemicals $47 bn")
    print(f"14-sector PLI ₹{PLI_OUTLAY_CR:,} cr — chemicals EXCLUDED; chem import $74bn (~₹{CHEM_PLI['moc_chem_import_cr']:,} cr), ~$15bn substitutable")
    print("Case: FM on record 'will consider PLI for chemicals'; MoC formulating 4-6% import-substitution scheme")
    print("Wrote outputs/forex_essentials_pli_case.md + forex_essentials.csv")


if __name__ == "__main__":
    main()
