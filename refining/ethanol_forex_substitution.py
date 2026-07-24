#!/usr/bin/env python3
"""Ethanol → freed petrol → petrochemicals: the rupee-vs-dollar import-substitution case.

The chain: ethanol blending (paid in RUPEES to Indian farmers/distilleries) frees
petrol-range volume; that volume can (a) cut crude imports, (b) be exported, or
(c) be cracked into petrochemicals that substitute DOLLAR imports. Because ethanol
is domestic rupee and crude/petrochemicals are forex, every litre swaps a dollar
outflow for a rupee flow that recirculates at home. This sizes the volume and the
forex saving at E20/E25/E30. Pure stdlib.
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"; OUT.mkdir(parents=True, exist_ok=True)

# ── inputs (editable) ────────────────────────────────────────────────────────
PETROL_BNL = 54.05                 # domestic petrol (MS) blended volume, bn L (40 MMT)
# PPAC Ready Reckoner Table 9.2/9.3 — official conversion factors (petrol, BS norms):
PETROL_KL_PER_MT = 1.4110          # 1 MT petrol = 1.411 KL  (=> density ≈ 0.709 kg/L)
PETROL_BBL_PER_MT = 8.88           # 1 MT petrol = 8.88 US bbl
L_PER_BBL = 159.0                  # Table 9.3: 1 US bbl = 159 L
BNL_PER_MMT = PETROL_KL_PER_MT     # 1 MMT petrol = 1.411 bn L  (so MMT = bnL / 1.411)
USD_INR = 86.0
NAPHTHA_TO_PETCHEM_YIELD = 0.60    # mass fraction of naphtha -> primary petrochemicals
PETROL_FOB_USD_BBL = 85.0          # freed petrol worth (FOB export / crude-parity)
POLYMER_USD_T = 1100.0             # avg polymer import price (substitution value)
ETHANOL_RS_L = 60.0                # ethanol procurement, ₹/L (DOMESTIC rupee)
SUBSTITUTABLE_PETCHEM_MMT = 13.0   # India's substitutable polymer imports, ~MMT (~$15 bn)
BLENDS = {"E20": 0.20, "E25": 0.25, "E30": 0.30}
CR = 1e7


def main():
    rows = []
    for tag, frac in BLENDS.items():
        freed_bnL = frac * PETROL_BNL
        freed_MMT = freed_bnL / BNL_PER_MMT
        petchem_MMT = freed_MMT * NAPHTHA_TO_PETCHEM_YIELD
        forex_petrol_usdbn = freed_bnL * (PETROL_FOB_USD_BBL / L_PER_BBL)             # crude saved / exported ($ bn)
        forex_petchem_usdbn = petchem_MMT * 1e6 * POLYMER_USD_T / 1e9                 # petchem imports substituted
        ethanol_rupee_cr = freed_bnL * 1e9 * ETHANOL_RS_L / CR                        # DOMESTIC rupee cost
        petchem_share = petchem_MMT / SUBSTITUTABLE_PETCHEM_MMT
        rows.append({
            "blend": tag, "freed_petrol_bnL": round(freed_bnL, 2), "freed_MMT": round(freed_MMT, 2),
            "petchem_MMT": round(petchem_MMT, 2),
            "forex_petrol_usdbn": round(forex_petrol_usdbn, 2),
            "forex_petchem_usdbn": round(forex_petchem_usdbn, 2),
            "ethanol_rupee_cr": round(ethanol_rupee_cr),
            "petchem_import_share_pct": round(petchem_share * 100),
        })

    with (OUT / "ethanol_forex_substitution.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    e20, e30 = rows[0], rows[-1]
    petrol_fob_rs_l = PETROL_FOB_USD_BBL / L_PER_BBL * USD_INR   # ₹/L equivalent of FOB petrol
    premium = ETHANOL_RS_L - petrol_fob_rs_l

    L = []
    L.append("# Ethanol → freed petrol → petrochemicals: the rupee-vs-dollar substitution\n")
    L.append("**The premise.** Ethanol blending is paid for in **rupees** — to Indian sugarcane/grain "
             "farmers and distilleries — while the crude it offsets and the petrochemicals India imports are "
             "paid in **dollars**. So beyond the litres saved, ethanol does something structural: it swaps a "
             "*forex* outflow for a *domestic rupee* flow. This traces the volume and the forex.\n")

    L.append("## 1. Volume — petrol saved → petrochemicals producible\n")
    L.append("| Blend | Petrol freed (bn L) | = MMT | If cracked → petchem (MMT, 60% yield) | Share of India's ~13 MMT substitutable polymer imports |")
    L.append("|---|--:|--:|--:|--:|")
    for r in rows:
        L.append(f"| {r['blend']} | {r['freed_petrol_bnL']} | {r['freed_MMT']} | {r['petchem_MMT']} | ~{r['petchem_import_share_pct']}% |")
    L.append("")
    L.append(f"- Ethanol frees **{e20['freed_MMT']} MMT** of petrol-range material at E20, **{e30['freed_MMT']} MMT** "
             f"at E30. Cracked, that yields **{e20['petchem_MMT']}–{e30['petchem_MMT']} MMT of petrochemicals** — "
             f"enough to substitute **~{e20['petchem_import_share_pct']}% (E20) to ~{e30['petchem_import_share_pct']}% "
             "(E30) of India's entire substitutable polymer import bill**, from freed feedstock alone.\n")

    L.append("## 2. The three fates of the freed petrol — all forex-positive\n")
    L.append("| Blend | (a) Crude saved / petrol exported ($ bn) | (b) Petchem imports substituted if cracked ($ bn) |")
    L.append("|---|--:|--:|")
    for r in rows:
        L.append(f"| {r['blend']} | ${r['forex_petrol_usdbn']} bn | ${r['forex_petchem_usdbn']} bn |")
    L.append("")
    L.append(f"- Whichever way the freed petrol is used, it is worth **~${e20['forex_petrol_usdbn']}–{e30['forex_petrol_usdbn']} bn/yr "
             "of forex** as crude-saved or exported fuel. **Cracked into petrochemicals it is worth even more** "
             f"(${e20['forex_petchem_usdbn']}–{e30['forex_petchem_usdbn']} bn) because polymers price above fuel — "
             "and it substitutes a dollar import instead of just earning a fuel margin.\n")

    L.append("## 3. The core — rupee in, dollars out (saved)\n")
    L.append("| | Currency | E20 | E30 |")
    L.append("|---|---|--:|--:|")
    L.append(f"| Ethanol production cost | **₹ (domestic)** | ₹{e20['ethanol_rupee_cr']:,} cr | ₹{e30['ethanol_rupee_cr']:,} cr |")
    L.append(f"| Forex freed (crude/petrol) | **$ (forex)** | ${e20['forex_petrol_usdbn']} bn | ${e30['forex_petrol_usdbn']} bn |")
    L.append(f"| Forex saved if cracked to petchem | **$ (forex)** | ${e20['forex_petchem_usdbn']} bn | ${e30['forex_petchem_usdbn']} bn |")
    L.append("")
    L.append(f"- India spends **₹{e20['ethanol_rupee_cr']:,}–{e30['ethanol_rupee_cr']:,} cr in rupees** on ethanol — "
             "money that stays in the country (farmer income, rural distilleries, ~2.5–3× local multiplier) — to "
             f"free **~${e20['forex_petrol_usdbn']}–{e30['forex_petchem_usdbn']} bn of dollar imports**. The rupee "
             "cost is a *domestic transfer*; the dollar saving is a *current-account and rupee-stability* gain.")
    L.append(f"- Honest premium: at ₹{ETHANOL_RS_L:.0f}/L, ethanol costs ~₹{premium:.0f}/L **more** than the freed "
             f"petrol's fuel value (~₹{petrol_fob_rs_l:.0f}/L FOB) — but that premium is paid in rupees to Indian "
             "producers, not dollars to crude exporters, and shrinks or reverses when the freed feedstock is "
             "cracked into higher-value petrochemicals rather than sold as fuel.\n")

    L.append("## 4. Why the currency matters (not just the number)\n")
    L.append("- **Crude** (~$137 bn/yr) and **petrochemicals** (~$15 bn substitutable) are India's largest "
             "dollar outflows — mineral fuels alone are ~54% of the trade deficit. Every unit shifted to "
             "domestic ethanol/feedstock **directly narrows the current-account gap** and reduces rupee "
             "pressure from oil-price and FX swings.")
    L.append("- **Ethanol is rupee-denominated end to end** — feedstock (Indian cane/grain), conversion "
             "(domestic distilleries), labour (rural) — so its cost recirculates as domestic demand and farm "
             "income, unlike a dollar paid to a crude or polymer exporter which leaves the economy.")
    L.append("- **The compounding move:** ethanol frees the petrol → the freed naphtha/reformate is cracked "
             "into the very petrochemicals India imports → a *second* dollar import is substituted, at a higher "
             "value per tonne. Rupee feedstock displacing dollar polymers is the crude-to-chemicals endgame.\n")

    L.append("## 5. Caveats\n")
    L.append("- **Unit conversions are PPAC Ready Reckoner Table 9.2/9.3** (official): 1 MT petrol = 1.411 KL "
             "= 8.88 bbl; 1 bbl = 159 L; 1 MMT = 1.411 bn L. PPAC **Table 9.6** designates naphtha as "
             "'feedstock for the petrochemical sector' — the petrol→petchem route is the reckoner's own "
             "classification, not an assumption.")
    L.append("- Freed volume = ethanol blended (blend% × domestic petrol), consistent with the sibling models. "
             "Naphtha-to-petchem yield (~60%) and polymer price ($1,100/t) are editable; petrol and petrol-range "
             "naphtha are treated as interchangeable cracker feed.")
    L.append("- 'Forex freed' via crude-saved and via petrol-export are the *same barrels, one lens* — not "
             "additive. The petchem route is an *alternative* to exporting, not on top of it.")
    L.append("- Ethanol carries a real rupee premium over fuel-value petrol; the case rests on the **currency "
             "composition** (rupee vs dollar) and rural recirculation, not on ethanol being cheaper per litre. "
             "Feedstock (cane/grain) availability bounds how far blending — hence this substitution — can go.\n")
    L.append("---\n*Analytical estimate tying ethanol volume to petrochemical potential and the forex balance; "
             "editable assumptions, not a fiscal forecast.*\n")
    (OUT / "ethanol_forex_substitution.md").write_text("\n".join(L))

    print(f"{'blend':6s}{'freed MMT':>11s}{'petchem MMT':>13s}{'%subst.imports':>16s}{'$bn petrol':>12s}{'$bn petchem':>13s}{'₹cr ethanol':>14s}")
    for r in rows:
        print(f"{r['blend']:6s}{r['freed_MMT']:>11}{r['petchem_MMT']:>13}{r['petchem_import_share_pct']:>15}%"
              f"{r['forex_petrol_usdbn']:>12}{r['forex_petchem_usdbn']:>13}{r['ethanol_rupee_cr']:>14,}")
    print(f"\nRupee-vs-dollar: E20 spends ₹{e20['ethanol_rupee_cr']:,} cr (domestic) to free ~${e20['forex_petrol_usdbn']}-{e20['forex_petchem_usdbn']} bn forex")
    print(f"Ethanol premium over freed-petrol FOB value: ~₹{premium:.0f}/L (rupee, to Indian producers)")
    print("Wrote outputs/ethanol_forex_substitution.md + .csv")


if __name__ == "__main__":
    main()
