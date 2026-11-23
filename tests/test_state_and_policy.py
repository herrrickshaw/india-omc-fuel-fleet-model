"""State-wise tax model (fake PPAC tables), Vahan state/fuel scripts, upstream, refining,
policy and the Excel builder. All inputs are synthetic or the scripts' own embedded tables."""
import csv
import math
import sys

import pytest
from loader import ROOT, load

CR = 1e7


def rows(path):
    return list(csv.DictReader(open(path)))


# ------------------------------------------------------------------ statewise_tax_impact
MS_ROWS = [
    ["Table 6.4(B)", "", "", "", "", ""],
    ["State", "FY22", "FY23", "FY24", "FY25", "x"],
    ["Region North", "9", "9", "9", "999999", "x"],           # 'region' rows are skipped
    ["Alpha", "1", "1", "1", "1000", "x"],
    ["Beta Land", "1", "1", "1", "500", "x"],
    ["Maharashtra", "1", "1", "1", "2000", "x"],
    ["Gamma", "1", "1", "1", "n/a", "x"],                      # non-numeric FY25 -> skipped
    ["Delta", "1", "1", "1", "300", "x"],                      # no VAT entry -> unmatched
    ["Short", "1", "2"],                                       # fewer than 6 cells -> skipped
    ["Five", "1", "1", "1", "777"],                            # exactly 5 cells -> still skipped (needs 6)
    ["", "1", "1", "1", "5", "x"],                             # blank state -> skipped
    ["All-India Total", "1", "1", "1", "3800", "x"],           # 'total' rows are skipped
    ["MS (TMT)", "1", "1", "1", "7", "x"],                     # startswith('ms ') -> skipped
]
VAT_ROWS = [
    ["Table 8.17", "State", "Rate"],
    ["Sl", "State", "Petrol"],
    ["1", "Alpha", "25% + Rs 2/L cess"],
    ["2", "Beta Land", "20.5 % ad valorem"],
    ["3", "Maharashtra - Mumbai", "26%"],
    ["4", "Maharashtra (Rest)", "25.5%"],
    ["5", "Gamma", "30%"],
    ["6", "Epsilon", "no percentage here"],
    ["7", "x"],
]


def write_csv(path, rws):
    with open(path, "w", newline="") as fh:
        csv.writer(fh).writerows(rws)


@pytest.fixture
def tax(tmp_path, monkeypatch):
    home = tmp_path / "home"
    d = home / "ppac-ready-reckoner-data" / "annual_fy2025-26_h1" / "csv"
    d.mkdir(parents=True)
    write_csv(d / "Table_6.4(B)_state_ms.csv", MS_ROWS)
    write_csv(d / "Table_8.17_vat.csv", VAT_ROWS)
    monkeypatch.setenv("HOME", str(home))
    return load("statewise_tax_impact.py", tmp_path / "run"), tmp_path / "run"


def test_norm_strips_everything_but_letters(tax):
    ns, _ = tax
    assert ns["norm"]("Dadra & Nagar-Haveli (UT) 2") == "dadranagarhaveliut"
    assert ns["norm"]("") == ""


def test_load_ms_filters_and_converts_tmt_to_litres(tax):
    ns, _ = tax
    ms = ns["load_ms"]()
    assert set(ms) == {"alpha", "betaland", "maharashtra", "delta"}
    assert ms["alpha"] == ("Alpha", pytest.approx(1000 * 1e6 / 0.74))
    assert ms["maharashtra"][1] == pytest.approx(2000 * 1e6 / 0.74)


def test_load_vat_takes_first_percentage_only(tax):
    ns, _ = tax
    vat = ns["load_vat"]()
    assert vat["alpha"] == ("Alpha", pytest.approx(0.25))          # not the cess
    assert vat["betaland"][1] == pytest.approx(0.205)              # '20.5 %' with a space
    assert vat["maharashtramumbai"][1] == pytest.approx(0.26)
    assert "epsilon" not in vat                                    # no % -> dropped
    assert "state" not in vat and "sl" not in vat                  # header rows dropped


def test_match_vat_exact_then_prefix_shortest(tax):
    ns, _ = tax
    vat = ns["load_vat"]()
    assert ns["match_vat"]("alpha", vat)[1] == pytest.approx(0.25)
    # no exact 'maharashtra': prefix candidates sorted by key length -> 'maharashtrarest' (15) beats 'maharashtramumbai' (17)
    assert ns["match_vat"]("maharashtra", vat)[0] == "Maharashtra (Rest)"
    assert ns["match_vat"]("nowhere", vat) is None


def test_main_state_losses_hand_computed(tax, capsys):
    ns, d = tax
    ns["main"]()
    out = capsys.readouterr().out
    assert "Matched 3 states." in out                                 # Delta has no VAT row
    e20 = rows(d / "outputs" / "statewise_tax_E20.csv")
    by = {r["state"]: r for r in e20}
    assert set(by) == {"Alpha", "Beta Land", "Maharashtra"}
    eth_l = 1000 * 1e6 / 0.74 * 0.20
    vat_lost = eth_l * 0.25 * 78.0 / CR
    sgst = eth_l * (60.0 * 0.05 * 0.5) / CR
    a = by["Alpha"]
    assert int(a["vat_lost_cr"]) == round(vat_lost)
    assert int(a["sgst_gain_cr"]) == round(sgst)
    assert int(a["net_state_loss_cr"]) == round(vat_lost - sgst)
    assert float(a["vat_pct"]) == 25.0 and float(a["ms_bnL"]) == round(1000 / 0.74 / 1e3, 2)
    assert float(by["Maharashtra"]["vat_pct"]) == 25.5            # split-state row resolved via match_vat
    # sorted descending by net loss (Maharashtra: 2x volume at 25.5% beats Alpha)
    assert [r["state"] for r in e20] == ["Maharashtra", "Alpha", "Beta Land"]
    nets = [int(r["net_state_loss_cr"]) for r in e20]
    assert nets == sorted(nets, reverse=True)
    e30 = {r["state"]: r for r in rows(d / "outputs" / "statewise_tax_E30.csv")}
    assert int(e30["Alpha"]["vat_lost_cr"]) == round(vat_lost * 1.5)
    assert (d / "outputs" / "statewise_tax_E25.csv").exists()
    md = (d / "outputs" / "statewise_tax_impact.md").read_text()
    assert "3 states matched" in md and "Top 15 states" in md


def test_missing_input_tables_fail_fast(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "empty"))
    with pytest.raises(StopIteration):
        load("statewise_tax_impact.py", tmp_path / "run")


# ------------------------------------------------------------------ vahan state scripts
@pytest.fixture
def vahan_path(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT + "/vahan"))
    before = set(sys.modules)
    yield
    for k in set(sys.modules) - before:
        sys.modules.pop(k, None)


@pytest.fixture
def sfa(tmp_path):
    return load("vahan/statewise_fuel_analysis.py", tmp_path), tmp_path


def test_state_matrix_is_internally_consistent(sfa):
    ns, _ = sfa
    assert len(ns["DATA"]) == 36 == len({d[0] for d in ns["DATA"]})
    for st, p, d, c, e, h, tot in ns["DATA"]:
        assert min(p, d, c, e, h) >= 0
        assert p + d + c + e + h <= tot, st            # categories never exceed the state total
    assert ns["COLS"] == ["Petrol", "Diesel", "CNG", "EV", "StrongHybrid", "Total"]


def test_statewise_leaders_and_small_state_floor(sfa, capsys):
    ns, d = sfa
    ns["main"]()
    out = capsys.readouterr().out
    data = ns["DATA"]
    top_total = max(data, key=lambda r: r[6])
    assert f"Biggest market: {top_total[0]} {top_total[6]:,}" in out
    md = (d / "vahan" / "outputs" / "statewise_fuel_analysis.md").read_text()
    # share leaders only rank states with >= 20,000 registrations
    eligible = [r for r in data if r[6] >= 20000]
    best_ev = max(eligible, key=lambda r: r[4] / r[6])
    assert f"| **EV share** | {best_ev[0]} ({100 * best_ev[4] / best_ev[6]:.0f}%)" in md
    diesel = sorted(eligible, key=lambda r: r[2] / r[6], reverse=True)[:3]
    assert "| **Diesel share** | " + " | ".join(f"{r[0]} ({100 * r[2] / r[6]:.0f}%)" for r in diesel) in md
    assert "Arunachal Pradesh" in md and "Nagaland" not in md.split("Diesel share")[1].splitlines()[0]
    small = [r[0] for r in data if r[6] < 20000]
    assert small and not any(f"| {s} (" in md for s in small)
    csvrows = rows(d / "vahan" / "outputs" / "statewise_fuel_cy2026.csv")
    assert len(csvrows) == 36 and csvrows[0]["state"] == "Andaman & Nicobar"
    assert int(csvrows[0]["Total"]) == 6892
    assert md.count("| **") >= 10


@pytest.fixture
def conc(tmp_path, vahan_path):
    return load("vahan/statewise_concentration.py", tmp_path), tmp_path


def test_concentration_metrics(conc):
    ns, _ = conc
    tot = sum(d[6] for d in ns["DATA"])
    ser = ns["series"]("Total")
    assert [v for _, v in ser] == sorted((v for _, v in ser), reverse=True)
    assert sum(v for _, v in ser) == tot
    assert ns["topn_share"]("Total", 1) == pytest.approx(ser[0][1] / tot)
    assert ns["topn_share"]("Total", 36) == pytest.approx(1.0)
    assert ns["topn_share"]("Total", 0) == 0
    shares = [v / tot for _, v in ser]
    assert ns["hhi"]("Total") == pytest.approx(sum(s * s for s in shares) * 10000)
    assert 10000 / 36 < ns["hhi"]("Total") < 10000
    n50 = ns["cum_to"]("Total", 0.5)
    assert sum(v for _, v in ser[:n50]) / tot >= 0.5 > sum(v for _, v in ser[:n50 - 1]) / tot
    assert ns["cum_to"]("Total", 0.8) > n50
    assert ns["cum_to"]("Total", ser[0][1] / tot) == 1          # share exactly met by the top state counts (>=)
    assert ns["cum_to"]("Total", ser[0][1] / tot + 1e-9) == 2
    assert ns["cum_to"]("Total", 1.0) <= 36
    assert ns["cum_to"]("Total", 1.1) == 36                # unreachable threshold falls through to len
    assert ns["hhi"]("CNG") > ns["hhi"]("Petrol")          # CNG is the more concentrated fuel


def test_concentration_main_outputs(conc, capsys):
    ns, d = conc
    ns["main"]()
    out = capsys.readouterr().out
    cum = rows(d / "vahan" / "outputs" / "statewise_cumulative_total.csv")
    assert len(cum) == 36 and cum[0]["rank"] == "1"
    assert float(cum[-1]["cumulative_pct"]) == pytest.approx(100.0, abs=0.05)
    cps = [float(r["cumulative_pct"]) for r in cum]
    assert cps == sorted(cps)
    assert "states to 50%" in out and "CNG" in out
    md = (d / "vahan" / "outputs" / "statewise_concentration.md").read_text()
    assert md.count("concentrated") >= 1


# ------------------------------------------------------------------ vahan fuel classifier
@pytest.fixture
def vf(tmp_path):
    return load("vahan/analyze_vahan_fuel.py", tmp_path), tmp_path


@pytest.mark.parametrize("label,group", [
    ("LPG ONLY", "LPG (dedicated)"),
    ("CNG ONLY", "CNG/CBG (dedicated)"),
    ("DUAL DIESEL/CNG", "Diesel"),                   # diesel is tested before CNG
    ("DUAL DIESEL/LNG", "Diesel"),
    ("PETROL/METHANOL", "Petrol (mono, incl. E20 & hybrid)"),
    ("PETROL(E20)/HYBRID/CNG", "Petrol + gas bi-fuel (CNG/LPG)"),   # bi-fuel beats hybrid
    ("DIESEL/HYBRID", "Diesel"),
    ("ETHANOL(E100)", "Ethanol (E100/flex)"),
    ("LNG", "Other (H2/LNG/methanol/solar/NA)"),
    ("SOLAR", "Other (H2/LNG/methanol/solar/NA)"),
    ("ELECTRIC(BOV)", "Electric (BEV/PHEV)"),
    ("DI-METHYL ETHER", "Other (H2/LNG/methanol/solar/NA)"),
])
def test_classify_precedence(vf, label, group):
    assert vf[0]["classify"](label) == group


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason='classify() tests `"ETHANOL" in f`, which also matches "METHANOL"; the CUM table\'s '
                          '"METHANOL" label lands in Ethanol (E100/flex) instead of Other')
def test_classify_plain_methanol_is_not_ethanol(vf):
    assert vf[0]["classify"]("METHANOL") == "Other (H2/LNG/methanol/solar/NA)"


def test_is_e20_and_broad(vf):
    ns, _ = vf
    assert ns["is_e20"]("PETROL(E20)") and ns["is_e20"]("PETROL(E20)/CNG")
    assert not ns["is_e20"]("PETROL") and not ns["is_e20"]("ETHANOL(E100)")
    assert [ns["broad"](c) for c in ("2WIC", "2WT", "3WIC", "3WN", "4WIC", "HGV", "OTH")] == \
        ["2W", "2W", "3W", "3W", "4W+", "4W+", "4W+"]


def test_group_totals_covers_every_label_and_conserves(vf):
    ns, _ = vf
    g = ns["group_totals"]({"PETROL": 10, "PURE EV": 5, "WEIRD NEW FUEL": 3})
    assert g["Petrol (mono, incl. E20 & hybrid)"] == 10
    assert g["Electric (BEV/PHEV)"] == 5
    assert g["Other (H2/LNG/methanol/solar/NA)"] == 3
    assert list(g) == ns["GROUP_ORDER"]
    assert sum(ns["group_totals"](ns["CUM"]).values()) == ns["CUM_GRAND"]


def test_main_writes_summaries_that_foot(vf):
    ns, d = vf
    ns["main"]()
    summ = rows(d / "vahan" / "outputs" / "fuel_group_summary.csv")
    assert summ[-1]["fuel_group"] == "TOTAL"
    assert sum(int(r["cy2025_vehicles"]) for r in summ[:-1]) == int(summ[-1]["cy2025_vehicles"]) == ns["GRAND"]
    assert sum(int(r["cumulative_vehicles"]) for r in summ[:-1]) == ns["CUM_GRAND"]
    shares = sum(float(r["cy2025_share_pct"]) for r in summ[:-1])
    assert shares == pytest.approx(100.0, abs=0.1)
    by_class = rows(d / "vahan" / "outputs" / "fuel_by_class.csv")
    total = by_class[-1]
    assert by_class[0]["fuel_group"] == ns["GROUP_ORDER"][0]
    assert sum(int(total[c]) for c in ("2W", "3W", "4W+")) == ns["GRAND"]
    cum = rows(d / "vahan" / "vahan_fuel_registrations_cumulative.csv")
    assert int(cum[0]["cumulative_registrations"]) == max(ns["CUM"].values())   # sorted desc
    assert cum[0]["fuel"] == "PETROL" and cum[0]["group"] == "Petrol (mono, incl. E20 & hybrid)"
    raw = rows(d / "vahan" / "vahan_fuel_registrations_cy2025.csv")
    assert len(raw) == len(ns["RAW"]) and list(raw[0])[-1] == "TOTAL"
    assert (d / "vahan" / "outputs" / "vahan_fuel_analysis.md").exists()


def test_main_asserts_on_row_total_mismatch(vf):
    ns, _ = vf
    f, counts, t = ns["RAW"][0]
    ns["RAW"][0] = (f, counts, t + 1)
    with pytest.raises(AssertionError, match="row/total mismatch"):
        ns["main"]()


# ------------------------------------------------------------------ upstream
@pytest.fixture
def up(tmp_path):
    return load("upstream/upstream_acreage_analysis.py", tmp_path), tmp_path


def test_upstream_cagr_and_change(up):
    ns, _ = up
    assert ns["chg"]([100, 150]) == pytest.approx(0.5)
    assert ns["cagr"]([100, 121, 144.1]) == pytest.approx((144.1 / 100) ** 0.5 - 1)
    assert ns["cagr"]([0, 5, 10]) == 0                         # zero base -> defined as 0, no ZeroDivisionError
    assert ns["cagr"]([100, 50]) == pytest.approx(-0.5)
    with pytest.raises(ZeroDivisionError):
        ns["chg"]([0, 5])


def test_upstream_tables_partition_and_rank(up):
    ns, _ = up
    assert sorted(ns["ONSHORE"] + ns["OFFSHORE"]) == sorted(ns["CRUDE"])
    assert all(len(v) == len(ns["FY"]) == 6 for v in ns["CRUDE"].values())
    assert len(ns["SELF_SUFFICIENCY"]) == 6
    for b in ns["BLOCKS"].values():
        assert b["operational"] <= b["awarded"] <= b["offered"]
    assert ns["CBM"]["established_TCF"] < ns["CBM"]["prognosticated_TCF"]
    assert ns["CBM"]["area_explored_sqkm"] < ns["CBM"]["area_total_sqkm"]


def test_upstream_main_totals(up):
    ns, d = up
    ns["main"]()
    tr = rows(d / "upstream" / "outputs" / "crude_production_trend.csv")
    by = {r["source"]: r for r in tr}
    on = [sum(ns["CRUDE"][k][i] for k in ns["ONSHORE"]) for i in range(6)]
    off = [sum(ns["CRUDE"][k][i] for k in ns["OFFSHORE"]) for i in range(6)]
    assert [int(by["ONSHORE TOTAL"][fy]) for fy in ns["FY"]] == on
    assert [int(by["TOTAL"][fy]) for fy in ns["FY"]] == [a + b for a, b in zip(on, off)]
    assert float(by["TOTAL"]["chg_5yr_pct"]) == round((((on[-1] + off[-1]) / (on[0] + off[0])) - 1) * 100, 1)
    kg = by["Eastern Offshore (KG deepwater)"]
    assert float(kg["chg_5yr_pct"]) == round((2437 / 557 - 1) * 100, 1)
    rec = rows(d / "upstream" / "outputs" / "new_area_recommendations.csv")
    assert [r["rank"] for r in rec] == [str(i) for i in range(1, len(ns["RECS"]) + 1)]
    assert (d / "upstream" / "outputs" / "upstream_acreage_analysis.md").exists() or any(
        (d / "upstream" / "outputs").glob("*.md"))


# ------------------------------------------------------------------ refining
@pytest.fixture
def rta(tmp_path):
    return load("refining/refining_trade_analysis.py", tmp_path), tmp_path


def test_refining_summary_derivations(rta, capsys):
    ns, d = rta
    ns["main"]()
    capsys.readouterr()
    r = {x["metric"]: x for x in rows(d / "refining" / "outputs" / "refining_trade_summary.csv")}
    hs = ns["HS27"]
    net = hs["imports_2024"] - hs["exports_2024"]
    assert float(r["HS-27 net (deficit)"]["value"]) == pytest.approx(-net)
    deficit = hs["total_imports_2024"] - hs["total_exports_2024"]
    assert float(r["HS-27 share of total trade deficit"]["value"]) == round(net / deficit * 100, 1)
    rr = ns["RR"]
    crude = rr["crude_import_usdbn"] * 1e9 / (rr["crude_import_MMT"] * 1e6 * 7.33)
    prod = rr["product_export_usdbn"] * 1e9 / (rr["product_export_MMT"] * 1e6 * 8.0)
    assert float(r["Crude cost"]["value"]) == round(crude, 1)
    assert float(r["Product realisation"]["value"]) == round(prod, 1)
    assert float(r["Implied gross value-add"]["value"]) == round(prod - crude, 1)
    assert prod > crude                     # exporting products earns more per barrel than crude costs


def test_refining_embedded_tables_are_consistent(rta):
    ns, _ = rta
    rr = ns["RR"]
    assert rr["crude_import_MMT"] + rr["product_import_MMT"] == pytest.approx(rr["total_oil_import_MMT"])
    # the dollar columns add to 160.9 against a published 160.8 total: source rounding, not a defect
    assert rr["crude_import_usdbn"] + rr["product_import_usdbn"] == pytest.approx(rr["total_oil_import_usdbn"], abs=0.15)
    assert rr["petrol_export_MMT"] + rr["diesel_export_MMT"] <= rr["product_export_MMT"]
    assert ns["RR_TREND"]["2024-25"] == (rr["total_oil_import_usdbn"], rr["product_export_usdbn"])
    assert ns["HS27"]["exports_2024"] < ns["HS27"]["exports_2023"]


@pytest.fixture
def efx(tmp_path):
    return load("refining/ethanol_forex_substitution.py", tmp_path), tmp_path


def test_ethanol_forex_rows(efx):
    ns, d = efx
    ns["main"]()
    out = rows(d / "refining" / "outputs" / "ethanol_forex_substitution.csv")
    assert [r["blend"] for r in out] == ["E20", "E25", "E30"]
    freed = 0.2 * 54.05
    mmt = freed / 1.4110
    e20 = out[0]
    assert float(e20["freed_petrol_bnL"]) == round(freed, 2)
    assert float(e20["freed_MMT"]) == round(mmt, 2)
    assert float(e20["petchem_MMT"]) == round(mmt * 0.6, 2)
    assert float(e20["forex_petrol_usdbn"]) == round(freed * 85.0 / 159.0, 2)
    assert float(e20["forex_petchem_usdbn"]) == round(mmt * 0.6 * 1100.0 / 1e3, 2)
    assert int(e20["ethanol_rupee_cr"]) == round(freed * 1e9 * 60.0 / CR)
    assert int(e20["petchem_import_share_pct"]) == round(mmt * 0.6 / 13.0 * 100)
    assert float(out[2]["freed_MMT"]) > float(e20["freed_MMT"])


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="the generated report says cracked petrochemicals are 'worth even more' than "
                          "crude-saved/exported petrol, but the model's own 60% yield x $1,100/t gives "
                          "$5.06 bn vs $5.78 bn at E20")
def test_ethanol_forex_report_claim_petchem_beats_petrol(efx):
    ns, d = efx
    ns["main"]()
    e20 = rows(d / "refining" / "outputs" / "ethanol_forex_substitution.csv")[0]
    assert float(e20["forex_petchem_usdbn"]) > float(e20["forex_petrol_usdbn"])


@pytest.fixture
def pis(tmp_path):
    return load("refining/petchem_import_substitution.py", tmp_path), tmp_path


def test_petchem_product_tree_is_well_formed(pis):
    ns, _ = pis
    P = ns["PRODUCTS"]
    assert {p[1] for p in P} <= set(ns["BLOCKS"]) and len({p[1] for p in P}) == 7
    assert {p[4] for p in P} <= {"High", "Med", "Low"}
    assert all(p[6].strip() for p in P)                           # every row carries an HSN reference
    assert len({p[0] for p in P}) == len(P)
    assert all(p[3] is None or p[3] > 0 for p in P)


def test_petchem_csv_converts_rupees_to_dollars(pis):
    ns, d = pis
    ns["main"]()
    out = rows(d / "refining" / "outputs" / "petchem_import_substitution.csv")
    assert len(out) == len(ns["PRODUCTS"])
    pe = next(r for r in out if r["product"].startswith("Polyethylene"))
    assert float(pe["import_value_usdbn"]) == round(17467 * CR / 86.0 / 1e9, 2)
    assert pe["feedstock_root"] == ns["BLOCKS"]["Ethylene"]
    blank = next(r for r in out if r["product"].startswith("Ethanolamines"))
    assert blank["import_value_cr"] == "" and blank["import_value_usdbn"] == ""


# ------------------------------------------------------------------ policy
@pytest.fixture
def pol(tmp_path):
    return load("policy/forex_essentials_pli_case.py", tmp_path), tmp_path


def test_policy_totals_and_shares(pol, capsys):
    ns, d = pol
    ns["main"]()
    out = capsys.readouterr().out
    ess = sum(r[1] for r in ns["IMPORTS"] if r[2])
    energy = sum(r[1] for r in ns["IMPORTS"] if r[0] in ("Crude oil", "Coal & coke", "LNG + LPG (petroleum gases)"))
    assert f"Essential-import forex ≈ ${ess} bn" in out and f"energy ${energy} bn" in out
    assert ess > energy
    csvr = rows(d / "policy" / "outputs" / "forex_essentials.csv")
    assert float(csvr[0]["share_of_imports_pct"]) == round(100 * 137 / 718.16, 1)
    assert [r["essential"] for r in csvr].count("True") == len([r for r in ns["IMPORTS"] if r[2]])
    assert sum(r[1] for r in ns["IMPORTS"]) < ns["TOTAL_IMPORTS_USDBN"]
    assert ns["CHEM_PLI"]["substitutable_petchem_cr"] < ns["CHEM_PLI"]["moc_chem_import_cr"]
    # chemicals is the one large essential drain flagged as missing a PLI
    assert [r[0] for r in ns["IMPORTS"] if r[4].startswith("NO")] == ["Chemicals (organic HS-29 + plastics HS-39)"]


# ------------------------------------------------------------------ Excel builder
openpyxl = pytest.importorskip("openpyxl")


@pytest.fixture(scope="module")
def wb(tmp_path_factory):
    d = tmp_path_factory.mktemp("xlsx")
    (d / "outputs").mkdir()
    load("build_xlsx.py", d)
    omc = load("omc_model.py", tmp_path_factory.mktemp("omc2"))
    book = openpyxl.load_workbook(d / "outputs" / "OMC_Retail_Profitability_Model.xlsx")
    return book, omc


def test_workbook_sheets_and_inputs_match_python_model(wb):
    book, omc = wb
    assert book.sheetnames == ["Inputs", "Base", "Scenarios", "BlendMix", "Projection", "Checks"]
    vals = {book["Inputs"].cell(r, 1).value: book["Inputs"].cell(r, 2).value for r in range(4, 21)}
    assert vals["Retail outlets (01.10.2025)"] == omc["N_RO_2025"]
    assert vals["Outlets prior year (01.10.2024)"] == omc["N_RO_2024"]
    assert vals["Petrol (MS) consumption FY24-25"] == omc["MS_MMT_FY2425"]
    assert vals["Diesel (HSD) consumption FY24-25"] == omc["HSD_MMT_FY2425"]
    assert vals["OMC marketing margin — petrol"] == omc["OMC_MARGIN_MS"]
    assert vals["OMC marketing margin — diesel"] == omc["OMC_MARGIN_HSD"]
    assert vals["Petrol demand growth (vehicle-driven)"] == omc["MS_GROWTH"]
    assert vals["Diesel demand growth (vehicle-driven)"] == omc["HSD_GROWTH"]
    assert vals["Outlet network growth"] == omc["RO_GROWTH"]
    for tag in ("E20", "E25", "E30"):
        assert vals[f"{tag} blend %"] == omc["BLEND"][tag]["pct"]
        assert vals[f"{tag} mileage drop"] == omc["BLEND"][tag]["mileage_drop"]


def test_workbook_mix_rows_match_python_mix_scenarios(wb):
    book, omc = wb
    mx = book["BlendMix"]
    for i, (name, shares) in enumerate(omc["MIX_SCENARIOS"].items()):
        r = 5 + i
        assert mx.cell(r, 1).value == name
        assert tuple(mx.cell(r, c).value for c in (2, 3, 4, 5)) == shares
        assert sum(shares) == pytest.approx(1.0)
        assert mx.cell(r, 6).value == f"=SUM(B{r}:E{r})"


def test_workbook_formulas_reference_inputs_and_roadmap(wb):
    book, omc = wb
    b = book["Base"]
    assert b["B4"].value == "=(Inputs!$B$6*1000/Inputs!$B$8)/1000"
    assert b["B6"].value == "=B4*1000000000*B5/10000000"
    assert b["D6"].value == "=B6+C6"
    s = book["Scenarios"]
    assert [s.cell(r, 1).value for r in (5, 6, 7)] == ["E20", "E25", "E30"]
    assert s["H5"].value == "=G5*1000000000*Inputs!$B$10/10000000"
    p = book["Projection"]
    assert [p.cell(4 + i, 1).value for i in range(5)] == list(omc["ROADMAP"])
    # roadmap -> mileage-drop input row: E20,E20,E25,E25,E30
    drop_row = {"E20": "$B$16", "E25": "$B$18", "E30": "$B$20"}
    for i, tag in enumerate(omc["ROADMAP"].values()):
        assert p.cell(4 + i, 2).value == "=Inputs!" + drop_row[tag]
    assert p["G4"].value in ("", None) and p["G5"].value == "=F5-F4"
    assert "^4" in p["C8"].value and "^0" in p["C4"].value
    ck = book["Checks"]
    assert ck.max_row - 3 == 9
    assert all('"PASS","FAIL"' in ck.cell(r, 2).value for r in range(4, 13))
