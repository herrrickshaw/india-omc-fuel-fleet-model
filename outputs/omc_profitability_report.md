# OMC Retail Profitability Model — petrol & diesel, with E20/E25/E30 ethanol effect

Inputs from PPAC *Oil & Gas Ready Reckoner FY 2025-26 (H1)*; margins and mileage-drop factors are editable levers in `omc_model.py`. Volumes anchored on Table 6.1 national consumption. **Illustrative — OMC marketing margins are not published cleanly and swing with crude; treat absolute ₹ as order-of-magnitude, and the ethanol *deltas* (which are margin-independent in %) as the robust result.**

## 1. Base retail book (FY 2024-25 actual)

| Item | Petrol (MS) | Diesel (HSD) |
|---|--:|--:|
| National consumption (MMT) | 40.0 | 91.4 |
| Volume (bn litres) | 54.1 | 110.1 |
| OMC marketing margin (₹/L, lever) | 3.5 | 2.5 |
| **OMC retail gross margin (₹ cr/yr)** | **18,919** | **27,530** |

Retail outlets (01.10.2025): **99,281** (PSU 90,022 + private 9,259). True avg throughput per RO: petrol **45 KL/month**, diesel **92 KL/month**.

**Total OMC retail marketing gross ≈ ₹46,449 crore/yr.**

> Network dilution: outlets grew +8.0% (91,949→99,281) while fuel demand grew ~3-7%, so PPAC's per-RO throughput (Table 6.4D) is *falling* YoY — more pumps splitting similar volume, squeezing per-outlet economics even as the OMC total rises.

## 2. Ethanol-blending scenarios (petrol only; same distance driven)

Ethanol cuts mileage, so more blended litres flow through the pump for the same distance — extra throughput the OMC earns margin on. Higher blends amplify it. Ethanol also *displaces* pure petrol (import substitution), shown separately.

| Scenario | Blend % | Mileage drop | Blend vol (bn L) | of which petrol | of which ethanol | Extra vs E0 (bn L) | **Extra OMC pump income (₹ cr/yr)** |
|---|--:|--:|--:|--:|--:|--:|--:|
| E0 | 0% | 0.0% | 51.9 | 51.9 | 0.0 | 0.00 | **0** |
| E20 | 20% | 4.0% | 54.1 | 43.2 | 10.8 | 2.16 | **757** |
| E25 | 25% | 5.5% | 54.9 | 41.2 | 13.7 | 3.02 | **1,057** |
| E30 | 30% | 7.0% | 55.8 | 39.1 | 16.7 | 3.91 | **1,367** |

- Going **E20→E25** adds ~₹300 cr/yr of extra pump throughput income; **E20→E30** adds ~₹610 cr/yr.
- But pure petrol (MS) sold *falls* 43.2→39.1 bn L as ethanol content rises 10.8→16.7 bn L — the import-substitution the blending programme is really for.

## 3. Fuel-pool MIX scenarios (E0 / E20 / E25 / E30 in a ratio)

The petrol pool does not jump uniformly to one blend — a share sits at E0 (legacy 2W, premium grades, ethanol-supply-short pockets), a share at E20, and E25/E30 roll in. Each row below is a volume-share mix; OMC pump income is the blend-weighted throughput × margin. Same underlying distance driven across all rows.

| Mix scenario | E0 | E20 | E25 | E30 | Wtd drop | Blend vol (bn L) | Petrol MS (bn L) | Ethanol (bn L) | OMC petrol income (₹ cr) | Extra vs all-E0 (₹ cr) |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| S0 Today (~E20) | 5% | 95% | 0% | 0% | 3.8% | 53.9 | 43.7 | 10.3 | 18,881 | 719 |
| S1 E20 universal | 0% | 100% | 0% | 0% | 4.0% | 54.1 | 43.2 | 10.8 | 18,919 | 757 |
| S2 Transition FY27 | 5% | 55% | 35% | 5% | 4.5% | 54.3 | 42.7 | 11.6 | 19,017 | 855 |
| S3 E25 majority FY28 | 5% | 20% | 60% | 15% | 5.2% | 54.7 | 41.8 | 12.9 | 19,153 | 991 |
| S4 E30 push FY30 | 5% | 10% | 25% | 60% | 6.0% | 55.2 | 40.6 | 14.6 | 19,322 | 1,160 |

Shifting the pool from **S0 Today (~E20)** to **S4 E30 push FY30** lifts OMC petrol throughput income ₹18,881→₹19,322 cr (+₹441 cr) purely from the mileage penalty, while pure-petrol volume falls 43.7→40.6 bn L and ethanol offtake rises 10.3→14.6 bn L.

## 4. Caveat — CBG blended into CNG does NOT behave like ethanol

The mileage-drop → extra-throughput mechanism above is **specific to ethanol-in-petrol**, because ethanol carries ~34% less energy per litre than petrol, so a blended litre drives fewer km and more litres are dispensed. **Compressed Bio-Gas (CBG) cascaded into the CNG grid does not do this**, for a quality-standard reason:

- CBG for automotive use / grid injection must meet **IS 16087** (Bio-CNG / bio-methane specification) — minimum **~90% methane**, tight caps on CO₂, moisture and H₂S. *(The "IS 1876" in the request appears to be shorthand for IS 16087; the fossil-CNG automotive spec it is matched against is **IS 15958**.)*

- Because IS 16087 forces CBG's methane content — and hence its **calorific value / Wobbe index** — to match pipeline/fossil CNG (IS 15958), CBG is *fungible* with CNG. A CNG vehicle running on a CBG-blended stream sees **no meaningful mileage change** (km/kg is preserved), unlike the petrol vehicle on E20+.

- **Consequence for this model:** there is **no CBG-driven throughput uplift** for the CNG book analogous to the ethanol effect. The OMC/CGD gain from CBG is instead in *procurement and policy* terms — SATAT assured-price offtake, GST/green-fuel treatment and import substitution of LNG — **not** extra kg dispensed. So the ethanol income lift is a petrol-pool phenomenon only; the CNG/CBG pool should not be credited with the same mechanism.

## 5. Year-on-year projection (vehicle demand + blend roadmap)

Petrol/diesel demand compounds with vehicle-sales-driven growth (MS +7%, HSD +3%/yr); blend steps E20→E25→E30 per an editable roadmap; outlets +4%/yr.

| FY | Blend | Outlets | Petrol blend (bn L) | Diesel (bn L) | OMC income (₹ cr) | YoY Δ (₹ cr) | of which ethanol (₹ cr) |
|---|---|--:|--:|--:|--:|--:|--:|
| FY25-26 | E20 | 99,281 | 54.05 | 110.12 | 46,449 | — | 757 |
| FY26-27 | E20 | 103,749 | 57.89 | 113.31 | 48,591 | 2,142 | 810 |
| FY27-28 | E25 | 108,417 | 62.99 | 116.6 | 51,195 | 2,605 | 1,212 |
| FY28-29 | E25 | 113,296 | 67.46 | 119.98 | 53,606 | 2,411 | 1,299 |
| FY29-30 | E30 | 118,394 | 73.41 | 123.46 | 56,560 | 2,954 | 1,799 |

---
*Generated by `omc_model.py`. Illustrative analytical estimates, not investment advice. OMC marketing margin is the key editable assumption.*