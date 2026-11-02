# India OMC Retail Fuel Profitability and Fleet Model

Models how much marketing margin India's Oil Marketing Companies (OMCs) earn from retail petrol (MS) and
diesel (HSD), how E20/E25/E30 ethanol blending changes that (mileage drop pulls more litres through the
pump for the same distance), and how many vehicles are actually driven, backed out from PPAC fuel
consumption and Vahan registrations. Outputs are Markdown reports, CSVs and an Excel workbook under
`outputs/`; a set of companion scripts extends the model to blend economics, CBG/DME/isobutanol pitches
and a textile-feedstock import study.

> Status: maintained. Analytical estimates built on PPAC *Oil & Gas Ready Reckoner FY 2025-26 (H1)* and
> Vahan4 dashboard captures; OMC margin is an editable assumption, not a published figure. Not investment advice.

The full pre-refactor README (every headline number, all companion-script write-ups, the textile section)
is kept verbatim in [`docs/README_FULL.md`](docs/README_FULL.md).

## What it does
- `omc_model.py`: base FY24-25 retail book, uniform E0/E20/E25/E30 scenarios, five fuel-pool mix scenarios and an FY25-26 to FY29-30 projection. Headline: base OMC retail gross about ₹46,450 cr/yr; extra pump income from ethanol E20 ₹757 cr, E25 ₹1,057 cr, E30 ₹1,367 cr.
- `fleet_from_fuel.py`: actively-driven fleet = annual fuel / (km/day x active-days / mileage) per sector, plus EV from Vahan registrations (about 24.5 crore vehicles vs 44.6 crore cumulative registrations; 21.6-28.8 crore two-wheeler sensitivity band).
- `vahan/analyze_vahan_fuel.py`: fuel-wise Vahan registrations (CY2025 and cumulative), fuel-group and vehicle-class summaries, E20-badged fleet share.
- `energy_blend_comparison.py`: LHV table, volumetric dilution per blend, and who collects the extra litres (excise, VAT, dealer commission, OMC) for petrol E20-E30 and diesel B7-B20.
- Companion scripts: price parity, ethanol supply match, SGST sweet spot, state-wise tax impact, petrol demand forecast, freed-petrol export value, CBG/DME/isobutanol/distillery pitch models, RON analysis (see `docs/README_FULL.md`).

## Quick start
```bash
git clone https://github.com/herrrickshaw/india-omc-fuel-fleet-model.git
cd india-omc-fuel-fleet-model
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # only openpyxl, for build_xlsx.py
python3 omc_model.py              # writes outputs/omc_profitability_report.md + CSVs
```
Other entry points: `python3 fleet_from_fuel.py`, `python3 vahan/analyze_vahan_fuel.py`,
`python3 energy_blend_comparison.py`, `python3 build_xlsx.py` (formula-driven Excel).

## How it works
| Stage | Module | Output |
|---|---|---|
| Inputs (PPAC constants, levers) | module-level constants in each script | n/a |
| Pure computation (`run_model`, `build_rows`, `summarise`, `class_breakdown`) | `omc_model.py`, `fleet_from_fuel.py`, `vahan/analyze_vahan_fuel.py`, `energy_blend_comparison.py` | dicts of results |
| Rendering (`render_md`) | same modules | Markdown text |
| Writing (`write_csvs`, `write_md`, `write_outputs`) | same modules | `outputs/*.md`, `outputs/*.csv` |

Design decision: volumes are anchored on PPAC Table 6.1 national consumption (not the per-RO KL column,
which is an H1-over-12-months artefact). Distance driven is held fixed at the E0-equivalent of today's
E20 pool so scenarios are comparable. Units: volumes in billion litres, money in ₹ crore.

## Repository layout
| Path | Purpose |
|---|---|
| `omc_model.py`, `fleet_from_fuel.py`, `energy_blend_comparison.py` | Core models (pure stdlib) |
| `vahan/` | Vahan registration analysis and state-wise scripts, raw CSV captures |
| `refining/`, `upstream/`, `policy/` | Refining trade, upstream acreage and policy analyses |
| `*_pitch_model.py`, `build_*.js`, `build_xlsx.py` | Pitch models and document/deck/workbook builders |
| `outputs/` | Generated reports and CSVs (tracked) |
| `docs/` | Decks, papers, pitch write-ups and the full legacy README |
| `textile_data/` | Textile import-export study (own README) |
| `tests/` | Characterisation tests |

## Data sources
| Source | What is taken | Access route | Licence / caveat |
|---|---|---|---|
| PPAC Oil & Gas Ready Reckoner FY2025-26 (H1) | Consumption, outlets, dealer commission | Manual extraction, constants in code | Public government data |
| Vahan4 dashboard (vahan.parivahan.gov.in) | Fuel-wise registrations, captured 2026-07-24 | Manual capture, embedded in `vahan/analyze_vahan_fuel.py` | Cumulative counts include scrapped vehicles |
| Nielsen/PPAC sectoral demand study (2013) | Fuel split by sector in `fleet_from_fuel.py` | Constants | 2013 vintage, overstates diesel cars |

## Configuration
No environment variables or secrets. Levers (OMC margins, mileage drops, blend roadmap, mix shares,
sector shares, daily usage) are named constants at the top of each script; edit and re-run.

## Testing
```bash
pip install pytest
pytest -q
```
The tests regenerate every output of the four core modules into a temp directory and compare them
byte-for-byte with the tracked `outputs/` files. No network access is used.

## Limitations and known issues
- OMC marketing margin (₹3.5/L petrol, ₹2.5/L diesel) is an editable estimate; treat absolute ₹ as order-of-magnitude and ethanol deltas as the robust result.
- Ethanol applies to petrol only; the mileage mechanism does not apply to CBG blended into CNG (IS 16087 keeps it fungible with CNG).
- E25/E30 mileage drops are extrapolated from E20's certified 4%.
- Fleet estimate: sector split is 2013-vintage; petrol/CNG bi-fuel cars are partly double-counted; EV row is registration-based.
- Retail outlet count: the model baseline is 99,281 (01.10.2025), later snapshots differ.
- Only four modules are covered by tests and lint; the remaining scripts still run everything at import time.

## Related repositories
- [`vehicle_fuel_mileage`](https://github.com/herrrickshaw/vehicle_fuel_mileage): mirror of the Volume Dividend paper and slides; `scripts/recalc.py` populates formula values in the Excel workbook.

## Licence
MIT, see [LICENSE](LICENSE).
