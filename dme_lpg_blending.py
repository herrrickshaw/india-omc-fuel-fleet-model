#!/usr/bin/env python3
"""DME blending in LPG — the Volume Dividend framework applied to cooking gas.

DME (dimethyl ether, CH3-O-CH3) blends into LPG up to 20% under BIS
IS 18698:2024. LERC (LPG Equipment Research Centre, Bengaluru) anchors the
engineering: material compatibility cleared at 20% (vapour phase), flex-fuel
burner trials stable, and a measured thermal-efficiency DECREASE of 5.26%
at DME20 (IS 4246 test protocol) — the LPG analogue of SIAM's E20 4% drop.

Key structural difference vs petrol-ethanol: LPG is sold PER KG in a fixed
14.2-kg cylinder, and domestic LPG is SUBSIDISED (PMUY) — so the energy
dilution creates extra cylinder purchases whose cost lands on households AND
the subsidy bill, instead of yielding tax revenue. DME is the fourth quadrant:
  ethanol-in-petrol: dilutes, taxed fuel      -> exchequer GAINS on volume
  biodiesel-in-diesel: mild dilution, taxed   -> small gain
  CBG-in-CNG: parity                          -> no volume effect at all
  DME-in-LPG: dilutes, SUBSIDISED fuel        -> exchequer PAYS on volume

Anchors: LPG LHV ~45.8 MJ/kg (Indian 60:40 butane:propane), DME 28.8 MJ/kg;
LPG consumption FY24-25 ~29.7 MMT (PPAC RR), imports ~60-65%; Delhi domestic
cylinder Rs 803 / 14.2 kg; PMUY subsidy Rs 300/cylinder, ~10.3 cr
beneficiaries; methanol route 1.4 t methanol per t DME, India imports ~90%
of its methanol.

Pure stdlib. Outputs: outputs/dme_lpg_blending.md + .csv
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)
CR = 1e7

MJ_LPG, MJ_DME = 45.8, 28.8          # LHV MJ/kg
CYL_KG, CYL_PRICE = 14.2, 803.0      # domestic cylinder, Delhi Rs
PMUY_SUBSIDY = 300.0                 # Rs/cylinder, ~10.3 cr beneficiaries
HH_CYL_YR = 7.0                      # cylinders/yr typical urban household
LPG_MMT = 29.7                       # national consumption FY24-25 (PPAC)
IMPORT_SHARE = 0.62
LPG_IMPORT_RS_KG = 52.0              # import-parity Rs/kg (lever)
METHANOL_T_PER_T = 1.4               # t methanol per t DME
METHANOL_RS_KG = 24.0                # imported methanol Rs/kg (lever)
LERC_DROP_20 = 0.0526                # measured thermal-efficiency drop at DME20

BLENDS = [("DME5", 0.05), ("DME10", 0.10), ("DME20", 0.20)]

rows = []
for tag, f in BLENDS:
    mj_kg = MJ_LPG * (1 - f) + MJ_DME * f
    e_drop = 1 - mj_kg / MJ_LPG                      # energy basis
    # LERC measured drop scales ~linearly with DME share from the 20% point
    lerc_drop = LERC_DROP_20 * (f / 0.20)
    extra_kg = 1 / (1 - lerc_drop) - 1               # extra kg for same cooking
    cyl_mj = CYL_KG * mj_kg
    hh_extra_cyl = HH_CYL_YR * extra_kg
    hh_extra_rs = hh_extra_cyl * CYL_PRICE
    # national arithmetic (whole pool blended; distance^H cooking demand constant)
    pool_mmt = LPG_MMT * (1 + extra_kg)
    extra_mmt = pool_mmt - LPG_MMT
    dme_mmt = pool_mmt * f
    consumer_cr = extra_mmt * 1e9 * (CYL_PRICE / CYL_KG) / CR
    pmuy_extra_cr = 10.3e7 * HH_CYL_YR * extra_kg * PMUY_SUBSIDY / CR
    # energy-parity price for a blended cylinder
    parity_cyl = CYL_PRICE * (1 - lerc_drop)
    # DME cost test: price/kg at which the blend is energy-neutral for the buyer
    dme_parity_rs_kg = LPG_IMPORT_RS_KG * (MJ_DME / MJ_LPG)
    rows.append({"blend": tag, "dme_frac": f, "mj_per_kg": round(mj_kg, 2),
        "energy_drop_pct": round(e_drop * 100, 2),
        "lerc_drop_pct": round(lerc_drop * 100, 2),
        "cylinder_mj": round(cyl_mj), "extra_kg_pct": round(extra_kg * 100, 2),
        "hh_extra_cyl_yr": round(hh_extra_cyl, 2), "hh_extra_rs_yr": round(hh_extra_rs),
        "dme_needed_mmt": round(dme_mmt, 2), "extra_pool_mmt": round(extra_mmt, 2),
        "consumer_extra_cr": round(consumer_cr),
        "pmuy_extra_subsidy_cr": round(pmuy_extra_cr),
        "parity_cylinder_rs": round(parity_cyl),
        "dme_energy_parity_rs_kg": round(dme_parity_rs_kg, 1)})

methanol_route_feed = METHANOL_T_PER_T * METHANOL_RS_KG   # Rs/kg DME, feed alone
d20 = rows[2]

with (OUT / "dme_lpg_blending.csv").open("w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

L = ["# DME blending in LPG — the fourth quadrant of the Volume Dividend\n",
     "DME (dimethyl ether) is now blendable into LPG up to 20% under **BIS IS 18698:2024**, "
     "with the engineering anchored by **LERC (LPG Equipment Research Centre, Bengaluru)**: "
     "material compatibility cleared at 20% DME (vapour phase), flex-fuel burner trials "
     "stable, and a measured **thermal-efficiency decrease of 5.26% at DME20** on the "
     "IS 4246 protocol — the cooking-gas analogue of SIAM's E20 mileage figure. DME carries "
     f"**{(1-MJ_DME/MJ_LPG)*100:.0f}% less energy per kg** than LPG (28.8 vs 45.8 MJ/kg).\n"]

L.append("## 1. Blend energetics and the cylinder\n")
L.append("| Blend | MJ/kg | Energy vs LPG | LERC-basis usable drop | 14.2-kg cylinder energy | Extra kg for same cooking |")
L.append("|---|---|---|---|---|---|")
for r in rows:
    L.append(f"| {r['blend']} | {r['mj_per_kg']} | −{r['energy_drop_pct']}% | −{r['lerc_drop_pct']}% | "
             f"{r['cylinder_mj']} MJ | +{r['extra_kg_pct']}% |")
L.append("\nLERC's measured drop (−5.26% at DME20) runs *below* the pure energy math (−7.4%) — "
         "oxygenated DME burns cleaner and partly compensates, exactly as E20's octane recovery "
         "softens its energy penalty. We use the LERC basis as the central case.\n")

L.append("## 2. Who pays: household and subsidy arithmetic (DME20)\n")
L.append(f"- A {HH_CYL_YR:.0f}-cylinder/yr household needs **+{d20['hh_extra_cyl_yr']} cylinders "
         f"≈ ₹{d20['hh_extra_rs_yr']:,}/yr** at an unchanged ₹{CYL_PRICE:.0f} cylinder price — "
         "the same invisible-levy mechanism as E20, but on a merit good.\n"
         f"- Nationally (whole {LPG_MMT} MMT pool blended): **+{d20['extra_pool_mmt']} MMT extra "
         f"LPG-equivalent bought = ₹{d20['consumer_extra_cr']:,} cr/yr** of extra consumer spend.\n"
         f"- **The exchequer PAYS, not collects**: PMUY's ₹{PMUY_SUBSIDY:.0f}/cylinder on 10.3 cr "
         f"beneficiary households adds **≈₹{d20['pmuy_extra_subsidy_cr']:,} cr/yr** of extra "
         "subsidy — the volume dividend inverts. Ethanol's dilution earns the exchequer excise; "
         "DME's dilution bills it.\n"
         f"- Honest pricing: a DME20 cylinder should sell at **₹{d20['parity_cylinder_rs']:,}** "
         f"(vs ₹{CYL_PRICE:.0f}) for cooking-energy parity.\n")

L.append("## 3. Does DME clear energy-parity economics?\n")
L.append(f"- Energy-neutral DME price = LPG price × (28.8/45.8) = **₹{d20['dme_energy_parity_rs_kg']}/kg** "
         f"against LPG import parity ₹{LPG_IMPORT_RS_KG:.0f}/kg.\n"
         f"- Methanol-route DME (1.4 t methanol/t) costs **₹{methanol_route_feed:.1f}/kg in feedstock "
         f"alone** at imported methanol ₹{METHANOL_RS_KG:.0f}/kg — above the ₹{d20['dme_energy_parity_rs_kg']} "
         "parity ceiling before conversion, logistics or margin. **Imported-methanol DME cannot "
         "clear energy parity**; it merely swaps a propane import for a methanol import at a "
         "worse ₹/MJ.\n"
         "- The route that works on paper: coal-gasification methanol (Coal India/BHEL projects, "
         "₹15–18/kg) or bio-DME from syngas — domestic molecules, but carbon-heavy (coal) or "
         "immature (bio). Import substitution is the honest rationale ONLY on those routes.\n"
         f"- At DME20 nationally, DME demand is **{d20['dme_needed_mmt']} MMT/yr** — ~6× India's "
         "current methanol production; the supply side does not exist yet.\n")

L.append("## 4. Verdict in the Volume Dividend framework\n")
L.append("| Blend | Dilution | Fuel's fiscal status | Volume effect lands on |")
L.append("|---|---|---|---|")
L.append("| Ethanol in petrol | −34%/L | heavily taxed | consumer pays, exchequer+trade collect |")
L.append("| Biodiesel in diesel | −8%/L | taxed | mild, lands on freight |")
L.append("| CBG in CNG | ~0%/kg | lightly taxed | nobody — the honest blend |")
L.append("| **DME in LPG** | **−37%/kg** | **subsidised** | **consumer AND exchequer pay** |")
L.append("\nDME-LPG is the worst quadrant: it combines ethanol's dilution problem with a "
         "subsidised fuel, so the hidden levy hits households (regressive — LPG is the Ujjwala "
         "merit good) *and* the subsidy bill simultaneously. If pursued for import substitution, "
         "two guardrails are non-negotiable: **(1) energy-parity cylinder pricing** (₹758 for a "
         "DME20 14.2-kg cylinder at today's ₹803) — or equivalently more kg per cylinder; "
         "**(2) domestic-carbon DME only** (coal/bio routes), since methanol-route DME just "
         "re-denominates the import bill.\n")

L.append("## 5. Caveats\n")
L.append("- LERC's 5.26% is a burner thermal-efficiency figure at DME20 (IS 4246); field "
         "cooking behaviour and older stoves may differ; we scale it linearly to DME5/10.\n"
         "- IS 18698:2024 caps blends at 20%; higher shares need elastomer/valve changes "
         "(DME attacks conventional seals) — LERC compatibility work is the binding reference.\n"
         "- Cylinder price and PMUY parameters are levers (Delhi ₹803, ₹300 subsidy); the "
         "whole-pool blend is a ceiling scenario — a phased urban rollout scales linearly.\n"
         "- LPG LHV varies with butane:propane season mix (45.5–46.3 MJ/kg); DME 28.4–28.9.\n")

(OUT / "dme_lpg_blending.md").write_text("\n".join(L))

for r in rows:
    print(f"{r['blend']}: {r['mj_per_kg']} MJ/kg (−{r['energy_drop_pct']}% | LERC −{r['lerc_drop_pct']}%) "
          f"extra kg +{r['extra_kg_pct']}% | HH +₹{r['hh_extra_rs_yr']}/yr | "
          f"consumer ₹{r['consumer_extra_cr']:,} cr | PMUY +₹{r['pmuy_extra_subsidy_cr']:,} cr | "
          f"parity cyl ₹{r['parity_cylinder_rs']}")
print(f"DME energy-parity ceiling ₹{rows[2]['dme_energy_parity_rs_kg']}/kg vs methanol-route feed ₹{methanol_route_feed:.1f}/kg")
