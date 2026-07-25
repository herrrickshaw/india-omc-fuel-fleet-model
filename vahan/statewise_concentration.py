#!/usr/bin/env python3
"""How concentrated is India's vehicle fleet across states? Cumulative (Pareto)
share of national registrations by ranked states, overall and by fuel, plus an
HHI concentration index per fuel. Data: Vahan4 CY2026 YTD (see statewise_fuel_analysis.py).
Pure stdlib.
"""
import csv
from pathlib import Path
from statewise_fuel_analysis import DATA, COLS   # reuse the 36-state matrix

OUT = Path(__file__).resolve().parent / "outputs"; OUT.mkdir(parents=True, exist_ok=True)
FUELS = ["Petrol","Diesel","CNG","EV","StrongHybrid","Total"]
IDX = {f: i+1 for i, f in enumerate(FUELS)}   # DATA row: [state, Petrol, Diesel, CNG, EV, StrongHybrid, Total]


def series(fuel):
    return sorted(((d[0], d[IDX[fuel]]) for d in DATA), key=lambda x: -x[1])


def cum_to(fuel, threshold):
    s = series(fuel); tot = sum(v for _, v in s); run = 0
    for i, (st, v) in enumerate(s, 1):
        run += v
        if run/tot >= threshold:
            return i
    return len(s)


def topn_share(fuel, n):
    s = series(fuel); tot = sum(v for _, v in s)
    return sum(v for _, v in s[:n]) / tot


def hhi(fuel):
    s = series(fuel); tot = sum(v for _, v in s)
    return sum((v/tot)**2 for _, v in s) * 10000   # 0-10000; >2500 concentrated


def main():
    # cumulative table for Total
    s = series("Total"); tot = sum(v for _, v in s); run = 0
    with (OUT / "statewise_cumulative_total.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["rank","state","vehicles","share_pct","cumulative_pct"])
        for i, (st, v) in enumerate(s, 1):
            run += v
            w.writerow([i, st, v, round(100*v/tot,2), round(100*run/tot,2)])

    L = ["# How concentrated is India's vehicle fleet across states?\n",
         f"Vahan4 CY2026 (YTD), 36 states/UTs; national ~{tot/1e6:.1f} million registrations. "
         "Cumulative (Pareto) share by ranked states, and an HHI concentration index per fuel "
         "(HHI 0–10,000; >2,500 = concentrated).\n"]

    L.append("## 1. Overall fleet — cumulative share\n| Ranked states | Cumulative share of all vehicles |\n|---|--:|")
    for n in (3,5,10,15):
        L.append(f"| Top {n} | {100*topn_share('Total',n):.0f}% |")
    L.append("")
    L.append(f"- **Top 5 states = {100*topn_share('Total',5):.0f}%** of all registrations; "
             f"**top 10 = {100*topn_share('Total',10):.0f}%**. It takes **{cum_to('Total',0.5)} states to reach half** "
             f"the national fleet and **{cum_to('Total',0.8)} to reach 80%** — moderately concentrated, "
             "with a long tail of small states/UTs.\n")

    L.append("## 2. Concentration by fuel — top-5 share & HHI\n| Fuel | Top-5 states | HHI | How concentrated |\n|---|--:|--:|---|")
    verdict = lambda h: "concentrated" if h>1000 else ("moderate" if h>750 else "dispersed")
    for fu in ["CNG","StrongHybrid","EV","Diesel","Petrol","Total"]:
        h = hhi(fu)
        t5 = topn_share(fu,5)
        L.append(f"| {fu} | {100*t5:.0f}% | {h:,.0f} | {verdict(h)} |")
    L.append("")
    L.append("- **CNG is the most concentrated** — a handful of CGD-network states (Maharashtra, Gujarat, "
             "UP, Rajasthan, Delhi/Haryana) hold the bulk; small states have almost none.")
    L.append("- **Strong hybrids and EVs are concentrated** in the big/affluent + e-rickshaw states.")
    L.append("- **Petrol and diesel are the most dispersed** — every state runs two-wheelers and CVs, so "
             "they track population/total more evenly.\n")

    L.append("## 3. Top-5 leaders per fuel (share of that fuel nationally)\n| Fuel | Top 5 states (cumulative) |\n|---|---|")
    for fu in FUELS:
        s = series(fu); tot_f = sum(v for _, v in s); run=0; parts=[]
        for st,v in s[:5]:
            run+=v; parts.append(f"{st} {100*run/tot_f:.0f}%")
        L.append(f"| **{fu}** | {' → '.join(parts)} |")
    L.append("")
    L.append("---\n*Vahan registration data, CY2026 YTD; concentration reflects new registrations, not the "
             "on-road parc. HHI = Σ(state share)² ×10,000.*\n")
    (OUT / "statewise_concentration.md").write_text("\n".join(L))

    print(f"National ~{tot/1e6:.1f}M. Top5 total {100*topn_share('Total',5):.0f}%, top10 {100*topn_share('Total',10):.0f}%; "
          f"{cum_to('Total',0.5)} states to 50%, {cum_to('Total',0.8)} to 80%")
    print(f"{'fuel':13s}{'top5':>7s}{'HHI':>8s}")
    for fu in ["CNG","StrongHybrid","EV","Diesel","Petrol","Total"]:
        print(f"{fu:13s}{100*topn_share(fu,5):>6.0f}%{hhi(fu):>8.0f}")
    print("Wrote outputs/statewise_concentration.md + statewise_cumulative_total.csv")


if __name__ == "__main__":
    main()
