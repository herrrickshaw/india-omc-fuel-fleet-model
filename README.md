# OMC Retail Profitability Model — petrol & diesel, with ethanol (E20/E25/E30) effect

Models how much marketing margin India's Oil Marketing Companies earn from
selling petrol (MS) and diesel (HSD) through retail outlets, how it grows
year-on-year with vehicle-driven demand, and how much *extra* comes from
ethanol blending (which cuts mileage, pushing more litres through the pump for
the same distance). Built on **PPAC Ready Reckoner FY 2025-26 (H1)** data.

## Drivers modelled (as requested)

1. **Number of retail outlets** — 99,281 (01.10.2025; PSU 90,022 + private 9,259).
2. **Average sales per outlet** — true throughput ~45 KL/mo petrol, ~92 KL/mo diesel;
   plus the *network-dilution* finding (outlets +8% vs demand +3-7% → per-RO throughput falling).
3. **Increased sales from vehicle-sales growth** — MS +7.1%/yr, HSD +2.9%/yr (RR 6.1 H1 YoY).
4. **Mileage drop from ethanol** — E20 4%, E25 5.5%, E30 7% (SIAM/ARAI central, LCV-scaled).
5. **Additional income from E20 YoY** — extra pump throughput × OMC margin.
6. **Scenarios E25 & E30** — higher blend → bigger mileage drop → more throughput income.

## Headline results (illustrative — OMC margin is the key lever)

- **Base OMC retail marketing gross ≈ ₹46,450 cr/yr** (petrol ₹18,920 + diesel ₹27,530).
- **Ethanol extra pump income:** E20 ₹757 cr · E25 ₹1,057 cr · E30 ₹1,367 cr per year.
- **YoY trajectory FY25-26 → FY29-30:** ₹46,450 → ₹56,560 cr as demand grows and blend steps up.
- Counterpoint: pure petrol sold *falls* 43→39 bn L as ethanol rises 11→17 bn L (import substitution).

### Fuel-pool MIX scenarios (E0/E20/E25/E30 in a ratio)

The pool doesn't jump uniformly — shares transition. As the mix shifts from **S0 Today (~E20)** to
**S4 E30-push**, OMC petrol throughput income rises ₹18,881 → ₹19,322 cr (+₹441 cr) from the mileage
penalty alone, ethanol offtake 10.3 → 14.6 bn L, pure petrol 43.7 → 40.6 bn L. Shares are editable.

### CBG caveat (important)

The mileage-drop → extra-throughput mechanism is **ethanol-in-petrol only**. **CBG cascaded into CNG
does not cut mileage**: it must meet **IS 16087** (Bio-CNG spec, ≥~90% methane) so its calorific
value/Wobbe index matches fossil CNG (**IS 15958**) — fungible, km/kg preserved. So there is **no
CBG throughput uplift** for the CNG book; CBG's OMC/CGD value is procurement/policy (SATAT offtake,
green-fuel tax treatment, LNG import substitution), not extra kg dispensed. *(The request's "IS 1876"
reads as shorthand for IS 16087.)*

## Files

| File | What |
|---|---|
| `omc_model.py` | The model (pure stdlib). Edit the INPUTS block, re-run. |
| `build_xlsx.py` | Formula-driven Excel version (levers on the Inputs sheet recalculate everything). |
| `outputs/omc_profitability_report.md` | Methodology + all tables. |
| `outputs/scenarios.csv`, `outputs/yoy_projection.csv` | Machine-readable results. |
| `outputs/OMC_Retail_Profitability_Model.xlsx` | 5-sheet workbook, 6 consistency checks (all PASS). |

## Run

```bash
python3 omc_model.py                                   # report + CSVs
python3 build_xlsx.py                                  # Excel (formulas)
python3 ~/vehicle_fuel_mileage/scripts/recalc.py \
        outputs/OMC_Retail_Profitability_Model.xlsx    # populate formula values (LibreOffice)
```

## Key caveats

- **OMC marketing margin (₹3.5/L petrol, ₹2.5/L diesel) is an editable estimate**, not a published
  figure — it swings with crude. Absolute ₹ are order-of-magnitude; the ethanol *deltas* (percentage
  effects) are the robust result. Dealer commission (RR 8.10) is the dealer's cut and is excluded.
- Ethanol blends into petrol only; diesel grows on vehicle demand alone (biodiesel out of scope).
- Higher-blend mileage drops (E25/E30) are extrapolated from E20's certified 4% by ethanol's lower
  calorific value; adjust in the Inputs sheet as real E25/E30 test data lands.

## Vehicle-count side (Vahan fuel-wise registrations)

`vahan/` holds the **vehicle-count counterpart** to this volume model — fuel-wise registrations
pulled live from the **Vahan4 dashboard** (all-India), both annual and cumulative:

- **CY2025:** 2.93 crore new registrations — petrol ~80%, diesel 10%, **EV 8.0%**, CNG 1.7%.
- **Cumulative ("Till Today"):** 44.6 crore all-time — petrol 80.7%, diesel 13.6%, **EV just 2.2%**
  (the fleet-turnover lag: EVs are 8% of new but 2% of stock). *Cumulative includes scrapped vehicles,
  so it overstates the live parc.*
- **E20-badged fleet:** Vahan now tracks `PETROL(E20)` as its own fuel — 21% of CY2025 registrations
  (and already the majority of new petrol vehicles in CY2026 YTD) — the population the ethanol
  mileage-penalty in this model actually applies to.

Run: `python3 vahan/analyze_vahan_fuel.py` → `vahan/outputs/vahan_fuel_analysis.md` + CSVs.

## State-wise tax revenue foregone from ethanol (`statewise_tax_impact.py`)

Ethanol (5% GST) displacing petrol (high state VAT + central excise) is revenue foregone. This pairs
**state petrol volumes (RR Table 6.4B)** with **state VAT rates (RR Table 8.17)** to size the *state*
portion (VAT lost net of SGST on ethanol), per state, at E20/E25/E30:

- **Net state VAT foregone: ₹17,865 cr (E20) → ₹22,331 cr (E25) → ₹26,792 cr (E30)** per year (36 states).
- Top losers combine high VAT and big volume: **Maharashtra ₹2,126 cr**, Karnataka ₹1,798 cr, UP
  ₹1,776 cr, Telangana ₹1,264 cr, Rajasthan/Kerala/MP ~₹1,150 cr each.
- The **centre** separately forgoes ~₹21,500 cr of excise at E20 (net of CGST) — larger, but borne by
  the Union, not states.

Framing: counterfactual revenue-foregone (petrol-vs-ethanol tax differential) — the E20 blend is still
sold at petrol VAT at the pump, so this is the VAT states *would* have collected had that volume been
petrol not 5%-GST ethanol. VAT uses headline rates only (fixed cesses/floors omitted → losses modestly
higher). Editable levers: pre-VAT base, ethanol price.

Run: `python3 statewise_tax_impact.py` → `outputs/statewise_tax_impact.md` + `statewise_tax_E20/E25/E30.csv`.

## Actively-driven fleet, implied from fuel burn (`fleet_from_fuel.py`)

Cross-check on how many vehicles are *really* on the road daily, backed out from PPAC fuel
consumption instead of registration counts: **active vehicles = annual fuel ÷ (km/day × active-days
÷ mileage)**, per sector, with non-road diesel (farm/rail/industry, ~34 bn L) separated out.

Now covers **petrol + diesel + CNG (fuel balance) and EV (Vahan reg × active-rate)**:

- Liquid-fuel road vehicles **23.0 cr** + CNG **0.73 cr** + EV **0.83 cr** = **~24.5 crore actively-driven**
  — only **~55% of the 44.6-crore cumulative Vahan count**. Chain: cumulative 44.6 cr → live parc
  ~35 cr → actively-driven ~24.5 cr.
- **±20% two-wheeler-usage sensitivity band: 21.6 – 28.8 crore** (2-wheelers, ~17 cr, dominate and burn
  ~0.6 L/day each; national avg ~1.5 L/day per active liquid-fuel vehicle).
- The gap vs cumulative is scrapped/dead/seasonal vehicles Vahan never removes — independent (fuel-based)
  evidence the cumulative figure roughly doubles the daily-driven fleet.
- Caveats baked in: 2013-vintage sector split (overstates diesel cars); petrol/CNG **bi-fuel double-count**
  inflates the raw sum slightly; EV row is registration-based (no fuel proxy). All levers editable.

Run: `python3 fleet_from_fuel.py` → `outputs/fleet_from_fuel.md` + `.csv`.

## Data source

PPAC *India's Oil & Gas Ready Reckoner FY 2025-26 (H1)*. Full 100-table CSV extraction of that
Ready Reckoner lives at `~/ppac-ready-reckoner-data/` (local, not committed).
