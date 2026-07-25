#!/usr/bin/env python3
"""Which state registers the most of each vehicle/fuel type — from the Vahan4
dashboard (Y-Axis=State, X-Axis=Fuel, all-India, CY2026 YTD, captured 2026-07-25).
Columns aggregate the raw Vahan fuel labels. Pure stdlib.
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"; OUT.mkdir(parents=True, exist_ok=True)

# State: [Petrol, Diesel, CNG(incl petrol/CNG), EV(BEV+PHEV), StrongHybrid, TOTAL]
DATA = [
 ["Andaman & Nicobar",6118,408,8,97,46,6892],["Andhra Pradesh",446652,80985,14034,61423,1236,612349],
 ["Arunachal Pradesh",16836,6784,37,98,103,24892],["Assam",278580,19718,427,61211,340,364595],
 ["Bihar",738218,60463,30940,82820,457,921032],["Chandigarh",20802,4090,673,3850,993,31096],
 ["Chhattisgarh",299811,54723,875,34950,868,404217],["Delhi",349240,7352,56366,57741,5817,481224],
 ["Goa",37311,3067,827,7036,247,49798],["Gujarat",845651,160569,156227,68193,5101,1243559],
 ["Haryana",392582,109663,99399,21288,5926,634621],["Himachal Pradesh",76375,13971,537,1297,523,95083],
 ["Jammu & Kashmir",99935,18426,131,9351,211,130461],["Jharkhand",331846,35705,8579,24358,377,405759],
 ["Karnataka",861292,134401,65320,167258,7277,1257827],["Kerala",427027,50554,16640,81920,5014,591218],
 ["Ladakh",2017,776,0,4,5,2967],["Lakshadweep",622,18,0,64,0,711],
 ["Madhya Pradesh",687979,139953,49904,106097,1208,990681],["Maharashtra",1348343,212598,172640,203910,9711,1968620],
 ["Manipur",19040,1329,1,1105,20,21891],["Meghalaya",21907,2934,5,543,49,26011],
 ["Mizoram",17218,2294,0,733,18,20395],["Nagaland",8402,8869,202,20,45,17969],
 ["Odisha",427299,58351,7780,82689,914,583134],["Puducherry",43384,2268,618,4420,335,51828],
 ["Punjab",348746,87113,11237,32825,3196,490187],["Rajasthan",632957,179593,65228,91066,1686,977726],
 ["Sikkim",5906,1455,0,12,10,7444],["Tamil Nadu",1211013,121240,43483,157548,5394,1554821],
 ["Telangana",436293,71193,20445,71226,1350,616199],["Tripura",20208,2081,3369,5412,21,31248],
 ["DNH & DD",9551,3386,1091,194,227,14697],["Uttarakhand",135237,16335,4637,14155,790,174198],
 ["Uttar Pradesh",1859562,208374,138753,255655,5762,2478330],["West Bengal",651038,47757,10974,95109,1230,813177],
]
COLS = ["Petrol","Diesel","CNG","EV","StrongHybrid","Total"]


def main():
    rows = [dict(state=d[0], Petrol=d[1], Diesel=d[2], CNG=d[3], EV=d[4], StrongHybrid=d[5], Total=d[6]) for d in DATA]
    with (OUT / "statewise_fuel_cy2026.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["state"]+COLS); w.writeheader(); w.writerows(rows)

    def top(metric, n=5, by_share=False):
        key = (lambda r: r[metric]/r["Total"] if r["Total"] else 0) if by_share else (lambda r: r[metric])
        return sorted([r for r in rows if r["Total"] >= 20000], key=key, reverse=True)[:n]

    L = ["# Which state registers the most of each vehicle/fuel type — Vahan CY2026 (YTD)\n",
         "Source: Vahan4 dashboard, Y-Axis=State × X-Axis=Fuel, all-India, all categories, CY2026 year-to-date. "
         "Captured 2026-07-25. EV = ELECTRIC(BOV)+PURE EV+PHEV; CNG incl. petrol/CNG bi-fuel; petrol incl. E20 & mild-hybrid.\n"]

    L.append("## Leaders by absolute count\n| Type | #1 | #2 | #3 |\n|---|---|---|---|")
    for m in ["Total","Petrol","Diesel","CNG","EV","StrongHybrid"]:
        t = top(m,3)
        L.append(f"| **{m}** | {t[0]['state']} ({t[0][m]:,}) | {t[1]['state']} ({t[1][m]:,}) | {t[2]['state']} ({t[2][m]:,}) |")
    L.append("")

    L.append("## Leaders by penetration (share of that state's registrations)\n| Type | #1 | #2 | #3 |\n|---|---|---|---|")
    for m in ["EV","CNG","Diesel","StrongHybrid"]:
        t = top(m,3,by_share=True)
        L.append(f"| **{m} share** | {t[0]['state']} ({100*t[0][m]/t[0]['Total']:.0f}%) | {t[1]['state']} ({100*t[1][m]/t[1]['Total']:.0f}%) | {t[2]['state']} ({100*t[2][m]/t[2]['Total']:.0f}%) |")
    L.append("")

    L.append("## The read\n")
    L.append("- **Uttar Pradesh is the biggest market overall** and leads **petrol** and **EV** by count — "
             "its EV lead is e-rickshaws/e-2W, not e-cars.")
    L.append("- **Maharashtra leads diesel, CNG and strong-hybrid by count** — the premium & commercial fuels.")
    L.append("- **By EV *share*, the east/northeast lead** (Assam, Tripura ~17%) on e-rickshaws; Delhi ~12% is "
             "the top big-state on e-cars/2W.")
    L.append("- **CNG penetration is highest in Haryana, Gujarat and Delhi** — the mature CGD-network states.\n")
    (OUT / "statewise_fuel_analysis.md").write_text("\n".join(L))

    print("Biggest market:", top("Total")[0]["state"], f"{top('Total')[0]['Total']:,}")
    for m in ["Petrol","Diesel","CNG","EV","StrongHybrid"]:
        t=top(m); ts=top(m,by_share=True)
        print(f"{m:13s} count -> {t[0]['state']:14s} ({t[0][m]:>9,}) | share -> {ts[0]['state']} ({100*ts[0][m]/ts[0]['Total']:.0f}%)")
    print("Wrote outputs/statewise_fuel_analysis.md + statewise_fuel_cy2026.csv")


if __name__ == "__main__":
    main()
