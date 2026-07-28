#!/usr/bin/env python3
"""CBG economics under SATAT pricing, benchmarked per megajoule and per km
against ethanol blending — using the SIAM/ARAI BS-VI FE declarations from
vehicle_fuel_mileage as the mileage anchor.

Cross-repo inputs:
  vehicle_fuel_mileage/data/fe_by_fuel_summary.csv (ARAI type-approval FE,
    303 4W models, 1 Apr 2020): petrol 16.67 kmpl, diesel 17.91 kmpl,
    CNG 27.40 km/kg; same-nameplate petrol->CNG distance uplift +40.3%.
  omc_model.py: ethanol procurement Rs62/L, petrol refinery Rs58/L.
  fleet_from_fuel.py: CNG(T) national consumption ~6.67 MMT (RR Table 3.7).

SATAT / CBG policy anchors (MoPNG, ESY/FY25-26 basis):
  - SATAT assured ex-plant CBG procurement Rs54/kg (excl. 5% GST), revised
    from the launch Rs46/kg; long-term offtake assurance to plant developers.
  - CBG Blending Obligation (CBO): 1% of CGD gas (CNG-T + PNG-D) FY25-26,
    stepping to ~5% by FY28-29.
  - Gas comparators: domestic APM gas ~$6.5/MMBtu; imported spot RLNG
    ~$12/MMBtu (swing supply that CBG actually displaces at the margin).

Energy basis (LHV): CBG (IS 16087) 46.5 MJ/kg, CNG pipeline 47.5 MJ/kg,
petrol 32.1 MJ/L, ethanol 21.1 MJ/L, diesel 35.7 MJ/L.

Pure stdlib. Outputs: outputs/cbg_satat_economics.md + .csv
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)
CR = 1e7

# energy content (LHV)
MJ_PETROL, MJ_ETH, MJ_DIESEL = 32.1, 21.1, 35.7   # MJ/L
MJ_CBG, MJ_CNG = 46.5, 47.5                        # MJ/kg

# SIAM/ARAI FE declarations (type-approval; relative gaps are the signal)
FE_PETROL, FE_DIESEL, FE_CNG = 16.67, 17.91, 27.40  # kmpl / kmpl / km-per-kg
CNG_UPLIFT = 0.403                                   # same-nameplate distance uplift

# retail prices (Delhi-basis, July 2026)
P_PETROL, P_DIESEL, P_CNG = 105.0, 92.0, 75.0        # Rs/L, Rs/L, Rs/kg

# procurement-side prices
ETH_PROC, PET_REF = 62.0, 58.0                       # Rs/L
SATAT_CBG = 54.0                                     # Rs/kg ex-plant (excl. GST)
GST_CBG = 0.05
USD_INR, MMBTU_MJ = 83.0, 1055.06
APM_USD, RLNG_USD = 6.5, 12.0

def gas_rs_per_kg(usd_mmbtu):
    return usd_mmbtu * USD_INR / MMBTU_MJ * MJ_CNG   # Rs/kg CNG-equivalent

APM_KG, RLNG_KG = gas_rs_per_kg(APM_USD), gas_rs_per_kg(RLNG_USD)

# ── 1. Rs per MJ: what a unit of energy costs, procurement & pump ──────────
proc_rows = [
    ("Petrol (refinery/trade parity)", PET_REF / MJ_PETROL, "Rs58/L"),
    ("Ethanol (OMC procurement)",      ETH_PROC / MJ_ETH,   "Rs62/L"),
    ("Domestic APM gas",               APM_KG / MJ_CNG,     f"~Rs{APM_KG:.0f}/kg eq"),
    ("Imported spot RLNG",             RLNG_KG / MJ_CNG,    f"~Rs{RLNG_KG:.0f}/kg eq"),
    ("CBG (SATAT assured)",            SATAT_CBG / MJ_CBG,  "Rs54/kg ex-plant"),
]
eth_prem = (ETH_PROC / MJ_ETH) / (PET_REF / MJ_PETROL) - 1     # ethanol vs petrol it displaces
cbg_prem = (SATAT_CBG / MJ_CBG) / (RLNG_KG / MJ_CNG) - 1       # CBG vs RLNG it displaces

pump_rows = [
    ("Petrol E20 (pump)", P_PETROL / MJ_PETROL / (1 - 0.068 * 0), "Rs105/L"),  # per-litre energy already E20-diluted below
    ("Diesel (pump)",     P_DIESEL / MJ_DIESEL, "Rs92/L"),
    ("CNG (pump)",        P_CNG / MJ_CNG,       "Rs75/kg"),
]

# ── 2. Rs per km on SIAM/ARAI declared FE ──────────────────────────────────
km_rows = [
    ("Petrol E0",  P_PETROL / FE_PETROL, "16.67 kmpl (SIAM decl.)"),
    ("Petrol E20", P_PETROL / (FE_PETROL * 0.96), "E20 real-world -4%"),
    ("Petrol E30", P_PETROL / (FE_PETROL * 0.93), "E30 real-world -7%"),
    ("Diesel B0",  P_DIESEL / FE_DIESEL, "17.91 kmpl (SIAM decl.)"),
    ("Diesel B20", P_DIESEL / (FE_DIESEL * 0.983), "B20 energy-basis -1.7%"),
    ("CNG",        P_CNG / FE_CNG, "27.40 km/kg (SIAM decl.)"),
    ("CBG (any % in CNG stream)", P_CNG / (FE_CNG * MJ_CBG / MJ_CNG), "energy-scaled 46.5/47.5 MJ/kg"),
]

# ── 3. CBO cost pass-through: does CBG blending move the CNG pump price? ───
CNG_MMT = 6.67                     # CNG(T) national consumption FY24-25 (RR 3.7)
cbo_rows = []
for share in (0.01, 0.05):
    kg = CNG_MMT * 1e9 * share     # kg CBG needed
    proc_cr = kg * SATAT_CBG * (1 + GST_CBG) / CR
    # incremental cost vs the marginal gas displaced (spot RLNG)
    delta_kg = SATAT_CBG * (1 + GST_CBG) - RLNG_KG
    pump_delta = share * delta_kg  # Rs/kg on the blended pump price
    # mileage penalty from CBG's slightly lower MJ/kg at IS 16087 floor
    kmkg_delta = share * (1 - MJ_CBG / MJ_CNG)
    cbo_rows.append({"cbo_share_pct": share*100, "cbg_tonnes": round(kg/1e3),
        "procurement_cr": round(proc_cr), "pump_delta_rs_kg": round(pump_delta, 2),
        "mileage_delta_pct": round(kmkg_delta*100, 2)})

# ── outputs ────────────────────────────────────────────────────────────────
with (OUT / "cbg_satat_economics.csv").open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["metric", "item", "value", "note"])
    for n, v, note in proc_rows: w.writerow(["rs_per_mj_procurement", n, round(v, 2), note])
    for n, v, note in km_rows:   w.writerow(["rs_per_km_siam_fe", n, round(v, 2), note])
    for r in cbo_rows: w.writerow(["cbo", f"{r['cbo_share_pct']}%", r["procurement_cr"],
                                   f"pump +Rs{r['pump_delta_rs_kg']}/kg, mileage {r['mileage_delta_pct']}%"])

L = ["# CBG economics under SATAT pricing — benchmarked against ethanol blending\n",
     "Mileage anchor: SIAM/ARAI BS-VI FE declarations (303 models, vehicle_fuel_mileage "
     "repo): petrol 16.67 kmpl, diesel 17.91 kmpl, CNG 27.40 km/kg; the same nameplate "
     "travels **+40.3% further per unit** on CNG than on petrol.\n"]

L.append("## 1. What a megajoule of energy costs to procure\n")
L.append("| Source | ₹/MJ | Basis |")
L.append("|---|---|---|")
for n, v, note in proc_rows:
    L.append(f"| {n} | {v:.2f} | {note} |")
L.append(f"\n- Ethanol's renewable premium over the petrol it displaces: **+{eth_prem*100:.0f}% per MJ** "
         "(₹2.94 vs ₹1.81) — *before* the mileage-dilution levy on the consumer.\n"
         f"- CBG's premium over the spot RLNG it displaces: **{cbg_prem*100:+.0f}% per MJ** "
         f"(₹{SATAT_CBG/MJ_CBG:.2f} vs ₹{RLNG_KG/MJ_CNG:.2f}) — and it *undercuts* imported gas "
         "whenever spot LNG runs above ~$14.8/MMBtu. Against domestic APM gas CBG is dearer "
         f"(₹{APM_KG/MJ_CNG:.2f}/MJ), but APM supply is static; imports are the margin.\n"
         "- Per MJ of renewable energy bought, SATAT CBG costs ₹1.16 vs ethanol's ₹2.94 — "
         "**2.5× cheaper**, with no volumetric side effects.\n")

L.append("## 2. Cost per km on SIAM/ARAI declared FE (Delhi prices)\n")
L.append("| Fuel | ₹/km | Mileage basis |")
L.append("|---|---|---|")
for n, v, note in km_rows:
    L.append(f"| {n} | {v:.2f} | {note} |")
L.append("\nCNG runs at ~43% of petrol's cost per km (the +40.3% same-nameplate distance "
         "uplift compounding the per-unit price gap). The blend walk moves petrol the "
         "WRONG way (E0 ₹6.30 → E30 ₹6.77/km) while CBG blending leaves the CNG ₹/km "
         "essentially untouched — at the IS 16087 floor the 100%-CBG penalty is 2.1%, "
         "and at CBO shares it rounds to zero.\n")

L.append("## 3. CBG Blending Obligation: national cost, zero consumer levy\n")
L.append(f"CNG(T) pool {CNG_MMT} MMT/yr (RR Table 3.7). SATAT ₹{SATAT_CBG:.0f}/kg + 5% GST vs "
         f"spot RLNG ~₹{RLNG_KG:.0f}/kg as the displaced marginal gas:\n")
L.append("| CBO share | CBG needed (tonnes/yr) | Procurement (₹ cr/yr) | Pump-price delta | Mileage delta |")
L.append("|---|---|---|---|---|")
for r in cbo_rows:
    L.append(f"| {r['cbo_share_pct']:.0f}% | {r['cbg_tonnes']:,} | {r['procurement_cr']:,} | "
             f"+₹{r['pump_delta_rs_kg']}/kg | −{r['mileage_delta_pct']}% |")
L.append("\nEven the 5% obligation carries a pump impact of ~₹0.59/kg (~0.8% of the CNG "
         "price) and a mileage effect of ~0.1% — against E20's silent 4% mileage cut and "
         "₹22,700 cr/yr volume dividend. The CBG subsidy, where needed, sits **on-budget "
         "and ex-plant** (SATAT assurance, GOBARdhan capex support, FOM/LFOM fertiliser "
         "offtake under FCO Schedule VIII) instead of hidden in the fuel gauge.\n")

L.append("## 4. Caveats\n")
L.append("- SIAM/ARAI FE figures are type-approval, not real-world; the analysis leans on "
         "*relative* gaps (petrol vs CNG vs diesel), which the same-nameplate pairs anchor.\n"
         "- SATAT ₹54/kg is the assured floor; market CBG deals near CGD city-gate parity "
         "can price higher. RLNG comparator swings with spot LNG ($12/MMBtu here).\n"
         "- CBG production cost varies by feedstock (press-mud cheapest, agri-residue "
         "dearest); ₹54/kg does not guarantee plant viability without the fertiliser and "
         "carbon-credit legs — see the GOBARdhan/FOM work in the digital-twin repo.\n"
         "- CBO shares apply to CGD gas incl. PNG(D); using the CNG(T) pool alone keeps "
         "the comparison transport-to-transport.\n")

(OUT / "cbg_satat_economics.md").write_text("\n".join(L))

print(f"Rs/MJ: petrol {PET_REF/MJ_PETROL:.2f} | ethanol {ETH_PROC/MJ_ETH:.2f} (+{eth_prem*100:.0f}%) | "
      f"APM {APM_KG/MJ_CNG:.2f} | RLNG {RLNG_KG/MJ_CNG:.2f} | CBG {SATAT_CBG/MJ_CBG:.2f} ({cbg_prem*100:+.0f}% vs RLNG)")
for n, v, note in km_rows: print(f"  {n:26s} ₹{v:.2f}/km  ({note})")
for r in cbo_rows:
    print(f"CBO {r['cbo_share_pct']:.0f}%: {r['cbg_tonnes']:,} t CBG, ₹{r['procurement_cr']:,} cr, "
          f"pump +₹{r['pump_delta_rs_kg']}/kg, mileage −{r['mileage_delta_pct']}%")
