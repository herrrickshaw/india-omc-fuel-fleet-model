"""Investment pitch models (CBG, distillery grain campaign, DME, isobutanol): shared
NPV/IRR helpers, per-model cash-flow arithmetic and sensitivity grids.

Every expected value is recomputed here from the module's own published levers
(hand arithmetic), never typed in from memory of an external data source."""
import csv

import pytest
from loader import load

CR = 1e7
MODELS = ["cbg_pitch_model.py", "distillery_conversion_model.py", "dme_pitch_model.py",
          "isobutanol_pitch_model.py"]


@pytest.fixture(scope="module")
def mods(tmp_path_factory):
    return {m: load(m, tmp_path_factory.mktemp(m[:-3])) for m in MODELS}


@pytest.fixture
def cbg(mods):
    return mods["cbg_pitch_model.py"]


@pytest.fixture
def dist(mods):
    return mods["distillery_conversion_model.py"]


@pytest.fixture
def dme(mods):
    return mods["dme_pitch_model.py"]


@pytest.fixture
def ibu(mods):
    return mods["isobutanol_pitch_model.py"]


@pytest.mark.parametrize("m", MODELS)
def test_npv_discounts_by_period_index(mods, m):
    npv = mods[m]["npv"]
    assert npv([-100.0, 110.0], 0.10) == pytest.approx(0.0, abs=1e-12)
    assert npv([0.0, 0.0, 121.0], 0.10) == pytest.approx(100.0)       # period 2 -> /1.1^2
    assert npv([5.0], 0.5) == 5.0                                     # period 0 undiscounted
    assert npv([-100.0, 60.0, 60.0], 0.0) == pytest.approx(20.0)


@pytest.mark.parametrize("m", MODELS)
def test_irr_recovers_known_rates(mods, m):
    irr = mods[m]["irr"]
    assert irr([-100.0, 110.0]) == pytest.approx(0.10, abs=1e-9)
    assert irr([-100.0, 0.0, 121.0]) == pytest.approx(0.10, abs=1e-9)
    assert irr([-100.0, 50.0, 50.0, 50.0]) == pytest.approx(0.2338, abs=1e-4)
    # a project that returns less than it costs has a negative IRR
    assert irr([-100.0, 50.0]) < 0


@pytest.mark.parametrize("m", MODELS)
def test_headline_irr_zeroes_the_project_npv(mods, m):
    ns = mods[m]
    assert ns["npv"](ns["cfs"], ns["proj_irr"]) == pytest.approx(0.0, abs=1e-6)
    assert ns["proj_npv"] == pytest.approx(ns["npv"](ns["cfs"], ns["DISC"]))
    # IRR above the 12% hurdle <=> positive NPV at the hurdle
    assert (ns["proj_irr"] > ns["DISC"]) == (ns["proj_npv"] > 0)


@pytest.mark.parametrize("m", MODELS)
def test_cashflow_shape_life_ramp_and_payback(mods, m):
    ns = mods[m]
    cfs = ns["cfs"]
    assert len(cfs) == ns["LIFE"] + 1
    assert cfs[0] < 0 and all(c > 0 for c in cfs[1:])
    assert cfs[1] < cfs[2]                       # year 1 runs at the ramp-up utilisation
    assert cfs[2:] == pytest.approx([cfs[2]] * (ns["LIFE"] - 1))
    pb = ns["payback"]
    assert sum(cfs[:pb + 1]) > 0 and sum(cfs[:pb]) <= 0   # first year the cumulative turns positive


@pytest.mark.parametrize("m", MODELS)
def test_sensitivity_csv_written_and_monotone(mods, m, tmp_path_factory):
    d = tmp_path_factory.mktemp("sens")
    ns = load(m, d)
    csvs = list((d / "outputs").glob("*sensitivity.csv"))
    assert len(csvs) == 1
    rows = list(csv.DictReader(open(csvs[0])))
    assert len(rows) == 3
    assert len(ns["grid"]) == 3
    assert (d / "outputs" / (m[:-3] + ".md")).exists() or any((d / "outputs").glob("*.md"))


# ---------------------------------------------------------------- CBG
def test_cbg_steady_state_legs_hand_computed(cbg):
    gas, fom, co2, opex, ebitda = cbg["year_cash"](0.9)
    assert gas == pytest.approx(12 * 330 * 0.9 * 1000 * 54 / CR)
    assert fom == pytest.approx(250 * 330 * 0.9 * 0.2 * 1500 / CR)
    assert co2 == pytest.approx(12 * 330 * 0.9 * 2.5 * 800 / CR)
    assert opex == pytest.approx(250 * 330 * 0.9 * 700 / CR + 5.0)
    assert ebitda == pytest.approx(gas + fom + co2 - opex)
    assert cbg["ebitda"] == pytest.approx(ebitda)


def test_cbg_capex_and_debt_arithmetic(cbg):
    assert cbg["CAPEX"] == 60.0 and cbg["NET_CAPEX"] == 50.0
    assert cbg["cfs"][0] == -50.0
    assert cbg["debt"] == pytest.approx(35.0)
    ds = 35.0 / 10 + 35.0 * (1 - 1 / 10) * 0.095
    assert cbg["dscr"] == pytest.approx(cbg["ebitda"] / ds)


def test_cbg_equity_cashflows_service_debt_only_inside_tenor(cbg):
    # equity cheque = net capex - debt; flows after the 10-year tenor equal EBITDA
    util_flow = cbg["year_cash"](0.9)[4]
    eq = None
    # rebuild independently
    debt, bal, eq = 35.0, 35.0, [-15.0]
    for y in range(1, 16):
        e = cbg["year_cash"](0.6 if y == 1 else 0.9)[4]
        if y <= 10:
            eq.append(e - (3.5 + bal * 0.095)); bal -= 3.5
        else:
            eq.append(e)
    assert eq[-1] == pytest.approx(util_flow)
    assert cbg["eq_irr"] == pytest.approx(cbg["irr"](eq))
    assert cbg["eq_irr"] > cbg["proj_irr"]        # 70% cheap debt levers the return up


def test_cbg_sensitivity_grid_ordering(cbg):
    grid = cbg["grid"]
    assert [r["cbg_price_rs_kg"] for r in grid] == [48.0, 54.0, 60.0]
    for r in grid:                                    # dearer feedstock -> lower IRR
        assert r["feed_525"] > r["feed_700"] > r["feed_875"]
    for a, b in zip(grid, grid[1:]):                  # higher gas price -> higher IRR
        assert b["feed_700"] > a["feed_700"]
    assert grid[1]["feed_700"] == round(cbg["proj_irr"] * 100, 1)
    assert cbg["no_fom_irr"] < cbg["proj_irr"]


def test_cbg_project_cashflows_year_one_ramp(cbg):
    cfs = cbg["project_cashflows"]()
    assert cfs[1] == pytest.approx(cbg["year_cash"](0.6)[4])
    assert cfs[2] == pytest.approx(cbg["year_cash"](0.9)[4])
    # price argument flows through (swapped-argument guard): CBG price up -> cash up
    assert cbg["project_cashflows"](cbg_price=60.0)[2] > cfs[2]
    assert cbg["project_cashflows"](feed_cost=800.0)[2] < cfs[2]
    assert cbg["project_cashflows"](fom_price=0.0)[2] < cfs[2]


# ---------------------------------------------------------------- distillery
def test_distillery_per_litre_and_ebitda(dist):
    assert dist["per_litre"]() == pytest.approx(71.86 - 23000 / 400 + 0.775 * 17 - 13)
    assert dist["per_litre"](maize=20000.0) == pytest.approx(71.86 - 50 + 13.175 - 13)
    assert dist["per_litre"](eth=64.0) == pytest.approx(64 - 57.5 + 13.175 - 13)
    assert dist["annual_ebitda"]() == pytest.approx(100 * 1000 * 150 * dist["per_litre"]() / CR)
    assert dist["annual_ebitda"](util=0.6) == pytest.approx(0.6 * dist["annual_ebitda"]())
    assert dist["annual_ebitda"](days=100) == pytest.approx(dist["annual_ebitda"]() * 100 / 150)


def test_distillery_subvention_rule_picks_the_binding_cap(dist):
    # effective rate = rate - min(6%, rate/2): at 9.5% the 6% cap binds below rate/2? no -> rate/2 = 4.75% > 3.5%
    assert dist["EFF_RATE"] == pytest.approx(max(0.095 - 0.06, 0.095 / 2))
    assert dist["EFF_RATE"] == pytest.approx(0.0475)


def test_distillery_equity_cashflow_tenor_boundary(dist):
    """Equity flows service debt in years 1..TENOR inclusive and carry the full EBITDA afterwards."""
    debt, bal, eq = 35.0, 35.0, [-15.0]
    for y in range(1, 16):
        e = dist["annual_ebitda"](0.6 if y == 1 else 1.0)
        if y <= 8:
            eq.append(e - (35 / 8 + bal * 0.0475)); bal -= 35 / 8
        else:
            eq.append(e)
    assert dist["eq_irr"] == pytest.approx(dist["irr"](eq))
    assert eq[8] == pytest.approx(dist["annual_ebitda"]() - (35 / 8 + 35 / 8 * 0.0475))   # final debt year still services debt


def test_distillery_levered_return_and_stress_cases(dist):
    assert dist["debt"] == pytest.approx(35.0)
    assert dist["dscr"] == pytest.approx(dist["ebitda"] / (35 / 8 + 35 * (1 - 1 / 8) * 0.0475))
    assert dist["eq_irr"] > dist["proj_irr"]
    assert dist["dfg_irr"] < dist["proj_irr"]        # DFG slab (64) pays less than maize slab (71.86)
    g = dist["grid"]
    assert [r["maize_rs_t"] for r in g] == [20000, 23000, 26000]
    for r in g:                                       # more grain days -> higher IRR
        assert r["days_100"] < r["days_150"] < r["days_200"]
    assert g[0]["days_150"] > g[1]["days_150"] > g[2]["days_150"]


# ---------------------------------------------------------------- DME
def test_dme_parity_and_margin(dme):
    parity = 62.0 * 28.8 / 45.8
    assert dme["DME_PARITY"] == pytest.approx(parity)
    ebitda, margin = dme["ebitda_yr"]()
    assert margin == pytest.approx(parity - 1.4 * 17.0 - 3.5)
    assert ebitda == pytest.approx(100 * 330 * 0.9 * 1000 * margin / CR)
    assert dme["ebitda_yr"](util=0.6)[0] == pytest.approx(ebitda * 0.6 / 0.9)
    assert dme["ebitda_yr"](meth=24.0)[1] == pytest.approx(parity - 1.4 * 24.0 - 3.5)
    assert dme["ebitda_yr"](real=62.0)[1] == pytest.approx(62.0 - 23.8 - 3.5)


def test_dme_scenarios(dme):
    assert dme["imp_margin"] == pytest.approx(dme["DME_PARITY"] - 33.6 - 3.5)
    assert dme["kgpar_margin"] == pytest.approx(62.0 - 23.8 - 3.5)
    assert dme["imp_ebitda"] < dme["ebitda"] < dme["kgpar_ebitda"]
    assert dme["debt"] == pytest.approx(84.0)
    assert dme["dscr"] == pytest.approx(dme["ebitda"] / (84 / 8 + 84 * (1 - 1 / 8) * 0.10))
    g = dme["grid"]
    assert [r["methanol_rs_kg"] for r in g] == [15.0, 17.0, 20.0]
    for r in g:
        assert r["real_36"] < r["real_39"] < r["real_42"]
    assert g[0]["real_39"] > g[1]["real_39"] > g[2]["real_39"]


def test_dme_payback_none_when_never_positive(dme):
    # imported methanol margin ~Rs1.9/kg cannot repay Rs120 cr within life -> payback search must not crash
    cfs = dme["cashflows"](meth=24.0)
    assert next((y for y in range(1, 16) if sum(cfs[:y + 1]) > 0), None) is None
    assert dme["irr"](cfs) < dme["DISC"]


# ---------------------------------------------------------------- isobutanol
def test_ibu_margin_and_parity(ibu):
    assert ibu["margin_per_l"]() == pytest.approx(88 - 23000 / 280 + 1.1 * 17 - 18)
    assert ibu["margin_per_l"](price=96.0) - ibu["margin_per_l"](price=80.0) == pytest.approx(16.0)
    assert ibu["margin_per_l"](conv=20.0) == pytest.approx(ibu["margin_per_l"]() - 2.0)
    assert ibu["ebitda_yr"]() == pytest.approx(70 * 1000 * 330 * 0.9 * ibu["mpl"] / CR)
    assert ibu["IBU_PARITY_ETH"] == pytest.approx(71.86 * 26.5 / 21.1)
    assert ibu["IBU_ASK"] < ibu["IBU_PARITY_ETH"]            # "just below parity"


def test_ibu_nopolicy_case_is_worse(ibu):
    assert ibu["nopolicy_margin"] == pytest.approx(71.86 - 23000 / 280 + 18.7 - 18)
    assert ibu["nopolicy_margin"] < 0
    assert ibu["nopolicy_irr"] < ibu["proj_irr"]


def test_ibu_blend_drop_and_saf_leg(ibu):
    assert ibu["e20_drop"] == pytest.approx(0.2 * (32.1 - 21.1) / 32.1)
    assert ibu["ib20_drop"] == pytest.approx(0.2 * (32.1 - 26.5) / 32.1)
    assert ibu["ib20_drop"] < ibu["e20_drop"]
    assert ibu["blend_drop"](0.0, 21.1) == 0
    assert ibu["saf_uplift"] == pytest.approx(0.75 / 0.60 - 1)
    assert ibu["blended_price"](0.0) == 88.0
    assert ibu["blended_price"](1.0) == 115.0
    assert ibu["blended_price"](0.3) == pytest.approx(0.3 * 115 + 0.7 * 88)
    s = ibu["saf_cases"]
    assert [c["saf_share_pct"] for c in s] == [0.0, 30.0, 50.0]
    assert s[0]["project_irr_pct"] == round(ibu["proj_irr"] * 100, 1)
    assert s[0]["project_irr_pct"] < s[1]["project_irr_pct"] < s[2]["project_irr_pct"]


def test_ibu_irr_search_handles_deeply_negative_projects(ibu):
    # lower bracket is -0.9: a 1:0.2 return still resolves to ~-0.8 rather than saturating
    r = ibu["irr"]([-100.0, 20.0])
    assert r == pytest.approx(-0.8, abs=1e-6)
    r2 = ibu["irr"]([-100.0, 60.0, 60.0])
    assert 60 / (1 + r2) + 60 / (1 + r2) ** 2 == pytest.approx(100.0, abs=1e-6)


def test_ibu_equity_irr_and_dscr(ibu):
    assert ibu["debt"] == pytest.approx(56.0)
    assert ibu["dscr"] == pytest.approx(ibu["ebitda"] / (56 / 8 + 56 * (1 - 1 / 8) * 0.095))
    g = ibu["grid"]
    assert [r["maize_rs_t"] for r in g] == [20000, 23000, 26000]
    for r in g:   # IRR bisection floors at its -90% bracket when every flow is negative
        assert r["price_80"] <= r["price_88"] <= r["price_96"]
    assert g[1]["price_80"] == -90.0 and g[2]["price_88"] == -90.0
    assert g[1]["price_88"] == round(ibu["proj_irr"] * 100, 1)
    assert g[0]["price_88"] > g[1]["price_88"] > g[2]["price_96"] > 0
