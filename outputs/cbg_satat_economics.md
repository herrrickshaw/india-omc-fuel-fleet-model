# CBG economics under SATAT pricing — benchmarked against ethanol blending

Mileage anchor: SIAM/ARAI BS-VI FE declarations (303 models, vehicle_fuel_mileage repo): petrol 16.67 kmpl, diesel 17.91 kmpl, CNG 27.40 km/kg; the same nameplate travels **+40.3% further per unit** on CNG than on petrol.

## 1. What a megajoule of energy costs to procure

| Source | ₹/MJ | Basis |
|---|---|---|
| Petrol (refinery/trade parity) | 1.81 | Rs58/L |
| Ethanol (OMC procurement) | 2.94 | Rs62/L |
| Domestic APM gas | 0.51 | ~Rs24/kg eq |
| Imported spot RLNG | 0.94 | ~Rs45/kg eq |
| CBG (SATAT assured) | 1.16 | Rs54/kg ex-plant |

- Ethanol's renewable premium over the petrol it displaces: **+63% per MJ** (₹2.94 vs ₹1.81) — *before* the mileage-dilution levy on the consumer.
- CBG's premium over the spot RLNG it displaces: **+23% per MJ** (₹1.16 vs ₹0.94) — and it *undercuts* imported gas whenever spot LNG runs above ~$14.8/MMBtu. Against domestic APM gas CBG is dearer (₹0.51/MJ), but APM supply is static; imports are the margin.
- Per MJ of renewable energy bought, SATAT CBG costs ₹1.16 vs ethanol's ₹2.94 — **2.5× cheaper**, with no volumetric side effects.

## 2. Cost per km on SIAM/ARAI declared FE (Delhi prices)

| Fuel | ₹/km | Mileage basis |
|---|---|---|
| Petrol E0 | 6.30 | 16.67 kmpl (SIAM decl.) |
| Petrol E20 | 6.56 | E20 real-world -4% |
| Petrol E30 | 6.77 | E30 real-world -7% |
| Diesel B0 | 5.14 | 17.91 kmpl (SIAM decl.) |
| Diesel B20 | 5.23 | B20 energy-basis -1.7% |
| CNG | 2.74 | 27.40 km/kg (SIAM decl.) |
| CBG (any % in CNG stream) | 2.80 | energy-scaled 46.5/47.5 MJ/kg |

CNG runs at ~43% of petrol's cost per km (the +40.3% same-nameplate distance uplift compounding the per-unit price gap). The blend walk moves petrol the WRONG way (E0 ₹6.30 → E30 ₹6.77/km) while CBG blending leaves the CNG ₹/km essentially untouched — at the IS 16087 floor the 100%-CBG penalty is 2.1%, and at CBO shares it rounds to zero.

## 3. CBG Blending Obligation: national cost, zero consumer levy

CNG(T) pool 6.67 MMT/yr (RR Table 3.7). SATAT ₹54/kg + 5% GST vs spot RLNG ~₹45/kg as the displaced marginal gas:

| CBO share | CBG needed (tonnes/yr) | Procurement (₹ cr/yr) | Pump-price delta | Mileage delta |
|---|---|---|---|---|
| 1% | 66,700 | 378 | +₹0.12/kg | −0.02% |
| 5% | 333,500 | 1,891 | +₹0.59/kg | −0.11% |

Even the 5% obligation carries a pump impact of ~₹0.59/kg (~0.8% of the CNG price) and a mileage effect of ~0.1% — against E20's silent 4% mileage cut and ₹22,700 cr/yr volume dividend. The CBG subsidy, where needed, sits **on-budget and ex-plant** (SATAT assurance, GOBARdhan capex support, FOM/LFOM fertiliser offtake under FCO Schedule VIII) instead of hidden in the fuel gauge.

## 4. Caveats

- SIAM/ARAI FE figures are type-approval, not real-world; the analysis leans on *relative* gaps (petrol vs CNG vs diesel), which the same-nameplate pairs anchor.
- SATAT ₹54/kg is the assured floor; market CBG deals near CGD city-gate parity can price higher. RLNG comparator swings with spot LNG ($12/MMBtu here).
- CBG production cost varies by feedstock (press-mud cheapest, agri-residue dearest); ₹54/kg does not guarantee plant viability without the fertiliser and carbon-credit legs — see the GOBARdhan/FOM work in the digital-twin repo.
- CBO shares apply to CGD gas incl. PNG(D); using the CNG(T) pool alone keeps the comparison transport-to-transport.
