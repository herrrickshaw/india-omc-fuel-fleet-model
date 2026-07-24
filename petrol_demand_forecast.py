#!/usr/bin/env python3
"""Forecast India petrol (MS) demand and the ethanol-blending requirement.

Growth is anchored on the literature/PPAC trend (RR: MS decadal CAGR 7.1%,
recent H1 +6.8-7.1%) and modulated by FADA vehicle-sales signals — two-wheelers
(~72% of sales, still ~93% petrol) keep demand rising, while a rising EV share
(FADA FY26: EV 6.5% of 2W, 4.25% of PV, 8.5% overall) drags the growth rate
down over time. Three scenarios bracket it. The ethanol requirement then follows
from a blend roadmap (E20→E30), and is checked against India's ethanol capacity.

Base: FY24-25 petrol 40.0 MMT (PPAC RR Table 6.1). Pure stdlib.
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"; OUT.mkdir(exist_ok=True)

# ── inputs ───────────────────────────────────────────────────────────────────
BASE_MMT = 40.0                      # petrol FY24-25 (RR Table 6.1)
DENS_MS = 0.74                       # -> 1 MMT = 1.3514 bn L
MMT_TO_BNL = 1e9 / DENS_MS / 1e9     # = 1.3514
FY = ["FY25-26", "FY26-27", "FY27-28", "FY28-29", "FY29-30", "FY30-31"]

# growth scenarios (YoY %). BASE declines as FADA EV share climbs (~1.5pp/yr).
GROWTH = {
    "High (7% trend)":            [0.070, 0.070, 0.070, 0.070, 0.070, 0.070],
    "Base (FADA-moderating)":     [0.065, 0.059, 0.053, 0.047, 0.041, 0.035],
    "Low (fast-EV, 3%)":          [0.030, 0.030, 0.030, 0.030, 0.030, 0.030],
}

# ethanol blend roadmap (E20 achieved 2025 -> E30, with Brazil-style E27 waypoint)
BLEND = {"FY25-26": 0.20, "FY26-27": 0.22, "FY27-28": 0.25,
         "FY28-29": 0.27, "FY29-30": 0.30, "FY30-31": 0.30}

# India fuel-ethanol capacity, crore litres (approx, 2024-25; editable)
ETHANOL_CAPACITY_CRL = 1600
CRORE_L_PER_BNL = 100                # 1 bn L = 100 crore L


def project(rates):
    out, v = [], BASE_MMT
    for r in rates:
        v *= (1 + r)
        out.append(v)
    return out


def main():
    scen = {name: project(rates) for name, rates in GROWTH.items()}

    # petrol demand table
    with (OUT / "petrol_demand_forecast.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["scenario"] + [f"{fy}_MMT" for fy in FY] + [f"{fy}_bnL" for fy in FY])
        for name, mmt in scen.items():
            w.writerow([name] + [round(x, 1) for x in mmt] + [round(x * MMT_TO_BNL, 1) for x in mmt])

    # ethanol requirement per scenario
    eth = {}
    for name, mmt in scen.items():
        eth[name] = []
        for i, fy in enumerate(FY):
            petrol_bnL = mmt[i] * MMT_TO_BNL
            eth_bnL = petrol_bnL * BLEND[fy]
            eth[name].append(eth_bnL)
    with (OUT / "ethanol_requirement_forecast.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["scenario"] + [f"{fy}_ethanol_croreL" for fy in FY])
        for name in scen:
            w.writerow([name] + [round(x * CRORE_L_PER_BNL) for x in eth[name]])

    base = "Base (FADA-moderating)"
    b_mmt, b_eth = scen[base], eth[base]

    L = []
    L.append("# India petrol-demand & ethanol-requirement forecast (FY26–FY31)\n")
    L.append("Growth anchored on the **PPAC/literature trend** (RR: MS decadal CAGR **7.1%**, recent H1 "
             "+6.8–7.1%) and shaped by **FADA vehicle-sales signals**: two-wheelers (~72% of sales, still "
             "~93% petrol) keep demand rising, while a climbing EV share (FADA FY26: 6.5% of 2W, 4.25% of "
             "PV, 8.5% overall) drags the growth rate down over time. Base petrol FY24-25 = 40.0 MMT "
             "(RR Table 6.1). Ethanol need follows a blend roadmap E20→E30 (Brazil-style E27 waypoint).\n")

    L.append("## 1. Petrol (MS) demand forecast — MMT\n")
    L.append("| Scenario | " + " | ".join(FY) + " | CAGR |")
    L.append("|---|" + "--:|" * (len(FY) + 1))
    for name, mmt in scen.items():
        cagr = (mmt[-1] / BASE_MMT) ** (1 / len(FY)) - 1
        L.append(f"| {name} | " + " | ".join(f"{x:.1f}" for x in mmt) + f" | {cagr*100:.1f}% |")
    L.append("")
    L.append(f"- **Base case:** petrol rises **{BASE_MMT:.0f} → {b_mmt[-1]:.0f} MMT** by FY30-31 "
             f"({b_mmt[-1]*MMT_TO_BNL:.0f} bn L) — a ~{((b_mmt[-1]/BASE_MMT)**(1/6)-1)*100:.1f}% CAGR, the "
             "7% trend bending down as EVs scale. High (EV stays niche) reaches "
             f"{scen['High (7% trend)'][-1]:.0f} MMT; Low (fast-EV) {scen['Low (fast-EV, 3%)'][-1]:.0f} MMT.\n")

    L.append("## 2. Ethanol requirement — blend roadmap × petrol demand (crore litres/yr)\n")
    L.append("| Scenario | " + " | ".join(f"{fy}<br>{int(BLEND[fy]*100)}%" for fy in FY) + " |")
    L.append("|---|" + "--:|" * len(FY))
    for name in scen:
        L.append(f"| {name} | " + " | ".join(f"{round(x*CRORE_L_PER_BNL):,}" for x in eth[name]) + " |")
    L.append("")
    cap = ETHANOL_CAPACITY_CRL
    fy31_base = b_eth[-1] * CRORE_L_PER_BNL
    fy26_base = b_eth[0] * CRORE_L_PER_BNL
    L.append(f"- **Base case ethanol need nearly doubles: ~{round(fy26_base):,} cr L (E20, FY26) → "
             f"~{round(fy31_base):,} cr L (E30, FY31).**")
    L.append(f"- India's fuel-ethanol capacity is ~{cap:,} cr L (2024-25). E20 today fits, but hitting "
             f"**E30 on a growing petrol base needs ~{round(fy31_base):,} cr L — about "
             f"{round((fy31_base/cap-1)*100)}% above current capacity**. The binding constraint on the "
             "blend roadmap is ethanol supply, not petrol demand.\n")

    L.append("## 3. Capacity gap (base case, ₹ / cr L)\n")
    L.append("| FY | Blend | Petrol (MMT) | Ethanol needed (cr L) | vs capacity (~%d cr L) |" % cap)
    L.append("|---|--:|--:|--:|--:|")
    for i, fy in enumerate(FY):
        need = b_eth[i] * CRORE_L_PER_BNL
        gap = need - cap
        tag = f"+{round(gap):,} over" if gap > 0 else f"{round(-gap):,} headroom"
        L.append(f"| {fy} | {int(BLEND[fy]*100)}% | {b_mmt[i]:.1f} | {round(need):,} | {tag} |")
    L.append("")

    L.append("## 4. What this scales across the rest of the model\n")
    L.append("Every ethanol-linked flow in this repo scales with the forecast. At the **base FY30-31 "
             f"(E30, {b_mmt[-1]:.0f} MMT petrol)**, versus today's E20:\n")
    fy31_eth_bnL = b_eth[-1]
    L.append(f"- Ethanol displacing petrol ≈ **{fy31_eth_bnL:.1f} bn L** (freed for export ≈ "
             f"{fy31_eth_bnL/MMT_TO_BNL:.0f} MMT, ~₹{round(fy31_eth_bnL*1e9*46.1/1e7):,} cr export forex).")
    L.append(f"- State VAT foregone ≈ ₹{round(fy31_eth_bnL*1e9*18/1e7):,} cr; central excise foregone ≈ "
             f"₹{round(fy31_eth_bnL*1e9*19.9/1e7):,} cr; a 5% ethanol SGST would yield ≈ "
             f"₹{round(fy31_eth_bnL*1e9*60*0.05/1e7):,} cr for states.\n")

    L.append("## 5. Caveats\n")
    L.append("- Growth scenarios anchor on RR's 7.1% decadal CAGR; the base *bend-down* is a judgement on "
             "FADA's EV-share trajectory, not a fitted fleet model — see `fleet_from_fuel.py` for the "
             "bottom-up cross-check. Rates are editable.")
    L.append("- Blend roadmap (E20→E30 by FY30) is an assumed policy path per NBP direction + Brazil's E27 "
             "precedent, not a notified schedule.")
    L.append(f"- Ethanol capacity (~{cap:,} cr L) is an approximate 2024-25 figure; feedstock (molasses/"
             "grain) availability, not just plant capacity, is the real limit. 1 bn L = 100 cr L; "
             "petrol density 0.74.\n")
    L.append("---\n*Forecast from PPAC/FADA-anchored trends + editable assumptions; not an official "
             "demand projection.*\n")
    (OUT / "petrol_demand_forecast.md").write_text("\n".join(L))

    print("Petrol demand (MMT):")
    print(f"  {'scenario':26s}" + "".join(f"{fy[-5:]:>9s}" for fy in FY) + "     CAGR")
    for name, mmt in scen.items():
        cagr = (mmt[-1]/BASE_MMT)**(1/len(FY))-1
        print(f"  {name:26s}" + "".join(f"{x:>9.1f}" for x in mmt) + f"   {cagr*100:5.1f}%")
    print(f"\nBase ethanol requirement (cr L): {round(fy26_base):,} (E20 FY26) -> {round(fy31_base):,} (E30 FY31)")
    print(f"India capacity ~{cap:,} cr L -> FY31 E30 needs ~{round((fy31_base/cap-1)*100)}% more")
    print("Wrote outputs/petrol_demand_forecast.md + .csv + ethanol_requirement_forecast.csv")


if __name__ == "__main__":
    main()
