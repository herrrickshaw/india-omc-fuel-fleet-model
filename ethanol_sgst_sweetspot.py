#!/usr/bin/env python3
"""The case for a state SGST on ethanol (1-5%), price-fixed, as blending rises
E20 -> E30 — and whether there is a Brazil-E27-style sweet spot.

Core economics: ethanol (~₹60/L) is cheaper than the petrol-base + central-excise
it displaces (~₹75/L), so at a FIXED pump price there is ~₹15/L of fiscal space
per litre of ethanol. Today that space is not captured by states (they get only
the ~2.5% SGST half of ethanol's 5% GST). A dedicated state SGST on ethanol,
funded from that space, gives states NEW revenue that scales with the blend —
without raising the consumer price.

Key result (derived below): the *fraction* of foregone petrol-VAT that a state
recovers depends only on the SGST rate (≈ rate×ethanol_price / VAT-per-litre),
NOT on the blend; the blend scales the absolute rupees. Full recovery needs ~30%
(still price-neutral, but a heavy tax on green fuel), so within 1-5% states
recover a modest but real slice — largest, in rupees, at the highest feasible
blend. Pure stdlib.
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"; OUT.mkdir(exist_ok=True)

# ── economics (editable) ─────────────────────────────────────────────────────
PETROL_BNL   = 54.05        # national petrol (MS) blended volume, bn L (40 MMT)
PETROL_BASE  = 55.0         # ₹/L trade-parity/refinery cost of petrol displaced
EXCISE       = 20.0         # ₹/L central excise avoided on the displaced petrol
AVG_VAT_PER_L = 18.0        # ₹/L national-avg state VAT on petrol (from statewise model)
CURRENT_SGST_PCT = 2.5      # today: state's half of ethanol's 5% GST
GST_ETH_PCT  = 5.0

# ethanol price rises gently with blend (cheap molasses -> pricier grain/imported)
def eth_price(blend):       # ₹/L
    return 60.0 + (blend - 0.20) * 80.0     # 60 @ E20 -> 68 @ E30

BLENDS = {"E20": 0.20, "E22": 0.22, "E25": 0.25, "E27 (Brazil)": 0.27, "E30": 0.30}
RATES = [1, 2, 3, 4, 5]     # candidate state SGST-on-ethanol rates, %
FLEET_CEILING = 0.27        # non-flex fleet realistically tolerates up to ~E27 (Brazil-proven)
CR = 1e7

# top-5 states by petrol volume (bn L, from statewise_tax model) for a concrete cut
TOP_STATES = [("Uttar Pradesh", 6.53), ("Maharashtra", 5.91), ("Tamil Nadu", 4.78),
              ("Karnataka", 4.13), ("Gujarat", 3.65)]


def sgst_cr(blend, rate_pct):
    eth_bnL = blend * PETROL_BNL
    levy = eth_price(blend) * rate_pct / 100          # ₹/L
    return eth_bnL * 1e9 * levy / CR, levy, eth_bnL

def space(blend):                                     # ₹/L fiscal room at fixed price
    return (PETROL_BASE + EXCISE) - eth_price(blend)

def vat_foregone_cr(blend):
    return blend * PETROL_BNL * 1e9 * AVG_VAT_PER_L / CR


def main():
    # grid: state SGST revenue (₹ cr) for each blend × rate
    grid = {b: {r: sgst_cr(frac, r)[0] for r in RATES} for b, frac in BLENDS.items()}

    with (OUT / "ethanol_sgst_grid.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["blend", "blend_pct", "ethanol_bnL", "ethanol_price", "fiscal_space_per_L"]
                   + [f"sgst_{r}pct_cr" for r in RATES]
                   + [f"recovery_{r}pct" for r in RATES])
        for b, frac in BLENDS.items():
            _, _, ethb = sgst_cr(frac, 1)
            row = [b, round(frac*100), round(ethb, 2), round(eth_price(frac), 1), round(space(frac), 1)]
            row += [round(grid[b][r]) for r in RATES]
            row += [f"{eth_price(frac)*r/100/AVG_VAT_PER_L*100:.1f}%" for r in RATES]
            w.writerow(row)

    # sweet spot: max price-neutral state revenue within the fleet ceiling, at 5%
    feasible = [(b, frac) for b, frac in BLENDS.items() if frac <= FLEET_CEILING + 1e-9]
    sweet_b, sweet_frac = max(feasible, key=lambda kv: kv[1])
    sweet_rev, sweet_levy, sweet_eth = sgst_cr(sweet_frac, 5)
    sweet_recovery = sweet_levy / AVG_VAT_PER_L
    full_rate = AVG_VAT_PER_L / eth_price(sweet_frac) * 100     # rate for 100% recovery

    L = []
    L.append("# The case for a state SGST on ethanol (1-5%), price-fixed, from E20 to E30\n")
    L.append("**Premise.** Ethanol (~₹60/L) is cheaper than the petrol base + central excise it "
             f"displaces (~₹{PETROL_BASE+EXCISE:.0f}/L), so at a **fixed pump price** every litre of "
             f"ethanol opens ~₹{space(0.20):.0f}/L of fiscal space. Today states capture almost none of "
             f"it — only the {CURRENT_SGST_PCT:.1f}% SGST half of ethanol's {GST_ETH_PCT:.0f}% GST. A "
             "dedicated **state SGST on ethanol**, funded from that space, is new state revenue at zero "
             "cost to the consumer.\n")

    L.append("## 1. State SGST revenue — blend × rate grid (₹ crore/yr)\n")
    L.append("| Blend | Ethanol (bn L) | SGST 1% | 2% | 3% | 4% | 5% |")
    L.append("|---|--:|--:|--:|--:|--:|--:|")
    for b, frac in BLENDS.items():
        _, _, ethb = sgst_cr(frac, 1)
        L.append(f"| {b} | {ethb:.1f} | " + " | ".join(f"{round(grid[b][r]):,}" for r in RATES) + " |")
    L.append("")
    L.append(f"Revenue rises on **both** axes — higher rate and higher blend. Going E20→E30 lifts the "
             f"5% take from ₹{round(grid['E20'][5]):,} cr to ₹{round(grid['E30'][5]):,} cr; the ethanol "
             "base grows 50% as blend goes 20→30%.\n")

    L.append("## 2. The recovery insight — rate sets the %, blend sets the ₹\n")
    L.append("Because both the SGST take **and** the foregone petrol-VAT scale with ethanol volume, the "
             "*fraction* of foregone VAT a state recovers depends only on the **rate**:\n")
    L.append("> recovery ≈ (SGST rate × ethanol price) ÷ petrol-VAT-per-litre\n")
    L.append("| SGST rate | Recovery of foregone petrol-VAT |")
    L.append("|---|--:|")
    for r in RATES:
        L.append(f"| {r}% | {eth_price(0.25)*r/100/AVG_VAT_PER_L*100:.0f}% |")
    L.append("")
    L.append(f"So 1-5% recovers ~3-18% of the foregone VAT at any blend. **Full recovery needs ~"
             f"{full_rate:.0f}%** — still price-neutral (it fits inside the ₹{space(sweet_frac):.0f}/L "
             "space) but a heavy levy on green fuel. The realistic play is a modest rate on a big base.\n")

    L.append("## 3. Price stays fixed — the levy fits the fiscal space\n")
    L.append("| Blend | Ethanol price | Fiscal space ₹/L | 5% levy ₹/L | Price-neutral? |")
    L.append("|---|--:|--:|--:|:--:|")
    for b, frac in BLENDS.items():
        levy5 = eth_price(frac)*0.05
        ok = "✅" if levy5 <= space(frac) else "⚠️ needs price rise"
        L.append(f"| {b} | ₹{eth_price(frac):.1f} | ₹{space(frac):.1f} | ₹{levy5:.2f} | {ok} |")
    L.append("")
    L.append("A 5% ethanol SGST costs ₹3-3.4/L — comfortably inside the space at every blend, so the "
             "**consumer price never moves**. The space shrinks as ethanol gets pricier at high blends "
             "(grain/imported feedstock), which is what eventually bounds the design.\n")

    L.append("## 4. Is there a Brazil-E27 sweet spot?\n")
    L.append(f"State SGST revenue is monotone in blend and rate, so the optimum is a **constrained** one, "
             "set by the fleet, not a revenue peak. Brazil settled at **E27** as the practical ceiling for "
             "regular (non-flex) engines (now moving to E30 with a flex fleet). India's fleet is E20-rated "
             "in 2025, stretching toward E27 as E20+ vehicles diffuse.\n")
    L.append(f"**Sweet spot = {sweet_b} @ 5% SGST:** ~**₹{round(sweet_rev):,} cr/yr** of new, price-neutral "
             f"state revenue (levy ₹{sweet_levy:.2f}/L inside ₹{space(sweet_frac):.0f}/L space), recovering "
             f"~{sweet_recovery*100:.0f}% of the foregone VAT — the highest blend India's non-flex fleet "
             "tolerates, mirroring Brazil. E30 @ 5% would add more (₹{:,} cr) but needs a flex/E20+ fleet "
             "and pricier ethanol, so it is the frontier, not the near-term optimum.\n".format(round(grid['E30'][5])))

    L.append(f"### Top-5 states at the {sweet_b} @ 5% sweet spot\n")
    L.append("| State | Petrol (bn L) | Ethanol (bn L) | New SGST (₹ cr) |")
    L.append("|---|--:|--:|--:|")
    for name, pv in TOP_STATES:
        ethb = pv * sweet_frac
        rev = ethb * 1e9 * eth_price(sweet_frac) * 0.05 / CR
        L.append(f"| {name} | {pv} | {ethb:.2f} | {round(rev):,} |")
    L.append("")

    L.append("## 5. The case, in one line\n")
    L.append(f"Blending is mandated and rising anyway; ethanol is cheaper than the taxed petrol it "
             f"replaces; so a **1-5% state SGST on ethanol, funded from the ₹{space(0.20):.0f}/L cost "
             "saving, hands states ₹0.6-4.8k cr/yr of new revenue with the pump price untouched** — and "
             f"the pragmatic design point is **{sweet_b} at ~5%**, India's Brazil-style equilibrium, with "
             "room to push the rate toward ~30% if states ever want full VAT-parity recovery.\n")

    L.append("## 6. Caveats\n")
    L.append("- Recovery is *partial* at 1-5% (~3-18%); this augments, not replaces, the VAT base. "
             "It reallocates the ethanol fiscal space (largely foregone central excise) toward states — a "
             "centre↔state transfer question as much as a tax-design one.")
    L.append("- Ethanol price/blend supply curve, VAT-per-litre and the ₹15/L space are editable "
             "estimates. Fleet ceiling (E27) is an engineering/Brazil-analog assumption, not a mandate.")
    L.append("- Keeps GST-council reality aside: ethanol GST is centrally set; a *dedicated state* ethanol "
             "levy would need a GST-council/legal route. Modeled as an economic proposal.\n")
    L.append("---\n*Policy scenario from PPAC-anchored economics + editable levers; not fiscal advice.*\n")
    (OUT / "ethanol_sgst_sweetspot.md").write_text("\n".join(L))

    print("State SGST-on-ethanol revenue (₹ cr/yr):")
    print(f"  {'blend':14s}" + "".join(f"{str(r)+'%':>9s}" for r in RATES))
    for b in BLENDS:
        print(f"  {b:14s}" + "".join(f"{round(grid[b][r]):>9,}" for r in RATES))
    print(f"\nRecovery of foregone VAT: {eth_price(0.25)*1/100/AVG_VAT_PER_L*100:.0f}% (1%) .. "
          f"{eth_price(0.25)*5/100/AVG_VAT_PER_L*100:.0f}% (5%); full recovery ~{full_rate:.0f}%")
    print(f"SWEET SPOT: {sweet_b} @ 5% -> ₹{round(sweet_rev):,} cr/yr, price-neutral "
          f"(levy ₹{sweet_levy:.2f}/L < space ₹{space(sweet_frac):.0f}/L), recovers ~{sweet_recovery*100:.0f}%")
    print("Wrote outputs/ethanol_sgst_sweetspot.md + ethanol_sgst_grid.csv")


if __name__ == "__main__":
    main()
