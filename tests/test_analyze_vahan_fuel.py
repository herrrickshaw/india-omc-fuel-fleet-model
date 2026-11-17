"""vahan/analyze_vahan_fuel.py: fuel-label classification and the hand-captured Vahan snapshot's integrity."""
import pytest


@pytest.fixture
def vf(run_copy):
    ns, tmp = run_copy("vahan/analyze_vahan_fuel.py")
    return ns, tmp


@pytest.mark.parametrize("label,group", [
    ("PURE EV", "Electric (BEV/PHEV)"), ("PLUG-IN HYBRID EV", "Electric (BEV/PHEV)"),
    ("PETROL(E20)/HYBRID/CNG", "Petrol + gas bi-fuel (CNG/LPG)"), ("PETROL/LPG", "Petrol + gas bi-fuel (CNG/LPG)"),
    ("STRONG HYBRID EV", "Petrol (mono, incl. E20 & hybrid)"), ("PETROL(E20)", "Petrol (mono, incl. E20 & hybrid)"),
    ("DUAL DIESEL/BIO CNG", "Diesel"), ("FLEX-FUEL(BIO-DIESEL)", "Diesel"),
    ("BIO-CNG/BIO-GAS", "CNG/CBG (dedicated)"), ("HCNG", "CNG/CBG (dedicated)"), ("CNG ONLY", "CNG/CBG (dedicated)"),
    ("LPG ONLY", "LPG (dedicated)"), ("FLEX-FUEL(ETHANOL)", "Ethanol (E100/flex)"),
    ("HYDROGEN(ICE)", "Other (H2/LNG/methanol/solar/NA)"), ("NOT APPLICABLE", "Other (H2/LNG/methanol/solar/NA)"),
])
def test_classify(vf, label, group):
    assert vf[0]["classify"](label) == group


def test_snapshot_rows_sum_to_reported_totals_and_groups_conserve(vf):
    ns, _ = vf
    for fuel, counts, total in ns["RAW"]:
        assert len(counts) == len(ns["CATS"]) and sum(counts) == total, fuel
    assert sum(ns["group_totals"](ns["tot"]).values()) == ns["GRAND"]
    assert sum(ns["group_totals"](ns["CUM"]).values()) == ns["CUM_GRAND"]
    assert [ns["broad"](c) for c in ("2WN", "3WT", "LMV")] == ["2W", "3W", "4W+"]


def test_main_runs_on_copy(vf):
    ns, tmp = vf
    ns["main"]()
    assert (tmp / "outputs" / "fuel_group_summary.csv").exists()
