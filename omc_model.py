#!/usr/bin/env python3
"""OMC retail profitability model — petrol (MS) & diesel (HSD) sold through
retail outlets, with the ethanol-blending (E20/E25/E30) income effect.

Business question: how much marketing margin do the Oil Marketing Companies
earn from retail petrol/diesel, how does that grow year-on-year from rising
vehicle demand, and how much *extra* comes from ethanol blending (which cuts
mileage, forcing more litres through the pump for the same distance driven)?

All inputs are PPAC "Ready Reckoner FY 2025-26 (H1)" actuals or clearly-flagged
editable levers. Volumes anchored on Table 6.1 national consumption (not the
6.4D per-RO KL column, which is an H1-over-12-months artifact). Pure stdlib.

Units: volumes in billion litres (bn L); money in ₹ crore (1 cr = 1e7).
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)

# ────────────────────────────────────────────────────────────────────────────
# INPUTS  (edit these; everything downstream recomputes)
# ────────────────────────────────────────────────────────────────────────────
# --- PPAC Ready Reckoner FY2025-26 (H1) actuals ---
N_RO_2025          = 99_281      # retail outlets as on 01.10.2025 (Table 6.6/6.7)
N_RO_2024          = 91_949      # as on 01.10.2024 (Table 6.4D) -> network +8.0% YoY
MS_MMT_FY2425      = 40.0        # MS (petrol) national consumption FY24-25, MMT (Table 6.1)
HSD_MMT_FY2425     = 91.4        # HSD (diesel) national consumption FY24-25, MMT (Table 6.1)
# H1 YoY growth from Table 6.1 (H1 25-26 vs H1 24-25): MS 21.2/19.8, HSD 45.7/44.4
MS_GROWTH          = 0.071       # petrol demand growth YoY (vehicle-sales driven)
HSD_GROWTH         = 0.029       # diesel demand growth YoY (vehicle-sales driven)
RO_GROWTH          = 0.045       # outlet-network growth YoY (slowing toward 1-lakh saturation)

# --- fuel density (kg/L) to convert MMT -> litres ---
DENS_MS            = 0.74
DENS_HSD           = 0.83

# --- OMC net marketing margin retained on retail auto-fuel (₹/L) — KEY LEVER ---
# Not published cleanly and swings with crude; central estimates. Dealer
# commission (RR 8.10, ~₹4.1/L petrol, ₹3.1/L diesel) is the DEALER's cut and
# is excluded — this is the OMC's own marketing margin.
OMC_MARGIN_MS      = 3.5
OMC_MARGIN_HSD     = 2.5

# --- ethanol blending: blend % -> real-world mileage drop ---
# E20 drop 4% is the SIAM/ARAI central figure (2-6% band); higher blends scale
# up ~linearly with ethanol's lower calorific value (~34% below petrol).
BLEND = {
    "E0":  {"pct": 0.00, "mileage_drop": 0.000},   # no ethanol (baseline / legacy pockets)
    "E20": {"pct": 0.20, "mileage_drop": 0.040},   # current (achieved ~2025)
    "E25": {"pct": 0.25, "mileage_drop": 0.055},
    "E30": {"pct": 0.30, "mileage_drop": 0.070},
}
CURRENT_BLEND      = "E20"

# Fuel-pool MIX scenarios: shares of petrol distance-demand served at each blend
# level (each row must sum to 1.0). Realistic transition — the pool shifts, it
# does not jump uniformly. Order: (E0, E20, E25, E30).
MIX_SCENARIOS = {
    "S0 Today (~E20)":       (0.05, 0.95, 0.00, 0.00),
    "S1 E20 universal":      (0.00, 1.00, 0.00, 0.00),
    "S2 Transition FY27":    (0.05, 0.55, 0.35, 0.05),
    "S3 E25 majority FY28":  (0.05, 0.20, 0.60, 0.15),
    "S4 E30 push FY30":      (0.05, 0.10, 0.25, 0.60),
}
ETHANOL_PROCURE    = 62.0    # ₹/L avg OMC ethanol procurement (indicative, ESY24-25)
PETROL_REFINERY    = 58.0    # ₹/L indicative refinery/trade-parity cost of petrol displaced

CR = 1e7   # ₹ per crore


def bnL_from_MMT(mmt, dens):
    """MMT -> billion litres.  1 MMT = 1e9 kg; /density = L; /1e9 = bn L."""
    return mmt * 1e9 / dens / 1e9


# ────────────────────────────────────────────────────────────────────────────
# BASE (FY24-25 actual)
# ────────────────────────────────────────────────────────────────────────────
ms_bnL_base  = bnL_from_MMT(MS_MMT_FY2425, DENS_MS)     # blended petrol dispensed (incl. ethanol)
hsd_bnL_base = bnL_from_MMT(HSD_MMT_FY2425, DENS_HSD)

def omc_income(ms_bnL, hsd_bnL):
    """OMC retail marketing gross margin, ₹ crore."""
    ms  = ms_bnL * 1e9 * OMC_MARGIN_MS / CR
    hsd = hsd_bnL * 1e9 * OMC_MARGIN_HSD / CR
    return ms, hsd, ms + hsd

ms_inc, hsd_inc, tot_inc = omc_income(ms_bnL_base, hsd_bnL_base)

# per-RO throughput (true, from national volume / outlets)
ms_perRO_klmo  = ms_bnL_base * 1e9 / N_RO_2025 / 12 / 1000
hsd_perRO_klmo = hsd_bnL_base * 1e9 / N_RO_2025 / 12 / 1000

# ────────────────────────────────────────────────────────────────────────────
# ETHANOL SCENARIOS  (petrol only; diesel unaffected by ethanol)
# ────────────────────────────────────────────────────────────────────────────
# Hold distance driven fixed at the E0-equivalent implied by the CURRENT blend,
# so scenarios are comparable. L0 = petrol litres needed with NO ethanol.
m_now = BLEND[CURRENT_BLEND]["mileage_drop"]
L0 = ms_bnL_base * (1 - m_now)      # E0-equivalent petrol volume (fixed distance)

def scenario(tag):
    b = BLEND[tag]
    m = b["mileage_drop"]
    blend_vol = L0 / (1 - m)                     # blended petrol dispensed for same distance
    ethanol_vol = blend_vol * b["pct"]           # ethanol content
    petrol_vol = blend_vol * (1 - b["pct"])      # pure MS content (petrol actually sold)
    extra_vs_e0 = blend_vol - L0                 # extra throughput vs no-ethanol baseline
    extra_income = extra_vs_e0 * 1e9 * OMC_MARGIN_MS / CR     # ₹ cr additional OMC pump income
    # ethanol vs displaced-petrol cost gap (import-substitution / cost view)
    ethanol_cost_gap = ethanol_vol * 1e9 * (ETHANOL_PROCURE - PETROL_REFINERY) / CR
    return {
        "scenario": tag,
        "blend_pct": b["pct"],
        "mileage_drop": m,
        "blend_vol_bnL": blend_vol,
        "petrol_MS_bnL": petrol_vol,
        "ethanol_bnL": ethanol_vol,
        "extra_throughput_bnL": extra_vs_e0,
        "extra_OMC_income_cr": extra_income,
        "ethanol_cost_gap_cr": ethanol_cost_gap,
    }

scenarios = [scenario(t) for t in ("E0", "E20", "E25", "E30")]

# ── MIX scenarios: petrol pool split across E0/E20/E25/E30 in a ratio ─────────
ORDER = ("E0", "E20", "E25", "E30")

def mix_scenario(name, shares):
    assert abs(sum(shares) - 1) < 1e-9, f"{name}: shares must sum to 1"
    blend_vol = ethanol_vol = wdrop = 0.0
    for tag, sh in zip(ORDER, shares):
        m = BLEND[tag]["mileage_drop"]
        L0_b = L0 * sh                        # E0-equivalent distance-demand for this slice
        bv = L0_b / (1 - m)                   # blended litres to serve it
        blend_vol += bv
        ethanol_vol += bv * BLEND[tag]["pct"]
        wdrop += sh * m
    petrol_vol = blend_vol - ethanol_vol
    extra_vs_e0 = blend_vol - L0
    return {
        "scenario": name,
        **{f"share_{t}": s for t, s in zip(ORDER, shares)},
        "wtd_mileage_drop": wdrop,
        "blend_vol_bnL": blend_vol,
        "petrol_MS_bnL": petrol_vol,
        "ethanol_bnL": ethanol_vol,
        "extra_vs_e0_bnL": extra_vs_e0,
        "omc_petrol_income_cr": blend_vol * 1e9 * OMC_MARGIN_MS / CR,
        "extra_OMC_income_cr": extra_vs_e0 * 1e9 * OMC_MARGIN_MS / CR,
    }

mixes = [mix_scenario(n, sh) for n, sh in MIX_SCENARIOS.items()]

# ────────────────────────────────────────────────────────────────────────────
# YoY PROJECTION  FY25-26 → FY29-30
#   - vehicle-driven demand growth compounds distance (L0 and HSD)
#   - ethanol blend steps up per NBP roadmap (editable)
#   - outlet network grows
# ────────────────────────────────────────────────────────────────────────────
ROADMAP = {  # fiscal-year-end -> blend tag
    "FY25-26": "E20", "FY26-27": "E20", "FY27-28": "E25",
    "FY28-29": "E25", "FY29-30": "E30",
}
proj = []
L0_y, hsd_y, nro_y = L0, hsd_bnL_base, N_RO_2025
prev_tot = None
for i, (fy, tag) in enumerate(ROADMAP.items()):
    if i:  # grow demand & network from year 1 onward
        L0_y  *= (1 + MS_GROWTH)
        hsd_y *= (1 + HSD_GROWTH)
        nro_y *= (1 + RO_GROWTH)
    m = BLEND[tag]["mileage_drop"]
    blend_vol = L0_y / (1 - m)
    ms_i  = blend_vol * 1e9 * OMC_MARGIN_MS / CR
    hsd_i = hsd_y * 1e9 * OMC_MARGIN_HSD / CR
    tot   = ms_i + hsd_i
    ethanol_extra = (blend_vol - L0_y) * 1e9 * OMC_MARGIN_MS / CR
    proj.append({
        "fy": fy, "blend": tag,
        "outlets": round(nro_y),
        "petrol_blend_bnL": round(blend_vol, 2),
        "diesel_bnL": round(hsd_y, 2),
        "omc_income_cr": round(tot),
        "yoy_growth_cr": None if prev_tot is None else round(tot - prev_tot),
        "ethanol_attributable_cr": round(ethanol_extra),
    })
    prev_tot = tot

# ────────────────────────────────────────────────────────────────────────────
# OUTPUT
# ────────────────────────────────────────────────────────────────────────────
def write_csvs():
    with (OUT / "scenarios.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(scenarios[0].keys())); w.writeheader()
        for s in scenarios:
            w.writerow({k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()})
    with (OUT / "yoy_projection.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(proj[0].keys())); w.writeheader(); w.writerows(proj)
    with (OUT / "blend_mix_scenarios.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(mixes[0].keys())); w.writeheader()
        for m in mixes:
            w.writerow({k: (round(v, 3) if isinstance(v, float) else v) for k, v in m.items()})


def write_md():
    L = []
    L.append("# OMC Retail Profitability Model — petrol & diesel, with E20/E25/E30 ethanol effect\n")
    L.append("Inputs from PPAC *Oil & Gas Ready Reckoner FY 2025-26 (H1)*; margins and mileage-drop "
             "factors are editable levers in `omc_model.py`. Volumes anchored on Table 6.1 national "
             "consumption. **Illustrative — OMC marketing margins are not published cleanly and swing "
             "with crude; treat absolute ₹ as order-of-magnitude, and the ethanol *deltas* (which are "
             "margin-independent in %) as the robust result.**\n")

    L.append("## 1. Base retail book (FY 2024-25 actual)\n")
    L.append("| Item | Petrol (MS) | Diesel (HSD) |")
    L.append("|---|--:|--:|")
    L.append(f"| National consumption (MMT) | {MS_MMT_FY2425} | {HSD_MMT_FY2425} |")
    L.append(f"| Volume (bn litres) | {ms_bnL_base:.1f} | {hsd_bnL_base:.1f} |")
    L.append(f"| OMC marketing margin (₹/L, lever) | {OMC_MARGIN_MS} | {OMC_MARGIN_HSD} |")
    L.append(f"| **OMC retail gross margin (₹ cr/yr)** | **{ms_inc:,.0f}** | **{hsd_inc:,.0f}** |")
    L.append(f"\nRetail outlets (01.10.2025): **{N_RO_2025:,}** (PSU 90,022 + private 9,259). "
             f"True avg throughput per RO: petrol **{ms_perRO_klmo:.0f} KL/month**, diesel "
             f"**{hsd_perRO_klmo:.0f} KL/month**.\n")
    L.append(f"**Total OMC retail marketing gross ≈ ₹{tot_inc:,.0f} crore/yr.**\n")
    L.append("> Network dilution: outlets grew +8.0% (91,949→99,281) while fuel demand grew ~3-7%, so "
             "PPAC's per-RO throughput (Table 6.4D) is *falling* YoY — more pumps splitting similar "
             "volume, squeezing per-outlet economics even as the OMC total rises.\n")

    L.append("## 2. Ethanol-blending scenarios (petrol only; same distance driven)\n")
    L.append("Ethanol cuts mileage, so more blended litres flow through the pump for the same distance "
             "— extra throughput the OMC earns margin on. Higher blends amplify it. Ethanol also "
             "*displaces* pure petrol (import substitution), shown separately.\n")
    L.append("| Scenario | Blend % | Mileage drop | Blend vol (bn L) | of which petrol | of which ethanol | Extra vs E0 (bn L) | **Extra OMC pump income (₹ cr/yr)** |")
    L.append("|---|--:|--:|--:|--:|--:|--:|--:|")
    for s in scenarios:
        L.append(f"| {s['scenario']} | {s['blend_pct']*100:.0f}% | {s['mileage_drop']*100:.1f}% "
                 f"| {s['blend_vol_bnL']:.1f} | {s['petrol_MS_bnL']:.1f} | {s['ethanol_bnL']:.1f} "
                 f"| {s['extra_throughput_bnL']:.2f} | **{s['extra_OMC_income_cr']:,.0f}** |")
    e0, e20, e25, e30 = scenarios
    L.append(f"\n- Going **E20→E25** adds ~₹{e25['extra_OMC_income_cr']-e20['extra_OMC_income_cr']:,.0f} cr/yr "
             f"of extra pump throughput income; **E20→E30** adds ~₹{e30['extra_OMC_income_cr']-e20['extra_OMC_income_cr']:,.0f} cr/yr.")
    L.append(f"- But pure petrol (MS) sold *falls* {e20['petrol_MS_bnL']:.1f}→{e30['petrol_MS_bnL']:.1f} bn L as "
             f"ethanol content rises {e20['ethanol_bnL']:.1f}→{e30['ethanol_bnL']:.1f} bn L — the import-"
             "substitution the blending programme is really for.\n")

    L.append("## 3. Fuel-pool MIX scenarios (E0 / E20 / E25 / E30 in a ratio)\n")
    L.append("The petrol pool does not jump uniformly to one blend — a share sits at E0 (legacy 2W, "
             "premium grades, ethanol-supply-short pockets), a share at E20, and E25/E30 roll in. Each "
             "row below is a volume-share mix; OMC pump income is the blend-weighted throughput × margin. "
             "Same underlying distance driven across all rows.\n")
    L.append("| Mix scenario | E0 | E20 | E25 | E30 | Wtd drop | Blend vol (bn L) | Petrol MS (bn L) | Ethanol (bn L) | OMC petrol income (₹ cr) | Extra vs all-E0 (₹ cr) |")
    L.append("|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
    for m in mixes:
        L.append(f"| {m['scenario']} | {m['share_E0']*100:.0f}% | {m['share_E20']*100:.0f}% "
                 f"| {m['share_E25']*100:.0f}% | {m['share_E30']*100:.0f}% | {m['wtd_mileage_drop']*100:.1f}% "
                 f"| {m['blend_vol_bnL']:.1f} | {m['petrol_MS_bnL']:.1f} | {m['ethanol_bnL']:.1f} "
                 f"| {m['omc_petrol_income_cr']:,.0f} | {m['extra_OMC_income_cr']:,.0f} |")
    m0, m4 = mixes[0], mixes[-1]
    L.append(f"\nShifting the pool from **{m0['scenario']}** to **{m4['scenario']}** lifts OMC petrol "
             f"throughput income ₹{m0['omc_petrol_income_cr']:,.0f}→₹{m4['omc_petrol_income_cr']:,.0f} cr "
             f"(+₹{m4['omc_petrol_income_cr']-m0['omc_petrol_income_cr']:,.0f} cr) purely from the mileage "
             f"penalty, while pure-petrol volume falls {m0['petrol_MS_bnL']:.1f}→{m4['petrol_MS_bnL']:.1f} bn L "
             f"and ethanol offtake rises {m0['ethanol_bnL']:.1f}→{m4['ethanol_bnL']:.1f} bn L.\n")

    L.append("## 4. Caveat — CBG blended into CNG does NOT behave like ethanol\n")
    L.append("The mileage-drop → extra-throughput mechanism above is **specific to ethanol-in-petrol**, "
             "because ethanol carries ~34% less energy per litre than petrol, so a blended litre drives "
             "fewer km and more litres are dispensed. **Compressed Bio-Gas (CBG) cascaded into the CNG "
             "grid does not do this**, for a quality-standard reason:\n")
    L.append("- CBG for automotive use / grid injection must meet **IS 16087** (Bio-CNG / bio-methane "
             "specification) — minimum **~90% methane**, tight caps on CO₂, moisture and H₂S. *(The "
             "\"IS 1876\" in the request appears to be shorthand for IS 16087; the fossil-CNG automotive "
             "spec it is matched against is **IS 15958**.)*\n")
    L.append("- Because IS 16087 forces CBG's methane content — and hence its **calorific value / Wobbe "
             "index** — to match pipeline/fossil CNG (IS 15958), CBG is *fungible* with CNG. A CNG vehicle "
             "running on a CBG-blended stream sees **no meaningful mileage change** (km/kg is preserved), "
             "unlike the petrol vehicle on E20+.\n")
    L.append("- **Consequence for this model:** there is **no CBG-driven throughput uplift** for the CNG "
             "book analogous to the ethanol effect. The OMC/CGD gain from CBG is instead in *procurement "
             "and policy* terms — SATAT assured-price offtake, GST/green-fuel treatment and import "
             "substitution of LNG — **not** extra kg dispensed. So the ethanol income lift is a petrol-"
             "pool phenomenon only; the CNG/CBG pool should not be credited with the same mechanism.\n")

    L.append("## 5. Year-on-year projection (vehicle demand + blend roadmap)\n")
    L.append("Petrol/diesel demand compounds with vehicle-sales-driven growth "
             f"(MS +{MS_GROWTH*100:.0f}%, HSD +{HSD_GROWTH*100:.0f}%/yr); blend steps E20→E25→E30 per an "
             "editable roadmap; outlets +{:.0f}%/yr.\n".format(RO_GROWTH*100))
    L.append("| FY | Blend | Outlets | Petrol blend (bn L) | Diesel (bn L) | OMC income (₹ cr) | YoY Δ (₹ cr) | of which ethanol (₹ cr) |")
    L.append("|---|---|--:|--:|--:|--:|--:|--:|")
    for p in proj:
        L.append(f"| {p['fy']} | {p['blend']} | {p['outlets']:,} | {p['petrol_blend_bnL']} | "
                 f"{p['diesel_bnL']} | {p['omc_income_cr']:,} | "
                 f"{'—' if p['yoy_growth_cr'] is None else format(p['yoy_growth_cr'], ',')} | "
                 f"{p['ethanol_attributable_cr']:,} |")
    L.append("")
    L.append("---")
    L.append("*Generated by `omc_model.py`. Illustrative analytical estimates, not investment advice. "
             "OMC marketing margin is the key editable assumption.*")
    (OUT / "omc_profitability_report.md").write_text("\n".join(L))


write_csvs()
write_md()

print(f"Base FY24-25: OMC retail gross ≈ ₹{tot_inc:,.0f} cr/yr "
      f"(petrol ₹{ms_inc:,.0f} + diesel ₹{hsd_inc:,.0f})")
sc = {s["scenario"]: s for s in scenarios}
print(f"Ethanol extra pump income:  E20 ₹{sc['E20']['extra_OMC_income_cr']:,.0f} cr | "
      f"E25 ₹{sc['E25']['extra_OMC_income_cr']:,.0f} cr | E30 ₹{sc['E30']['extra_OMC_income_cr']:,.0f} cr")
print("Mix scenarios (OMC petrol income ₹cr):",
      " | ".join(f"{m['scenario'].split()[0]} ₹{m['omc_petrol_income_cr']:,.0f}" for m in mixes))
print(f"YoY projection {proj[0]['fy']}→{proj[-1]['fy']}: "
      f"₹{proj[0]['omc_income_cr']:,} → ₹{proj[-1]['omc_income_cr']:,} cr")
print(f"Wrote: outputs/omc_profitability_report.md, scenarios.csv, yoy_projection.csv")
