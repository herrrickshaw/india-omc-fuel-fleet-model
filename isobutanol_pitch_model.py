#!/usr/bin/env python3
"""Financial model behind the isobutanol blending pitch.

Play: retrofit an idle/underutilised 100-KLPD grain distillery to produce
BIO-ISOBUTANOL (C4, engineered-yeast fermentation) instead of a share of its
ethanol — selling into two markets the ethanol molecule serves badly:
  (a) petrol blending at HALF the energy dilution per unit renewable content
      (isobutanol 26.5 MJ/L vs ethanol 21.1; petrol 32.1), and
  (b) ATJ / Sustainable Aviation Fuel, where isobutanol yields 0.75 t
      distillate per t vs ethanol's 0.60 (ICAO conversion factors, per the
      E20->E30 stakeholder workbook's excess-ethanol waterfall) = +25% more
      jet per tonne of feedstock carbon.

The honest problem this model surfaces: there is NO administered price slab
for isobutanol (unlike ethanol's six). Everything therefore hinges on a
policy ask — parity-with-ethanol-on-energy pricing — which we compute and
present as the gate, not as an assumption.

Yield reality: fermentation to isobutanol gives ~0.30-0.33 kg/kg sugar vs
ethanol's ~0.45-0.48 — roughly 30% fewer litres per tonne of grain, partly
offset by +26% energy per litre and a higher-value co-product slate.

Pure stdlib. Outputs: outputs/isobutanol_pitch_model.md + _sensitivity.csv
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)
CR = 1e7

# ── energy anchors (MJ/L) ───────────────────────────────────────────────────
MJ_PETROL, MJ_ETH, MJ_IBU = 32.1, 21.1, 26.5

# ── plant & retrofit capital ────────────────────────────────────────────────
KLPD_ETH_EQ = 100.0     # existing ethanol nameplate being repurposed
IBU_KLPD    = 70.0      # isobutanol output after the ~30% volumetric yield penalty
DAYS        = 330
RETROFIT    = 80.0      # Rs cr: organism/fermentation, separation (isobutanol is
                        # NOT water-miscible -> decanter train), tankage, safety
DEBT_SHARE  = 0.70
RATE        = 0.095
ISS_SUBV    = 0.0       # NOT assumed: no isobutanol-specific subvention exists yet
TENOR       = 8
LIFE        = 15
DISC        = 0.12
RAMP_Y1     = 0.55      # slower than a plain grain retrofit — new organism
UTIL        = 0.90

# ── prices ──────────────────────────────────────────────────────────────────
ETH_MAIZE_SLAB = 71.86              # Rs/L administered maize-route ethanol
IBU_PARITY_ETH = ETH_MAIZE_SLAB * MJ_IBU / MJ_ETH    # energy parity vs ethanol slab
IBU_ASK        = 88.0               # Rs/L the pitch asks for (just below parity)
MAIZE_RS_T     = 23000.0
YIELD_L_T      = 280.0              # L isobutanol per tonne maize (vs ~400 ethanol)
DDGS_KG_L      = 1.10               # kg DDGS per litre (more, since fewer litres)
DDGS_RS_KG     = 17.0
CONV_COST      = 18.0               # Rs/L: energy-intensive separation vs ethanol's 13

def margin_per_l(price=IBU_ASK, maize=MAIZE_RS_T, conv=CONV_COST):
    return price - maize / YIELD_L_T + DDGS_KG_L * DDGS_RS_KG - conv

def ebitda_yr(util=UTIL, price=IBU_ASK, maize=MAIZE_RS_T):
    litres = IBU_KLPD * 1000 * DAYS * util
    return litres * margin_per_l(price, maize) / CR

def cashflows(price=IBU_ASK, maize=MAIZE_RS_T):
    cfs = [-RETROFIT]
    for y in range(1, LIFE + 1):
        cfs.append(ebitda_yr(RAMP_Y1 if y == 1 else UTIL, price, maize))
    return cfs

def npv(cfs, r): return sum(c / (1 + r) ** i for i, c in enumerate(cfs))
def irr(cfs):
    lo, hi = -0.9, 2.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if npv(cfs, mid) > 0: lo = mid
        else: hi = mid
    return (lo + hi) / 2

mpl = margin_per_l()
ebitda = ebitda_yr()
cfs = cashflows()
proj_irr, proj_npv = irr(cfs), npv(cfs, DISC)
payback = next((y for y in range(1, LIFE + 1) if sum(cfs[:y + 1]) > 0), None)

debt = RETROFIT * DEBT_SHARE
eq = [-(RETROFIT - debt)]; bal = debt
for y in range(1, LIFE + 1):
    e = ebitda_yr(RAMP_Y1 if y == 1 else UTIL)
    if y <= TENOR:
        ds = debt / TENOR + bal * RATE; bal -= debt / TENOR
        eq.append(e - ds)
    else:
        eq.append(e)
eq_irr = irr(eq)
dscr = ebitda / (debt / TENOR + debt * (1 - 1 / TENOR) * RATE)

# the no-policy case: isobutanol forced to sell at the ETHANOL slab price
nopolicy_irr = irr(cashflows(price=ETH_MAIZE_SLAB))
nopolicy_margin = margin_per_l(ETH_MAIZE_SLAB)

# blend-side consumer arithmetic: IB24 vs E20 at equal renewable VOLUME share
def blend_drop(frac, mj_blend):
    mix = MJ_PETROL * (1 - frac) + mj_blend * frac
    return 1 - mix / MJ_PETROL
e20_drop, ib20_drop = blend_drop(0.20, MJ_ETH), blend_drop(0.20, MJ_IBU)

# SAF leg: ICAO ATJ conversion factors
ATJ_ETH, ATJ_IBU = 0.60, 0.75      # t distillate per t alcohol
saf_uplift = ATJ_IBU / ATJ_ETH - 1

# ── the SAF leg: isobutanol's real premium market ──────────────────────────
# ATJ-SPK sells at a large premium to fossil jet (global SAF 2-4x jet; India's
# 1-2% SAF mandate from 2027 creates captive demand). Modelled as a blended
# realisation when a share of output is routed to an ATJ offtaker.
SAF_REALISATION = 115.0     # Rs/L isobutanol equivalent under an ATJ offtake (lever)
def blended_price(saf_share, saf=SAF_REALISATION, blend=IBU_ASK):
    return saf_share * saf + (1 - saf_share) * blend
saf_cases = []
for share in (0.0, 0.30, 0.50):
    pr = blended_price(share)
    saf_cases.append({"saf_share_pct": share * 100, "blended_price": round(pr, 1),
                      "margin_rs_l": round(margin_per_l(pr), 2),
                      "ebitda_cr": round(ebitda_yr(price=pr), 1),
                      "project_irr_pct": round(irr(cashflows(pr)) * 100, 1)})

# sensitivity: price x maize
prices = [80.0, IBU_ASK, 96.0]
maizes = [20000.0, 23000.0, 26000.0]
grid = []
for m in maizes:
    row = {"maize_rs_t": int(m)}
    for p in prices:
        row[f"price_{int(p)}"] = round(irr(cashflows(p, m)) * 100, 1)
    grid.append(row)

with (OUT / "isobutanol_pitch_sensitivity.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(grid[0])); w.writeheader(); w.writerows(grid)

L = [f"""# Bio-isobutanol retrofit model — 100 KLPD grain distillery → {IBU_KLPD:.0f} KLPD isobutanol

Retrofit capex ₹{RETROFIT:.0f} cr (engineered organism, decanter separation train — isobutanol is
NOT water-miscible, tankage, safety). 70:30 debt at {RATE*100:.1f}%, **no subvention assumed**
(none exists for isobutanol). {LIFE}-yr life, {UTIL*100:.0f}% utilisation, year-1 ramp {RAMP_Y1*100:.0f}%.

## Why isobutanol at all — the two structural advantages
| Metric | Ethanol | Isobutanol | Advantage |
|---|---|---|---|
| Energy, MJ/L | {MJ_ETH} | {MJ_IBU} | **+{MJ_IBU/MJ_ETH-1:.0%} per litre** |
| Blend dilution at 20% | −{e20_drop*100:.1f}% | −{ib20_drop*100:.1f}% | **half the mileage penalty** |
| ATJ/SAF yield, t distillate per t | {ATJ_ETH} | {ATJ_IBU} | **+{saf_uplift:.0%} more jet fuel** |
| Water miscibility / phase separation | yes (blending-terminal only) | no | **pipeline-transportable** |
| Vapour pressure blending effect | raises RVP | neutral/lowers | easier summer-grade compliance |

## Per-litre economics (maize route)
| Item | ₹/L |
|---|---|
| Realisation asked (policy gate) | {IBU_ASK:.2f} |
| Maize @ ₹{MAIZE_RS_T:,.0f}/t ÷ {YIELD_L_T:.0f} L/t | ({MAIZE_RS_T/YIELD_L_T:.2f}) |
| DDGS credit {DDGS_KG_L:.2f} kg × ₹{DDGS_RS_KG:.0f} | {DDGS_KG_L*DDGS_RS_KG:.2f} |
| Conversion (separation-heavy) | ({CONV_COST:.2f}) |
| **Margin** | **{mpl:.2f}** |

Energy parity with the maize ethanol slab (₹{ETH_MAIZE_SLAB}) would be **₹{IBU_PARITY_ETH:.1f}/L**;
the pitch asks ₹{IBU_ASK:.0f} — *below* parity, so the OMC buys isobutanol energy cheaper than
ethanol energy.

## Returns
| Metric | Value |
|---|---|
| EBITDA | ₹{ebitda:.1f} cr/yr |
| Project IRR | **{proj_irr*100:.1f}%** |
| Equity IRR | **{eq_irr*100:.1f}%** |
| NPV @ {DISC*100:.0f}% | ₹{proj_npv:.1f} cr |
| Payback | year {payback} |
| DSCR (steady) | {dscr:.2f}× |
| **No-policy case** (sold at the ethanol slab ₹{ETH_MAIZE_SLAB}) | margin ₹{nopolicy_margin:.2f}/L → IRR {nopolicy_irr*100:.1f}% |

**The no-policy row is the whole pitch.** Isobutanol makes ~30% fewer litres per tonne of grain,
so selling it at ethanol's per-LITRE slab is a guaranteed loss. A per-ENERGY (or dedicated)
price slab is the gate: with it, the project clears comfortably; without it, nothing gets built.

## Sensitivity — project IRR (%): maize price × isobutanol realisation
| Maize ₹/t | ₹80/L | ₹{IBU_ASK:.0f}/L (ask) | ₹96/L |
|---|---|---|---|"""]
for r in grid:
    L.append(f"| {r['maize_rs_t']:,} | {r['price_80']} | {r[f'price_{int(IBU_ASK)}']} | {r['price_96']} |")
L.append("\n## The SAF leg — where isobutanol's premium actually lives\n")
L.append("| Output routed to ATJ/SAF | Blended realisation ₹/L | Margin ₹/L | EBITDA ₹ cr | Project IRR |")
L.append("|---|---|---|---|---|")
for c in saf_cases:
    L.append(f"| {c['saf_share_pct']:.0f}% | {c['blended_price']} | {c['margin_rs_l']} | "
             f"{c['ebitda_cr']} | {c['project_irr_pct']}% |")
L.append(f"\nAt ₹{SAF_REALISATION:.0f}/L under an ATJ offtake, routing **30% of output to SAF lifts the "
         f"project from {saf_cases[0]['project_irr_pct']}% to {saf_cases[1]['project_irr_pct']}%**; at 50% it is "
         f"{saf_cases[2]['project_irr_pct']}%. Blending alone is marginal — **the SAF optionality is the "
         "investment case**, and isobutanol's +25% ATJ yield over ethanol is why the molecule is "
         "worth the technology risk at all.\n")

L.append(f"""
Caveats: bio-isobutanol at Indian commercial scale is UNPROVEN — global players (Gevo, Butamax)
have run retrofits, but no Indian plant operates today; yield ({YIELD_L_T:.0f} L/t) and conversion
cost (₹{CONV_COST:.0f}/L) are the two most uncertain levers and both are technology-risk, not market-risk.
No BIS blending standard for isobutanol exists in India (ethanol has IS 15464; petrol IS 2796) —
a standards ask sits alongside the price ask. SAF economics are indicative (ICAO ATJ factors) and
depend on the CORSIA/Indian SAF mandate trajectory. DDGS from a C4 fermentation needs feed-safety
clearance. Retrofit capex ₹60–100 cr band.""")
(OUT / "isobutanol_pitch_model.md").write_text("\n".join(L))

print(f"margin ₹{mpl:.2f}/L | EBITDA ₹{ebitda:.1f} cr | IRR {proj_irr*100:.1f}% | eq {eq_irr*100:.1f}% | "
      f"NPV ₹{proj_npv:.1f} cr | payback {payback} | DSCR {dscr:.2f}")
print(f"energy-parity price ₹{IBU_PARITY_ETH:.1f}/L (ask ₹{IBU_ASK:.0f}) | no-policy: margin ₹{nopolicy_margin:.2f}/L IRR {nopolicy_irr*100:.1f}%")
print(f"E20 drop {e20_drop*100:.1f}% vs IB20 {ib20_drop*100:.1f}% | SAF uplift +{saf_uplift:.0%}")
for r in grid: print(r)
