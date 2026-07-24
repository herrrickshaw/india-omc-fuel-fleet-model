# Actively-driven fleet, implied from fuel burn (PPAC) — petrol, diesel, CNG + EV

Method: for each sector, **active vehicles = annual fuel ÷ (km/day × active-days ÷ mileage)**. Fuel totals are PPAC FY24-25 (petrol 40.0 MMT = 54.1 bn L; diesel 91.4 MMT = 110.1 bn L; CNG 6.67 MMT = 6.67 bn kg, RR Table 3.7). Sector shares (Nielsen/PPAC study) and daily-usage are editable. Non-road diesel (farm/rail/industry) is separated out. EVs burn no fuel, so they are estimated from Vahan registrations × an 85% active-rate.

## 1. Segment build-up

| Fuel | Sector | % of fuel | Fuel (bn L/kg) | km/day | mileage | per-veh/day | per-veh/yr | Active vehicles |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| Petrol | Two-wheeler | 61.4% | 33.2 | 28 | 48 | 0.58 | 192 | 172,467,532 |
| Petrol | Car | 34.3% | 18.56 | 30 | 15 | 2.0 | 600 | 30,927,928 |
| Petrol | Three-wheeler | 2.3% | 1.26 | 60 | 30 | 2.0 | 600 | 2,108,108 |
| Petrol | Other (gensets/misc) | 1.9% | 1.03 |  |  |  |  | (non-road) |
| Diesel | Truck / LCV (freight) | 28.2% | 31.11 | 220 | 6.0 | 36.67 | 12100 | 2,570,995 |
| Diesel | Bus | 9.6% | 10.52 | 200 | 4.5 | 44.44 | 15111 | 695,945 |
| Diesel | Car / UV / taxi | 28.5% | 31.36 | 90 | 16.0 | 5.62 | 1744 | 17,985,556 |
| Diesel | Three-wheeler | 3.3% | 3.63 | 90 | 22.0 | 4.09 | 1268 | 2,865,501 |
| Diesel | Railways | 3.2% | 3.57 |  |  |  |  | (non-road) |
| Diesel | Agriculture (tractor/pump) | 13.0% | 14.32 |  |  |  |  | (non-road) |
| Diesel | Industry / gensets | 14.2% | 15.62 |  |  |  |  | (non-road) |
| CNG | Car (incl. bi-fuel) | 38.0% | 2.53 | 40 | 25.0 | 1.6 | 480 | 5,280,417 |
| CNG | Three-wheeler | 25.0% | 1.67 | 90 | 30.0 | 3.0 | 930 | 1,793,011 |
| CNG | Bus | 22.0% | 1.47 | 200 | 3.8 | 52.63 | 17895 | 82,002 |
| CNG | LCV / truck | 15.0% | 1.0 | 140 | 4.5 | 31.11 | 10267 | 97,451 |
| EV | Electric (registration-based) | — | — | — | — | — | — | 8,318,046 |

## 2. Implied actively-driven fleet

| Energy type | Active vehicles | Method |
|---|--:|---|
| Petrol + diesel (road) | 229,621,565 | fuel balance |
| CNG | 7,252,881 | fuel balance |
| Electric (BEV/e-3W) | 8,318,046 | Vahan reg × 85% active |
| **Total actively-driven** | **245,192,492** (~24.5 cr) | |

- Liquid-fuel road burn 129.6 bn L/yr; non-road diesel (farm/rail/industry) 34.5 bn L excluded. Avg **1.55 L/day per active liquid-fuel vehicle**.
- ⚠️ **Bi-fuel overlap:** petrol/CNG cars burn both fuels, so the CNG 'Car' line partly double-counts vehicles already in the petrol 'Car' line — the true *distinct* headcount is modestly below the raw sum. Read the total as ~24–25 crore.

## 3. Sensitivity — ±20% on two-wheeler daily usage

2-wheelers dominate the count, so their assumed daily-km is the biggest swing factor. Holding fuel fixed, higher usage per 2W ⇒ fewer active 2W (each burns more):

| Scenario | Total actively-driven | ~crore |
|---|--:|--:|
| 2W usage −20% (22.4 km/day) | 288,309,375 | 28.8 |
| 2W usage base (28 km/day) | 245,192,492 | 24.5 |
| 2W usage +20% (33.6 km/day) | 216,447,903 | 21.6 |

**Band: ~22–29 crore actively-driven vehicles** (central ~25 cr).

## 4. Reality check vs Vahan registrations

| Basis | Vehicles | vs implied-active |
|---|--:|--:|
| Implied actively-driven (this model) | 245,192,492 | 1.00× |
| MoRTH-style live parc (illustrative) | 350,000,000 | 1.43× |
| Vahan cumulative 'Till Today' | 446,191,165 | 1.82× |

Fuel burn + EV registrations imply **~25 crore vehicles are driven with any regularity** — roughly **55% of the 45-crore cumulative registration count**. The chain: cumulative registered 45 cr → live parc ~35 cr → actively-driven ~25 cr. The gap is scrapped/dead/seasonal vehicles Vahan never removes.

## 5. Caveats

- **Sector split is the main uncertainty**: Nielsen shares are 2013-vintage (diesel cars have since collapsed); per-segment counts are order-of-magnitude, the aggregate more robust.
- **Bi-fuel double-count** (petrol/CNG) inflates the raw sum slightly — see §2.
- EV row is registration-based (no fuel proxy); e-rickshaws in ELECTRIC(BOV) have high churn, so the active-rate is a lever.
- 'Active' = driven enough to appear in annual fuel, not a legal-status count.

---
*Fuel-balance + registration estimate; editable assumptions; not an official census.*
