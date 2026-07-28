#!/usr/bin/env python3
"""Price-adjustment scenarios: what pump discount would neutralise the blend
mileage loss (cost-per-km parity with E0), and WHO can fund it.

Cross-repo inputs:
  vehicle_fuel_mileage (bang-for-your-buck): ethanol fraction bears only 5%
    GST — escapes both central excise and state VAT — but the saving is
    retained in the E20 price build-up, not rebated to the buyer.
  omc_model.py: ethanol procurement Rs62/L avg, petrol refinery Rs58/L,
    OMC margin Rs3.5/L; E20/E25/E30 mileage drops 4/5.5/7%.
  statewise_tax_impact.py: excise Rs19.90/L, VAT 25% on Rs78/L base.
  ESY 2024-25 OMC ethanol procurement slabs (feedstock -> Rs/L): C-heavy
    molasses 57.97, FCI rice 58.50, B-heavy 60.73, damaged grain 64.00,
    juice/syrup 65.61, maize 71.86 — grain mandi prices set these floors.

Parity rule: cost/km equal to E0 requires P_blend = P_E0 * (1 - drop),
i.e. a discount of P_E0 * drop per litre.

Pure stdlib. Outputs: outputs/price_parity_scenarios.md + .csv
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)
CR = 1e7

PUMP      = 105.0          # Rs/L petrol (E20 today)
EXCISE    = 19.90          # Rs/L central excise (petrol fraction)
VAT_L     = 0.25 * 78.0    # ~Rs19.5/L effective state VAT (petrol fraction)
GST_ETH   = 0.05           # GST on ethanol supplied for blending
ETH_PRICE = 62.0           # Rs/L avg OMC ethanol procurement (ESY24-25)
PET_REF   = 58.0           # Rs/L petrol refinery/trade-parity cost displaced
MS_BNL    = 40.0 * 1e3 / 0.74 / 1e3      # 54.05 bn L blended pool FY24-25
L0        = MS_BNL * (1 - 0.04)          # E0-equivalent distance demand

SLABS = [("C-heavy molasses", 57.97), ("FCI surplus rice", 58.50),
         ("B-heavy molasses", 60.73), ("Damaged food grains", 64.00),
         ("Sugarcane juice/syrup", 65.61), ("Maize", 71.86)]

BLENDS = [("E20", 0.20, 0.040), ("E25", 0.25, 0.055), ("E30", 0.30, 0.070)]

rows = []
for tag, frac, drop in BLENDS:
    pool = L0 / (1 - drop)                       # blended litres dispensed
    disc = PUMP * drop                           # Rs/L discount for cost/km parity
    parity_price = PUMP - disc
    total_cr = disc * pool * 1e9 / CR            # national cost of the discount

    # S1: pass through the tax break already embedded in the blend.
    # The ethanol fraction escapes excise+VAT and bears only 5% GST; today that
    # saving stays in the price build-up. Net headroom per blended litre:
    tax_break = frac * (EXCISE + VAT_L)          # dual tax NOT collected on ethanol
    gst_paid  = frac * ETH_PRICE * GST_ETH       # what the ethanol fraction DOES pay
    eth_cost_penalty = frac * (ETH_PRICE - PET_REF)   # ethanol dearer than petrol displaced
    headroom  = tax_break - gst_paid - eth_cost_penalty
    s1_cover  = headroom / disc                  # >1 => embedded break fully funds parity

    # S2: centre funds via excise cut on the blended litre
    s2_excise_new = EXCISE - disc
    s2_cost_cr    = disc * pool * 1e9 / CR

    # S3: states fund via VAT cut
    s3_vat_new = VAT_L - disc

    # S4: fund from ethanol procurement (grain economics test)
    s4_eth_price = ETH_PRICE - disc / frac       # required Rs/L ethanol price
    s4_floor     = SLABS[0][1]                   # cheapest feedstock slab
    s4_feasible  = s4_eth_price >= s4_floor
    s4_max_disc  = (ETH_PRICE - s4_floor) * frac # discount fundable before hitting floor

    rows.append({"blend": tag, "mileage_drop_pct": drop*100,
        "parity_discount_rs_l": round(disc, 2), "parity_price_rs_l": round(parity_price, 2),
        "national_cost_cr": round(total_cr),
        "s1_embedded_headroom_rs_l": round(headroom, 2), "s1_coverage_x": round(s1_cover, 2),
        "s2_excise_after_rs_l": round(s2_excise_new, 2), "s2_centre_cost_cr": round(s2_cost_cr),
        "s3_vat_after_rs_l": round(s3_vat_new, 2),
        "s4_ethanol_price_needed_rs_l": round(s4_eth_price, 2),
        "s4_feasible_vs_grain_floor": s4_feasible,
        "s4_max_discount_rs_l": round(s4_max_disc, 2)})

with (OUT / "price_parity_scenarios.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

# ── report ──────────────────────────────────────────────────────────────────
L = ["# Price-adjustment scenarios: neutralising the blend mileage loss\n",
     "If blended petrol delivered honest **cost-per-km**, its pump price would be "
     "discounted by exactly the mileage it takes away: `P_blend = P_E0 x (1-drop)`. "
     "This note quantifies that discount for E20-E30 and tests four ways to fund "
     "it, using the ethanol procurement, grain-price and taxation numbers from "
     "the companion repos (vehicle_fuel_mileage, omc_model, statewise_tax_impact).\n"]

L.append("## 1. The parity discount\n")
L.append("| Blend | Mileage drop | Parity discount (₹/L) | Parity pump price | National cost (₹ cr/yr) |")
L.append("|---|---|---|---|---|")
for r in rows:
    L.append(f"| {r['blend']} | {r['mileage_drop_pct']:.1f}% | {r['parity_discount_rs_l']} | "
             f"{r['parity_price_rs_l']} | {r['national_cost_cr']:,} |")
L.append(f"\nAt ₹{PUMP:.0f}/L, E20 should sell at ₹{rows[0]['parity_price_rs_l']}/L for the "
         "consumer to be indifferent per km. The FY23 budget's ₹2/L penalty on "
         "UNblended petrol is a stick pointing the other way — it widens the gap "
         "instead of closing it.\n")

L.append("## 2. Scenario S1 — pass through the tax break already embedded (preferred)\n")
L.append("From the bang-for-your-buck tax analysis: the ethanol molecule escapes both "
         f"central excise (₹{EXCISE}/L) and state VAT (~₹{VAT_L:.1f}/L), paying only 5% GST "
         f"(~₹{62*0.05:.1f}/L on ₹{ETH_PRICE:.0f} ethanol). Today that saving is retained in "
         "the price build-up. Netting off ethanol's cost premium over refinery petrol "
         f"(₹{ETH_PRICE:.0f} vs ₹{PET_REF:.0f}):\n")
L.append("| Blend | Embedded headroom (₹/L) | Parity needs (₹/L) | Coverage |")
L.append("|---|---|---|---|")
for r in rows:
    L.append(f"| {r['blend']} | {r['s1_embedded_headroom_rs_l']} | {r['parity_discount_rs_l']} | "
             f"{r['s1_coverage_x']:.2f}× |")
L.append("\n**The embedded tax break more than funds parity at every blend level.** "
         "Passing it through prices E20 honestly with ~₹2/L still left in the chain — "
         "no NEW subsidy, no NEW revenue loss vs an unblended counterfactual; it stops "
         "collecting a windfall the blend walk silently creates. (What it does end is "
         "the exchequer/OMC gain from the volume effect — that gain IS the consumer's "
         "loss.)\n")

L.append("## 3. Scenarios S2-S4 — who else could fund it\n")
L.append("| Blend | S2 excise cut → ₹/L left | S2 centre cost (₹ cr) | S3 VAT left (₹/L) | S4 ethanol price needed | S4 feasible vs grain floor? |")
L.append("|---|---|---|---|---|---|")
for r in rows:
    L.append(f"| {r['blend']} | {r['s2_excise_after_rs_l']} | {r['s2_centre_cost_cr']:,} | "
             f"{r['s3_vat_after_rs_l']} | ₹{r['s4_ethanol_price_needed_rs_l']}/L | "
             f"{'yes' if r['s4_feasible_vs_grain_floor'] else 'NO'} |")
L.append("\n**S4 (cheaper ethanol) fails on grain economics.** Parity funded from "
         "procurement alone needs ethanol at ₹41/L (E20) falling to ₹37/L (E30) — far "
         "below every ESY 2024-25 feedstock slab:\n")
L.append("| Feedstock | OMC procurement (₹/L) |")
L.append("|---|---|")
for s, pr in SLABS:
    L.append(f"| {s} | {pr:.2f} |")
L.append(f"\nGrain/cane mandi prices set these floors (maize at ₹71.86/L is the marginal "
         "slab the E30 walk leans on — the *most* expensive, moving procurement cost UP "
         "not down). Squeezing procurement to the cheapest slab funds only "
         f"₹{rows[0]['s4_max_discount_rs_l']}/L of E20's ₹{rows[0]['parity_discount_rs_l']}/L "
         "need (~19%). Ethanol economics cannot pay for parity; the tax side can.\n")

L.append("## 4. Bottom line\n")
L.append("- Honest pricing = ₹4.20/₹5.78/₹7.35 per litre off E20/E25/E30 at a ₹105 pump.\n"
         "- The money already exists inside the price build-up: the dual-tax exemption "
         "on the ethanol fraction (S1) covers parity ~1.5× at every blend.\n"
         "- Making the centre (S2) or states (S3) fund it via duty cuts costs "
         "₹22,700-41,000 cr/yr — politically identical to today's arrangement in "
         "reverse, which is precisely why the discount hasn't happened.\n"
         "- Grain prices make S4 impossible: parity-priced ethanol would have to be "
         "bought below its cheapest feedstock cost.\n"
         "- CBG needs NO such scenario — energy parity per kg is physical, not fiscal.\n")

(OUT / "price_parity_scenarios.md").write_text("\n".join(L))

for r in rows:
    print(f"{r['blend']}: discount ₹{r['parity_discount_rs_l']}/L -> ₹{r['parity_price_rs_l']}/L "
          f"(₹{r['national_cost_cr']:,} cr/yr) | S1 headroom ₹{r['s1_embedded_headroom_rs_l']}/L "
          f"= {r['s1_coverage_x']}x | S4 needs ethanol @₹{r['s4_ethanol_price_needed_rs_l']}/L "
          f"({'ok' if r['s4_feasible_vs_grain_floor'] else 'below grain floor'})")
