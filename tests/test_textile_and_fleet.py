"""textile_data analysis scripts (synthetic TradeStat JSON, no repo data), the PowerPoint
builder (save redirected to tmp_path) and fleet_from_fuel via the coverage-aware loader."""
import csv
import json

import pytest
from loader import load

pd = pytest.importorskip("pandas")


def rows(path):
    return list(csv.DictReader(open(path)))


def lay_out(tmp_path, payload, script_dir="analysis"):
    raw = tmp_path / "textile_data" / "raw"
    raw.mkdir(parents=True)
    (raw / "tradestat_hsn_2018-26.json").write_text(json.dumps(payload))
    return tmp_path


# ------------------------------------------------------------------ chapter_level_analysis
CHAPTER_JSON = {
    "source": "synthetic", "retrieved": "2026-01-01", "years_covered": "2018-26",
    "by_chapter": {
        "export": {"52": {"2024 - 2025": 900.0}, "39": {"2024 - 2025": 100.0}, "61": {"2024 - 2025": 500.0},
                   "54": {"2023 - 2024": 7.0}},
        "import": {"52": {"2024 - 2025": 400.0}, "39": {"2024 - 2025": 700.0}, "61": {"2024 - 2025": 500.0}},
    },
}


@pytest.fixture
def chap(tmp_path):
    lay_out(tmp_path, CHAPTER_JSON)
    return load("textile_data/analysis/chapter_level_analysis.py", tmp_path)


def test_extract_chapter_data_net_and_status_boundary(chap):
    ns = chap
    t = ns["extract_chapter_data"](CHAPTER_JSON)
    assert set(t) == set(ns["TEXTILE_CHAPTERS"])
    assert t["52"] == {"name": "Cotton", "exports": 900.0, "imports": 400.0, "net": 500.0, "status": "Surplus"}
    assert t["39"]["net"] == -600.0 and t["39"]["status"] == "Deficit"
    assert t["61"]["net"] == 0.0 and t["61"]["status"] == "Deficit"      # exports == imports is not a surplus
    assert t["54"]["exports"] == 0 and t["54"]["imports"] == 0           # wrong FY key -> zero, not KeyError
    assert ns["extract_chapter_data"]({})["29"]["status"] == "Deficit"   # empty payload tolerated


def test_create_chapter_analysis_rounds_and_sorts(chap):
    ns = chap
    t = {"B": {"name": "b", "exports": 1.26, "imports": 0.0, "net": 1.26, "status": "Surplus"},
         "A": {"name": "a", "exports": 0.0, "imports": 2.04, "net": -2.04, "status": "Deficit"}}
    df = ns["create_chapter_analysis"](t)
    assert list(df["chapter"]) == ["A", "B"]
    assert list(df.columns) == ["chapter", "name", "exports_usd_mn", "imports_usd_mn", "net_usd_mn", "trade_balance"]
    assert df.loc[1, "exports_usd_mn"] == 1.3 and df.loc[0, "net_usd_mn"] == -2.0


def test_chapter_main_writes_csv_and_reports_deficits(tmp_path, capsys):
    lay_out(tmp_path, CHAPTER_JSON)
    ns = load("textile_data/analysis/chapter_level_analysis.py", tmp_path)
    ns["main"]()
    out = capsys.readouterr().out
    res = rows(tmp_path / "textile_data" / "processed" / "chapter_trade_fy25.csv")
    assert len(res) == len(ns["TEXTILE_CHAPTERS"])
    by = {r["chapter"]: r for r in res}
    assert by["39"]["trade_balance"] == "Deficit" and float(by["39"]["net_usd_mn"]) == -600.0
    assert "Data Source: synthetic" in out
    assert "Exports: $100.0bn | Imports: $700.0bn | Deficit: $600.0bn" in out
    first_deficit = out.split("IMPORT DEFICITS")[1].splitlines()[1]
    assert "Ch 39" in first_deficit                      # largest deficit listed first


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="values are USD millions (column exports_usd_mn) but main() prints them with a "
                          "'bn' suffix, e.g. 'Deficit: $600.0bn' for a 600 USD-mn gap")
def test_chapter_main_units_are_consistent(tmp_path, capsys):
    lay_out(tmp_path, CHAPTER_JSON)
    ns = load("textile_data/analysis/chapter_level_analysis.py", tmp_path)
    ns["main"]()
    assert "Deficit: $600.0bn" not in capsys.readouterr().out


# ------------------------------------------------------------------ segment_trade_extractor
def rec(year, month, hsn, exp, imp):
    return {"year": year, "month": month, "hsn_code": hsn, "exports": exp, "imports": imp}


@pytest.fixture
def seg(tmp_path):
    return load("textile_data/analysis/segment_trade_extractor.py", tmp_path)


def test_fy25_window_boundaries(seg):
    data = {"data": [
        rec(2024, 3, 56075010, 100, 1),      # Mar 2024 -> FY24, excluded
        rec(2024, 4, 56075010, 10, 1),       # Apr 2024 -> first month of FY25
        rec(2025, 3, "56075010", "5", "2"),  # Mar 2025 -> last month of FY25; strings coerced
        rec(2025, 4, 56075010, 100, 1),      # Apr 2025 -> FY26, excluded
        rec(2024, 12, 12345678, 7, 0),
    ]}
    got = seg["extract_fy25_data"](data)
    assert got[56075010] == {"exports": 15.0, "imports": 3.0}
    assert got[12345678] == {"exports": 7.0, "imports": 0.0}
    assert seg["extract_fy25_data"]({}) == {}


def test_assign_segments_and_unassigned(seg):
    fy = {56075010: {"exports": 10.0, "imports": 4.0}, 56075090: {"exports": 1.0, "imports": 1.0},
          99999999: {"exports": 3.0, "imports": 9.0}}
    segs, un = seg["assign_segments"](fy)
    assert segs["Agrotech"]["exports"] == 11.0 and segs["Agrotech"]["imports"] == 5.0
    assert sorted(segs["Agrotech"]["codes"]) == [56075010, 56075090]
    assert un == {99999999: {"exports": 3.0, "imports": 9.0}}


def test_net_balance_and_ordering(seg):
    st = {"A": {"exports": 5.0, "imports": 5.0, "codes": [1, 1]},
          "B": {"exports": 9.0, "imports": 1.0, "codes": [2]},
          "C": {"exports": 0.0, "imports": 3.0, "codes": []}}
    df = seg["calculate_net_and_growth"](st)
    assert list(df["segment"]) == ["B", "A", "C"]                        # descending net
    assert dict(zip(df["segment"], df["trade_balance"])) == {"B": "Surplus", "A": "Deficit", "C": "Deficit"}
    assert dict(zip(df["segment"], df["hsn_codes_count"])) == {"B": 1, "A": 1, "C": 0}   # duplicates de-duplicated


def test_segment_main_outputs_and_coverage(tmp_path, capsys):
    lay_out(tmp_path, {"data": [rec(2024, 6, 56075010, 3000, 1000), rec(2024, 6, 77777777, 1000, 500)]})
    ns = load("textile_data/analysis/segment_trade_extractor.py", tmp_path)
    ns["main"]()
    out = capsys.readouterr().out
    proc = tmp_path / "textile_data" / "processed"
    res = rows(proc / "segment_trade_fy25.csv")
    assert res[0]["segment"] == "Agrotech" and float(res[0]["net_usd_mn"]) == 2000.0
    un = rows(proc / "unassigned_hsn_codes_fy25.csv")
    assert un == [{"hsn": "77777777", "exports": "1000.0", "imports": "500.0", "net": "500.0"}]
    assert "Coverage: 75.0%" in out and "1 HSN codes not in 12-segment mapping" in out


def test_segment_main_without_input_file_reports_and_returns(tmp_path, capsys):
    ns = load("textile_data/analysis/segment_trade_extractor.py", tmp_path)
    ns["main"]()
    assert "not found" in capsys.readouterr().out
    assert not (tmp_path / "textile_data" / "processed").exists()


def test_segment_main_without_gaps_skips_unassigned_file(tmp_path, capsys):
    lay_out(tmp_path, {"data": [rec(2024, 6, 56075010, 10, 5)]})
    ns = load("textile_data/analysis/segment_trade_extractor.py", tmp_path)
    ns["main"]()
    assert "Coverage: 100.0%" in capsys.readouterr().out
    assert not (tmp_path / "textile_data" / "processed" / "unassigned_hsn_codes_fy25.csv").exists()


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="several HSN codes (e.g. 54021910, 59050010, 62011100, 63061200, 58071010, 63051010) "
                          "are listed under two segments; assign_segments() breaks at the first match so the "
                          "second segment can never receive them")
def test_each_hsn_code_belongs_to_exactly_one_segment(seg):
    seen, dupes = {}, set()
    for name, codes in seg["SEGMENTS"].items():
        for c in codes:
            if c in seen:
                dupes.add(c)
            seen[c] = name
    assert not dupes, sorted(dupes)


def test_duplicate_code_goes_to_first_segment_only(seg):
    segs, _ = seg["assign_segments"]({54021910: {"exports": 4.0, "imports": 1.0}})
    assert list(segs) == ["Clothtech"] and "Indutech" not in segs        # documents the first-match-wins behaviour


# ------------------------------------------------------------------ create_presentation
pptx = pytest.importorskip("pptx")


@pytest.fixture(scope="module")
def deck(tmp_path_factory):
    from pptx.presentation import Presentation as P

    saved = {}
    orig = P.save

    def fake_save(self, path):
        saved["path"] = path
        saved["slides"] = len(self.slides)
        orig(self, str(tmp_path_factory.mktemp("deck") / "deck.pptx"))

    P.save = fake_save
    try:
        ns = load("textile_data/research/create_presentation.py", tmp_path_factory.mktemp("pp"))
    finally:
        P.save = orig
    return ns, saved


def test_deck_slide_count_matches_its_own_banner(deck):
    ns, saved = deck
    assert saved["slides"] == len(ns["prs"].slides) == 18
    assert saved["path"].endswith("Textile_Chemical_Investment_Analysis.pptx")


def test_deck_helpers_build_titled_slides(deck):
    ns, _ = deck
    from pptx import Presentation
    p = Presentation()
    s = ns["add_content_slide"](p, "Heading", ["a", "b", "c"])
    texts = [sh.text_frame.text for sh in s.shapes if sh.has_text_frame]
    assert "Heading" in texts and "a\nb\nc" in texts
    bare = ns["add_content_slide"](p, "Only title")
    assert len([sh for sh in bare.shapes if sh.has_text_frame]) == 1       # no body box without points
    t = ns["add_table_slide"](p, "Tbl", [["h1", "h2"], ["1", "2"], ["3", "4"]])
    tbl = next(sh for sh in t.shapes if sh.has_table).table
    assert len(tbl.rows) == 3 and len(tbl.columns) == 2
    title = ns["add_title_slide"](p, "T", "S")
    assert [sh.text_frame.text for sh in title.shapes][:2] == ["T", "S"]


# ------------------------------------------------------------------ fleet_from_fuel (coverage-aware loader)
@pytest.fixture
def fleet(tmp_path):
    return load("fleet_from_fuel.py", tmp_path), tmp_path


def test_fuel_volumes_and_litres_per_vehicle_year(fleet):
    ns, _ = fleet
    assert ns["bnL"](40.0, 0.74) == pytest.approx(40 / 0.74)
    assert ns["PETROL_BNL"] == pytest.approx(54.054, abs=1e-3)
    assert ns["DIESEL_BNL"] == pytest.approx(91.4 / 0.83)
    assert ns["CNG_BNKG"] == 6.67


def test_two_w_active_unknown_sector_returns_zero(fleet):
    ns, _ = fleet
    ns["SEGMENTS"][:] = [s for s in ns["SEGMENTS"] if s[1] != "Two-wheeler"]
    assert ns["two_w_active"](28) == 0


def test_main_totals_hand_computed(fleet, capsys):
    ns, d = fleet
    ns["main"]()
    out = capsys.readouterr().out
    rws = rows(d / "outputs" / "fleet_from_fuel.csv")
    car = next(r for r in rws if r["fuel"] == "Petrol" and r["sector"] == "Car")
    assert int(car["active_vehicles"]) == round(0.3433 * 40 / 0.74 * 1e9 / (30 * 300 / 15))
    assert int(car["L_per_veh_yr"]) == 600 and float(car["L_per_veh_day"]) == 2.0
    truck = next(r for r in rws if r["sector"].startswith("Truck"))
    assert int(truck["active_vehicles"]) == round(0.2825 * 91.4 / 0.83 * 1e9 / (220 * 330 / 6.0))
    road = [int(r["active_vehicles"]) for r in rws if r["active_vehicles"].isdigit()]
    ev = 9_785_936 * 0.85
    grand = sum(road) + ev
    assert f"TOTAL actively-driven: {round(grand):,}" in out
    assert f"= {100 * grand / 446_191_165:.0f}% of Vahan cumulative" in out
    md = (d / "outputs" / "fleet_from_fuel.md").read_text()
    assert "Bi-fuel overlap" in md and "Segment build-up" in md
    nonroad_share = sum(s[2] for s in ns["SEGMENTS"] if s[0] == "Diesel" and not s[3])
    assert nonroad_share == pytest.approx(0.3042)


def test_sensitivity_band_is_ordered_and_inverse(fleet, capsys):
    ns, _ = fleet
    ns["main"]()
    out = capsys.readouterr().out
    lo_usage = ns["two_w_active"](22.4)
    hi_usage = ns["two_w_active"](33.6)
    assert lo_usage > ns["two_w_active"](28) > hi_usage
    assert lo_usage == pytest.approx(ns["two_w_active"](28) * 28 / 22.4)
    assert "2W ±20% sensitivity band:" in out
