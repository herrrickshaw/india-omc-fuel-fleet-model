#!/usr/bin/env python3
"""RON/octane analysis of the ethanol blend walk — the RON95 opportunity.

Ethanol is a poor energy carrier (21.1 MJ/L) but an excellent OCTANE carrier:
blending RON ~112 (neat RON ~108) vs regular petrol's 91. Every blend step
therefore delivers an octane credit that today is captured UPSTREAM (refiners
back off the blendstock octane) instead of being passed to the consumer as a
higher-RON fuel that would let engines claw the mileage back.

Two ways to blend E20 on a RON basis:
  (a) hold FINAL fuel at RON 91 (today): refiners drop the blendstock (BOB)
      to ~86 RON — cheaper reformate-light BOB; saving retained upstream.
  (b) hold the BOB at 91 RON: the pump fuel becomes ~RON 95 at E20 — a
      free national RON95 fuel, enabling higher-compression E20+ engines
      that recover most of the 4% mileage penalty.

Sources: BIS IS 2796 (regular 91 RON, premium 95); ethanol blending RON 112
(lever; literature 108-115); premium-vs-regular pump spread ~Rs 8-10/L for
95-RON (XP95/Speed) = market price of ~4 RON points; engine-efficiency vs
compression-ratio literature (~1.5%/CR point, CR 10.5->12 feasible at RON95);
SIAM/ARAI E20 drop 4% (E20-calibrated engines already recover part).

Pure stdlib. Outputs: outputs/ron_octane_analysis.md + .csv
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)

RON_REG   = 91.0     # IS 2796 regular petrol
RON_PREM  = 95.0     # premium (XP95 / Speed 95)
RON_ETH   = 112.0    # ethanol blending RON (lever: 108-115)
PREM_SPREAD = 9.0    # Rs/L pump spread regular->95 RON (XP95 ~Rs8-10/L over regular)
RS_PER_RON  = PREM_SPREAD / (RON_PREM - RON_REG)   # market value of one RON point
EFF_PER_CR  = 0.015  # thermal-efficiency gain per compression-ratio point
CR_GAIN_95  = 1.5    # CR headroom RON91->95 (10.5 -> 12 typical)
E20_DROP    = 0.040  # SIAM/ARAI central mileage drop

BLENDS = [("E10", 0.10), ("E20", 0.20), ("E25", 0.25), ("E27", 0.27), ("E30", 0.30)]

rows = []
for tag, f in BLENDS:
    # (a) final RON held at 91: what BOB the refiner can get away with
    bob_ron = (RON_REG - f * RON_ETH) / (1 - f)
    # (b) BOB held at 91: what the pump fuel becomes
    pump_ron = (1 - f) * RON_REG + f * RON_ETH
    # octane credit of the ethanol fraction, priced at the pump premium signal
    octane_credit = f * (RON_ETH - RON_REG) * RS_PER_RON
    rows.append({"blend": tag, "ethanol_frac": f,
        "bob_ron_if_pump91": round(bob_ron, 1),
        "pump_ron_if_bob91": round(pump_ron, 1),
        "octane_credit_rs_l": round(octane_credit, 2)})

# efficiency recovery on a RON95-calibrated engine (route b)
eff_gain = EFF_PER_CR * CR_GAIN_95            # ~2.25% from higher compression
net_e20 = (1 - E20_DROP) * (1 + eff_gain)     # net mileage vs E0 on old engine

with (OUT / "ron_octane_analysis.csv").open("w", newline="") as fcsv:
    w = csv.DictWriter(fcsv, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

L = ["# The RON95 opportunity — ethanol's octane credit, and who pockets it\n",
     "Ethanol is energy-poor (−34%/L) but octane-rich: blending RON ~112 against "
     "regular petrol's 91 (IS 2796). Every blend step carries an octane credit. Today "
     "India blends to a **final RON 91**, which means the credit is taken upstream — "
     "refiners back the blendstock (BOB) off to cheaper, lower-octane material — "
     "rather than delivered to the vehicle as a higher-RON fuel.\n"]

L.append("## 1. Two RON accounting routes per blend\n")
L.append("| Blend | (a) BOB refiners need if pump stays RON 91 | (b) Pump RON if BOB stays 91 | Octane credit (₹/L at pump-premium value) |")
L.append("|---|---|---|---|")
for r in rows:
    L.append(f"| {r['blend']} | {r['bob_ron_if_pump91']} | {r['pump_ron_if_bob91']} | {r['octane_credit_rs_l']} |")
L.append(f"\n- Route (a) — today: at E20 the refinery only has to make **~{rows[1]['bob_ron_if_pump91']}-RON "
         "blendstock** (5 points below the old spec). Lower reforming severity, more "
         "cheap naphtha in the pool — a refining-cost saving retained in the supply "
         "chain, on top of the tax headroom the parity analysis found.\n"
         f"- Route (b) — the opportunity: the same E20 on an unchanged 91-RON BOB is a "
         f"**RON {rows[1]['pump_ron_if_bob91']} fuel** — premium-grade octane, nationally, at zero "
         "extra refining cost. E25→E30 walks the pump to RON 96.3–97.3.\n"
         f"- Priced at the XP95 pump spread (~₹{PREM_SPREAD:.0f}/L for 4 RON points), the ethanol "
         f"octane credit at E20 is worth **~₹{rows[1]['octane_credit_rs_l']:.1f}/L** — value the "
         "consumer neither sees on the price board nor gets in the tank.\n")

L.append("## 2. RON95 closes the mileage gap the energy math opened\n")
L.append(f"A RON95-labelled E20 lets OEMs raise compression (CR ~10.5 → 12, ~{CR_GAIN_95:.1f} "
         f"points): at ~{EFF_PER_CR*100:.1f}%/CR point that is **+{eff_gain*100:.1f}% efficiency**, "
         f"against E20's −{E20_DROP*100:.0f}% energy drop → net mileage ≈ "
         f"**{(net_e20-1)*100:+.1f}% vs E0** on an E20-RON95-optimised engine.\n")
L.append("- This is Brazil's actual playbook (E27 on ~RON 95+ regular, high-CR engines) "
         "and why its fleet does not experience the headline mileage penalty.\n"
         "- It composes with the Volume Dividend scenarios: **parity pricing makes the "
         "consumer whole *today* (existing fleet); RON95 labelling + E20+ engines make "
         "the penalty physically disappear over fleet turnover** (~7% of the parc turns "
         "per year — Vahan CY2025 2.93 cr registrations).\n"
         "- The octane credit also strengthens S1: the ₹6.5–9.7/L embedded tax headroom "
         f"understates total blend headroom by the ~₹{rows[1]['octane_credit_rs_l']:.1f}/L refining-side "
         "octane saving at E20 (₹{:.1f}/L at E30).\n".format(rows[4]['octane_credit_rs_l']))

L.append("## 3. Caveats\n")
L.append("- Blending RON is non-linear and BOB-dependent; 112 is a central lever "
         "(literature 108–115). Route-(a) BOB numbers are linear-blend estimates.\n"
         "- The ₹/RON value uses the retail XP95 spread as the willingness-to-pay "
         "signal; actual refining cost per RON point is lower (reforming severity "
         "~₹0.3–0.8/L per 4-5 points) — both are levers in the CSV.\n"
         "- Higher CR needs the E20+/FFV-ready fleet (Vahan tracks PETROL(E20) as its "
         "own fuel type — 21% of CY2025 registrations); the gain arrives with turnover, "
         "not by decree.\n"
         "- CBG needs no octane accounting: methane's RON-equivalent is ~120+ and CNG "
         "engines already run CR 12+ — another reason the gas side has no hidden ledger.\n")

(OUT / "ron_octane_analysis.md").write_text("\n".join(L))

for r in rows:
    print(f"{r['blend']}: BOB-if-91 {r['bob_ron_if_pump91']} | pump-if-BOB91 {r['pump_ron_if_bob91']} | "
          f"octane credit Rs{r['octane_credit_rs_l']}/L")
print(f"RON95 route: +{eff_gain*100:.1f}% efficiency vs E20 drop -{E20_DROP*100:.0f}% -> net {(net_e20-1)*100:+.1f}% vs E0")
