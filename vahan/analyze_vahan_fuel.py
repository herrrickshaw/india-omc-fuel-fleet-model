#!/usr/bin/env python3
"""Fuel-wise vehicle registration analysis — Vahan dashboard, Calendar Year 2025.

Source: Vahan4 dashboard (vahan.parivahan.gov.in), Y-Axis=Fuel × X-Axis=Vehicle
Category, All States (36/36), Actual Value, Calendar Year 2025. Captured
2026-07-24. Columns are Vahan vehicle-category codes; last value is the row TOTAL.

Writes:
  vahan_fuel_registrations_cy2025.csv   raw fuel × category matrix
  outputs/fuel_group_summary.csv        aggregated to headline fuel groups
  outputs/fuel_by_class.csv             fuel mix within 2W / 3W / 4W+ classes
  outputs/vahan_fuel_analysis.md        narrative + tables
"""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"; OUT.mkdir(exist_ok=True)

# 17 Vahan category columns, in order:
CATS = ["2WIC","2WN","2WT","3WIC","3WN","3WT","4WIC","HGV","HMV","HPV",
        "LGV","LMV","LPV","MGV","MMV","MPV","OTH"]

# fuel, [17 category counts], reported TOTAL  (Vahan CY2025, all-India)
RAW = [
 ("CNG ONLY",[0,42046,93,0,386,329445,0,7253,0,1108,87943,625,9566,6587,5,3907,20],488984),
 ("DIESEL",[0,2,0,1,263,166567,411,277332,3977,33244,497243,1734154,104471,42021,7808,34357,84309],2986160),
 ("DIESEL/HYBRID",[0,0,0,0,0,0,0,0,0,0,1,8650,75,0,0,0,0],8726),
 ("DUAL DIESEL/CNG",[0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],1),
 ("DUAL DIESEL/LNG",[0,0,0,0,0,0,0,39,0,0,0,0,0,0,0,0,0],39),
 ("ELECTRIC(BOV)",[11,210902,5326,0,556,513084,29,125,0,1722,4495,53154,1579,0,0,36,165],791184),
 ("ETHANOL(E100)",[0,1290,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0],1292),
 ("FUEL CELL HYDROGEN",[0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,5,0],6),
 ("LNG",[0,0,0,0,0,0,0,607,0,0,0,0,0,0,0,0,0],607),
 ("LPG ONLY",[0,0,0,0,53,42705,0,0,0,0,0,8,2,0,0,0,0],42768),
 ("NOT APPLICABLE",[0,1,0,0,0,111,0,1701,19,0,13331,62809,1,157,2965,0,9],81104),
 ("PETROL",[18643,14397302,11206,58,20,3815,1652,1,0,5,21892,1425747,41904,1,0,10,361],15922617),
 ("PETROL/CNG",[0,964,0,0,1,12186,603,0,0,0,6009,661538,199608,0,0,0,20],880929),
 ("PETROL(E20)",[5820,5221029,2911,1,3,1603,749,1,0,2,13094,775610,12024,0,0,0,42],6032889),
 ("PETROL(E20)/CNG",[0,0,0,0,0,0,38,0,0,0,372,83380,26447,0,0,0,0],110237),
 ("PETROL(E20)/HYBRID",[0,0,0,0,0,0,19,0,0,0,0,35447,742,0,0,0,0],36208),
 ("PETROL(E20)/HYBRID/CNG",[0,0,0,0,0,0,0,0,0,0,0,68,13,0,0,0,0],81),
 ("PETROL(E20)/LPG",[0,0,0,0,0,0,0,0,0,0,21,584,13,0,0,0,0],618),
 ("PETROL/HYBRID",[0,0,0,0,0,0,95,0,0,0,0,207269,7655,0,0,0,0],215019),
 ("PETROL/HYBRID/CNG",[0,0,0,0,0,0,1,0,0,0,0,357,146,0,0,0,0],504),
 ("PETROL/LPG",[0,0,0,0,0,6008,6,0,0,0,140,9648,495,0,0,0,0],16297),
 ("PETROL/METHANOL",[0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0],2),
 ("PLUG-IN HYBRID EV",[0,0,0,0,0,0,0,0,0,0,0,73,0,0,0,0,0],73),
 ("PURE EV",[50,1120132,5893,0,203,287557,42,457,0,3152,6657,136299,5222,0,0,48,38],1565750),
 ("STRONG HYBRID EV",[0,0,0,0,0,0,47,0,0,0,0,106219,2227,0,1,0,0],108494),
]

# Cumulative "Till Today" registrations by fuel (Vahan, all-India, captured
# 2026-07-24). Fuel -> total only (no category split at this granularity).
# NOTE: Vahan cumulative counts ALL registrations ever made; it does NOT net out
# scrapped / de-registered / expired vehicles, so it OVERSTATES the live on-road
# parc (MoRTH's live-vehicle estimate is materially lower).
CUM = {
 "BIO-CNG/BIO-GAS":7, "CNG ONLY":2610419, "DIESEL":60489963, "DIESEL/HYBRID":187305,
 "DI-METHYL ETHER":3, "DUAL DIESEL/BIO CNG":1, "DUAL DIESEL/CNG":112, "DUAL DIESEL/LNG":83,
 "ELECTRIC(BOV)":6261756, "ETHANOL(E100)":1700, "FLEX-FUEL(BIO-DIESEL)":14,
 "FLEX-FUEL(ETHANOL)":12, "FUEL CELL HYDROGEN":43, "HCNG":9, "HYDROGEN(ICE)":1,
 "LNG":1496, "LPG ONLY":233966, "METHANOL":50, "NOT APPLICABLE":2772320,
 "PETROL":342598206, "PETROL/CNG":7268404, "PETROL(E20)":15494452, "PETROL(E20)/CNG":701839,
 "PETROL(E20)/HYBRID":169888, "PETROL(E20)/HYBRID/CNG":457, "PETROL(E20)/LPG":1847,
 "PETROL/HYBRID":1379974, "PETROL/HYBRID/CNG":3902, "PETROL/LPG":2253466,
 "PETROL/METHANOL":11, "PLUG-IN HYBRID EV":131, "PURE EV":3524049, "SOLAR":2171,
 "STRONG HYBRID EV":233108,
}

# ordered display groups
GROUP_ORDER = [
    "Petrol (mono, incl. E20 & hybrid)", "Petrol + gas bi-fuel (CNG/LPG)", "Diesel",
    "CNG/CBG (dedicated)", "LPG (dedicated)", "Electric (BEV/PHEV)",
    "Ethanol (E100/flex)", "Other (H2/LNG/methanol/solar/NA)",
]

def classify(f):
    """Map any Vahan fuel label to a headline group (works for both datasets)."""
    if f in ("PURE EV", "ELECTRIC(BOV)", "PLUG-IN HYBRID EV"):
        return "Electric (BEV/PHEV)"
    if "PETROL" in f and ("CNG" in f or "LPG" in f):
        return "Petrol + gas bi-fuel (CNG/LPG)"
    if "PETROL" in f or f == "STRONG HYBRID EV":
        return "Petrol (mono, incl. E20 & hybrid)"
    if "DIESEL" in f:                       # incl. dual-diesel & bio-diesel flex
        return "Diesel"
    if "CNG" in f or "CBG" in f or "HCNG" in f or "BIO-GAS" in f:
        return "CNG/CBG (dedicated)"
    if f == "LPG ONLY":
        return "LPG (dedicated)"
    if "ETHANOL" in f:
        return "Ethanol (E100/flex)"
    return "Other (H2/LNG/methanol/solar/NA)"

def is_e20(f):
    return "(E20)" in f

def group_totals(tot_map):
    g = {k: 0 for k in GROUP_ORDER}
    for f, v in tot_map.items():
        g[classify(f)] += v
    return g

tot = {f: t for f, _, t in RAW}
GRAND = sum(tot.values())
CUM_GRAND = sum(CUM.values())


def broad(cat):
    if cat.startswith("2W"): return "2W"
    if cat.startswith("3W"): return "3W"
    return "4W+"


def main():
    # integrity: CY2025 row categories sum to reported total
    bad = [(f, sum(c), t) for f, c, t in RAW if sum(c) != t]
    assert not bad, f"row/total mismatch: {bad}"

    # raw CSVs (annual matrix + cumulative fuel totals)
    with (HERE / "vahan_fuel_registrations_cy2025.csv").open("w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["fuel"] + CATS + ["TOTAL"])
        for f, c, t in RAW:
            w.writerow([f] + c + [t])
    with (HERE / "vahan_fuel_registrations_cumulative.csv").open("w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["fuel", "cumulative_registrations", "group"])
        for f, v in sorted(CUM.items(), key=lambda kv: -kv[1]):
            w.writerow([f, v, classify(f)])

    # fuel-group summaries — annual (flow) and cumulative (stock)
    grp = group_totals(tot)
    cgrp = group_totals(CUM)
    with (OUT / "fuel_group_summary.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["fuel_group", "cy2025_vehicles", "cy2025_share_pct",
                    "cumulative_vehicles", "cumulative_share_pct"])
        for g in GROUP_ORDER:
            w.writerow([g, grp[g], round(100*grp[g]/GRAND, 2),
                        cgrp[g], round(100*cgrp[g]/CUM_GRAND, 2)])
        w.writerow(["TOTAL", GRAND, 100.0, CUM_GRAND, 100.0])

    # fuel mix within broad classes (CY2025 only — category split available there)
    classes = ["2W", "3W", "4W+"]
    class_grp = {c: {k: 0 for k in GROUP_ORDER} for c in classes}
    class_tot = {c: 0 for c in classes}
    for f, counts, _ in RAW:
        g = classify(f)
        for cat, n in zip(CATS, counts):
            b = broad(cat)
            class_grp[b][g] += n
            class_tot[b] += n
    with (OUT / "fuel_by_class.csv").open("w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["fuel_group"] + classes)
        for g in GROUP_ORDER:
            w.writerow([g] + [class_grp[c][g] for c in classes])
        w.writerow(["TOTAL"] + [class_tot[c] for c in classes])

    e20 = sum(v for f, v in tot.items() if is_e20(f))
    ce20 = sum(v for f, v in CUM.items() if is_e20(f))
    petrol_any = grp["Petrol (mono, incl. E20 & hybrid)"] + grp["Petrol + gas bi-fuel (CNG/LPG)"]
    cpetrol_any = cgrp["Petrol (mono, incl. E20 & hybrid)"] + cgrp["Petrol + gas bi-fuel (CNG/LPG)"]
    ev = grp["Electric (BEV/PHEV)"]

    # markdown
    L = []
    L.append("# Fuel-wise vehicle registrations — Vahan dashboard (all-India)\n")
    L.append("Source: **Vahan4 dashboard** (vahan.parivahan.gov.in), Y-Axis=Fuel, all 36 states/UTs, "
             "Actual Value. Captured 2026-07-24. Two views: **CY2025** (one year's new registrations, "
             f"with the vehicle-category split) and **cumulative 'Till Today'** (all registrations "
             "ever recorded).\n")
    L.append(f"- **CY2025 registrations:** {GRAND:,} (~{GRAND/1e7:.2f} crore)")
    L.append(f"- **Cumulative registrations:** {CUM_GRAND:,} (~{CUM_GRAND/1e7:.1f} crore)\n")
    L.append("> ⚠️ **Cumulative caveat:** Vahan's cumulative count does **not** remove scrapped, "
             "de-registered or expired vehicles, so ~44.6 crore *overstates* the live on-road parc "
             "(MoRTH's live-vehicle estimate is materially lower, ~30-35 crore). Read cumulative as "
             "'all-time registered', the annual figure as the true yearly flow.\n")

    L.append("## 1. Headline fuel groups — annual flow vs cumulative stock\n")
    L.append("| Fuel group | CY2025 | share | Cumulative | share |")
    L.append("|---|--:|--:|--:|--:|")
    for g in sorted(GROUP_ORDER, key=lambda k: -cgrp[k]):
        L.append(f"| {g} | {grp[g]:,} | {100*grp[g]/GRAND:.1f}% | {cgrp[g]:,} | {100*cgrp[g]/CUM_GRAND:.1f}% |")
    L.append(f"| **Total** | **{GRAND:,}** | **100%** | **{CUM_GRAND:,}** | **100%** |")
    L.append("")
    L.append(f"- **Petrol dominates both** — {100*petrol_any/GRAND:.0f}% of CY2025 flow and "
             f"{100*cpetrol_any/CUM_GRAND:.0f}% of the cumulative stock ({cpetrol_any:,}).")
    L.append(f"- **EV is a flow story:** {100*ev/GRAND:.1f}% of CY2025 registrations but only "
             f"{100*cgrp['Electric (BEV/PHEV)']/CUM_GRAND:.1f}% of the cumulative stock — new EVs are "
             "arriving far faster than they sit in the legacy base, exactly the fleet-turnover lag the "
             "cost model flags.")
    L.append(f"- **Diesel** is a bigger share of the old stock ({100*cgrp['Diesel']/CUM_GRAND:.0f}%) "
             f"than of new flow ({100*grp['Diesel']/GRAND:.0f}%) — diesel is retreating in new sales.\n")

    L.append("## 2. The E20 signal (directly relevant to the ethanol/OMC model)\n")
    L.append(f"Vahan records **PETROL(E20)** as its own fuel type — vehicles type-approved for E20. "
             f"CY2025: **{e20:,}** ({100*e20/GRAND:.1f}% of all, {100*e20/petrol_any:.0f}% of petrol). "
             f"Cumulative: **{ce20:,}** ({100*ce20/CUM_GRAND:.1f}% of stock). In CY2026 year-to-date the "
             "E20 badge has already overtaken plain PETROL in new registrations — the compatible-fleet "
             "ramp the OMC ethanol model assumes is directly visible in the registration data.\n")

    L.append("## 3. CY2025 fuel mix by broad vehicle class\n")
    L.append("| Fuel group | 2-wheeler | 3-wheeler | 4-wheeler+ |")
    L.append("|---|--:|--:|--:|")
    for g in GROUP_ORDER:
        L.append(f"| {g} | {class_grp['2W'][g]:,} | {class_grp['3W'][g]:,} | {class_grp['4W+'][g]:,} |")
    L.append(f"| **Total** | **{class_tot['2W']:,}** | **{class_tot['3W']:,}** | **{class_tot['4W+']:,}** |")
    L.append("")
    tw, th = class_tot["2W"], class_tot["3W"]
    ev2 = class_grp["2W"]["Electric (BEV/PHEV)"]; ev3 = class_grp["3W"]["Electric (BEV/PHEV)"]
    cng3 = class_grp["3W"]["CNG/CBG (dedicated)"]
    L.append(f"- **2-wheelers** ({tw:,}) — overwhelmingly petrol, EV {100*ev2/tw:.1f}%.")
    L.append(f"- **3-wheelers** ({th:,}) — the most electrified/gas class: EV {100*ev3/th:.0f}%, "
             f"dedicated CNG {100*cng3/th:.0f}%.")
    L.append("- **4-wheelers+** carry nearly all the diesel and the petrol/CNG bi-fuel cars.\n")

    L.append("## 4. Link to the OMC / ethanol model\n")
    L.append("Vehicle *counts* here are the counterpart to the OMC model's fuel *volumes*: petrol's "
             "~80% vehicle share underpins the petrol throughput the OMC retail book rests on; EV/CNG "
             "are the slices eroding it; and the explicit E20-badged fleet is the population over which "
             "the ethanol mileage-penalty — and its OMC throughput uplift — actually applies. The "
             "cumulative-vs-annual gap quantifies fleet-turnover lag: even as new-sales blends and EVs "
             "shift fast, the on-road stock changes slowly, so petrol/diesel volumes persist for years.\n")
    L.append("---\n*Vahan retail registration data (the source FADA compiles). Cumulative includes "
             "scrapped/de-registered vehicles and overstates the live parc.*\n")
    (OUT / "vahan_fuel_analysis.md").write_text("\n".join(L))

    print(f"CY2025 total: {GRAND:,}   |   Cumulative total: {CUM_GRAND:,} (~{CUM_GRAND/1e7:.1f} cr)")
    print(f"{'group':40s}{'CY2025':>14s}{'share':>7s}{'cumulative':>16s}{'share':>7s}")
    for g in sorted(GROUP_ORDER, key=lambda k: -cgrp[k]):
        print(f"{g:40s}{grp[g]:>14,}{100*grp[g]/GRAND:>6.1f}%{cgrp[g]:>16,}{100*cgrp[g]/CUM_GRAND:>6.1f}%")
    print(f"E20-badged — CY2025 {e20:,} ({100*e20/GRAND:.1f}%) | cumulative {ce20:,} ({100*ce20/CUM_GRAND:.1f}%)")
    print("Wrote: raw CSVs (annual+cumulative) + outputs/ (summary, by_class, analysis.md)")


if __name__ == "__main__":
    main()
