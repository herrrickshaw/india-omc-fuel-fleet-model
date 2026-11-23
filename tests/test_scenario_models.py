"""Blend / price / supply scenario scripts: hand-computed rows, boundary behaviour and the
CSV/markdown artefacts they write (redirected into tmp_path by the loader)."""
import csv

import pytest
from loader import load

CR = 1e7
MS = 40.0 * 1e3 / 0.74 / 1e3          # 54.054 bn L, the pool every script anchors on


def rows(path):
    return list(csv.DictReader(open(path)))


# ------------------------------------------------------------------ omc_model
@pytest.fixture(scope="module")
def omc(tmp_path_factory):
    d = tmp_path_factory.mktemp("omc")
    return load("omc_model.py", d), d


def test_omc_projection_compounds_and_yoy(omc):
    ns, _ = omc
    p = ns["proj"]
    assert p[0]["yoy_growth_cr"] is None
    assert p[0]["outlets"] == 99281
    assert p[1]["outlets"] == round(99281 * 1.045)
    assert p[4]["outlets"] == round(99281 * 1.045 ** 4)
    L0 = ns["L0"]
    ms0 = L0 / (1 - 0.04) * 1e9 * 3.5 / CR
    hsd0 = 91.4 / 0.83 * 2.5 * 100
    assert p[0]["omc_income_cr"] == round(ms0 + hsd0)
    L1 = L0 * 1.071
    tot1 = L1 / (1 - 0.04) * 3.5 * 100 + 91.4 / 0.83 * 1.029 * 2.5 * 100
    assert p[1]["omc_income_cr"] == round(tot1)
    assert p[1]["yoy_growth_cr"] == round(tot1 - (ms0 + hsd0))
    # ethanol-attributable income: litres above the E0-equivalent only
    assert p[0]["ethanol_attributable_cr"] == round((L0 / 0.96 - L0) * 3.5 * 100)
    assert p[4]["blend"] == "E30"
    assert p[4]["ethanol_attributable_cr"] > p[0]["ethanol_attributable_cr"]


def test_omc_mix_scenarios_are_share_weighted_and_conserve_distance(omc):
    ns, _ = omc
    assert len(ns["mixes"]) == 5
    for name, shares in ns["MIX_SCENARIOS"].items():
        assert sum(shares) == pytest.approx(1.0), name
    today = ns["mixes"][0]
    assert today["share_E20"] == 0.95 and today["share_E0"] == 0.05
    assert today["wtd_mileage_drop"] == pytest.approx(0.95 * 0.04)
    assert today["petrol_MS_bnL"] + today["ethanol_bnL"] == pytest.approx(today["blend_vol_bnL"])
    s1 = ns["mixes"][1]                          # universal E20 reproduces the actual pool
    assert s1["blend_vol_bnL"] == pytest.approx(ns["ms_bnL_base"])
    assert s1["omc_petrol_income_cr"] == pytest.approx(ns["ms_inc"])
    incomes = [m["omc_petrol_income_cr"] for m in ns["mixes"]]
    assert incomes[1] < incomes[2] < incomes[3] < incomes[4]
    assert ns["mix_scenario"]("allE0", (1, 0, 0, 0))["extra_vs_e0_bnL"] == pytest.approx(0.0, abs=1e-12)


def test_omc_mix_scenario_rejects_shares_not_summing_to_one(omc):
    ns, _ = omc
    ns["mix_scenario"]("ok", (0.25, 0.25, 0.25, 0.25))
    with pytest.raises(AssertionError, match="shares must sum to 1"):
        ns["mix_scenario"]("bad", (0.25, 0.25, 0.25, 0.2499))
    ns["mix_scenario"]("tol", (0.25, 0.25, 0.25, 0.25 + 1e-10))   # inside the 1e-9 tolerance


def test_omc_outputs_written_and_rounded(omc):
    ns, d = omc
    out = d / "outputs"
    sc = rows(out / "scenarios.csv")
    assert [r["scenario"] for r in sc] == ["E0", "E20", "E25", "E30"]
    assert sc[1]["blend_pct"] == "0.2"
    assert float(sc[1]["blend_vol_bnL"]) == round(ns["scenarios"][1]["blend_vol_bnL"], 3)
    yoy = rows(out / "yoy_projection.csv")
    assert yoy[0]["yoy_growth_cr"] == "" and len(yoy) == 5
    mix = rows(out / "blend_mix_scenarios.csv")
    assert len(mix) == 5 and mix[0]["scenario"] == "S0 Today (~E20)"
    md = (out / "omc_profitability_report.md").read_text()
    assert md.startswith("# OMC Retail Profitability Model")
    assert f"{ns['N_RO_2025']:,}" in md and "IS 16087" in md
    assert "| FY25-26 | E20 | 99,281 |" in md


# ------------------------------------------------------------------ cbg_satat_economics
@pytest.fixture(scope="module")
def satat(tmp_path_factory):
    d = tmp_path_factory.mktemp("satat")
    return load("cbg_satat_economics.py", d), d


def test_satat_gas_parity_and_premiums(satat):
    ns, _ = satat
    assert ns["gas_rs_per_kg"](6.5) == pytest.approx(6.5 * 83.0 / 1055.06 * 47.5)
    assert ns["gas_rs_per_kg"](0) == 0
    assert ns["RLNG_KG"] > ns["APM_KG"]
    assert ns["eth_prem"] == pytest.approx((62 / 21.1) / (58 / 32.1) - 1)
    assert ns["cbg_prem"] == pytest.approx((54 / 46.5) / (ns["RLNG_KG"] / 47.5) - 1)
    assert ns["eth_prem"] > 0            # ethanol per MJ costs more than the petrol it displaces


def test_satat_cost_per_km_rows(satat):
    ns, _ = satat
    km = {r[0]: r[1] for r in ns["km_rows"]}
    assert km["Petrol E0"] == pytest.approx(105 / 16.67)
    assert km["Petrol E20"] == pytest.approx(105 / (16.67 * 0.96))
    assert km["Petrol E30"] == pytest.approx(105 / (16.67 * 0.93))
    assert km["Diesel B20"] == pytest.approx(92 / (17.91 * 0.983))
    assert km["CNG"] == pytest.approx(75 / 27.40)
    assert km["CBG (any % in CNG stream)"] == pytest.approx(75 / (27.40 * 46.5 / 47.5))
    assert km["CBG (any % in CNG stream)"] > km["CNG"]    # CBG's lower MJ/kg costs a hair more per km
    assert km["Petrol E0"] < km["Petrol E20"] < km["Petrol E30"]


def test_satat_cbo_pass_through(satat):
    ns, d = satat
    r1, r5 = ns["cbo_rows"]
    assert r1["cbo_share_pct"] == 1 and r5["cbo_share_pct"] == 5
    assert r1["cbg_tonnes"] == round(6.67e9 * 0.01 / 1e3) == 66700
    assert r5["cbg_tonnes"] == 333500
    assert r1["procurement_cr"] == round(6.67e9 * 0.01 * 54 * 1.05 / CR)
    delta = 54 * 1.05 - ns["RLNG_KG"]
    assert r1["pump_delta_rs_kg"] == round(0.01 * delta, 2)
    assert r5["pump_delta_rs_kg"] == round(0.05 * delta, 2)
    assert r1["mileage_delta_pct"] == round(0.01 * (1 - 46.5 / 47.5) * 100, 2)
    assert r5["procurement_cr"] == pytest.approx(5 * r1["procurement_cr"], abs=3)
    assert (d / "outputs" / "cbg_satat_economics.csv").exists()
    assert (d / "outputs" / "cbg_satat_economics.md").exists()


# ------------------------------------------------------------------ dme_lpg_blending
@pytest.fixture(scope="module")
def dme(tmp_path_factory):
    d = tmp_path_factory.mktemp("dme")
    return load("dme_lpg_blending.py", d), d


def test_dme_blend_rows(dme):
    ns, d = dme
    r5, r10, r20 = ns["rows"]
    assert [r["blend"] for r in ns["rows"]] == ["DME5", "DME10", "DME20"]
    assert r20["mj_per_kg"] == round(45.8 * 0.8 + 28.8 * 0.2, 2)
    assert r20["energy_drop_pct"] == round((1 - (45.8 * 0.8 + 28.8 * 0.2) / 45.8) * 100, 2)
    assert r20["lerc_drop_pct"] == 5.26                      # measured anchor reproduced at DME20
    assert r10["lerc_drop_pct"] == round(5.26 / 2, 2)        # scales linearly with the DME share
    assert r5["lerc_drop_pct"] == round(5.26 / 4, 2)
    extra = 1 / (1 - 0.0526) - 1
    assert r20["extra_kg_pct"] == round(extra * 100, 2)
    assert r20["hh_extra_cyl_yr"] == round(7 * extra, 2)
    assert r20["hh_extra_rs_yr"] == round(7 * extra * 803)
    assert r20["extra_pool_mmt"] == round(29.7 * extra, 2)
    assert r20["dme_needed_mmt"] == round(29.7 * (1 + extra) * 0.2, 2)
    assert r20["parity_cylinder_rs"] == round(803 * (1 - 0.0526))
    assert r20["dme_energy_parity_rs_kg"] == round(52.0 * 28.8 / 45.8, 1)
    assert r20["pmuy_extra_subsidy_cr"] == round(10.3e7 * 7 * extra * 300 / CR)
    assert r20["consumer_extra_cr"] == round(29.7 * extra * 1e9 * (803 / 14.2) / CR)
    assert ns["methanol_route_feed"] == pytest.approx(1.4 * 24.0)
    assert ns["d20"] is r20
    assert len(rows(d / "outputs" / "dme_lpg_blending.csv")) == 3
    # LERC's measured drop is smaller than the pure-energy drop (documented in the report)
    assert r20["lerc_drop_pct"] < r20["energy_drop_pct"]


# ------------------------------------------------------------------ energy_blend_comparison
@pytest.fixture(scope="module")
def eb(tmp_path_factory):
    d = tmp_path_factory.mktemp("eb")
    return load("energy_blend_comparison.py", d), d


def test_energy_per_litre_and_blend_dilution(eb):
    ns, _ = eb
    assert ns["E_PETROL"] == pytest.approx(43.4 * 0.74)
    assert ns["mj_per_litre"]("CNG (pipeline gas)") is None
    assert ns["mj_per_litre"]("Pure methane") is None
    e20 = next(r for r in ns["blend_rows"] if r["blend"] == "E20")
    mix = ns["E_PETROL"] * 0.8 + ns["E_ETH"] * 0.2
    assert e20["mj_per_l"] == round(mix, 2)
    assert e20["energy_drop_pct"] == round((1 - mix / ns["E_PETROL"]) * 100, 2)
    drop = 1 - mix / ns["E_PETROL"]
    assert e20["extra_litres_pct"] == round((1 / (1 - drop) - 1) * 100, 2)
    drops = [r["energy_drop_pct"] for r in ns["blend_rows"] if r["base"] == "petrol" and r["blend"].startswith("E")]
    assert drops == sorted(drops)
    ib24 = next(r for r in ns["blend_rows"] if r["blend"].startswith("IB24"))
    e25 = next(r for r in ns["blend_rows"] if r["blend"] == "E25")
    assert ib24["energy_drop_pct"] < e25["energy_drop_pct"]


def test_national_extra_throughput_is_fraction_of_pool(eb):
    ns, _ = eb
    e20 = ns["national"]("E20", 0.04)
    assert e20["pool_bnL"] == round(MS, 2)                # E20 pool is today's pool by construction
    assert e20["extra_bnL"] == round(MS * 0.04, 2)
    e = MS * 0.04 * 1e9
    assert e20["consumer_extra_cr"] == round(e * 105 / CR)
    assert e20["excise_extra_cr"] == round(e * 19.90 / CR)
    assert e20["vat_extra_cr"] == round(e * 0.25 * 78 / CR)
    assert e20["dealer_extra_cr"] == round(e * 4.1 / CR)
    assert e20["omc_extra_cr"] == round(e * 3.5 / CR)
    e30 = ns["national"]("E30", 0.07)
    assert e30["extra_bnL"] > e20["extra_bnL"]
    zero = ns["national"]("X", 0.04)
    assert zero == e20 | {"blend": "X"}


def test_incremental_walk_is_difference_against_e20(eb):
    ns, _ = eb
    e30_inc = ns["incremental"]("E30", 0.07)
    e30 = ns["national"]("E30", 0.07)
    e20 = ns["nat_rows"][0]
    assert e30_inc["blend"] == "E30 (vs E20 today)"
    assert e30_inc["extra_bnL"] == round(e30["extra_bnL"] - e20["extra_bnL"], 2)
    assert e30_inc["omc_extra_cr"] == round(e30["omc_extra_cr"] - e20["omc_extra_cr"])
    assert [r["blend"] for r in ns["inc_rows"]] == ["E25 (vs E20 today)", "E27 (vs E20 today)", "E30 (vs E20 today)"]
    ex = [r["extra_bnL"] for r in ns["inc_rows"]]
    assert ex == sorted(ex) and ex[0] > 0
    # E20 vs itself adds nothing
    assert ns["incremental"]("E20", 0.04)["extra_bnL"] == 0


def test_diesel_and_per_vehicle(eb):
    ns, d = eb
    b7, b10, b15, b20 = ns["diesel_rows"]
    assert b10["mileage_drop_pct"] == round((1 - (ns["E_DIESEL"] * 0.9 + ns["E_FAME"] * 0.1) / ns["E_DIESEL"]) * 100, 2)
    assert b7["extra_bnL"] < b10["extra_bnL"] < b15["extra_bnL"] < b20["extra_bnL"]
    hsd = 91.4 * 1e3 / 0.83 / 1e3
    assert ns["HSD_BNL"] == pytest.approx(hsd)
    drop20 = 1 - (ns["E_DIESEL"] * 0.8 + ns["E_FAME"] * 0.2) / ns["E_DIESEL"]
    assert b20["extra_bnL"] == round(hsd / (1 - drop20) - hsd, 2)
    assert b20["consumer_extra_cr"] == round((hsd / (1 - drop20) - hsd) * 1e9 * 92 / CR)
    # 10,000 km at 20 km/L = 500 L on E0; a 4% mileage drop -> 500/0.96 - 500 L
    extra_l, extra_rs = ns["per_vehicle"](0.04)
    assert extra_l == pytest.approx(500 / 0.96 - 500)
    assert extra_rs == pytest.approx(extra_l * 105)
    assert ns["per_vehicle"](0.0) == (0.0, 0.0)
    out = d / "outputs"
    assert len(rows(out / "fuel_energy_table.csv")) == 9
    assert len(rows(out / "blend_dilution_fiscal.csv")) == 5
    assert len(rows(out / "blend_walk_incremental.csv")) == 3
    assert len(rows(out / "diesel_biodiesel_fiscal.csv")) == 4


# ------------------------------------------------------------------ price_parity_scenarios
@pytest.fixture(scope="module")
def pp(tmp_path_factory):
    d = tmp_path_factory.mktemp("pp")
    return load("price_parity_scenarios.py", d), d


def test_price_parity_discount_rows(pp):
    ns, d = pp
    e20, e25, e30 = ns["rows"]
    assert e20["parity_discount_rs_l"] == 4.2 and e20["parity_price_rs_l"] == 100.8
    assert e30["parity_discount_rs_l"] == round(105 * 0.07, 2)
    pool = MS * 0.96 / 0.96
    assert e20["national_cost_cr"] == round(4.2 * pool * 1e9 / CR)
    assert e20["s2_excise_after_rs_l"] == round(19.90 - 4.2, 2)
    assert e20["s3_vat_after_rs_l"] == round(0.25 * 78 - 4.2, 2)
    assert e20["mileage_drop_pct"] == pytest.approx(4.0)


def test_price_parity_funding_scenarios(pp):
    ns, _ = pp
    e20 = ns["rows"][0]
    headroom = 0.2 * (19.90 + 19.5) - 0.2 * 62 * 0.05 - 0.2 * (62 - 58)
    assert e20["s1_embedded_headroom_rs_l"] == round(headroom, 2)
    assert e20["s1_coverage_x"] == round(headroom / 4.2, 2)
    assert e20["s1_coverage_x"] > 1                    # embedded tax break more than funds E20 parity
    assert e20["s4_ethanol_price_needed_rs_l"] == round(62 - 4.2 / 0.2, 2) == 41.0
    assert e20["s4_feasible_vs_grain_floor"] is False  # 41 < cheapest slab 57.97
    assert e20["s4_max_discount_rs_l"] == round((62 - 57.97) * 0.2, 2)
    assert all(r["s4_feasible_vs_grain_floor"] is False for r in ns["rows"])
    cov = [r["s1_coverage_x"] for r in ns["rows"]]
    assert cov[0] > cov[1] > cov[2]                    # coverage thins as the mileage penalty grows


def test_price_parity_slab_table_and_csv(pp):
    ns, d = pp
    prices = [p for _, p in ns["SLABS"]]
    assert prices == sorted(prices) and ns["SLABS"][0][0] == "C-heavy molasses"
    assert len(rows(d / "outputs" / "price_parity_scenarios.csv")) == 3
    assert ns["VAT_L"] == pytest.approx(19.5)
    assert ns["MS_BNL"] == pytest.approx(MS)


# ------------------------------------------------------------------ ron_octane_analysis
@pytest.fixture(scope="module")
def ron(tmp_path_factory):
    d = tmp_path_factory.mktemp("ron")
    return load("ron_octane_analysis.py", d), d


def test_ron_rows(ron):
    ns, d = ron
    assert ns["RS_PER_RON"] == pytest.approx(9.0 / 4.0)
    by = {r["blend"]: r for r in ns["rows"]}
    assert by["E20"]["bob_ron_if_pump91"] == round((91 - 0.2 * 112) / 0.8, 1)
    assert by["E20"]["pump_ron_if_bob91"] == round(0.8 * 91 + 0.2 * 112, 1) == 95.2
    assert by["E20"]["octane_credit_rs_l"] == round(0.2 * 21 * 2.25, 2) == 9.45
    assert by["E10"]["octane_credit_rs_l"] == round(0.1 * 21 * 2.25, 2)
    # higher blend -> lower BOB octane needed, higher pump octane, bigger credit
    assert by["E10"]["bob_ron_if_pump91"] > by["E30"]["bob_ron_if_pump91"]
    assert by["E10"]["pump_ron_if_bob91"] < by["E30"]["pump_ron_if_bob91"]
    assert [r["ethanol_frac"] for r in ns["rows"]] == [0.10, 0.20, 0.25, 0.27, 0.30]
    assert ns["eff_gain"] == pytest.approx(0.015 * 1.5)
    assert ns["net_e20"] == pytest.approx(0.96 * 1.0225)
    assert ns["net_e20"] < 1.0
    assert len(rows(d / "outputs" / "ron_octane_analysis.csv")) == 5


# ------------------------------------------------------------------ ethanol_supply_match
@pytest.fixture(scope="module")
def esm(tmp_path_factory):
    d = tmp_path_factory.mktemp("esm")
    return load("ethanol_supply_match.py", d), d


def test_supply_match_rows(esm):
    ns, d = esm
    r = {x["blend"]: x for x in ns["rows"]}
    L0 = 54.05 * 0.96
    eth20 = L0 / 0.96 * 0.20 * 100
    assert r["E20"]["fuel_ethanol_crL"] == round(eth20)
    assert r["E20"]["total_demand_crL"] == round(eth20 + 325)
    assert r["E20"]["util_on_2000"] == round((eth20 + 325) / 2000 * 100, 1)
    assert r["E20"]["util_on_2400"] == round((eth20 + 325) / 2400 * 100, 1)
    assert r["E20"]["fci_leg_share_pct"] == round(211 / eth20 * 100, 1)
    eth27 = L0 / (1 - 0.0625) * 0.27 * 100
    assert r["E27"]["fuel_ethanol_crL"] == round(eth27)
    assert r["E30"]["fci_leg_share_pct"] < r["E20"]["fci_leg_share_pct"]
    u = [x["util_on_2000"] for x in ns["rows"]]
    assert u == sorted(u)
    assert ns["fy31_util"] == pytest.approx((2173 + 325) / 2400 * 100)
    assert ns["fy31_util"] > 100                       # FY31 E30 demand exceeds FY27 capacity
    assert len(rows(d / "outputs" / "ethanol_supply_match.csv")) == 4


def test_supply_match_coop_wave_arithmetic(esm):
    ns, _ = esm
    assert ns["coop_klpd"] == pytest.approx(251.4 / 96.8 * 113.0)
    assert ns["coop_crl"] == pytest.approx(ns["coop_klpd"] * 330 / 1e4)
    # the three tranches add to the headline total only to within the source's rounding (10,005.4 vs 10,005)
    assert ns["NCDC_WC"] + ns["NCDC_ETH"] + ns["NCDC_COGEN"] == pytest.approx(ns["NCDC_TOTAL"], abs=0.5)


# ------------------------------------------------------------------ ethanol_sgst_sweetspot
@pytest.fixture
def sgst(tmp_path):
    return load("ethanol_sgst_sweetspot.py", tmp_path), tmp_path


def test_sgst_helpers(sgst):
    ns, _ = sgst
    assert ns["eth_price"](0.20) == pytest.approx(60.0)
    assert ns["eth_price"](0.30) == pytest.approx(68.0)
    cr, levy, eth = ns["sgst_cr"](0.20, 5)
    assert eth == pytest.approx(0.2 * 54.05)
    assert levy == pytest.approx(60 * 0.05)
    assert cr == pytest.approx(0.2 * 54.05 * 1e9 * 3.0 / CR)
    assert ns["sgst_cr"](0.20, 0)[0] == 0
    assert ns["space"](0.20) == pytest.approx(75 - 60)
    assert ns["space"](0.30) == pytest.approx(75 - 68)
    assert ns["vat_foregone_cr"](0.20) == pytest.approx(0.2 * 54.05 * 1e9 * 18 / CR)
    assert ns["sgst_cr"](0.25, 4)[0] > ns["sgst_cr"](0.25, 3)[0]


def test_sgst_main_grid_and_sweet_spot(sgst, capsys):
    ns, d = sgst
    ns["main"]()
    out = capsys.readouterr().out
    grid = rows(d / "outputs" / "ethanol_sgst_grid.csv")
    assert [r["blend"] for r in grid] == ["E20", "E22", "E25", "E27 (Brazil)", "E30"]
    e20 = grid[0]
    assert e20["sgst_5pct_cr"] == str(round(0.2 * 54.05 * 1e9 * 3.0 / CR))
    assert e20["fiscal_space_per_L"] == "15.0"
    assert e20["recovery_5pct"] == f"{60 * 5 / 100 / 18 * 100:.1f}%"
    # fleet ceiling E27: sweet spot must be E27 (Brazil), never E30
    assert "SWEET SPOT: E27 (Brazil)" in out
    assert "SWEET SPOT: E30" not in out
    assert (d / "outputs" / "ethanol_sgst_sweetspot.md").exists()


def test_sgst_sweet_spot_respects_ceiling_boundary(sgst, capsys):
    ns, _ = sgst
    ns["FLEET_CEILING"] = 0.30          # E30 now feasible -> becomes the sweet spot
    ns["main"]()
    assert "SWEET SPOT: E30" in capsys.readouterr().out
    ns["FLEET_CEILING"] = 0.25 - 1e-12  # inside the 1e-9 tolerance -> E25 still feasible
    ns["main"]()
    assert "SWEET SPOT: E25" in capsys.readouterr().out
    ns["FLEET_CEILING"] = 0.25 - 2e-9   # outside the tolerance -> E22 is the highest feasible blend
    ns["main"]()
    assert "SWEET SPOT: E22" in capsys.readouterr().out


# ------------------------------------------------------------------ petrol_demand_forecast
@pytest.fixture
def pdf(tmp_path):
    return load("petrol_demand_forecast.py", tmp_path), tmp_path


def test_project_compounds_each_year(pdf):
    ns, _ = pdf
    assert ns["project"]([0.1, 0.1]) == pytest.approx([44.0, 48.4])
    assert ns["project"]([]) == []
    assert ns["project"]([0.0]) == [40.0]
    assert ns["MMT_TO_BNL"] == pytest.approx(1 / 0.74)
    assert ns["project"]([-0.5])[0] == pytest.approx(20.0)


def test_demand_forecast_outputs(pdf, capsys):
    ns, d = pdf
    ns["main"]()
    out = capsys.readouterr().out
    dem = rows(d / "outputs" / "petrol_demand_forecast.csv")
    assert [r["scenario"] for r in dem] == ["High (7% trend)", "Base (FADA-moderating)", "Low (fast-EV, 3%)"]
    hi = dem[0]
    assert float(hi["FY25-26_MMT"]) == round(40 * 1.07, 1)
    assert float(hi["FY30-31_MMT"]) == round(40 * 1.07 ** 6, 1)
    assert float(hi["FY25-26_bnL"]) == round(40 * 1.07 / 0.74, 1)
    base = ns["project"](ns["GROWTH"]["Base (FADA-moderating)"])
    assert float(dem[1]["FY27-28_MMT"]) == round(base[2], 1)
    eth = rows(d / "outputs" / "ethanol_requirement_forecast.csv")
    assert int(eth[0]["FY25-26_ethanol_croreL"]) == round(40 * 1.07 / 0.74 * 0.20 * 100)
    assert int(eth[1]["FY30-31_ethanol_croreL"]) == round(base[5] / 0.74 * 0.30 * 100)
    assert int(eth[0]["FY30-31_ethanol_croreL"]) > int(eth[2]["FY30-31_ethanol_croreL"])
    assert "Base ethanol requirement" in out and "CAGR" in out
    assert (d / "outputs" / "petrol_demand_forecast.md").exists()


def test_growth_scenarios_ordered_every_year(pdf):
    ns, _ = pdf
    g = ns["GROWTH"]
    for i in range(6):
        assert g["High (7% trend)"][i] >= g["Base (FADA-moderating)"][i] >= g["Low (fast-EV, 3%)"][i]
    base = g["Base (FADA-moderating)"]
    assert base == sorted(base, reverse=True)          # FADA moderation: growth only declines


# ------------------------------------------------------------------ petrol_export_value
@pytest.fixture
def pev(tmp_path):
    return load("petrol_export_value.py", tmp_path), tmp_path


def test_export_realisation_formulas(pev):
    ns, _ = pev
    lpt = 1000 / 0.7087
    assert ns["realisation_rs_per_l"](15.8, 98379) == pytest.approx(98379 * CR / (15.8e6 * lpt))
    assert ns["realisation_usd_per_t"](15.8, 11.6) == pytest.approx(11.6e9 / 15.8e6)
    assert ns["realisation_usd_per_t"](10, 5) == 500.0
    assert ns["L_PER_TONNE"] == pytest.approx(1411.0, abs=0.2)


def test_export_value_rows(pev, capsys):
    ns, d = pev
    ns["main"]()
    capsys.readouterr()
    tr = rows(d / "outputs" / "petrol_export_trend.csv")
    assert [r["fy"] for r in tr] == ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]
    assert float(tr[-1]["realisation_rs_per_L"]) == round(ns["realisation_rs_per_l"](15.8, 98379), 1)
    assert int(tr[0]["realisation_usd_per_t"]) == round(5.0e9 / 11.6e6)
    val = rows(d / "outputs" / "petrol_export_value.csv")
    assert [r["blend"] for r in val] == ["E20", "E25", "E30"]
    central = round(ns["realisation_rs_per_l"](15.8, 98379), 1)
    e20 = val[0]
    assert float(e20["freed_bnL"]) == round(0.2 * 54.05, 2)
    assert float(e20["freed_MMT"]) == round(0.2 * 54.05 / (1000 / 0.7087 / 1000), 2)
    assert int(e20["export_value_cr_central"]) == round(0.2 * 54.05 * 1e9 * central / CR)
    lows = min(float(t["realisation_rs_per_L"]) for t in tr)
    highs = max(float(t["realisation_rs_per_L"]) for t in tr)
    assert int(e20["export_value_cr_low"]) == round(0.2 * 54.05 * 1e9 * lows / CR)
    assert int(e20["export_value_cr_high"]) == round(0.2 * 54.05 * 1e9 * highs / CR)
    assert int(e20["export_value_cr_low"]) < int(e20["export_value_cr_central"]) <= int(e20["export_value_cr_high"])
    assert int(e20["vs_current_exports_pct"]) == round(100 * (0.2 * 54.05 / (1000 / 0.7087 / 1000)) / 15.8)
    assert int(val[2]["export_value_cr_central"]) > int(val[0]["export_value_cr_central"])
