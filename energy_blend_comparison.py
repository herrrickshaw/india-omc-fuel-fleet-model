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
    ("B10 (biodiesel)",  E_DIESEL, E_FAME, 0.10, "diesel"),
    ("B15 (biodiesel)",  E_DIESEL, E_FAME, 0.15, "diesel"),
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

# ── Incremental E20 -> E30 walk: what the NEXT blend step adds vs today ──────
# Today's baseline is E20. Each step's delta = its extra litres minus E20's.
def incremental(blend, drop, ref=nat_rows[0]):
    r = national(blend, drop)
    d = {"blend": f"{blend} (vs E20 today)"}
    for k in ("extra_bnL", "consumer_extra_cr", "excise_extra_cr", "vat_extra_cr",
              "dealer_extra_cr", "omc_extra_cr"):
        d[k] = round(r[k] - ref[k], 2 if k == "extra_bnL" else 0)
    return d

inc_rows = [incremental("E25", 0.055), incremental("E27", 0.0625), incremental("E30", 0.070)]

# ── Diesel pool: B10 / B15 / B20 (biodiesel walk) ───────────────────────────
# Diesel has no octane-recovery mechanism, so real-world ~= energy basis.
# FAME dilutes only -0.85% per B10 step, but the pool is 2x petrol's.
HSD_BNL      = 91.4 * 1e3 / 0.83 / 1e3          # 110.12 bn L FY24-25
D_PUMP       = 92.0     # Rs/L indicative pan-India diesel
D_EXCISE     = 15.80    # Rs/L central excise on diesel
D_VAT_PER_L  = 0.175 * 70.0   # ~Rs12.3/L effective state VAT (lower rates than petrol)
D_DEALER     = 3.1      # Rs/L dealer commission (RR 8.10)
D_OMC        = 2.5      # Rs/L OMC marketing margin (omc_model.py lever)

def diesel_national(blend, frac):
    e_mix = E_DIESEL * (1 - frac) + E_FAME * frac
    drop = 1 - e_mix / E_DIESEL
    litres = HSD_BNL / (1 - drop)      # pool today ~B0; L0 = HSD_BNL
    extra = litres - HSD_BNL
    e = extra * 1e9
    return {"blend": blend, "mileage_drop_pct": round(drop * 100, 2),
            "pool_bnL": round(litres, 2), "extra_bnL": round(extra, 2),
            "consumer_extra_cr": round(e * D_PUMP / CR),
            "excise_extra_cr": round(e * D_EXCISE / CR),
            "vat_extra_cr": round(e * D_VAT_PER_L / CR),
            "dealer_extra_cr": round(e * D_DEALER / CR),
            "omc_extra_cr": round(e * D_OMC / CR)}

diesel_rows = [diesel_national(b, f) for b, f in
               [("B7", 0.07), ("B10", 0.10), ("B15", 0.15), ("B20", 0.20)]]

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
L.append("\n### 4a. The E20 → E30 walk: what each NEXT step adds (vs today's E20)\n")
L.append("India is already at ~E20, so the live policy question is the *increment*. "
         "Deltas below are each blend's extra litres/rupees **beyond what E20 already "
         "extracts** (real-world drops: E25 5.5%, E27 6.25%, E30 7%):\n")
L.append("| Step | Δ bn L | Δ Consumer | Δ Excise | Δ VAT | Δ Dealer comm. | Δ OMC margin |")
L.append("|---|---|---|---|---|---|---|")
for r in inc_rows:
    L.append(f"| {r['blend']} | +{r['extra_bnL']} | +{r['consumer_extra_cr']:,} | "
             f"+{r['excise_extra_cr']:,} | +{r['vat_extra_cr']:,} | "
             f"+{r['dealer_extra_cr']:,} | +{r['omc_extra_cr']:,} |")
L.append("\nThe walk from E20 to E30 roughly **doubles** the volume-effect take: "
         "~₹18,300 cr/yr more consumer spend, ~₹6,900 cr/yr more excise+VAT, "
         "~₹715 cr/yr more dealer commission — on top of what E20 already collects. "
         "Per rupee of renewable content added, the increments get *worse*: mileage "
         "loss scales linearly with ethanol share, so each step buys the same "
         "import-substitution at the same hidden-levy rate, with no efficiency "
         "recovery left (engines are calibrated for E20, not E30).\n")

L.append("### 4b. Diesel pool: B7 → B20 biodiesel walk\n")
L.append(f"Diesel is the bigger prize by volume: {HSD_BNL:.0f} bn L/yr (91.4 MMT) — "
         "2× the petrol pool. FAME dilutes far less per litre (−8.5% vs ethanol's "
         "−34%), and diesel engines have no octane-recovery offset, so real-world "
         f"≈ energy basis. Pump ₹{D_PUMP:.0f}/L, excise ₹{D_EXCISE:.2f}/L, effective "
         f"VAT ~₹{D_VAT_PER_L:.1f}/L, dealer ₹{D_DEALER:.1f}/L, OMC ₹{D_OMC:.1f}/L:\n")
L.append("| Blend | Mileage drop | Extra bn L | Consumer pays | Excise | VAT | Dealer comm. | OMC margin |")
L.append("|---|---|---|---|---|---|---|---|")
for r in diesel_rows:
    L.append(f"| {r['blend']} | −{r['mileage_drop_pct']}% | {r['extra_bnL']} | "
             f"{r['consumer_extra_cr']:,} | {r['excise_extra_cr']:,} | {r['vat_extra_cr']:,} | "
             f"{r['dealer_extra_cr']:,} | {r['omc_extra_cr']:,} |")
L.append("\nB20 on the diesel pool pulls **~1.9 bn extra litres** — nearly as many as "
         "E20 does on petrol — because the pool is huge even though the per-litre "
         "dilution is mild. But the consumer burden per km is far gentler (−1.7% vs "
         "−4%), and diesel's freight exposure means the extra cost cascades into "
         "logistics/inflation rather than household budgets. Feasibility caveat: "
         "India's biodiesel supply is nowhere near B10 nationally (blending was "
         "<1% in FY24-25; the NBP target is B5 by 2030) — B15/B20 rows are a "
         "what-if ceiling, and OEM warranties beyond B7 are unresolved.\n")

L.append("Every rupee column is a *per-litre* levy × extra litres: the volume effect "
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

with (OUT / "blend_walk_incremental.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(inc_rows[0])); w.writeheader(); w.writerows(inc_rows)

with (OUT / "diesel_biodiesel_fiscal.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(diesel_rows[0])); w.writeheader(); w.writerows(diesel_rows)

print(f"Petrol {E_PETROL:.1f} MJ/L | ethanol {E_ETH:.1f} ({E_ETH/E_PETROL-1:+.0%}) | "
      f"isobutanol {E_IBU:.1f} ({E_IBU/E_PETROL-1:+.0%})")
for r in blend_rows:
    print(f"{r['blend']:20s} {r['mj_per_l']:6.2f} MJ/L  energy −{r['energy_drop_pct']}%  "
          f"extra litres +{r['extra_litres_pct']}%")
for r in nat_rows:
    print(f"{r['blend']:22s} extra {r['extra_bnL']:5.2f} bnL  consumer ₹{r['consumer_extra_cr']:>6,} cr  "
          f"excise ₹{r['excise_extra_cr']:>5,} cr  VAT ₹{r['vat_extra_cr']:>5,} cr  "
          f"dealer ₹{r['dealer_extra_cr']:>4,} cr  OMC ₹{r['omc_extra_cr']:>4,} cr")
print("-- incremental walk vs E20 --")
for r in inc_rows:
    print(f"{r['blend']:20s} Δ{r['extra_bnL']:+5.2f} bnL  consumer +₹{r['consumer_extra_cr']:>6,} cr  "
          f"excise +₹{r['excise_extra_cr']:>5,} cr  VAT +₹{r['vat_extra_cr']:>5,} cr  "
          f"dealer +₹{r['dealer_extra_cr']:>4,} cr")
print("-- diesel biodiesel walk --")
for r in diesel_rows:
    print(f"{r['blend']:5s} drop {r['mileage_drop_pct']:4.2f}%  extra {r['extra_bnL']:5.2f} bnL  "
          f"consumer ₹{r['consumer_extra_cr']:>6,} cr  excise ₹{r['excise_extra_cr']:>5,} cr  "
          f"VAT ₹{r['vat_extra_cr']:>5,} cr  dealer ₹{r['dealer_extra_cr']:>4,} cr  OMC ₹{r['omc_extra_cr']:>4,} cr")
xl, xr = per_vehicle(0.04)
print(f"Hatchback E20: +{xl:.0f} L/yr = ₹{xr:,.0f}/yr hidden cost")
