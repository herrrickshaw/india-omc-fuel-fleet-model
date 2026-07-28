#!/usr/bin/env python3
"""Reference-plant financial model behind the CBG investment pitch.

Plant: 12 TPD (tonnes per day) multi-feedstock CBG plant (press-mud +
agri-residue), the standard SATAT-scale unit. ALL inputs are editable levers;
industry-range sources noted inline. Three revenue legs: gas (SATAT floor),
fermented organic manure (FOM under FCO Schedule VIII + MDA), carbon credits.

Outputs: outputs/cbg_pitch_model.md + cbg_pitch_sensitivity.csv
Pure stdlib (IRR via bisection).
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)
CR = 1e7

# ── plant & capital ─────────────────────────────────────────────────────────
TPD          = 12.0        # tonnes CBG/day (12,000 kg/d)
DAYS         = 330         # operating days/yr
CAPEX_PER_TPD = 5.0        # Rs cr per TPD (industry band 4-6)
CAPEX        = TPD * CAPEX_PER_TPD          # Rs 60 cr gross
MNRE_CFA     = 10.0        # Rs cr central financial assistance (capped)
NET_CAPEX    = CAPEX - MNRE_CFA             # Rs 50 cr
DEBT_SHARE   = 0.70        # priority-sector lending
RATE         = 0.095       # PSL interest
TENOR        = 10          # yrs, equal principal
LIFE         = 15          # project life, yrs
DISC         = 0.12        # discount rate for NPV
RAMP_Y1      = 0.60        # year-1 capacity utilisation
UTIL         = 0.90        # steady-state utilisation

# ── revenue legs ────────────────────────────────────────────────────────────
CBG_PRICE    = 54.0        # Rs/kg SATAT assured (lever)
FEED_TPD     = 250.0       # tonnes/day feedstock in
FOM_YIELD    = 0.20        # FOM out as share of feedstock (twin layer: ~20%)
FOM_PRICE    = 1500.0      # Rs/t net realisation (sale ~Rs 0-1,500 + MDA Rs 1,500; conservative net)
CO2_PER_T    = 2.5         # tCO2e avoided per tonne CBG (lever; lifecycle basis)
CARBON_PRICE = 800.0       # Rs per credit (~$9.6; CCTS/voluntary lever)

# ── opex ────────────────────────────────────────────────────────────────────
FEED_COST    = 700.0       # Rs/t feedstock delivered (press-mud/residue mix)
OM_FIXED     = 5.0         # Rs cr/yr O&M + power + manpower + admin

def year_cash(util, feed_cost=FEED_COST, cbg_price=CBG_PRICE, fom_price=FOM_PRICE):
    gas_t   = TPD * DAYS * util
    gas_rev = gas_t * 1000 * cbg_price / CR
    fom_rev = FEED_TPD * DAYS * util * FOM_YIELD * fom_price / CR
    co2_rev = gas_t * CO2_PER_T * CARBON_PRICE / CR
    opex    = FEED_TPD * DAYS * util * feed_cost / CR + OM_FIXED
    return gas_rev, fom_rev, co2_rev, opex, gas_rev + fom_rev + co2_rev - opex

def project_cashflows(feed_cost=FEED_COST, cbg_price=CBG_PRICE, fom_price=FOM_PRICE):
    cfs = [-NET_CAPEX]
    for y in range(1, LIFE + 1):
        util = RAMP_Y1 if y == 1 else UTIL
        cfs.append(year_cash(util, feed_cost, cbg_price, fom_price)[4])
    return cfs

def npv(cfs, r):
    return sum(c / (1 + r) ** i for i, c in enumerate(cfs))

def irr(cfs):
    lo, hi = -0.5, 1.5
    for _ in range(100):
        mid = (lo + hi) / 2
        if npv(cfs, mid) > 0: lo = mid
        else: hi = mid
    return (lo + hi) / 2

cfs = project_cashflows()
g, f, c, o, ebitda = year_cash(UTIL)
proj_irr, proj_npv = irr(cfs), npv(cfs, DISC)
payback = next(y for y in range(1, LIFE + 1) if sum(cfs[:y + 1]) > 0)

# debt service (steady state, mid-tenor average) for DSCR context
debt = NET_CAPEX * DEBT_SHARE
ds_y2 = debt / TENOR + debt * (1 - 1 / TENOR) * RATE
dscr = ebitda / ds_y2

# equity IRR (simple: equity out, EBITDA - debt service in during tenor, EBITDA after)
eq_cfs = [-(NET_CAPEX - debt)]
bal = debt
for y in range(1, LIFE + 1):
    util = RAMP_Y1 if y == 1 else UTIL
    e = year_cash(util)[4]
    if y <= TENOR:
        ds = debt / TENOR + bal * RATE
        bal -= debt / TENOR
        eq_cfs.append(e - ds)
    else:
        eq_cfs.append(e)
eq_irr = irr(eq_cfs)

# sensitivity: CBG price x feedstock cost -> project IRR
prices = [48.0, 54.0, 60.0]
feeds  = [525.0, 700.0, 875.0]      # -25% / base / +25%
grid = []
for pr in prices:
    row = {"cbg_price_rs_kg": pr}
    for fc in feeds:
        row[f"feed_{int(fc)}"] = round(irr(project_cashflows(fc, pr)) * 100, 1)
    grid.append(row)
no_fom_irr = irr(project_cashflows(fom_price=0.0))

with (OUT / "cbg_pitch_sensitivity.csv").open("w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(grid[0])); w.writeheader(); w.writerows(grid)

L = [f"""# CBG reference-plant model — 12 TPD multi-feedstock (all inputs are levers)

Capex ₹{CAPEX:.0f} cr (₹{CAPEX_PER_TPD:.0f} cr/TPD) − MNRE CFA ₹{MNRE_CFA:.0f} cr = **net ₹{NET_CAPEX:.0f} cr**;
70:30 debt:equity at {RATE*100:.1f}% (priority-sector), {TENOR}-yr tenor, {LIFE}-yr life, {UTIL*100:.0f}% steady utilisation.

## Steady-state year (₹ cr)
| Leg | Amount |
|---|---|
| Gas @ SATAT ₹{CBG_PRICE:.0f}/kg ({TPD*DAYS*UTIL:,.0f} t) | {g:.2f} |
| FOM @ ₹{FOM_PRICE:,.0f}/t net incl MDA ({FEED_TPD*DAYS*UTIL*FOM_YIELD:,.0f} t) | {f:.2f} |
| Carbon @ ₹{CARBON_PRICE:,.0f}/credit ({TPD*DAYS*UTIL*CO2_PER_T:,.0f} credits) | {c:.2f} |
| Opex (feedstock ₹{FEED_COST:,.0f}/t + O&M ₹{OM_FIXED:.0f} cr) | ({o:.2f}) |
| **EBITDA** | **{ebitda:.2f}** ({ebitda/(g+f+c)*100:.0f}% margin) |

## Returns
| Metric | Value |
|---|---|
| Project IRR ({LIFE} yr) | **{proj_irr*100:.1f}%** |
| Equity IRR (levered) | **{eq_irr*100:.1f}%** |
| NPV @ {DISC*100:.0f}% | ₹{proj_npv:.1f} cr |
| Payback | year {payback} |
| DSCR (steady) | {dscr:.2f}× |
| Project IRR with NO fertiliser leg | {no_fom_irr*100:.1f}% — the FOM+MDA leg is load-bearing |

## Sensitivity — project IRR (%) : CBG price × feedstock cost
| CBG ₹/kg | feed ₹525/t (−25%) | ₹700/t (base) | ₹875/t (+25%) |
|---|---|---|---|"""]
for r in grid:
    L.append(f"| {r['cbg_price_rs_kg']:.0f} | {r['feed_525']} | {r['feed_700']} | {r['feed_875']} |")
L.append("\nCaveats: capex/TPD, FOM realisation, carbon price and CO2e factor are the sensitive "
         "levers; SATAT price revisions (May-2025 methodology) can move the gas leg either way; "
         "feedstock supply contracts, not price, are the usual execution failure; ramp-up year "
         "modelled at 60%.")
(OUT / "cbg_pitch_model.md").write_text("\n".join(L))

print(f"EBITDA ₹{ebitda:.1f} cr | project IRR {proj_irr*100:.1f}% | equity IRR {eq_irr*100:.1f}% | "
      f"NPV@12% ₹{proj_npv:.1f} cr | payback yr {payback} | DSCR {dscr:.2f}x | no-FOM IRR {no_fom_irr*100:.1f}%")
for r in grid: print(r)
