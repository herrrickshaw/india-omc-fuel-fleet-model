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

## Petrol-demand & ethanol-requirement forecast (`petrol_demand_forecast.py`)

Forecasts petrol demand FY26–FY31 anchored on the **PPAC/literature trend** (RR: MS decadal CAGR 7.1%,
recent H1 +6.8–7.1%) and shaped by **FADA vehicle-sales signals** (2W ~72% of sales still ~93% petrol;
rising EV share — 8.5% overall — bends the growth rate down), then derives the ethanol requirement
against an E20→E30 roadmap:

- **Petrol demand (MMT):** High/7% → 60; **Base/moderating → 53.6 (5.0% CAGR)**; Low/fast-EV → 47.8.
- **Ethanol requirement nearly doubles:** ~1,150 cr L (E20, FY26) → **~2,170 cr L (E30, FY31)** in the base.
- **Supply is the binding constraint:** India's ~1,600 cr L fuel-ethanol capacity fits E20 today, but
  **E30 on a growing petrol base needs ~36% more** — the roadmap is limited by ethanol, not petrol demand.
- Scales the whole model: at base FY30-31 (E30), freed-petrol export ≈ ₹1.0 lakh cr, state VAT foregone
  ≈ ₹39k cr, a 5% SGST ≈ ₹6.5k cr for states.

Run: `python3 petrol_demand_forecast.py` → `outputs/petrol_demand_forecast.md` + `petrol_demand_forecast.csv` + `ethanol_requirement_forecast.csv`.

## Freed-petrol export value (`petrol_export_value.py`)

Ethanol displaces domestic petrol, freeing it for export (India is a net product exporter). Valued at
India's actual petrol-export realisation and its trend (RR Table 4.11: exports grew 11.6→15.8 MMT,
₹98,379 cr in FY24-25; realisation ₹23–58/L with crude, ~₹46/L central):

- **E20 frees ~8.0 MMT** of petrol — **51% of India's entire current petrol export** — worth
  **~₹49,834 cr ($5.9 bn)/yr** FOB. Ethanol has effectively *already enabled ~half* of what India exports.
- **E25 → 10.0 MMT (~₹62,300 cr / $7.3 bn); E30 → 12.0 MMT (~₹74,751 cr / $8.8 bn)** — roughly doubling
  exportable petrol vs E20.
- This is the **single largest rupee item** ethanol blending creates — bigger than the state VAT
  foregone (~₹17,900 cr) or central excise foregone (~₹21,500 cr) — and it accrues as **export/forex
  earnings**, not domestic tax. (Export vs import-substitution are the same barrels, one lens.)

Run: `python3 petrol_export_value.py` → `outputs/petrol_export_value.md` + `petrol_export_value.csv` + `petrol_export_trend.csv`.

## Policy case — a price-neutral state SGST on ethanol (`ethanol_sgst_sweetspot.py`)

Turns the revenue-foregone problem into a design: ethanol (~₹60/L) is cheaper than the petrol
base+excise it displaces (~₹75/L), so at a **fixed pump price** every ethanol litre opens ~₹15/L of
fiscal space. A **state SGST on ethanol at 1–5%**, funded from that space, is new state revenue with
zero consumer-price impact — and it scales with the blend.

- **State SGST revenue grid:** ₹649 cr (E20 @ 1%) → **₹4,787 cr (E27 @ 5%)** → ₹5,513 cr (E30 @ 5%).
- **Recovery insight:** the *fraction* of foregone petrol-VAT recovered depends only on the rate
  (~4% at 1% … ~18% at 5%), not the blend; the blend sets the rupees. Full VAT-parity recovery needs
  ~27% (still price-neutral, but a heavy green-fuel levy).
- **Sweet spot = E27 @ 5%** — India's Brazil-style equilibrium: the highest blend a non-flex fleet
  tolerates (Brazil settled at E27 before flex E30), yielding ~₹4,787 cr price-neutral, top states UP
  ₹578 cr / Maharashtra ₹523 cr / Tamil Nadu ₹423 cr. E30 is the frontier (needs flex/E20+ fleet).
- Levies of ₹3–3.4/L sit comfortably inside the ₹9–15/L space at every blend, so **prices never move**.

Run: `python3 ethanol_sgst_sweetspot.py` → `outputs/ethanol_sgst_sweetspot.md` + `ethanol_sgst_grid.csv`.

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
