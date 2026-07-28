#!/usr/bin/env python3
"""Financial model behind the DME blending pitch ("DME, done right").

Venture: a 100-TPD methanol-to-DME dehydration plant (catalytic, alumina —
the simple, proven step) co-located with domestic methanol capacity, selling
DME to blenders for the UNSUBSIDISED commercial/industrial LPG segment
(19-kg cylinders, price-deregulated) under BIS IS 18698:2024 (20% cap).

Underwriting discipline from dme_lpg_blending.py: DME is sold at ENERGY
PARITY (LPG price x 28.8/45.8 = ~0.63x per kg) — never at kg-parity. The
kg-parity scenario is shown only as "the temptation" (it is the consumer-harm
case that would eventually kill the programme politically). Domestic-carbon
methanol (coal-gasification / bio) is the feed case; imported methanol is
shown failing, as the blending analysis proved.

Pure stdlib. Outputs: outputs/dme_pitch_model.md + _sensitivity.csv
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)
CR = 1e7

# ── plant & capital ─────────────────────────────────────────────────────────
TPD        = 100.0        # tonnes DME/day
DAYS       = 330
CAPEX      = 120.0        # Rs cr dehydration unit + storage + loading (lever 100-150)
DEBT_SHARE = 0.70
RATE       = 0.10         # no PSL/subvention assumed for DME (unlike CBG/ethanol)
TENOR      = 8
LIFE       = 15
DISC       = 0.12
RAMP_Y1    = 0.60
UTIL       = 0.90

# ── prices ──────────────────────────────────────────────────────────────────
MJ_LPG, MJ_DME = 45.8, 28.8
LPG_COMM_RS_KG = 62.0      # commercial LPG realisation Rs/kg (19-kg cyl ~Rs1,180; lever)
DME_PARITY     = LPG_COMM_RS_KG * MJ_DME / MJ_LPG    # ~Rs39/kg energy-parity realisation
METH_T_PER_T   = 1.4
METH_DOM       = 17.0      # Rs/kg domestic coal/bio methanol (long-term contract, lever)
METH_IMP       = 24.0      # Rs/kg imported methanol
CONV_COST      = 3.5       # Rs/kg dehydration opex (utilities, catalyst, manpower)

def ebitda_yr(util=UTIL, meth=METH_DOM, real=DME_PARITY):
    t = TPD * DAYS * util
    margin = real - METH_T_PER_T * meth - CONV_COST
    return t * 1000 * margin / CR, margin

def cashflows(meth=METH_DOM, real=DME_PARITY):
    cfs = [-CAPEX]
    for y in range(1, LIFE + 1):
        cfs.append(ebitda_yr(RAMP_Y1 if y == 1 else UTIL, meth, real)[0])
    return cfs

def npv(cfs, r): return sum(c / (1 + r) ** i for i, c in enumerate(cfs))
def irr(cfs):
    lo, hi = -0.5, 2.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if npv(cfs, mid) > 0: lo = mid
        else: hi = mid
    return (lo + hi) / 2

ebitda, margin = ebitda_yr()
cfs = cashflows()
proj_irr, proj_npv = irr(cfs), npv(cfs, DISC)
payback = next((y for y in range(1, LIFE + 1) if sum(cfs[:y + 1]) > 0), None)

debt = CAPEX * DEBT_SHARE
eq = [-(CAPEX - debt)]; bal = debt
for y in range(1, LIFE + 1):
    e = ebitda_yr(RAMP_Y1 if y == 1 else UTIL)[0]
    if y <= TENOR:
        ds = debt / TENOR + bal * RATE; bal -= debt / TENOR
        eq.append(e - ds)
    else:
        eq.append(e)
eq_irr = irr(eq)
dscr = ebitda / (debt / TENOR + debt * (1 - 1 / TENOR) * RATE)

# scenarios
imp_ebitda, imp_margin = ebitda_yr(meth=METH_IMP)          # imported methanol: fails
kgpar_ebitda, kgpar_margin = ebitda_yr(real=LPG_COMM_RS_KG)  # the temptation: kg-parity

# sensitivity: methanol price x DME realisation
meths = [15.0, 17.0, 20.0]
reals = [36.0, DME_PARITY, 42.0]
grid = []
for m in meths:
    row = {"methanol_rs_kg": m}
    for r in reals:
        row[f"real_{r:.0f}"] = round(irr(cashflows(m, r)) * 100, 1)
    grid.append(row)

with (OUT / "dme_pitch_sensitivity.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(grid[0])); w.writeheader(); w.writerows(grid)

kt = TPD * DAYS * UTIL / 1000
L = [f"""# DME dehydration plant model — 100 TPD, energy-parity underwriting

Capex ₹{CAPEX:.0f} cr · 70:30 @ {RATE*100:.0f}% (no subvention assumed) · {LIFE}-yr life · {UTIL*100:.0f}% utilisation
→ {kt:.1f} kt DME/yr, enough to blend ~{kt/0.2/1000:.0f} kt of DME20 commercial LPG.

## Per-kg economics (₹/kg)
| Item | Domestic methanol (base) | Imported methanol | Temptation: kg-parity pricing |
|---|---|---|---|
| DME realisation | {DME_PARITY:.1f} (energy parity vs comm. LPG ₹{LPG_COMM_RS_KG:.0f}) | {DME_PARITY:.1f} | {LPG_COMM_RS_KG:.1f} |
| Methanol feed (1.4×) | ({METH_T_PER_T*METH_DOM:.1f}) | ({METH_T_PER_T*METH_IMP:.1f}) | ({METH_T_PER_T*METH_DOM:.1f}) |
| Conversion | ({CONV_COST:.1f}) | ({CONV_COST:.1f}) | ({CONV_COST:.1f}) |
| **Margin** | **{margin:.1f}** | **{imp_margin:.1f}** | **{kgpar_margin:.1f}** |

- Imported methanol margin is ₹{imp_margin:.1f}/kg — **the route fails at honest pricing**, as the
  blending analysis proved. Domestic-carbon methanol is a condition, not a preference.
- kg-parity pricing would earn ₹{kgpar_margin:.1f}/kg (EBITDA ₹{kgpar_ebitda:.0f} cr) — the margin IS the
  consumer's hidden 37% energy loss. We underwrite at energy parity; the temptation row exists
  to show what we are refusing.

## Returns (base: domestic methanol ₹{METH_DOM:.0f}/kg, energy-parity ₹{DME_PARITY:.1f}/kg)
| Metric | Value |
|---|---|
| EBITDA | ₹{ebitda:.1f} cr/yr |
| Project IRR | **{proj_irr*100:.1f}%** |
| Equity IRR | **{eq_irr*100:.1f}%** |
| NPV @ {DISC*100:.0f}% | ₹{proj_npv:.1f} cr |
| Payback | year {payback} |
| DSCR (steady) | {dscr:.2f}× |

## Sensitivity — project IRR (%): methanol price × DME realisation
| Methanol ₹/kg | ₹36/kg | ₹{DME_PARITY:.0f}/kg (parity, base) | ₹42/kg |
|---|---|---|---|"""]
for r in grid:
    L.append(f"| {r['methanol_rs_kg']:.0f} | {r[f'real_36']} | {r[f'real_{DME_PARITY:.0f}']} | {r['real_42']} |")
L.append(f"""
## Why commercial LPG first
The 19-kg commercial cylinder is price-DEREGULATED and unsubsidised: energy-parity pricing is a
private negotiation with the blender/marketer, not a subsidy-policy fight, and the PMUY inversion
(₹1,201 cr/yr at domestic DME20) never arises. Commercial+industrial LPG is ~4-5 MMT/yr — a
DME20 ceiling of ~0.9-1.1 MMT DME, 27-33 plants of this size. Domestic kitchens only after
parity cylinder pricing is regulated in.

Caveats: capex band ₹100-150 cr; commercial LPG realisation swings with propane (Saudi CP);
domestic methanol at ₹15-17 assumes coal-gasification supply (Coal India/BHEL projects) or
long-term bio-methanol — TODAY'S market methanol is imported at ~₹24 (the failing column);
elastomer retrofit costs at the blender sit outside this model; no subvention assumed — a
DME-specific ISS analogue would move equity IRR materially.""")
(OUT / "dme_pitch_model.md").write_text("\n".join(L))

print(f"margin ₹{margin:.1f}/kg | EBITDA ₹{ebitda:.1f} cr | IRR {proj_irr*100:.1f}% | eq {eq_irr*100:.1f}% | "
      f"NPV ₹{proj_npv:.1f} cr | payback {payback} | DSCR {dscr:.2f}")
print(f"imported-methanol margin ₹{imp_margin:.1f}/kg (fails) | kg-parity margin ₹{kgpar_margin:.1f}/kg (refused)")
for r in grid: print(r)
