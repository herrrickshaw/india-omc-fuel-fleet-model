"""fleet_from_fuel.py: active fleet = annual fuel / (km/day x days / mileage)."""
import csv

import pytest


@pytest.fixture
def ff(run_copy):
    return run_copy("fleet_from_fuel.py")


def test_sector_shares_sum_to_one_per_fuel(ff):
    ns, _ = ff
    tot = {}
    for fuel, _s, share, *_ in ns["SEGMENTS"]:
        tot[fuel] = tot.get(fuel, 0) + share
    assert tot == pytest.approx({"Petrol": 1.0, "Diesel": 1.0, "CNG": 1.0}, abs=1e-9)


def test_two_wheeler_active_hand_computed(ff):
    ns, _ = ff
    # 0.6142 x 54.054 bn L / (28 km x 330 d / 48 kmpl = 192.5 L/yr) = 172.5 million
    assert ns["two_w_active"](28) == pytest.approx(0.6142 * 40 / 0.74 * 1e9 / 192.5, rel=1e-12)
    # more km per vehicle -> fewer vehicles for the same fuel (inverse proportion)
    assert ns["two_w_active"](56) == pytest.approx(ns["two_w_active"](28) / 2)


def test_main_writes_segment_table_and_excludes_non_road(ff, capsys):
    ns, tmp = ff
    ns["main"]()
    rows = list(csv.DictReader(open(tmp / "outputs" / "fleet_from_fuel.csv")))
    nonroad = [r["sector"] for r in rows if r["active_vehicles"] == "(non-road)"]
    assert set(nonroad) == {"Other (gensets/misc)", "Railways", "Agriculture (tractor/pump)", "Industry / gensets"}
    bus = next(r for r in rows if r["fuel"] == "CNG" and r["sector"] == "Bus")
    # CNG bus: 0.22 x 6.67 bn kg / (200 x 340 / 3.8) kg/yr
    assert int(bus["active_vehicles"]) == round(0.22 * 6.67e9 / (200 * 340 / 3.8))
    out = capsys.readouterr().out
    assert "TOTAL actively-driven" in out
