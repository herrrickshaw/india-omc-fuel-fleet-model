# Energy density, blending dilution, and who profits per extra litre

Companion to `omc_model.py` (OMC income) and `statewise_tax_impact.py` (tax
differential). This note isolates the **volume effect**: lower-energy blends
make vehicles buy more litres for the same km, and every per-litre levy
(excise, effective VAT, dealer commission, OMC margin) scales with litres.

## 1. Energy content of the fuels themselves (LHV)

| Fuel | MJ/kg | MJ/litre | Sold by | vs its base |
|---|---|---|---|---|
| Petrol (E0) | 43.4 | 32.1 | litre | — |
| Ethanol | 26.8 | 21.1 | litre | -34% |
| Isobutanol | 33.1 | 26.5 | litre | -17% |
| Diesel (B0) | 43.0 | 35.7 | litre | — |
| Biodiesel (FAME) | 37.2 | 32.7 | litre | -8% |
| HVO renewable diesel | 44.0 | 34.3 | litre | -4% |
| CNG (pipeline gas) | 47.5 | n/a (gas) | kg | — |
| CBG (IS 16087) | 46.5 | n/a (gas) | kg | -2% |
| Pure methane | 50.0 | n/a (gas) | kg | +5% |

Ethanol carries **34% less energy per litre** than petrol; isobutanol only ~17% less (denser, less oxygen). FAME biodiesel is ~8% below diesel. **CBG at IS 16087 spec is at or near CNG parity per kg** — pure methane is actually *above* typical pipeline CNG.

## 2. Blend energy dilution → extra litres for the same distance

| Blend | MJ/L | Energy vs base | Extra litres needed (energy basis) | Real-world mileage drop |
|---|---|---|---|---|
| E10 | 31.02 | −3.42% | +3.54% | — |
| E20 | 29.92 | −6.83% | +7.33% | 4% (SIAM/ARAI central) |
| E25 | 29.37 | −8.54% | +9.34% | 6% (SIAM/ARAI central) |
| E30 | 28.82 | −10.25% | +11.42% | 7% (SIAM/ARAI central) |
| IB16 (isobutanol) | 31.22 | −2.77% | +2.85% | — |
| IB24 (isobutanol) | 30.78 | −4.16% | +4.34% | — |
| B7  (biodiesel) | 35.48 | −0.58% | +0.58% | — |
| B20 (biodiesel) | 35.1 | −1.66% | +1.68% | — |

**CBG blended into CNG: 0% dilution.** CNG/CBG is retailed per kg, and CBG's energy per kg matches or exceeds pipeline gas — a bus fleet co-fuelled on CBG buys the *same* kg for the same km. There is no volumetric pass-through to harvest.

## 3. Per-vehicle: what the dilution costs a petrol owner

Hatchback, 20 km/L on E0, 10,000 km/yr, pump ₹105/L (pump price per litre is the SAME for E0 and E20 — the energy cut is invisible on the price board):

| Blend | Extra litres/yr | Extra ₹/yr | Effective hidden levy |
|---|---|---|---|
| E20 | +21 L | ₹2,188 | 4.2% on every km driven |
| E25 | +29 L | ₹3,056 | 5.8% on every km driven |
| E30 | +38 L | ₹3,952 | 7.5% on every km driven |

## 4. National petrol pool: where the extra litres' money goes (₹ cr/yr)

Base: FY24-25 petrol pool 54.1 bn L (40 MMT). Distance demand held constant at its E0-equivalent; each blend's real-world drop pulls extra litres through 99,281 retail outlets.

| Blend | Extra bn L | Consumer pays | Central excise | State VAT | Dealer commission | OMC margin |
|---|---|---|---|---|---|---|
| E20 | 2.16 | 22,703 | 4,303 | 4,216 | 886 | 757 |
| E25 | 3.02 | 31,712 | 6,010 | 5,889 | 1,238 | 1,057 |
| E30 | 3.91 | 41,011 | 7,773 | 7,616 | 1,601 | 1,367 |
| IB16 (energy-basis) | 1.49 | 15,696 | 2,975 | 2,915 | 613 | 523 |
| IB24 (energy-basis) | 2.22 | 23,295 | 4,415 | 4,326 | 910 | 776 |

Every rupee column is a *per-litre* levy × extra litres: the volume effect alone hands the exchequer ~₹8,500 cr/yr at E20 (excise+VAT) and retail outlets ~₹900 cr/yr in commission — rising with the blend walk to E30. The OMC-margin column reconciles with omc_model.py's ₹757 cr E20 figure.

## 5. The CBG contrast

- **Petrol+ethanol**: energy dilution is real, pump price/litre unchanged → consumer silently buys ~4% more litres; every per-litre stakeholder (centre, state, dealer, OMC) collects on the extra volume.
- **Diesel+FAME (B7)**: same mechanism but small (−0.6% energy) — largely noise.
- **CNG+CBG**: sold per **kg** at methane-grade energy. Substituting CBG for natural gas changes the *sourcing* (domestic waste vs imported LNG) without changing kg bought per km. As a decarbonisation lever it delivers the import substitution WITHOUT the hidden consumer levy — the fiscally honest blend.

## 6. Caveats

- Real-world E20 drop (4%) is below the pure energy math (6.8%): calibrated engines recover part of it via octane/combustion gains; older vehicles can lose up to ~12% (SIAM band 2-6% for compliant engines).
- Excise ₹19.90/L and VAT-on-₹78 base are the same levers as statewise_tax_impact.py; that script covers the *tax-differential* on the displaced petrol (states LOSE VAT on the ethanol fraction) — the two effects are additive but distinct: states lose on substitution, everyone gains on volume.
- Isobutanol rows are energy-basis only (no India fleet trial data); its appeal is precisely the smaller dilution per unit of renewable content.
- CBG range 45-48.5 MJ/kg depends on purification; IS 16087 floor (CH4 90%) sits marginally below rich pipeline gas, well-purified CBG above it.
