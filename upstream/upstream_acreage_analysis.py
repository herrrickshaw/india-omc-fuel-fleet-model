#!/usr/bin/env python3
"""India upstream oil & gas: domestic crude decline, offshore acreage, and where
to explore next. Quantitative base from the PPAC Ready Reckoner FY2025-26 (H1):
Table 2.5A (state/basin crude), 2.6 (self-sufficiency), 2.7A/2.7B (NELP/OALP/DSF
blocks), 2.9 (CBM), 2.10 (shale). Recommendations combine those trends with
India's sedimentary-basin framework. Pure stdlib.
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"; OUT.mkdir(parents=True, exist_ok=True)
FY = ["2019-20", "2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]

# ── Table 2.5A crude production by source (TMT, incl. condensate) ─────────────
CRUDE = {  # source: [FY20..FY25]
    "Assam (onshore)":            [4093, 3902, 3991, 4166, 4361, 4454],
    "Gujarat (onshore)":          [4707, 4651, 4626, 4849, 4950, 5135],
    "Rajasthan / Barmer (onshore)":[6653, 5891, 5885, 5074, 4421, 3428],
    "Andhra Pradesh (onshore)":   [243, 195, 202, 236, 250, 284],
    "Tamil Nadu (onshore)":       [415, 410, 367, 324, 294, 263],
    "Arunachal (onshore)":        [56, 53, 48, 47, 52, 50],
    "Western Offshore (Mumbai High)":[14857, 14236, 13604, 13552, 13239, 12471],
    "Eastern Offshore (KG deepwater)":[557, 744, 626, 550, 1463, 2437],
    "Gujarat Offshore":           [589, 411, 338, 379, 326, 181],
}
ONSHORE = ["Assam (onshore)","Gujarat (onshore)","Rajasthan / Barmer (onshore)",
           "Andhra Pradesh (onshore)","Tamil Nadu (onshore)","Arunachal (onshore)"]
OFFSHORE = ["Western Offshore (Mumbai High)","Eastern Offshore (KG deepwater)","Gujarat Offshore"]

SELF_SUFFICIENCY = [15.0, 15.6, 14.5, 12.6, 12.2, 11.9]     # % (Table 2.6)

# ── Table 2.7 blocks (as on 01.10.2025) ──────────────────────────────────────
BLOCKS = {
    "NELP (1999-2010)":   {"offered": 360, "awarded": 254, "operational": 27,  "note": "227 relinquished — most acreage explored & dropped"},
    "OALP / HELP (2018-24)":{"offered": 172, "awarded": 172, "operational": 104, "note": "OALP-IX (2024): 28 blocks, 11 deepwater + 8 shallow (PEL awaited)"},
    "DSF (2016-24)":      {"offered": 105, "awarded": 87,  "operational": 51,  "note": "discovered small fields — quick, low-risk barrels"},
}
OALP_DW_AWARDED = 22        # deep/ultra-deep blocks awarded under OALP (2.7B)
CBM = {"prognosticated_TCF": 91.8, "established_TCF": 12.1, "area_total_sqkm": 32760, "area_explored_sqkm": 11578}

# ── ranked recommendations (evidence + basin framework) ──────────────────────
RECS = [
    ("Eastern Offshore deepwater — KG basin extension", "Cat-I (proven)", "Low–Med",
     "The one growing source: +337% (0.56→2.44 MMT) as ONGC KG-DWN-98/2 ramped. Step-out around producing deepwater cluster is de-risked.", "Development + near-field exploration"),
    ("Andaman deepwater", "Cat-III (frontier)", "High",
     "India's biggest frontier upside — direct along-strike analog to Indonesia's 2023-24 giant gas finds (Geng North / Layaran, ~5+ TCF each) just across the maritime boundary. Barely drilled.", "Frontier seismic + high-impact wildcat"),
    ("Mahanadi offshore (East Coast deepwater)", "Cat-II", "Med–High",
     "Gas-prone deepwater between the proven KG and Bengal fans; under-drilled. Rides the same East-Coast petroleum system as KG.", "3D seismic + appraisal"),
    ("Cauvery deepwater", "Cat-II", "Med",
     "Adjacent to KG success on the same margin; shallow Cauvery already produces. Deepwater flank largely untested.", "Seismic + exploration"),
    ("Released 'No-Go' acreage (~1 million sq km)", "Mixed", "Med",
     "Defence 'No-Go' zones opened 2016-22 unlocked ~99% of restricted offshore/onshore — vast new-to-industry acreage on the west & east margins now biddable via OALP.", "Fast-track into OALP rounds"),
    ("Kutch–Saurashtra offshore (NW)", "Cat-II", "Med–High",
     "Under-explored western-margin basin near proven Mumbai/Gujarat systems; recent ONGC interest.", "Seismic + exploration"),
    ("Western Offshore deepwater (beyond Mumbai High)", "Cat-I flank", "Med",
     "Mumbai High is a mature decliner (−16%); the deeper Arabian-Sea flank of the same prolific basin is comparatively untested.", "Deepwater exploration + EOR onshelf"),
    ("Discovered Small Fields (DSF) monetisation", "Discovered", "Low",
     "87 already-discovered fields awarded but many undeveloped — fastest, cheapest barrels; no exploration risk, only development.", "Accelerate development"),
    ("EOR/IOR in mature fields (Mumbai High, Barmer)", "Producing", "Low",
     "Barmer collapsed 6.65→3.43 MMT (−48%) and Mumbai High is declining; enhanced recovery adds barrels cheaper than any new hole.", "EOR (polymer/CO2), infill drilling"),
    ("CBM expansion (Damodar, Son-Mahanadi)", "Unconventional", "Med",
     "91.8 TCF prognosticated, only 12.1 TCF established; ~65% of coal-bearing area still unexplored.", "New CBM/coal-gasification blocks"),
]


def cagr(series):
    n = len(series) - 1
    return (series[-1] / series[0]) ** (1 / n) - 1 if series[0] > 0 else 0

def chg(series):
    return series[-1] / series[0] - 1


def main():
    onshore_tot = [sum(CRUDE[k][i] for k in ONSHORE) for i in range(6)]
    offshore_tot = [sum(CRUDE[k][i] for k in OFFSHORE) for i in range(6)]
    total = [onshore_tot[i] + offshore_tot[i] for i in range(6)]

    # producer trend CSV
    with (OUT / "crude_production_trend.csv").open("w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["source"] + FY + ["chg_5yr_pct", "cagr_pct"])
        for k, v in CRUDE.items():
            w.writerow([k] + v + [round(chg(v)*100, 1), round(cagr(v)*100, 1)])
        w.writerow(["ONSHORE TOTAL"] + onshore_tot + [round(chg(onshore_tot)*100,1), round(cagr(onshore_tot)*100,1)])
        w.writerow(["OFFSHORE TOTAL"] + offshore_tot + [round(chg(offshore_tot)*100,1), round(cagr(offshore_tot)*100,1)])
        w.writerow(["TOTAL"] + total + [round(chg(total)*100,1), round(cagr(total)*100,1)])

    with (OUT / "new_area_recommendations.csv").open("w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["rank","area","basin_class","risk","rationale","action"])
        for i, r in enumerate(RECS, 1):
            w.writerow([i] + list(r))

    L = []
    L.append("# India upstream: crude decline, offshore acreage & where to drill next\n")
    L.append("Base data: PPAC Ready Reckoner FY2025-26 (H1). India's crude output is in structural "
             "decline while import dependence sits near 88% — the exploration question is not *whether* "
             "to open new acreage but *where*.\n")

    L.append("## 1. The problem — production down, self-sufficiency at ~12%\n")
    L.append(f"- Total crude **{total[0]/1000:.1f} → {total[-1]/1000:.1f} MMT** FY20→FY25 "
             f"({chg(total)*100:+.0f}%, {cagr(total)*100:+.1f}%/yr).")
    L.append(f"- **Self-sufficiency has slipped {SELF_SUFFICIENCY[0]:.0f}% → {SELF_SUFFICIENCY[-1]:.1f}%** "
             "(Table 2.6) — India refines ~88% imported crude. Even overseas (OVL) output is falling.")
    L.append(f"- **Onshore {onshore_tot[0]/1000:.1f}→{onshore_tot[-1]/1000:.1f} MMT ({chg(onshore_tot)*100:+.0f}%)** "
             f"vs **offshore {offshore_tot[0]/1000:.1f}→{offshore_tot[-1]/1000:.1f} MMT ({chg(offshore_tot)*100:+.0f}%)** — "
             "offshore is now the majority and the only side holding up.\n")

    L.append("## 2. Where the barrels are moving — by basin\n")
    L.append("| Source | FY20 (MMT) | FY25 (MMT) | 5-yr change | Read |")
    L.append("|---|--:|--:|--:|---|")
    reads = {
        "Eastern Offshore (KG deepwater)":"**the growth engine** — KG-DWN-98/2 online",
        "Rajasthan / Barmer (onshore)":"**collapsing** — Mangala field decline",
        "Western Offshore (Mumbai High)":"mature decline",
        "Gujarat (onshore)":"stable / slight growth",
        "Assam (onshore)":"stable",
        "Gujarat Offshore":"declining",
    }
    ordered = sorted(CRUDE.items(), key=lambda kv: -chg(kv[1]))
    for k, v in ordered:
        L.append(f"| {k} | {v[0]/1000:.2f} | {v[-1]/1000:.2f} | {chg(v)*100:+.0f}% | {reads.get(k,'—')} |")
    L.append("")
    L.append("**The signal:** every onshore and shallow legacy source is flat-to-falling; the single "
             "source growing is **Eastern Offshore deepwater (KG), up 4×**. New oil in India is a "
             "**deepwater, East-Coast** story.\n")

    L.append("## 3. Acreage — a lot explored and dropped, a new offshore push\n")
    L.append("| Regime | Offered | Awarded | Operational | Note |")
    L.append("|---|--:|--:|--:|---|")
    for name, b in BLOCKS.items():
        L.append(f"| {name} | {b['offered']} | {b['awarded']} | {b['operational']} | {b['note']} |")
    L.append("")
    L.append(f"- **NELP's legacy:** of 360 blocks offered, only **27 are operational** — 227 were "
             "relinquished. Much of the *easy, already-mapped* acreage has been tried; the remaining "
             "prize is frontier and deepwater.")
    L.append(f"- **OALP is tilting offshore:** {OALP_DW_AWARDED} deep/ultra-deep blocks awarded, and "
             "**OALP-IX (2024) alone added 11 deepwater + 8 shallow-water** blocks — the policy is already "
             "pointing where the geology says to go.")
    L.append(f"- **CBM & shale** remain under-tapped: {CBM['prognosticated_TCF']} TCF CBM prognosticated "
             f"vs {CBM['established_TCF']} TCF established; only ~{100*CBM['area_explored_sqkm']/CBM['area_total_sqkm']:.0f}% "
             "of coal-bearing area explored.\n")

    L.append("## 4. Recommended new areas to explore — ranked\n")
    L.append("Ranked by a blend of *evidence in the data* (what's already growing / discovered) and "
             "*basin prospectivity* (India's Cat-I→III sedimentary framework + regional analogs).\n")
    L.append("| # | Area | Basin class | Risk | Why here | Action |")
    L.append("|--:|---|---|---|---|---|")
    for i, r in enumerate(RECS, 1):
        L.append(f"| {i} | **{r[0]}** | {r[1]} | {r[2]} | {r[3]} | {r[4]} |")
    L.append("")

    L.append("## 5. The thesis in three moves\n")
    L.append("1. **Defend the base cheaply** — EOR in Mumbai High & Barmer and fast-track the 87 DSF "
             "fields; these are the lowest-risk barrels and slow the decline now.")
    L.append("2. **Press the proven deepwater winner** — extend the KG-basin deepwater cluster and its "
             "along-margin neighbours (Mahanadi, Cauvery) where the petroleum system is already proven.")
    L.append("3. **Take one big frontier swing — Andaman deepwater** — the only place with plausible "
             "*giant* upside, validated by Indonesia's back-to-back multi-TCF discoveries next door. "
             "High risk, but it's where a step-change in self-sufficiency could actually come from.\n")

    L.append("## 6. Caveats\n")
    L.append("- Production & acreage figures are PPAC RR (DGH/ONGC/OIL); basin classes and analog "
             "reasoning are geological judgement, not reserve estimates. 'Suggestions' are exploration "
             "priorities, not drilling commitments.")
    L.append("- KG deepwater growth reflects one project (KG-DWN-98/2) ramping; near-term national "
             "output still declines until new areas deliver. Deepwater lead times are 5-10 years.")
    L.append("- Andaman/frontier upside is analog-based and unproven in Indian acreage; commercial "
             "success is uncertain. TMT = thousand tonnes; MMT = million tonnes; TCF = trillion cu ft.\n")
    L.append("---\n*Analysis from PPAC RR data + basin framework; exploration priorities, not investment "
             "advice or reserve certification.*\n")
    (OUT / "upstream_acreage_analysis.md").write_text("\n".join(L))

    print(f"Total crude FY20->FY25: {total[0]/1000:.1f} -> {total[-1]/1000:.1f} MMT ({chg(total)*100:+.0f}%)")
    print(f"Self-sufficiency: {SELF_SUFFICIENCY[0]:.0f}% -> {SELF_SUFFICIENCY[-1]:.1f}%")
    print("Source 5-yr change (sorted):")
    for k, v in ordered:
        print(f"  {k:34s} {chg(v)*100:+6.0f}%   {v[0]/1000:5.2f} -> {v[-1]/1000:5.2f} MMT")
    print(f"\nBlocks: NELP 27 operational of 360 offered; OALP {OALP_DW_AWARDED} deepwater awarded (IX: 11 DW+8 SW)")
    print("Top-3 new-area picks: KG deepwater extension, Andaman deepwater, Mahanadi/Cauvery deepwater")
    print("Wrote outputs/upstream_acreage_analysis.md + crude_production_trend.csv + new_area_recommendations.csv")


if __name__ == "__main__":
    main()
