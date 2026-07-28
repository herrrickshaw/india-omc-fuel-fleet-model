# India's Multi-Market Analysis Platform
## Petrol-Ethanol-Textiles Integrated Research

This repository combines **three interconnected research areas**:

### 🔴 **Oil Marketing & Ethanol** (Primary: OMC Retail Profitability Model)
Models how much marketing margin India's Oil Marketing Companies earn from selling petrol (MS) and diesel (HSD) through retail outlets, plus *ethanol-blending effects* (E20/E25/E30). Includes freed-petrol export value calculations and ethanol supply forecasts.

### 🧵 **Textile Import-Export Analysis** (NEW: FY25 Full Trade Mapping + Policy Roadmap)
Comprehensive analysis of India's **$20.4bn annual textile feedstock import deficit** (Chapters 29+39, TradeStat DGCIS), integrated with:
- **Government initiatives**: BHAVYA Rasayan ($365M), PM Mitra parks, refinery capex ($38.5B)
- **Capacity roadmap**: +5.2 MMTPA by FY30, addressing 40-60% of polymer import gap
- **Segment mapping**: 12 technical textile segments, HSN code framework (315 codes)
- **Policy impact**: 2-3% textile cost reduction + $2-3B export growth potential by FY30
- **Visualizations**: 6 major trend charts, 3 scenario analyses, risk assessment

📊 **Start here**: `textile_data/research/CHEMICAL_SUBSTITUTION_OPPORTUNITY.md` (10-part analysis)

---

# OMC Retail Profitability Model — petrol & diesel, with ethanol (E20/E25/E30) effect

Built on **PPAC Ready Reckoner FY 2025-26 (H1)** data.

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

## The Volume Dividend — energy comparison, parity pricing & CBG economics (2026-07-28)

A four-script extension quantifying the **volume effect**: blends dilute energy per litre, vehicles
buy more litres for the same km, and every per-litre levy (excise ₹19.90, effective VAT ~₹19.5,
dealer ₹4.1, OMC ₹3.5) scales with the extra volume. Published as a paper + slide deck (also
mirrored in [`vehicle_fuel_mileage`](https://github.com/herrrickshaw/vehicle_fuel_mileage)).

| Script | What it shows |
|---|---|
| `energy_blend_comparison.py` | LHV table (ethanol −34%/L vs petrol, isobutanol −17%, FAME −8% vs diesel; CBG ≈ CNG per kg). E20 volume effect: **+2.16 bn L = ₹22,703 cr/yr consumer spend** (excise ₹4,303 / VAT ₹4,216 / dealer ₹886 / OMC ₹757 cr — reconciles with `omc_model.py`). Incremental E20→E30 walk (+₹18,300 cr) and diesel B7→B20 (B20: 1.85 bn L on the 110 bn L pool). |
| `price_parity_scenarios.py` | Honest pricing `P_blend = P_E0×(1−drop)`: E20 ₹100.80, E25 ₹99.22, E30 ₹97.65 (vs ₹105). **S1 — passing through the dual-tax exemption already embedded in the ethanol fraction funds parity 1.3–1.5× at every blend** (no new subsidy). S4 (cheaper ethanol) fails: needs ₹37–41/L vs the ₹57.97 cheapest feedstock slab — grain prices set the floor. |
| `cbg_satat_economics.py` | Renewable ₹/MJ: SATAT CBG 1.16 vs ethanol 2.94 (**2.5× cheaper**), +23% over spot RLNG (undercuts LNG above ~$14.8/MMBtu). ₹/km on SIAM FE: CNG 2.74 vs petrol E20 6.56. CBO 1→5%: ₹378→1,891 cr/yr, pump +₹0.12→0.59/kg, mileage −0.02→−0.11% — vs E20's silent 4%. |
| `ethanol_supply_match.py` | Blend scenarios vs supply: installed ~2,000 cr L (+400 by FY27, CareEdge May-2026), DFPD sanction register 4,530 cr L (1,212 projects). **E20 IS the overcapacity (59% utilisation on FY27 steel); E27 lifts it to 76% — top of CareEdge's consolidation band — with zero new construction.** NCDC coop-mill scheme is 96.5% working capital: the ₹251 cr ethanol tranche ≈ 9.7 cr L/yr (0.5% of installed) — no coop capacity wave. FCI rice leg ~211 cr L (3.9 blend ppt, Jul-2023 suspension risk); feedstock (maize), not steel, binds. |
| `dme_lpg_blending.py` | **DME in LPG — the fourth quadrant** (LERC basis): DME 28.8 vs LPG 45.8 MJ/kg (−37%); LERC-measured −5.26% thermal efficiency at DME20 (IS 4246), BIS IS 18698:2024 caps 20%. On a subsidised per-kg fuel the volume dividend INVERTS: DME20 = +₹312/yr per household + ₹9,325 cr consumer + **₹1,201 cr extra PMUY subsidy** — consumer AND exchequer pay. Methanol-route DME (₹33.6/kg feed) can't clear the ₹32.7/kg energy-parity ceiling; guardrails = parity cylinder pricing (₹761) + domestic-carbon DME only. |
| `ron_octane_analysis.py` | Ethanol blending RON ~112 vs regular petrol 91. Today's route holds the pump at RON 91 → refiners drop the blendstock (BOB) to 85.7 at E20 and keep the saving (worth up to ₹9.5/L at the XP95 spread). **Holding the BOB at 91 instead makes E20 a free national RON95 fuel** (E30 → 97.3); the compression-ratio headroom recovers +2.2% efficiency → net E20 penalty ≈ −1.8% on a RON95-calibrated engine (Brazil's E27 playbook). |
| `build_energy_doc.js` → `docs/Energy_Blend_Volume_Dividend.docx/.pdf` | 10-section paper with methodology/assumptions/caveats per section, a 16-row abbreviations glossary, and **Annex A — the CBG incentive stack**: 19 instruments by lever (SATAT/CBO offtake, MNRE-VGF-SASCI capital, DPI/BAM infrastructure, FCO Schedule VIII + Bulk Sale + MDA fertiliser leg, PSL/AIF/AHIDF finance, GST/excise/carbon, IS 16087/CPCB standards, 7 state policies) compiled from the 70-circular GOBARdhan register, gazette-checked (docx-js; do not hand-edit outputs). |
| `build_slides.js` → `docs/Volume_Dividend_Slides.pptx` | 13-slide deck: mechanism → who collects → blend walk → consumer parity prices → funding scenarios → **ethanol SGST (E27@5% ≈ ₹4,787 cr/yr, price-neutral)** → the E27 grand bargain (parity ₹98.44 + SGST still leaves ₹1.27/L slack) → CBG → supply check → RON95 → CBG incentive stack. |
| `cbg_pitch_model.py` + `build_cbg_pitch.js` → `docs/CBG_Investment_Pitch.pptx/.pdf` | **CBG investment pitch** (9 slides, problem→market→moat→model→financials→ask) on a 12-TPD reference-plant model: ₹60 cr capex − ₹10 cr MNRE CFA, 70:30 @ 9.5% PSL → EBITDA ₹12 cr (54%), **project IRR 20.6% / equity IRR 32% / NPV@12% ₹26.6 cr / DSCR 1.85×**, sensitivity 13.5–27.1%; no-FOM IRR 16.1% (the fertiliser leg is load-bearing). Ask: ₹150 cr for a 10-plant platform anchored on cooperative-sugar-mill press-mud (BOT/JV entry). |
| `distillery_conversion_model.py` + `build_distillery_pitch.js` → `docs/Distillery_MultiFeed_Pitch.pptx/.pdf` | **Multi-feed conversion pitch**: 100-KLPD molasses distillery + ₹50 cr grain conversion → 180→330 days, +1.5 cr L/yr at the maize slab. Per-L EBITDA ₹14.5 → **project IRR 38.4% / equity IRR 81% (DFPD-subvented debt ~3.5%) / NPV ₹90.7 cr / DSCR 3.74×**; honest stress: damaged-grain-slab pricing 17%, maize ₹26k 10–25%. Ask: 5-mill ₹250 cr BOT/JV conversion programme with cooperative sugar mills. |
| `dme_pitch_model.py` + `build_dme_pitch.js` → `docs/DME_Blending_Pitch.pptx/.pdf` | **DME pitch — "DME, done right"**: 100-TPD methanol-to-DME dehydration (₹120 cr) under three guardrails — energy-parity pricing always (₹39/kg vs commercial LPG ₹62), **unsubsidised C&I segment first** (PMUY inversion never arises), domestic-carbon methanol only (imported fails at ₹1.9/kg margin). Base: **IRR 26.0% / equity 42.1% / NPV ₹106 cr / DSCR 1.94×**; the refused kg-parity margin (₹34.7/kg = the consumer's hidden loss) shown explicitly. Gated ask: ₹120 cr pilot after a ≤₹17/kg take-or-pay methanol contract. |
| `isobutanol_pitch_model.py` + `build_isobutanol_pitch.js` → `docs/Isobutanol_Blending_Pitch.pptx/.pdf` | **Bio-isobutanol pitch**: retrofit an idle 100-KLPD grain distillery to 70 KLPD isobutanol (₹80 cr). The molecule wins on physics — 26.5 vs 21.1 MJ/L, **IB20 dilutes 3.5% vs E20's 6.9%**, ATJ/SAF yield 0.75 vs 0.60 t/t (+25% jet), water-immiscible so pipeline-shippable. But **no price slab and no BIS standard exist**: at ethanol's per-litre slab the margin is −₹9.58/L, so the ask is energy-basis pricing (₹88/L vs ₹90.3 parity). Blending-only IRR 13.8%; **30% routed to ATJ/SAF → 33.9%** (EBITDA ₹30.5 cr) — the SAF leg is the investment case. |

Headline synthesis: **blend more (E27), charge less (₹98.44/L), tax smarter (5% ethanol SGST)** all
fit simultaneously inside the ₹8.72/L tax headroom the blend itself creates — while CBG delivers the
gas-side decarbonisation with no hidden consumer levy at all.

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

## Upstream & refining (full value chain)

The repo grew from downstream retail/ethanol into the whole India oil & gas chain:

- **`upstream/upstream_acreage_analysis.py`** — domestic crude decline (32.2→28.7 MMT, self-sufficiency
  15%→12%), basin trends (KG deepwater +338%, Barmer −48%), NELP/OALP/DSF acreage, and **ranked new
  areas to explore** (KG-basin extension, Andaman deepwater, Mahanadi/Cauvery, released 'No-Go' acreage).
- **`refining/refining_trade_analysis.py`** — India's crude-in/product-out economics: HS-27 net −$149.5 bn
  (~54% of the trade deficit, DGCIS/Tradestat); PPAC net oil bill ~$116 bn (exports offset ~28%); MS crack
  ~$24/bbl, GRMs normalised to ~$5–6; the **EU-ban/Russian-crude squeeze**; and the **petrochemical GRM
  upside** (Digital Refining: +$1.5–2/bbl marginal, COTC $60–80 vs $15–25/bbl fuels). Refer to
  Niryat/Tradestat (HS-2709/2710/2711) to drill deeper.

## Data source

PPAC *India's Oil & Gas Ready Reckoner FY 2025-26 (H1)*. Full 100-table CSV extraction of that
Ready Reckoner lives at `~/ppac-ready-reckoner-data/` (local, not committed).

---

## 🧵 Textile Import-Export Analysis (`textile_data/`)

India's textiles sector faces a **$20.4bn annual feedstock import dependency** (polymer + chemical feedstocks, FY25). Government capex pipeline ($38.5B in refinery expansion) can close 40-60% of the gap by FY30.

### Key Deliverables

| Document | Focus | Key Metric |
|----------|-------|-----------|
| **CHEMICAL_SUBSTITUTION_OPPORTUNITY.md** | 10-part policy roadmap integrating trade data + capex + government initiatives | $20.4bn deficit → 40-60% addressable by FY30 |
| **VISUALIZATIONS.md** | 6 major trend charts: import trend (FY21-25), capacity roadmap (FY25-30), segment opportunities, trade balance, government incentives, scenarios | ASCII charts + interpretation |
| **CAPEX_TIMELINE_PROJECTIONS.csv** | 8 major projects (BPCL, RIL, L&T, private, BHAVYA parks) tracked by capacity FY26/28/30 + investment + textile relevance | +5.2 MMTPA capacity by FY30 |
| **SEGMENT_FEEDSTOCK_MATRIX.csv** | 12 technical textile segments mapped to specific feedstock needs, import dependence, and addressable opportunity | Indutech $2.4bn (70% addressable) |
| **chapter_trade_fy25.csv** | FY25 baseline: 20 textile chapters from TradeStat DGCIS export-import data | Verified trade flows |

### Starting Points

1. **For Policy Teams**: Start with `CHEMICAL_SUBSTITUTION_OPPORTUNITY.md` (Parts 1-3 for problem + solution, Parts 9-10 for policy recommendations)
2. **For Industry**: Use `SEGMENT_FEEDSTOCK_MATRIX.csv` to find your segment, then review capex timeline
3. **For Visual Briefing**: `VISUALIZATIONS.md` provides 6 trend charts + scenario analysis
4. **For Technical Validation**: `TRADESTAT_HSN_QUERY_GUIDE.md` explains how to extract 8-digit HSN data for segment-level analysis

### Key Findings (FY25-FY30)

| Metric | FY25 | FY30 Addressable | Policy Anchor |
|--------|------|---|---|
| **Polymer imports (Ch 39)** | $22.1bn/yr | Reduce 70% | BPCL AP + RIL O2C |
| **Chemical imports (Ch 29)** | $26.6bn/yr | Reduce 50% | Refinery integration |
| **Total feedstock gap** | $48.7bn/yr | $40-50bn remaining (domestic + imports) | BHAVYA Rasayan parks |
| **Textile export potential** | $18.8bn | +$2-3bn from cost reduction | Packtech leadership |
| **National benefit (FY30)** | — | $8.5bn net (base case) | 40-50% import substitution |

### Government Initiatives

- **BHAVYA Rasayan**: Rs 3,030cr for 3 chemical parks (FY26-31), 25% state co-investment
- **PM Mitra Parks**: 5 sites (AP, GJ, OD, MH, TN) with infrastructure + logistics + G-Sec subsidy support
- **Refinery Capex**: $38.5bn from BPCL ($11.4B AP greenfield), RIL ($8.6B O2C), L&T ($7.5B Bina unit), private sector

### Files Structure

```
textile_data/
├── README.md                          # Segment definitions, data sources
├── TRADESTAT_HSN_QUERY_GUIDE.md       # Phase 2: HSN extraction workflow
├── VALIDATION_CHECKLIST.md            # QA framework for data validation
├── research/
│   ├── CHEMICAL_SUBSTITUTION_OPPORTUNITY.md    # Main policy analysis (10 parts)
│   ├── VISUALIZATIONS.md              # 6 trends + scenario charts
│   ├── CAPEX_TIMELINE_PROJECTIONS.csv # Project-level tracking
│   ├── SEGMENT_FEEDSTOCK_MATRIX.csv   # 12 segments × feedstock needs
│   └── visualization_data.json        # Raw data for programmatic use
├── processed/
│   └── chapter_trade_fy25.csv         # FY25 trade baseline (20 chapters)
├── raw/
│   ├── hsn_codes_12segments.xlsx      # 315 official HSN codes
│   └── tradestat_hsn_2018-26.json    # TradeStat chapter-level archive
└── analysis/
    ├── chapter_level_analysis.py      # FY25 extraction script
    └── segment_trade_extractor.py     # HSN aggregation template
```

### Ready for Use By

- 🏛️ **Government agencies**: DPIIT, Ministry of Textiles, Ministry of Petroleum
- 🏢 **Industry associations**: AIPMA, textile exporters, chemical processors
- 🗺️ **State governments**: PM Mitra site planning, BHAVYA park attracting industry
- 📊 **Researchers**: Trade policy, petrochemical integration, textile competitiveness

### Integration with Broader Platform

This textile analysis integrates with:
- **Fuel-to-fibre loop**: Ethanol displacement → freed naphtha → polymer feedstock (petrol demand forecast)
- **Refining economics**: Petrochemical GRM upside, crude processing trends (refining_trade_analysis.py)
- **Global markets**: European textile imports, US competitiveness, China trade patterns

---

**Textile Data Last Updated**: 2026-07-27 (FY25 TradeStat, Cabinet-approved policy, industry announcements 2025-26)  
**Repository Status**: PUBLIC, All analysis reproducible and source-linked

<!-- 
DATA LIBRARY LINK - Add this section to every repo README.md
This snippet provides discovery and documentation links.
-->

## 📊 Data Discovery

This repository is part of the **Global Data Library** — a unified catalog of 10,528 datasets across 40+ repositories.

### Quick Links

- **[Global Data Library README](.ruflo/DATA_LIBRARY_README.md)** — Full catalog, search API, and usage examples
- **[Data Library Python Interface](.ruflo/data-library/data_library.py)** — Query datasets programmatically
- **[Repository Scanner](.ruflo/data-library/repo_scanner.py)** — Reindex all repos to update the catalog

### Datasets in This Repository

The data catalog automatically inventories all datasets in this repo. To find your data:

```python
from data_library import DataLibrary

lib = DataLibrary()

# Search this repo's datasets
results = lib.search("", source="<repo-name>")

# Get dataset details
dataset = lib.get("<dataset_id>")
print(f"Rows: {dataset['row_count']}")
print(f"Freshness: {dataset['freshness_hours']} hours old")
print(f"Storage: {dataset['storage_tier']}")
```

### Browse the Full Catalog

**Market Coverage** (5 markets, 21,279 symbols):
- India (NSE/BSE): 2,364 instruments
- US (NASDAQ/NYSE): 7,442 instruments
- Europe (17 exchanges): 1,214 instruments
- Japan (TSE): 3,709 instruments
- Korea (KRX): 2,768 instruments

**Government Sources** (30+ ministries):
- MOSPI: 25 datasets (GDP, CPI, trade, agri, power)
- SEBI: 151,928 XBRL results + IPO pipeline
- PIB: 25+ ministry announcements
- DGFT: India trade data (monthly)
- Agmarknet: 300+ mandi prices (daily)
- NSE/MCX: Real-time derivatives chains

See [Global Data Library README](.ruflo/DATA_LIBRARY_README.md) for complete documentation.

### Finding Data Across All Repos

```python
# Find India OHLCV data (might be in multiple repos)
lib.search("india ohlcv", market="india")

# Get the fastest/freshest version
optimal = lib.get_optimal("india ohlcv", latency="<100ms", freshness="<1day")
# Returns: {"storage_tier": "cassandra", "path": "..."}

# Check data gaps
gaps = lib.gaps("india", date_from="2026-01-01")

# See which collectors are stale
status = lib.collectors_status()
```

---
