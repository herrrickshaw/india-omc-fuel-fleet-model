"""omc_model.py: litre conversion, margin income, ethanol mileage-drop throughput, mix and projection."""
import pytest


@pytest.fixture
def om(run_copy):
    ns, tmp = run_copy("omc_model.py")
    return ns, tmp


def test_mmt_to_billion_litres(om):
    ns, _ = om
    assert ns["bnL_from_MMT"](40.0, 0.74) == pytest.approx(54.054, abs=1e-3)
    assert ns["bnL_from_MMT"](91.4, 0.83) == pytest.approx(110.120, abs=1e-3)


def test_base_income_hand_computed(om):
    ns, _ = om
    # 54.054 bn L x Rs 3.5 = Rs 18,919 cr ; 110.120 bn L x Rs 2.5 = Rs 27,530 cr
    assert ns["ms_inc"] == pytest.approx(40 / 0.74 * 3.5 * 100, rel=1e-12)
    assert ns["hsd_inc"] == pytest.approx(91.4 / 0.83 * 2.5 * 100, rel=1e-12)
    assert round(ns["tot_inc"]) == 46449
    # per-RO throughput: 54.054e9 L / 99,281 / 12 / 1000 = 45.4 KL/month
    assert ns["ms_perRO_klmo"] == pytest.approx(45.37, abs=0.01)


def test_ethanol_scenarios_hold_distance_fixed(om):
    ns, _ = om
    sc = {s["scenario"]: s for s in ns["scenarios"]}
    base = ns["ms_bnL_base"]
    L0 = base * 0.96
    assert sc["E20"]["blend_vol_bnL"] == pytest.approx(base)          # current blend reproduces the actual
    assert sc["E0"]["blend_vol_bnL"] == pytest.approx(L0) and sc["E0"]["extra_throughput_bnL"] == 0
    assert sc["E30"]["blend_vol_bnL"] == pytest.approx(L0 / 0.93)
    for s in sc.values():
        assert s["petrol_MS_bnL"] + s["ethanol_bnL"] == pytest.approx(s["blend_vol_bnL"])
        assert s["extra_OMC_income_cr"] == pytest.approx(s["extra_throughput_bnL"] * 3.5 * 100)
    # ethanol vs displaced petrol: E20 ethanol = 0.2 x base, cost gap Rs 4/L
    assert sc["E20"]["ethanol_cost_gap_cr"] == pytest.approx(0.2 * base * 4 * 100)
    assert sc["E20"]["extra_OMC_income_cr"] < sc["E25"]["extra_OMC_income_cr"] < sc["E30"]["extra_OMC_income_cr"]
    assert sc["E20"]["petrol_MS_bnL"] > sc["E25"]["petrol_MS_bnL"] > sc["E30"]["petrol_MS_bnL"]


def test_mix_scenarios_weight_slices(om):
    ns, _ = om
    mix = ns["mix_scenario"]("x", (0.5, 0.5, 0.0, 0.0))
    L0 = ns["L0"]
    assert mix["blend_vol_bnL"] == pytest.approx(0.5 * L0 + 0.5 * L0 / 0.96)
    assert mix["ethanol_bnL"] == pytest.approx(0.5 * L0 / 0.96 * 0.2)
    assert mix["wtd_mileage_drop"] == pytest.approx(0.02)
    pure = ns["mix_scenario"]("u", (0, 1, 0, 0))
    assert pure["blend_vol_bnL"] == pytest.approx(ns["ms_bnL_base"])
    with pytest.raises(AssertionError):
        ns["mix_scenario"]("bad", (0.5, 0.6, 0, 0))


def test_projection_compounds_growth_and_steps_blend(om):
    ns, _ = om
    p = ns["proj"]
    assert [r["blend"] for r in p] == ["E20", "E20", "E25", "E25", "E30"]
    # by design the first row is the base book (build_xlsx checks 'FY25-26 income = Base total')
    assert p[0]["omc_income_cr"] == round(ns["tot_inc"]) and p[0]["yoy_growth_cr"] is None
    L0 = ns["L0"]
    assert p[4]["petrol_blend_bnL"] == round(L0 * 1.071 ** 4 / 0.93, 2)
    assert p[4]["diesel_bnL"] == round(ns["hsd_bnL_base"] * 1.029 ** 4, 2)
    assert p[4]["outlets"] == round(99_281 * 1.045 ** 4)
    assert all(b["yoy_growth_cr"] > 0 for b in p[1:])


def test_outputs_written_to_copy_dir(om):
    _, tmp = om
    assert (tmp / "outputs" / "yoy_projection.csv").exists()
    assert "Base retail book" in (tmp / "outputs" / "omc_profitability_report.md").read_text()
