# India petrol-demand & ethanol-requirement forecast (FY26–FY31)

Growth anchored on the **PPAC/literature trend** (RR: MS decadal CAGR **7.1%**, recent H1 +6.8–7.1%) and shaped by **FADA vehicle-sales signals**: two-wheelers (~72% of sales, still ~93% petrol) keep demand rising, while a climbing EV share (FADA FY26: 6.5% of 2W, 4.25% of PV, 8.5% overall) drags the growth rate down over time. Base petrol FY24-25 = 40.0 MMT (RR Table 6.1). Ethanol need follows a blend roadmap E20→E30 (Brazil-style E27 waypoint).

## 1. Petrol (MS) demand forecast — MMT

| Scenario | FY25-26 | FY26-27 | FY27-28 | FY28-29 | FY29-30 | FY30-31 | CAGR |
|---|--:|--:|--:|--:|--:|--:|--:|
| High (7% trend) | 42.8 | 45.8 | 49.0 | 52.4 | 56.1 | 60.0 | 7.0% |
| Base (FADA-moderating) | 42.6 | 45.1 | 47.5 | 49.7 | 51.8 | 53.6 | 5.0% |
| Low (fast-EV, 3%) | 41.2 | 42.4 | 43.7 | 45.0 | 46.4 | 47.8 | 3.0% |

- **Base case:** petrol rises **40 → 54 MMT** by FY30-31 (72 bn L) — a ~5.0% CAGR, the 7% trend bending down as EVs scale. High (EV stays niche) reaches 60 MMT; Low (fast-EV) 48 MMT.

## 2. Ethanol requirement — blend roadmap × petrol demand (crore litres/yr)

| Scenario | FY25-26<br>20% | FY26-27<br>22% | FY27-28<br>25% | FY28-29<br>27% | FY29-30<br>30% | FY30-31<br>30% |
|---|--:|--:|--:|--:|--:|--:|
| High (7% trend) | 1,157 | 1,362 | 1,655 | 1,913 | 2,274 | 2,434 |
| Base (FADA-moderating) | 1,151 | 1,341 | 1,605 | 1,815 | 2,099 | 2,173 |
| Low (fast-EV, 3%) | 1,114 | 1,262 | 1,477 | 1,643 | 1,880 | 1,936 |

- **Base case ethanol need nearly doubles: ~1,151 cr L (E20, FY26) → ~2,173 cr L (E30, FY31).**
- India's fuel-ethanol capacity is ~1,600 cr L (2024-25). E20 today fits, but hitting **E30 on a growing petrol base needs ~2,173 cr L — about 36% above current capacity**. The binding constraint on the blend roadmap is ethanol supply, not petrol demand.

## 3. Capacity gap (base case, ₹ / cr L)

| FY | Blend | Petrol (MMT) | Ethanol needed (cr L) | vs capacity (~1600 cr L) |
|---|--:|--:|--:|--:|
| FY25-26 | 20% | 42.6 | 1,151 | 449 headroom |
| FY26-27 | 22% | 45.1 | 1,341 | 259 headroom |
| FY27-28 | 25% | 47.5 | 1,605 | +5 over |
| FY28-29 | 27% | 49.7 | 1,815 | +215 over |
| FY29-30 | 30% | 51.8 | 2,099 | +499 over |
| FY30-31 | 30% | 53.6 | 2,173 | +573 over |

## 4. What this scales across the rest of the model

Every ethanol-linked flow in this repo scales with the forecast. At the **base FY30-31 (E30, 54 MMT petrol)**, versus today's E20:

- Ethanol displacing petrol ≈ **21.7 bn L** (freed for export ≈ 16 MMT, ~₹100,153 cr export forex).
- State VAT foregone ≈ ₹39,105 cr; central excise foregone ≈ ₹43,233 cr; a 5% ethanol SGST would yield ≈ ₹6,518 cr for states.

## 5. Caveats

- Growth scenarios anchor on RR's 7.1% decadal CAGR; the base *bend-down* is a judgement on FADA's EV-share trajectory, not a fitted fleet model — see `fleet_from_fuel.py` for the bottom-up cross-check. Rates are editable.
- Blend roadmap (E20→E30 by FY30) is an assumed policy path per NBP direction + Brazil's E27 precedent, not a notified schedule.
- Ethanol capacity (~1,600 cr L) is an approximate 2024-25 figure; feedstock (molasses/grain) availability, not just plant capacity, is the real limit. 1 bn L = 100 cr L; petrol density 0.74.

---
*Forecast from PPAC/FADA-anchored trends + editable assumptions; not an official demand projection.*
