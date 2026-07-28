#!/usr/bin/env python3
"""Energy comparison across fuels & blending options — the volumetric-dilution
effect and who profits from it.

Thesis being tested: blending LOWER-energy-dense oxygenates (ethanol,
isobutanol) into petrol/diesel cuts km-per-litre, so the same distance driven
pulls MORE litres through the pump. Since central excise, dealer commission
and OMC marketing margin are all PER-LITRE (and state VAT is per-litre in
effect, being ad valorem on a per-litre price), every extra litre mechanically
raises tax collection and retail-outlet income — paid by the consumer at an
unchanged pump price per litre. Compressed biogas (CBG), by contrast, is
purified to near-CNG methane content and is SOLD PER KG at CNG-equivalent
energy, so blending it into the CNG stream carries no such hidden dilution.

Anchors shared with omc_model.py / statewise_tax_impact.py:
  MS pool 40 MMT (54.05 bn L) FY24-25, density 0.74; OMC margin Rs3.5/L;
  dealer commission Rs4.1/L (RR 8.10); excise Rs19.90/L petrol; VAT ~25%
  on Rs78/L pre-VAT base. E20 real-world mileage drop 4% (SIAM 2-6% band).

Pure stdlib. Outputs: outputs/energy_blend_comparison.md + two CSVs.
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)
CR = 1e7

# ────────────────────────────────────────────────────────────────────────────
# 1. FUEL ENERGY TABLE  (lower heating values — the work a litre/kg can do)
# ────────────────────────────────────────────────────────────────────────────
# name -> (LHV MJ/kg, density kg/L at 15C, sold-by unit, note)
FUELS = {
    "Petrol (E0)":        (43.4, 0.740, "litre", "reference gasoline"),
    "Ethanol":            (26.8, 0.789, "litre", "anhydrous fuel ethanol"),
    "Isobutanol":         (33.1, 0.802, "litre", "bio-isobutanol drop-in oxygenate"),
    "Diesel (B0)":        (43.0, 0.830, "litre", "reference HSD"),
    "Biodiesel (FAME)":   (37.2, 0.880, "litre", "fatty-acid methyl ester"),
    "HVO renewable diesel": (44.0, 0.780, "litre", "hydrotreated veg oil, drop-in"),
    "CNG (pipeline gas)": (47.5, None,  "kg",    "~90% CH4 + ethane, sold per kg"),
    "CBG (IS 16087)":     (46.5, None,  "kg",    "purified biogas, CH4 >=90% (range 45-48.5)"),
    "Pure methane":       (50.0, None,  "kg",    "upper bound for CBG at full purification"),
}

def mj_per_litre(name):
    lhv, dens, unit, _ = FUELS[name]
    return lhv * dens if dens else None

E_PETROL = mj_per_litre("Petrol (E0)")     # ~32.1 MJ/L
E_ETH    = mj_per_litre("Ethanol")         # ~21.1 MJ/L
E_IBU    = mj_per_litre("Isobutanol")      # ~26.5 MJ/L
E_DIESEL = mj_per_litre("Diesel (B0)")     # ~35.7 MJ/L
E_FAME   = mj_per_litre("Biodiesel (FAME)")# ~32.7 MJ/L

# ────────────────────────────────────────────────────────────────────────────
# 2. BLENDS — volumetric energy dilution vs base fuel
# ────────────────────────────────────────────────────────────────────────────
# label -> (base MJ/L, blendstock MJ/L, vol fraction, base fuel name)
BLENDS = [
    ("E10",  E_PETROL, E_ETH, 0.10, "petrol"),
    ("E20",  E_PETROL, E_ETH, 0.20, "petrol"),
    ("E25",  E_PETROL, E_ETH, 0.25, "petrol"),
    ("E30",  E_PETROL, E_ETH, 0.30, "petrol"),
    ("IB16 (isobutanol)", E_PETROL, E_IBU, 0.16, "petrol"),
    ("IB24 (isobutanol)", E_PETROL, E_IBU, 0.24, "petrol"),
    ("B7  (biodiesel)",  E_DIESEL, E_FAME, 0.07, "diesel"),
    ("B20 (biodiesel)",  E_DIESEL, E_FAME, 0.20, "diesel"),
]

def blend_row(label, e_base, e_blk, frac, base):
    e_mix = e_base * (1 - frac) + e_blk * frac
    energy_drop = 1 - e_mix / e_base            # theoretical km/L loss at equal efficiency
    extra_vol   = 1 / (1 - energy_drop) - 1     # extra litres for the same km
    return {"blend": label, "base": base, "mj_per_l": round(e_mix, 2),
            "energy_drop_pct": round(energy_drop * 100, 2),
            "extra_litres_pct": round(extra_vol * 100, 2)}

blend_rows = [blend_row(*b) for b in BLENDS]

# Real-world central figures (SIAM/ARAI) where they exist — engines partly
# recover octane/oxygenate effects, so real drop < pure energy math at E20.
REAL_WORLD = {"E20": 0.040, "E25": 0.055, "E30": 0.070}   # same levers as omc_model.py

# ────────────────────────────────────────────────────────────────────────────
# 3. NATIONAL VOLUME → RUPEE ARITHMETIC (petrol pool, FY24-25 basis)
# ────────────────────────────────────────────────────────────────────────────
MS_BLENDED_BNL = 40.0 * 1e6 / 0.74 / 1e6 / 1000 * 1e3   # 40 MMT -> 54.05 bn L
PUMP_PRICE   = 105.0    # Rs/L indicative pan-India petrol
EXCISE       = 19.90    # Rs/L central excise (statewise_tax_impact.py basis)
VAT_PER_L    = 0.25 * 78.0   # ~Rs19.5/L effective state VAT (25% on Rs78 pre-VAT base)
DEALER_COMM  = 4.1      # Rs/L dealer commission (RR 8.10)
OMC_MARGIN   = 3.5      # Rs/L OMC marketing margin (omc_model.py lever)

def national(blend, drop):
    """Extra litres pulled through pumps vs an E0 pool delivering the SAME km."""
    # today's dispensed pool is E20; every blend serves the same distance-demand,
    # i.e. L0 fixed at the E0-equivalent of today's pool.
    l0 = MS_BLENDED_BNL * (1 - REAL_WORLD["E20"])
    litres = l0 / (1 - drop)
    extra  = litres - l0
    e = extra * 1e9
    return {"blend": blend, "mileage_drop_pct": drop * 100,
            "pool_bnL": round(litres, 2), "extra_bnL": round(extra, 2),
            "consumer_extra_cr": round(e * PUMP_PRICE / CR),
            "excise_extra_cr": round(e * EXCISE / CR),
            "vat_extra_cr": round(e * VAT_PER_L / CR),
            "dealer_extra_cr": round(e * DEALER_COMM / CR),
            "omc_extra_cr": round(e * OMC_MARGIN / CR)}

nat_rows = [national(b, d) for b, d in [("E20", 0.040), ("E25", 0.055), ("E30", 0.070),
                                        ("IB16 (energy-basis)", 0.028), ("IB24 (energy-basis)", 0.041)]]

# Per-vehicle: hatchback 20 km/L on E0, 10,000 km/yr
KMPL_E0, KM_YR = 20.0, 10_000
def per_vehicle(drop):
    litres_e0 = KM_YR / KMPL_E0
    litres_bl = KM_YR / (KMPL_E0 * (1 - drop))
    return litres_bl - litres_e0, (litres_bl - litres_e0) * PUMP_PRICE

# ────────────────────────────────────────────────────────────────────────────
# 4. REPORT
# ────────────────────────────────────────────────────────────────────────────
L = ["# Energy density, blending dilution, and who profits per extra litre\n",
     "Companion to `omc_model.py` (OMC income) and `statewise_tax_impact.py` (tax\n"
     "differential). This note isolates the **volume effect**: lower-energy blends\n"
     "make vehicles buy more litres for the same km, and every per-litre levy\n"
     "(excise, effective VAT, dealer commission, OMC margin) scales with litres.\n"]

L.append("## 1. Energy content of the fuels themselves (LHV)\n")
L.append("| Fuel | MJ/kg | MJ/litre | Sold by | vs its base |")
L.append("|---|---|---|---|---|")
base_of = {"Ethanol": E_PETROL, "Isobutanol": E_PETROL, "Biodiesel (FAME)": E_DIESEL,
           "HVO renewable diesel": E_DIESEL, "CBG (IS 16087)": 47.5, "Pure methane": 47.5}
for name, (lhv, dens, unit, note) in FUELS.items():
    epl = f"{lhv*dens:.1f}" if dens else "n/a (gas)"
    if name in base_of:
        ref = base_of[name]
        val = (lhv * dens) if dens else lhv
        rel = f"{(val/ref-1)*100:+.0f}%"
    else:
        rel = "—"
    L.append(f"| {name} | {lhv:.1f} | {epl} | {unit} | {rel} |")
L.append("\nEthanol carries **34% less energy per litre** than petrol; isobutanol only "
         "~17% less (denser, less oxygen). FAME biodiesel is ~8% below diesel. "
         "**CBG at IS 16087 spec is at or near CNG parity per kg** — pure methane is "
         "actually *above* typical pipeline CNG.\n")

L.append("## 2. Blend energy dilution → extra litres for the same distance\n")
L.append("| Blend | MJ/L | Energy vs base | Extra litres needed (energy basis) | Real-world mileage drop |")
L.append("|---|---|---|---|---|")
for r in blend_rows:
    key = r["blend"].split()[0]
    rw = f"{REAL_WORLD[key]*100:.0f}% (SIAM/ARAI central)" if key in REAL_WORLD else "—"
    L.append(f"| {r['blend']} | {r['mj_per_l']} | −{r['energy_drop_pct']}% | +{r['extra_litres_pct']}% | {rw} |")
L.append("\n**CBG blended into CNG: 0% dilution.** CNG/CBG is retailed per kg, and CBG's "
         "energy per kg matches or exceeds pipeline gas — a bus fleet co-fuelled on CBG "
         "buys the *same* kg for the same km. There is no volumetric pass-through to "
         "harvest.\n")

L.append("## 3. Per-vehicle: what the dilution costs a petrol owner\n")
L.append(f"Hatchback, {KMPL_E0:.0f} km/L on E0, {KM_YR:,} km/yr, pump ₹{PUMP_PRICE:.0f}/L "
         "(pump price per litre is the SAME for E0 and E20 — the energy cut is invisible "
         "on the price board):\n")
L.append("| Blend | Extra litres/yr | Extra ₹/yr | Effective hidden levy |")
L.append("|---|---|---|---|")
for tag, d in [("E20", 0.040), ("E25", 0.055), ("E30", 0.070)]:
    xl, xr = per_vehicle(d)
    L.append(f"| {tag} | +{xl:.0f} L | ₹{xr:,.0f} | {d/(1-d)*100:.1f}% on every km driven |")

L.append("\n## 4. National petrol pool: where the extra litres' money goes (₹ cr/yr)\n")
L.append(f"Base: FY24-25 petrol pool {MS_BLENDED_BNL:.1f} bn L (40 MMT). Distance demand "
         "held constant at its E0-equivalent; each blend's real-world drop pulls extra "
         "litres through 99,281 retail outlets.\n")
L.append("| Blend | Extra bn L | Consumer pays | Central excise | State VAT | Dealer commission | OMC margin |")
L.append("|---|---|---|---|---|---|---|")
for r in nat_rows:
    L.append(f"| {r['blend']} | {r['extra_bnL']} | {r['consumer_extra_cr']:,} | "
             f"{r['excise_extra_cr']:,} | {r['vat_extra_cr']:,} | "
             f"{r['dealer_extra_cr']:,} | {r['omc_extra_cr']:,} |")
L.append("\nEvery rupee column is a *per-litre* levy × extra litres: the volume effect "
         "alone hands the exchequer ~₹8,500 cr/yr at E20 (excise+VAT) and retail "
         "outlets ~₹900 cr/yr in commission — rising with the blend walk to E30. "
         "The OMC-margin column reconciles with omc_model.py's ₹757 cr E20 figure.\n")

L.append("## 5. The CBG contrast\n")
L.append("- **Petrol+ethanol**: energy dilution is real, pump price/litre unchanged → "
         "consumer silently buys ~4% more litres; every per-litre stakeholder "
         "(centre, state, dealer, OMC) collects on the extra volume.\n"
         "- **Diesel+FAME (B7)**: same mechanism but small (−0.6% energy) — largely noise.\n"
         "- **CNG+CBG**: sold per **kg** at methane-grade energy. Substituting CBG for "
         "natural gas changes the *sourcing* (domestic waste vs imported LNG) without "
         "changing kg bought per km. As a decarbonisation lever it delivers the import "
         "substitution WITHOUT the hidden consumer levy — the fiscally honest blend.\n")

L.append("## 6. Caveats\n")
L.append("- Real-world E20 drop (4%) is below the pure energy math (6.8%): calibrated "
         "engines recover part of it via octane/combustion gains; older vehicles can "
         "lose up to ~12% (SIAM band 2-6% for compliant engines).\n"
         "- Excise ₹19.90/L and VAT-on-₹78 base are the same levers as "
         "statewise_tax_impact.py; that script covers the *tax-differential* on the "
         "displaced petrol (states LOSE VAT on the ethanol fraction) — the two effects "
         "are additive but distinct: states lose on substitution, everyone gains on "
         "volume.\n"
         "- Isobutanol rows are energy-basis only (no India fleet trial data); its "
         "appeal is precisely the smaller dilution per unit of renewable content.\n"
         "- CBG range 45-48.5 MJ/kg depends on purification; IS 16087 floor (CH4 90%) "
         "sits marginally below rich pipeline gas, well-purified CBG above it.\n")

(OUT / "energy_blend_comparison.md").write_text("\n".join(L))

with (OUT / "fuel_energy_table.csv").open("w", newline="") as f:
    w = csv.writer(f); w.writerow(["fuel", "lhv_mj_kg", "density_kg_l", "mj_per_litre", "sold_by", "note"])
    for name, (lhv, dens, unit, note) in FUELS.items():
        w.writerow([name, lhv, dens or "", round(lhv*dens, 2) if dens else "", unit, note])

with (OUT / "blend_dilution_fiscal.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(nat_rows[0])); w.writeheader(); w.writerows(nat_rows)

print(f"Petrol {E_PETROL:.1f} MJ/L | ethanol {E_ETH:.1f} ({E_ETH/E_PETROL-1:+.0%}) | "
      f"isobutanol {E_IBU:.1f} ({E_IBU/E_PETROL-1:+.0%})")
for r in blend_rows:
    print(f"{r['blend']:20s} {r['mj_per_l']:6.2f} MJ/L  energy −{r['energy_drop_pct']}%  "
          f"extra litres +{r['extra_litres_pct']}%")
for r in nat_rows:
    print(f"{r['blend']:22s} extra {r['extra_bnL']:5.2f} bnL  consumer ₹{r['consumer_extra_cr']:>6,} cr  "
          f"excise ₹{r['excise_extra_cr']:>5,} cr  VAT ₹{r['vat_extra_cr']:>5,} cr  "
          f"dealer ₹{r['dealer_extra_cr']:>4,} cr  OMC ₹{r['omc_extra_cr']:>4,} cr")
xl, xr = per_vehicle(0.04)
print(f"Hatchback E20: +{xl:.0f} L/yr = ₹{xr:,.0f}/yr hidden cost")
