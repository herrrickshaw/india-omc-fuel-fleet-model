#!/usr/bin/env python3
"""Financial model behind the distillery multi-feed conversion pitch.

Play: convert an existing 100-KLPD molasses distillery (cane-season bound,
~180 operating days) into a MULTI-FEED plant by adding grain handling,
milling/liquefaction, and a DDGS dryer — running maize/damaged grain in the
off-season. Days go 180 -> 330; the grain litres price at the HIGHER
administered slabs (maize Rs 71.86/L vs C-heavy molasses Rs 57.97).

All inputs are levers. Anchors:
  OMC price slabs ESY24-25 (this repo: price_parity_scenarios.py SLABS).
  DFPD ISS: 1,212 approved projects, grain+dual windows 2021-22 dominate
  (~770 approvals) — the register already shows the pivot.
  Conversion capex band Rs 40-60 cr per 100 KLPD grain addition (brownfield;
  greenfield grain 100 KLPD is ~Rs 120-150 cr) — industry/DPR band, lever.
  Maize->ethanol: ~400 L/t + ~310 kg DDGS/t.

Outputs: outputs/distillery_conversion_model.md + _sensitivity.csv
Pure stdlib (IRR via bisection).
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)
CR = 1e7

# ── plant & conversion capital ──────────────────────────────────────────────
KLPD         = 100.0
GRAIN_DAYS   = 150       # incremental off-season operating days (lever 100-200)
CONV_CAPEX   = 50.0      # Rs cr: grain silos+milling+liquefaction+DDGS dryer+boiler mods
DEBT_SHARE   = 0.70
RATE         = 0.095     # base lending rate
ISS_SUBVENTION = 0.06    # DFPD interest subvention (6% or half of rate, whichever lower)
EFF_RATE     = max(RATE - ISS_SUBVENTION, RATE / 2)   # effective rate on eligible loan
TENOR        = 8
LIFE         = 15
DISC         = 0.12
RAMP_Y1      = 0.60

# ── grain-campaign economics (per litre) ────────────────────────────────────
ETH_PRICE    = 71.86     # Rs/L maize slab (ESY24-25)
MAIZE_PRICE  = 23000.0   # Rs/t delivered (lever)
YIELD_L_T    = 400.0     # L ethanol per tonne maize
DDGS_KG_L    = 0.775     # kg DDGS per litre (310 kg/t / 400 L/t)
DDGS_PRICE   = 17.0      # Rs/kg
CONV_COST    = 13.0      # Rs/L: steam+power+enzymes+yeast+chemicals+manpower+maintenance

def per_litre(maize=MAIZE_PRICE, eth=ETH_PRICE):
    feed = maize / YIELD_L_T
    ddgs = DDGS_KG_L * DDGS_PRICE
    return eth - feed + ddgs - CONV_COST      # EBITDA per litre

def annual_ebitda(util=1.0, maize=MAIZE_PRICE, eth=ETH_PRICE, days=GRAIN_DAYS):
    litres = KLPD * 1000 * days * util        # L/yr incremental
    return litres * per_litre(maize, eth) / CR

def cashflows(maize=MAIZE_PRICE, eth=ETH_PRICE, days=GRAIN_DAYS):
    cfs = [-CONV_CAPEX]
    for y in range(1, LIFE + 1):
        cfs.append(annual_ebitda(RAMP_Y1 if y == 1 else 1.0, maize, eth, days))
    return cfs

def npv(cfs, r): return sum(c / (1 + r) ** i for i, c in enumerate(cfs))
def irr(cfs):
    lo, hi = -0.5, 2.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if npv(cfs, mid) > 0: lo = mid
        else: hi = mid
    return (lo + hi) / 2

pl = per_litre()
ebitda = annual_ebitda()
cfs = cashflows()
proj_irr, proj_npv = irr(cfs), npv(cfs, DISC)
payback = next(y for y in range(1, LIFE + 1) if sum(cfs[:y + 1]) > 0)

# levered equity IRR with ISS-subvented debt
debt = CONV_CAPEX * DEBT_SHARE
eq = [-(CONV_CAPEX - debt)]; bal = debt
for y in range(1, LIFE + 1):
    e = annual_ebitda(RAMP_Y1 if y == 1 else 1.0)
    if y <= TENOR:
        ds = debt / TENOR + bal * EFF_RATE
        bal -= debt / TENOR
        eq.append(e - ds)
    else:
        eq.append(e)
eq_irr = irr(eq)
ds2 = debt / TENOR + debt * (1 - 1 / TENOR) * EFF_RATE
dscr = ebitda / ds2

# sensitivity: maize price x grain days
maizes = [20000.0, 23000.0, 26000.0]
days_l = [100, 150, 200]
grid = []
for m in maizes:
    row = {"maize_rs_t": int(m)}
    for d in days_l:
        row[f"days_{d}"] = round(irr(cashflows(maize=m, days=d)) * 100, 1)
    grid.append(row)
# stress: allocation cut — grain litres priced at DFG slab instead of maize slab
dfg_irr = irr(cashflows(eth=64.0))

with (OUT / "distillery_conversion_sensitivity.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(grid[0])); w.writeheader(); w.writerows(grid)

L = [f"""# Multi-feed conversion model — 100 KLPD molasses distillery + grain campaign

Conversion capex ₹{CONV_CAPEX:.0f} cr (grain handling + milling/liquefaction + DDGS dryer +
boiler mods). Incremental {GRAIN_DAYS} off-season days at {KLPD:.0f} KLPD = {KLPD*1000*GRAIN_DAYS/1e7:.1f} cr L/yr
of grain ethanol. Debt 70% at {RATE*100:.1f}% − {ISS_SUBVENTION*100:.0f}% DFPD interest subvention = {EFF_RATE*100:.1f}% effective.

## Per-litre grain economics (maize campaign)
| Item | ₹/L |
|---|---|
| Realisation (maize slab) | {ETH_PRICE:.2f} |
| Maize @ ₹{MAIZE_PRICE:,.0f}/t ÷ {YIELD_L_T:.0f} L/t | ({MAIZE_PRICE/YIELD_L_T:.2f}) |
| DDGS credit {DDGS_KG_L:.3f} kg × ₹{DDGS_PRICE:.0f} | {DDGS_KG_L*DDGS_PRICE:.2f} |
| Conversion cost (utilities, enzymes, manpower) | ({CONV_COST:.2f}) |
| **EBITDA / litre** | **{pl:.2f}** |

## Returns (incremental, conversion only)
| Metric | Value |
|---|---|
| Incremental EBITDA | ₹{ebitda:.1f} cr/yr |
| Project IRR ({LIFE} yr) | **{proj_irr*100:.1f}%** |
| Equity IRR (ISS-subvented debt) | **{eq_irr*100:.1f}%** |
| NPV @ {DISC*100:.0f}% | ₹{proj_npv:.1f} cr |
| Payback | year {payback} |
| DSCR (steady) | {dscr:.2f}× |
| Stress: litres priced at damaged-grain slab ₹64 | IRR {dfg_irr*100:.1f}% |

## Sensitivity — project IRR (%): maize price × grain-campaign days
| Maize ₹/t | 100 days | 150 days (base) | 200 days |
|---|---|---|---|"""]
for r in grid:
    L.append(f"| {r['maize_rs_t']:,} | {r['days_100']} | {r['days_150']} | {r['days_200']} |")
L.append("\nCaveats: slab prices are administered and revised each ESY — the maize-slab premium "
         "over molasses is a policy artefact, not a market spread; OMC allocation (only ~60% of "
         "offered ethanol absorbed) is the real volume risk — multi-feed flexibility hedges it "
         "but does not eliminate it; DDGS realisation swings with poultry-feed demand; capex "
         "band ₹40–60 cr depends on existing boiler/ETP headroom; ramp year at 60%.")
(OUT / "distillery_conversion_model.md").write_text("\n".join(L))

print(f"per-L EBITDA ₹{pl:.2f} | EBITDA ₹{ebitda:.1f} cr | IRR {proj_irr*100:.1f}% | eq IRR {eq_irr*100:.1f}% | "
      f"NPV ₹{proj_npv:.1f} cr | payback yr {payback} | DSCR {dscr:.2f}x | DFG-slab stress {dfg_irr*100:.1f}%")
for r in grid: print(r)
