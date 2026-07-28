#!/usr/bin/env python3
"""Match the E20-E30 blend scenarios against ethanol SUPPLY: installed
distillery capacity, the CareEdge overcapacity finding, the DFPD sanction
register, the FCI rice leg, and the NCDC cooperative-sugar-mill scheme.

Question: can supply serve the higher blends the Volume Dividend scenarios
propose (E25/E27/E30 at parity prices) — and does the blend walk fix the
overcapacity the rating agencies are flagging?

Sources (all figures cited inline):
  CareEdge Ratings, "E85 Impact: Ethanol Overcapacity to Persist" (14 May
    2026): installed ~2,000 cr L + ~400 cr L by FY27; E20 fuel demand ~1,100
    cr L; non-fuel 300-350 cr L; only ~60% of offered ethanol absorbed;
    utilisation to stay 65-75% for ~3 years; state skew MH +277 / TN -77 cr L.
  DFPD ISS annexures (via E20_to_E30_Stakeholder_Impact_v2_FCI_patched.xlsx,
    'DFPD Capacity Benchmark'): 1,212 approved projects, 1,37,282 KLPD =
    4,530 cr L/yr annualised sanctioned; avg 113 KLPD / Rs 96.8 cr loan.
  FCI leg (same workbook, 'FCI Availability & Risk' + FCI-warehouse repo
    ethanol_allocation.csv): 7.2 MMT/yr rice allocation, 65% lifting lever,
    Jul-2023 suspension precedent -> effective ~211 cr L (~3.9 blend ppt).
  NCDC coop-sugar-mill scheme (Ministry of Cooperation, RS reply): Rs 10,005
    cr disbursed to 56 CSMs — Rs 9,657 cr working capital, Rs 251.4 cr
    ethanol plants, Rs 97.1 cr cogen.
  Digital-twin layer 24d: UP ~236-250 cr L capacity, ~50 cr L added in 2025
    alone, grain wave on DFPD subvention.
  This repo: petrol_demand_forecast.py (demand-grown E30 needs 2,173 cr L by
    FY30-31 base case); price_parity_scenarios.py (blend fractions & pools).

Pure stdlib. Outputs: outputs/ethanol_supply_match.md + .csv
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)

# ── supply side ─────────────────────────────────────────────────────────────
CAP_NOW      = 2000.0   # cr L installed ESY25-26 (CareEdge May-2026; twin corroborates ~1,990)
CAP_FY27     = 2400.0   # + ~400 cr L expected operational by FY27 (CareEdge)
NONFUEL      = 325.0    # cr L potable + industrial (CareEdge 300-350 midpoint)
UTIL_BAND    = (0.65, 0.75)   # CareEdge consolidation-phase utilisation band
ABSORPTION   = 0.60     # share of offered ethanol OMCs currently absorb
DFPD_SANCTioned = 4530.0  # cr L/yr annualised sanction register (1,212 projects, 1,37,282 KLPD)
FCI_EFFECTIVE = 211.0   # cr L ethanol from the FCI rice leg at 65% lifting (7.2 MMT alloc)
AVG_KLPD, AVG_LOAN = 113.0, 96.8   # DFPD averages: KLPD per project, Rs cr loan per project

# NCDC coop-sugar-mill scheme split (Rs cr)
NCDC_TOTAL, NCDC_WC, NCDC_ETH, NCDC_COGEN = 10005.0, 9656.9, 251.4, 97.1
# capacity the ethanol tranche buys at DFPD average intensity
coop_klpd = NCDC_ETH / AVG_LOAN * AVG_KLPD
coop_crl  = coop_klpd * 330 / 1e4          # KLPD -> cr L/yr @330 days (100 KLPD = 3.3 cr L)

# ── demand side: blend scenarios on the FY24-25 pool + demand-grown FY30-31 ──
MS_BLENDED = 54.05      # bn L blended petrol pool FY24-25
L0 = MS_BLENDED * (1 - 0.04)
BLENDS = [("E20", 0.20, 0.040), ("E25", 0.25, 0.055), ("E27", 0.27, 0.0625), ("E30", 0.30, 0.070)]

rows = []
for tag, frac, drop in BLENDS:
    pool = L0 / (1 - drop)                    # bn L dispensed at that blend
    eth  = pool * frac * 100                  # cr L ethanol needed (fuel leg)
    total = eth + NONFUEL
    rows.append({"blend": tag, "fuel_ethanol_crL": round(eth),
        "total_demand_crL": round(total),
        "util_on_2000": round(total / CAP_NOW * 100, 1),
        "util_on_2400": round(total / CAP_FY27 * 100, 1),
        "fci_leg_share_pct": round(FCI_EFFECTIVE / eth * 100, 1)})

# demand-grown check (petrol_demand_forecast.py base case, FY30-31 E30)
E30_FY31 = 2173.0
fy31_util = (E30_FY31 + NONFUEL) / CAP_FY27 * 100

with (OUT / "ethanol_supply_match.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

# ── report ──────────────────────────────────────────────────────────────────
L = ["# Ethanol supply vs the blend scenarios — capacity, overcapacity, and the coop-mill wave\n",
     "Do the Volume Dividend scenarios (E25/E27/E30 at parity prices) clear the supply "
     "side? Short answer: **yes on capacity — the higher blends are the *cure* for the "
     "overcapacity CareEdge is flagging — with feedstock, not steel, as the real "
     "constraint, and the cooperative-mill scheme adding almost no new supply.**\n"]

L.append("## 1. The supply picture (ESY 2025-26)\n")
L.append("| Item | cr L/yr | Source |")
L.append("|---|---|---|")
L.append(f"| Installed capacity | ~{CAP_NOW:.0f} | CareEdge (May 2026); twin layer 24d corroborates ~1,990 |")
L.append(f"| Additions by FY27 | +400 | CareEdge |")
L.append(f"| DFPD sanction register | {DFPD_SANCTioned:.0f} | 1,212 approved projects, 1,37,282 KLPD annualised |")
L.append(f"| E20 fuel demand | ~1,100 | CareEdge (our pool math: {rows[0]['fuel_ethanol_crL']}) |")
L.append(f"| Non-fuel demand | 300–350 | CareEdge |")
L.append(f"| FCI rice leg (effective) | ~{FCI_EFFECTIVE:.0f} | 7.2 MMT alloc × 65% lifting × 450 L/t; ~3.9 blend ppt |")
L.append("\nCapacity tripled from 680 cr L (2018-19) — the sanction register alone is 2.3× "
         "what is built. At E20 only ~60% of offered ethanol is absorbed; CareEdge sees "
         "utilisation stuck at 65–75% for three years and the sector entering a "
         "consolidation phase (EPC moderating, brownfield focus, margins under pressure). "
         "Regional skew: Maharashtra +277 cr L surplus vs Tamil Nadu −77 deficit.\n")

L.append("## 2. Matching the blend scenarios to capacity\n")
L.append("| Blend | Fuel ethanol (cr L) | +Non-fuel total | Utilisation on 2,000 | On 2,400 (FY27) | FCI leg covers |")
L.append("|---|---|---|---|---|---|")
for r in rows:
    L.append(f"| {r['blend']} | {r['fuel_ethanol_crL']:,} | {r['total_demand_crL']:,} | "
             f"{r['util_on_2000']}% | {r['util_on_2400']}% | {r['fci_leg_share_pct']}% |")
L.append(f"\n- **E20 is the overcapacity scenario**: {rows[0]['total_demand_crL']:,} cr L demand on "
         "2,400 cr L of FY27 steel = 59% — exactly the malaise CareEdge describes.\n"
         "- **E25 lands inside the consolidation band** (71%); **E27 tops it** (76%) — the "
         "grand-bargain blend absorbs the Maharashtra surplus and lifts realisations "
         "without new construction.\n"
         "- **E30 (83%) runs hot but fits today's pool**; the demand-grown E30 of "
         f"FY30-31 (2,173 cr L fuel) pushes utilisation to ~{fy31_util:.0f}% — THAT is when "
         "the 4,530 cr L sanction register gets called on, not before.\n"
         "- The blend walk and the parity pricing are therefore **complements**: parity "
         "pricing (S1 pass-through) removes the consumer objection; the higher blend "
         "removes the distillers' overcapacity. Same policy, two problems.\n")

L.append("## 3. The cooperative-sugar-mill 'wave' is a working-capital rescue, not capacity\n")
L.append("| NCDC scheme tranche | ₹ cr | Share |")
L.append("|---|---|---|")
L.append(f"| Working capital | {NCDC_WC:,.0f} | {NCDC_WC/NCDC_TOTAL*100:.1f}% |")
L.append(f"| Ethanol plants | {NCDC_ETH:,.1f} | {NCDC_ETH/NCDC_TOTAL*100:.1f}% |")
L.append(f"| Cogeneration | {NCDC_COGEN:,.1f} | {NCDC_COGEN/NCDC_TOTAL*100:.1f}% |")
L.append(f"| **Total to 56 coop mills** | **{NCDC_TOTAL:,.0f}** | 100% |")
L.append(f"\nAt the DFPD average intensity (₹{AVG_LOAN:.1f} cr loan ↔ {AVG_KLPD:.0f} KLPD), the "
         f"₹{NCDC_ETH:.0f} cr ethanol tranche buys ~{coop_klpd:.0f} KLPD ≈ **{coop_crl:.0f} cr L/yr "
         f"— {coop_crl/CAP_NOW*100:.1f}% of installed capacity**. The scheme is 96.5% "
         "working-capital relief for distressed CSMs; the 229 functional coop mills "
         "(~30% of sugar output) remain marginal to the ethanol build-out, which is a "
         "private grain-based wave (UP added ~50 cr L in 2025 alone; Gorakhpur GIDA "
         "cluster). Do NOT count a coop capacity wave in supply projections.\n")

L.append("## 4. Feedstock is the binding constraint, not steel\n")
L.append("- The E27/E30 increment is **grain-led**: molasses is capped by cane politics "
         "and the sugar-diversion cap; the marginal litre is maize (₹71.86/L, the "
         "dearest slab — consistent with S4's failure in the parity analysis).\n"
         f"- The FCI rice leg covers only ~{FCI_EFFECTIVE:.0f} cr L (≈3.9 blend ppt) at 65% "
         "lifting — and carries the Jul-2023 suspension precedent as a policy risk. "
         "E30's grain leg leans on open-market maize, linking fuel policy to feed/"
         "poultry prices.\n"
         "- CareEdge's infrastructure caveat transfers intact: ~1.03 lakh outlets are "
         "single-grade, storage ~77.8 cr L, ~300 depots — fine for one national blend "
         "(E20→E27 as a step), hostile to a multi-blend E85/FFV world.\n")

L.append("## 5. Verdict per scenario\n")
L.append("| Scenario | Supply verdict |")
L.append("|---|---|")
L.append("| E20 (today) | Structural overcapacity — 59% utilisation, ~700 cr L unabsorbed, margins compressed |")
L.append("| E25 parity | Clears easily; utilisation 71% (mid consolidation band) |")
L.append("| **E27 grand bargain** | **Sweet spot on supply too**: 76% utilisation, absorbs state surpluses, zero new construction needed |")
L.append("| E30 (today's pool) | Fits (83%) but leans on marginal maize; watch feedstock prices |")
L.append("| E30 (FY30-31, demand-grown) | ~104% of FY27 capacity — needs the sanction register to actually build; supply becomes binding again |\n")

(OUT / "ethanol_supply_match.md").write_text("\n".join(L))

for r in rows:
    print(f"{r['blend']}: fuel {r['fuel_ethanol_crL']:,} cr L, total {r['total_demand_crL']:,} "
          f"-> util {r['util_on_2000']}% / {r['util_on_2400']}% (2000/2400 cr L), FCI leg {r['fci_leg_share_pct']}%")
print(f"FY30-31 demand-grown E30: util {fy31_util:.0f}% of FY27 capacity")
print(f"Coop ethanol tranche Rs{NCDC_ETH:.0f} cr -> ~{coop_klpd:.0f} KLPD = {coop_crl:.1f} cr L/yr "
      f"({coop_crl/CAP_NOW*100:.2f}% of installed)")
