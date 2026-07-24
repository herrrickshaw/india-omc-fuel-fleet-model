#!/usr/bin/env python3
"""Value the petrol freed by ethanol blending as export revenue.

Ethanol blended into petrol displaces domestic petrol (MS) demand. Because India
is a net exporter of petroleum products, that freed petrol can be sold abroad at
export (FOB) prices. This sizes the freed volume at E20/E25/E30 and values it
using India's actual petrol-export realisation and its trend (PPAC RR Table 4.11).

Freed volume = ethanol blended = blend% × domestic petrol (blend) volume
             (consistent with the OMC / statewise / sweet-spot models here).
Pure stdlib.
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"; OUT.mkdir(exist_ok=True)

# ── inputs ───────────────────────────────────────────────────────────────────
PETROL_BNL = 54.05            # domestic petrol (MS) blended volume, bn L (40 MMT FY24-25)
DENS_MS = 0.7087             # kg/L, PPAC RR Table 9.2 (petrol 1 MT = 1.411 KL = 8.88 bbl)
L_PER_TONNE = 1000 / DENS_MS  # = 1411 L/t ; 1 MMT = 1.411 bn L
USD_INR = 86.0
BLENDS = {"E20": 0.20, "E25": 0.25, "E30": 0.30}
CR = 1e7

# India petrol (MS) EXPORTS, PPAC RR Table 4.11: [FY, MMT, US$ bn, ₹ crore]
EXPORTS = [
    ("2020-21", 11.6, 5.0, 36530),
    ("2021-22", 13.5, 10.9, 81649),
    ("2022-23", 13.1, 12.9, 102800),
    ("2023-24", 13.5, 11.2, 92957),
    ("2024-25", 15.8, 11.6, 98379),
]


def realisation_rs_per_l(mmt, rs_cr):
    return rs_cr * CR / (mmt * 1e6 * L_PER_TONNE)      # ₹/L

def realisation_usd_per_t(mmt, usd_bn):
    return usd_bn * 1e9 / (mmt * 1e6)                  # $/tonne


def main():
    # export price trend
    trend = []
    for fy, mmt, usdbn, rscr in EXPORTS:
        trend.append({
            "fy": fy, "export_MMT": mmt, "value_usd_bn": usdbn, "value_rs_cr": rscr,
            "realisation_rs_per_L": round(realisation_rs_per_l(mmt, rscr), 1),
            "realisation_usd_per_t": round(realisation_usd_per_t(mmt, usdbn)),
        })
    latest = trend[-1]
    price_central = latest["realisation_rs_per_L"]                 # FY24-25 ~₹46/L
    lows = min(t["realisation_rs_per_L"] for t in trend)           # ~₹23 (FY20-21, COVID)
    highs = max(t["realisation_rs_per_L"] for t in trend)          # ~₹58 (FY22-23, oil spike)
    cur_exp_mmt = latest["export_MMT"]
    cur_exp_cr = latest["value_rs_cr"]

    # freed volume + export value per blend
    rows = []
    for b, frac in BLENDS.items():
        freed_bnL = frac * PETROL_BNL
        freed_mmt = freed_bnL / (L_PER_TONNE / 1000)              # bn L -> MMT
        rev_cr = freed_bnL * 1e9 * price_central / CR
        rev_lo = freed_bnL * 1e9 * lows / CR
        rev_hi = freed_bnL * 1e9 * highs / CR
        rev_usd_bn = freed_mmt * 1e6 * realisation_usd_per_t(cur_exp_mmt, latest["value_usd_bn"]) / 1e9
        rows.append({
            "blend": b, "freed_bnL": round(freed_bnL, 2), "freed_MMT": round(freed_mmt, 2),
            "vs_current_exports_pct": round(100 * freed_mmt / cur_exp_mmt),
            "export_value_cr_central": round(rev_cr),
            "export_value_usd_bn": round(rev_usd_bn, 1),
            "export_value_cr_low": round(rev_lo), "export_value_cr_high": round(rev_hi),
        })

    with (OUT / "petrol_export_value.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    with (OUT / "petrol_export_trend.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(trend[0].keys())); w.writeheader(); w.writerows(trend)

    L = []
    L.append("# Valuing the petrol freed by ethanol blending as export revenue\n")
    L.append("Ethanol blended into petrol frees domestic petrol (MS) that India — a net product exporter "
             "with surplus refining — can sell abroad at FOB prices. Freed volume = ethanol blended = "
             "blend% × domestic petrol volume (54.05 bn L / 40 MMT). Valued at India's own petrol-export "
             "realisation (PPAC RR Table 4.11).\n")

    L.append("## 1. India's petrol-export trend (RR Table 4.11)\n")
    L.append("| FY | Exports (MMT) | Value (₹ cr) | Value ($ bn) | Realisation (₹/L) | ($/tonne) |")
    L.append("|---|--:|--:|--:|--:|--:|")
    for t in trend:
        L.append(f"| {t['fy']} | {t['export_MMT']} | {t['value_rs_cr']:,} | {t['value_usd_bn']} "
                 f"| {t['realisation_rs_per_L']} | {t['realisation_usd_per_t']:,} |")
    L.append("")
    L.append(f"Petrol exports grew from 11.6 MMT to **{cur_exp_mmt} MMT (₹{cur_exp_cr:,} cr)** over five "
             f"years. Realisation swung ₹{lows:.0f}–₹{highs:.0f}/L with crude — central (FY24-25) "
             f"**₹{price_central}/L (~${latest['realisation_usd_per_t']:,}/tonne, ~$86/bbl)**.\n")

    L.append("## 2. Petrol freed by blending, and its export value\n")
    L.append("| Blend | Freed petrol (bn L) | Freed (MMT) | vs current exports | Export value @ ₹%.0f/L (central) | ($ bn) | range ₹%.0f–%.0f/L |"
             % (price_central, lows, highs))
    L.append("|---|--:|--:|--:|--:|--:|--:|")
    for r in rows:
        L.append(f"| {r['blend']} | {r['freed_bnL']} | {r['freed_MMT']} | +{r['vs_current_exports_pct']}% "
                 f"| ₹{r['export_value_cr_central']:,} cr | ${r['export_value_usd_bn']} bn "
                 f"| ₹{r['export_value_cr_low']:,}–{r['export_value_cr_high']:,} cr |")
    L.append("")
    e20, e30 = rows[0], rows[-1]
    L.append(f"- At **E20**, blending frees **{e20['freed_MMT']} MMT** of petrol — **{e20['vs_current_exports_pct']}% "
             f"of India's current 15.8 MMT petrol exports** — worth **~₹{e20['export_value_cr_central']:,} cr "
             f"(${e20['export_value_usd_bn']} bn)/yr** at FOB. In effect, ethanol has *already enabled roughly "
             "half of the petrol India exports today.*")
    L.append(f"- Pushing to **E30** frees **{e30['freed_MMT']} MMT** (~₹{e30['export_value_cr_central']:,} cr / "
             f"${e30['export_value_usd_bn']} bn), which would roughly **double** exportable petrol vs the E20 level.\n")

    L.append("## 3. How this stacks against the other flows in this repo (E20, ₹ cr/yr)\n")
    L.append("| Flow | ₹ cr/yr | Beneficiary |")
    L.append("|---|--:|---|")
    L.append(f"| **Freed-petrol export value** | **~{e20['export_value_cr_central']:,}** | OMC/refiner forex earnings |")
    L.append("| State VAT foregone (ethanol vs petrol) | ~17,900 | states (loss) |")
    L.append("| Central excise foregone | ~21,500 | centre (loss) |")
    L.append("| OMC extra pump throughput income | ~760 | OMC |")
    L.append("| State SGST-on-ethanol @5% (proposed) | ~3,200 | states (gain) |")
    L.append("")
    L.append("The export value dwarfs the domestic tax flows — the freed petrol is the single largest "
             "rupee item ethanol blending creates, and it accrues as **export/forex earnings** rather "
             "than domestic tax.\n")

    L.append("## 4. Caveats\n")
    L.append("- **Export vs import-substitution:** the freed petrol can either be exported (valued here) "
             "*or* let India cut crude imports — the same barrels, valued at a similar FOB/import-parity "
             "price. This is the export lens as requested, not additive to an import-saving claim.")
    L.append("- India already blends ~E20, so today's 15.8 MMT export is *already net* of that; the E20 "
             "row is best read as 'ethanol has enabled ~8 MMT of current exports', E25/E30 as the "
             "incremental frontier (assumes refining runs flat and demand is displaced, not cut).")
    L.append("- Realisation is FOB petrol (~$86/bbl); it swings with crude — the ±band spans the "
             "FY20-25 range. Export excise (RR Table 8.6A, periodic) and freight are not netted.")
    L.append("- Freed volume = ethanol volume (blend%×domestic petrol), consistent with the sibling "
             "models; second-order mileage effects are ignored here.\n")
    L.append("---\n*Analytical estimate from PPAC export data + editable assumptions; not a trade forecast.*\n")
    (OUT / "petrol_export_value.md").write_text("\n".join(L))

    print(f"Export realisation trend (₹/L): " + ", ".join(f"{t['fy']} {t['realisation_rs_per_L']}" for t in trend))
    print(f"Central price {price_central} ₹/L (FY24-25); band {lows:.0f}-{highs:.0f}\n")
    print(f"{'blend':6s}{'freed bnL':>11s}{'freed MMT':>11s}{'%curExp':>9s}{'₹cr central':>13s}{'$bn':>7s}")
    for r in rows:
        print(f"{r['blend']:6s}{r['freed_bnL']:>11}{r['freed_MMT']:>11}{r['vs_current_exports_pct']:>8}%"
              f"{r['export_value_cr_central']:>13,}{r['export_value_usd_bn']:>7}")
    print("Wrote outputs/petrol_export_value.md + petrol_export_value.csv + petrol_export_trend.csv")


if __name__ == "__main__":
    main()
