#!/usr/bin/env python3
"""Estimate the ACTIVELY-DRIVEN on-road fleet from fuel burn (PPAC consumption).

Cumulative Vahan registrations (44.6 cr) include scrapped / dead vehicles, so they
overstate what's really on the road. This backs the number out from physics instead:

    active vehicles(segment) = annual fuel(segment) / (km/day × active-days / mileage)

Total petrol & diesel come from PPAC (Table 6.1). Each fuel is split across sectors
using the PPAC-commissioned Nielsen 'Sectoral demand of petrol & diesel' study, and
every segment carries an editable daily-usage assumption. Non-road diesel (farm
pumps, gensets, railways, industry) is separated out — it burns fuel but is not a
'vehicle going daily on the road'. Pure stdlib.
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"; OUT.mkdir(exist_ok=True)

# ── PPAC national consumption (FY24-25, Table 6.1 & 3.7) ─────────────────────
PETROL_MMT, DIESEL_MMT = 40.0, 91.4
CNG_MMT = 6.67                          # all-India CNG sales FY24-25 (RR Table 3.7)
DENS_MS, DENS_HSD = 0.74, 0.83          # kg/L
def bnL(mmt, dens): return mmt * 1e9 / dens / 1e9
PETROL_BNL, DIESEL_BNL = bnL(PETROL_MMT, DENS_MS), bnL(DIESEL_MMT, DENS_HSD)
CNG_BNKG = CNG_MMT                      # CNG billed by mass: 1 MMT = 1 bn kg; mileage in km/kg

# ── EV: no combustion fuel, so estimated from Vahan registrations × active-rate ──
VAHAN_CUM_EV = 9_785_936               # PURE EV + ELECTRIC(BOV) + PHEV (Vahan cumulative)
EV_ACTIVE_RATE = 0.85                  # recent vintage -> most still active (editable)

# ── sector split of each fuel (PPAC/Nielsen 2013 study — EDITABLE) ───────────
# share = fraction of that fuel; on_road = counts as a daily-driven road vehicle.
# km_day / mileage / active_days -> annual litres per vehicle.
# unit = km/L (kmpl). Non-road rows omit usage and are reported as fuel only.
SEGMENTS = [
  # fuel,     sector,                 share,  on_road, km_day, mileage, active_days
  ("Petrol", "Two-wheeler",           0.6142, True,    28,     48,      330),
  ("Petrol", "Car",                   0.3433, True,    30,     15,      300),
  ("Petrol", "Three-wheeler",         0.0234, True,    60,     30,      300),
  ("Petrol", "Other (gensets/misc)",  0.0191, False,   None,   None,    None),
  ("Diesel", "Truck / LCV (freight)", 0.2825, True,    220,    6.0,     330),
  ("Diesel", "Bus",                   0.0955, True,    200,    4.5,     340),
  # Diesel car/UV fuel is taxi/fleet-heavy (high daily km), not private cars — so
  # blended km/day is high; a low figure would over-count vehicles massively.
  ("Diesel", "Car / UV / taxi",       0.2848, True,    90,     16.0,    310),
  ("Diesel", "Three-wheeler",         0.0330, True,    90,     22.0,    310),
  ("Diesel", "Railways",              0.0324, False,   None,   None,    None),
  ("Diesel", "Agriculture (tractor/pump)", 0.1300, False, None, None,   None),
  ("Diesel", "Industry / gensets",    0.1418, False,   None,   None,    None),
  # CNG (mileage in km/kg; shares of transport CNG — EDITABLE). Note: petrol/CNG
  # bi-fuel cars also burn petrol, so the CNG 'Car' line overlaps the petrol 'Car'
  # line — the two fuel balances double-count bi-fuel vehicles in part.
  ("CNG",    "Car (incl. bi-fuel)",   0.38,   True,    40,     25.0,    300),
  ("CNG",    "Three-wheeler",         0.25,   True,    90,     30.0,    310),
  ("CNG",    "Bus",                   0.22,   True,    200,    3.8,     340),
  ("CNG",    "LCV / truck",           0.15,   True,    140,    4.5,     330),
]

# Vahan reference counts (from vahan/ analysis) for comparison
VAHAN_CUM_TOTAL = 446_191_165        # cumulative all-time registrations
VAHAN_CY2025    = 29_290_589         # one year's new registrations
MORTH_LIVE_EST  = 350_000_000        # ~ MoRTH-style live-parc order (illustrative)


def two_w_active(km_day):
    """2-wheeler active count for a given daily-km (for the sensitivity band)."""
    for fuel, sector, share, on_road, kmd, mpl, days in SEGMENTS:
        if sector == "Two-wheeler":
            return PETROL_BNL * share * 1e9 / (km_day * days / mpl)
    return 0


def main():
    fuel_bnl = {"Petrol": PETROL_BNL, "Diesel": DIESEL_BNL, "CNG": CNG_BNKG}
    rows, road_total = [], 0
    nonroad_bnl = 0.0
    for fuel, sector, share, on_road, kmd, mpl, days in SEGMENTS:
        seg_bnl = fuel_bnl[fuel] * share
        if on_road:
            l_per_veh_yr = kmd * days / mpl                    # litres/vehicle/year
            active = seg_bnl * 1e9 / l_per_veh_yr
            road_total += active
            rows.append({
                "fuel": fuel, "sector": sector, "share_pct": round(share*100, 1),
                "fuel_bnL": round(seg_bnl, 2), "km_day": kmd, "mileage": mpl,
                "active_days": days, "L_per_veh_day": round(kmd/mpl, 2),
                "L_per_veh_yr": round(l_per_veh_yr), "active_vehicles": round(active),
            })
        else:
            nonroad_bnl += seg_bnl
            rows.append({
                "fuel": fuel, "sector": sector, "share_pct": round(share*100, 1),
                "fuel_bnL": round(seg_bnl, 2), "km_day": "", "mileage": "",
                "active_days": "", "L_per_veh_day": "", "L_per_veh_yr": "",
                "active_vehicles": "(non-road)",
            })

    with (OUT / "fleet_from_fuel.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    # split active counts by energy type
    liquid_active = sum(r["active_vehicles"] for r in rows
                        if isinstance(r["active_vehicles"], int) and r["fuel"] in ("Petrol", "Diesel"))
    cng_active = sum(r["active_vehicles"] for r in rows
                     if isinstance(r["active_vehicles"], int) and r["fuel"] == "CNG")
    ev_active = VAHAN_CUM_EV * EV_ACTIVE_RATE
    grand_active = liquid_active + cng_active + ev_active

    liquid_road_bnl = (PETROL_BNL + DIESEL_BNL) - nonroad_bnl
    avg_l_day = liquid_road_bnl * 1e9 / liquid_active / 365

    # sensitivity: ±20% on two-wheeler daily-km -> total actively-driven band
    base_2w = two_w_active(28)
    band = {}
    for tag, kmd in (("2W usage −20% (22.4 km/day)", 22.4),
                     ("2W usage base (28 km/day)", 28.0),
                     ("2W usage +20% (33.6 km/day)", 33.6)):
        delta = two_w_active(kmd) - base_2w
        band[tag] = grand_active + delta

    L = []
    L.append("# Actively-driven fleet, implied from fuel burn (PPAC) — petrol, diesel, CNG + EV\n")
    L.append(f"Method: for each sector, **active vehicles = annual fuel ÷ (km/day × active-days ÷ mileage)**. "
             f"Fuel totals are PPAC FY24-25 (petrol {PETROL_MMT} MMT = {PETROL_BNL:.1f} bn L; diesel "
             f"{DIESEL_MMT} MMT = {DIESEL_BNL:.1f} bn L; CNG {CNG_MMT} MMT = {CNG_BNKG:.2f} bn kg, RR Table 3.7). "
             "Sector shares (Nielsen/PPAC study) and daily-usage are editable. Non-road diesel (farm/rail/"
             "industry) is separated out. EVs burn no fuel, so they are estimated from Vahan registrations "
             f"× an {EV_ACTIVE_RATE:.0%} active-rate.\n")

    L.append("## 1. Segment build-up\n")
    L.append("| Fuel | Sector | % of fuel | Fuel (bn L/kg) | km/day | mileage | per-veh/day | per-veh/yr | Active vehicles |")
    L.append("|---|---|--:|--:|--:|--:|--:|--:|--:|")
    for r in rows:
        av = r["active_vehicles"]
        av = f"{av:,}" if isinstance(av, int) else av
        L.append(f"| {r['fuel']} | {r['sector']} | {r['share_pct']}% | {r['fuel_bnL']} | "
                 f"{r['km_day']} | {r['mileage']} | {r['L_per_veh_day']} | {r['L_per_veh_yr']} | {av} |")
    L.append(f"| EV | Electric (registration-based) | — | — | — | — | — | — | {round(ev_active):,} |")
    L.append("")

    L.append("## 2. Implied actively-driven fleet\n")
    L.append("| Energy type | Active vehicles | Method |")
    L.append("|---|--:|---|")
    L.append(f"| Petrol + diesel (road) | {liquid_active:,} | fuel balance |")
    L.append(f"| CNG | {cng_active:,} | fuel balance |")
    L.append(f"| Electric (BEV/e-3W) | {round(ev_active):,} | Vahan reg × {EV_ACTIVE_RATE:.0%} active |")
    L.append(f"| **Total actively-driven** | **{round(grand_active):,}** (~{grand_active/1e7:.1f} cr) | |")
    L.append("")
    L.append(f"- Liquid-fuel road burn {liquid_road_bnl:.1f} bn L/yr; non-road diesel (farm/rail/industry) "
             f"{nonroad_bnl:.1f} bn L excluded. Avg **{avg_l_day:.2f} L/day per active liquid-fuel vehicle**.")
    L.append("- ⚠️ **Bi-fuel overlap:** petrol/CNG cars burn both fuels, so the CNG 'Car' line partly "
             "double-counts vehicles already in the petrol 'Car' line — the true *distinct* headcount is "
             "modestly below the raw sum. Read the total as ~24–25 crore.\n")

    L.append("## 3. Sensitivity — ±20% on two-wheeler daily usage\n")
    L.append("2-wheelers dominate the count, so their assumed daily-km is the biggest swing factor. "
             "Holding fuel fixed, higher usage per 2W ⇒ fewer active 2W (each burns more):\n")
    L.append("| Scenario | Total actively-driven | ~crore |")
    L.append("|---|--:|--:|")
    for tag, val in band.items():
        L.append(f"| {tag} | {round(val):,} | {val/1e7:.1f} |")
    lo, hi = min(band.values()), max(band.values())
    L.append(f"\n**Band: ~{lo/1e7:.0f}–{hi/1e7:.0f} crore actively-driven vehicles** "
             f"(central ~{grand_active/1e7:.0f} cr).\n")

    L.append("## 4. Reality check vs Vahan registrations\n")
    L.append("| Basis | Vehicles | vs implied-active |")
    L.append("|---|--:|--:|")
    L.append(f"| Implied actively-driven (this model) | {round(grand_active):,} | 1.00× |")
    L.append(f"| MoRTH-style live parc (illustrative) | {MORTH_LIVE_EST:,} | {MORTH_LIVE_EST/grand_active:.2f}× |")
    L.append(f"| Vahan cumulative 'Till Today' | {VAHAN_CUM_TOTAL:,} | {VAHAN_CUM_TOTAL/grand_active:.2f}× |")
    L.append("")
    L.append(f"Fuel burn + EV registrations imply **~{grand_active/1e7:.0f} crore vehicles are driven with "
             f"any regularity** — roughly **{100*grand_active/VAHAN_CUM_TOTAL:.0f}% of the "
             f"{VAHAN_CUM_TOTAL/1e7:.0f}-crore cumulative registration count**. The chain: cumulative "
             f"registered {VAHAN_CUM_TOTAL/1e7:.0f} cr → live parc ~{MORTH_LIVE_EST/1e7:.0f} cr → "
             f"actively-driven ~{grand_active/1e7:.0f} cr. The gap is scrapped/dead/seasonal vehicles "
             "Vahan never removes.\n")

    L.append("## 5. Caveats\n")
    L.append("- **Sector split is the main uncertainty**: Nielsen shares are 2013-vintage (diesel cars have "
             "since collapsed); per-segment counts are order-of-magnitude, the aggregate more robust.")
    L.append("- **Bi-fuel double-count** (petrol/CNG) inflates the raw sum slightly — see §2.")
    L.append("- EV row is registration-based (no fuel proxy); e-rickshaws in ELECTRIC(BOV) have high "
             "churn, so the active-rate is a lever.")
    L.append("- 'Active' = driven enough to appear in annual fuel, not a legal-status count.\n")
    L.append("---\n*Fuel-balance + registration estimate; editable assumptions; not an official census.*\n")
    (OUT / "fleet_from_fuel.md").write_text("\n".join(L))

    print(f"Liquid road: {liquid_active:,} | CNG: {cng_active:,} | EV: {round(ev_active):,}")
    print(f"TOTAL actively-driven: {round(grand_active):,} (~{grand_active/1e7:.1f} crore) "
          f"= {100*grand_active/VAHAN_CUM_TOTAL:.0f}% of Vahan cumulative")
    print(f"Avg burn per active liquid-fuel vehicle: {avg_l_day:.2f} L/day")
    print(f"2W ±20% sensitivity band: {lo/1e7:.1f}–{hi/1e7:.1f} crore")
    print("Segment detail:")
    for r in rows:
        if isinstance(r["active_vehicles"], int):
            print(f"  {r['fuel']:7s} {r['sector']:26s} {r['L_per_veh_day']:>6} /day -> {r['active_vehicles']:>13,}")
    print("Wrote outputs/fleet_from_fuel.md + .csv")


if __name__ == "__main__":
    main()
