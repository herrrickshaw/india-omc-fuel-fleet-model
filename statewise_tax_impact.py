#!/usr/bin/env python3
"""State-wise tax revenue foregone when ethanol displaces petrol (E20/E25/E30).

Ethanol blended into petrol carries only 5% GST, while the petrol it displaces
would have carried central excise + a high state VAT. So each litre of petrol
displaced by ethanol is revenue *foregone* — this quantifies the STATE portion
(VAT lost, net of the SGST gained on ethanol), state by state.

Inputs (from the PPAC Ready Reckoner FY2025-26 H1, extracted to
~/ppac-ready-reckoner-data/):
  Table 6.4(B) — state-wise MS/petrol annual sales (TMT)
  Table 8.17   — state-wise petrol VAT/sales-tax rates

Counterfactual framing: the displaced volume, had it stayed petrol rather than
being ethanol, would have borne petrol taxes. (At the pump the E20 blend is still
sold as 'petrol' at petrol VAT; this is the standard tax-differential / revenue-
foregone view used in policy analysis, not a pump cash-flow statement.)
Pure stdlib.
"""
import csv
import re
from pathlib import Path

RR = Path.home() / "ppac-ready-reckoner-data" / "annual_fy2025-26_h1" / "csv"
OUT = Path(__file__).resolve().parent / "outputs"; OUT.mkdir(exist_ok=True)

# ── levers ───────────────────────────────────────────────────────────────────
DENS_MS = 0.74                      # petrol kg/L -> 1 TMT = 1e6/0.74 L
PRE_VAT_BASE = 78.0                 # ₹/L pre-VAT price (base+excise+dealer) VAT is charged on
ETHANOL_PRICE = 60.0                # ₹/L avg ethanol procurement (GST base)
GST_ETHANOL = 0.05                  # ethanol GST
SGST_SHARE = 0.5                    # state gets half of GST as SGST
EXCISE_PETROL = 19.90               # ₹/L central excise on petrol (for the national context line)
BLENDS = {"E20": 0.20, "E25": 0.25, "E30": 0.30}
CR = 1e7

MS_FILE = next(RR.glob("Table_6.4(B)_*.csv"))
VAT_FILE = next(RR.glob("Table_8.17_*.csv"))


def norm(s):
    return re.sub(r"[^a-z]", "", s.lower())


def load_ms():
    """state -> MS (blended petrol) FY24-25, litres/year."""
    out = {}
    for row in csv.reader(MS_FILE.open()):
        if len(row) < 6:
            continue
        st = row[0].strip()
        if not st or "region" in st.lower() or "total" in st.lower() \
           or st.lower().startswith(("state", "table", "ms ", "(tmt")):
            continue
        try:
            tmt_2425 = float(row[4])          # FY2024-25 full year column
        except ValueError:
            continue
        out[norm(st)] = (st, tmt_2425 * 1e6 / DENS_MS)   # TMT -> L
    return out


def load_vat():
    """state -> (display_name, petrol VAT fraction from headline %)."""
    out = {}
    for row in csv.reader(VAT_FILE.open()):
        if len(row) < 3:
            continue
        st = row[1].strip()
        if not st or st.lower().startswith(("state", "sl")) or "table" in row[0].lower():
            continue
        cell = row[2]
        m = re.search(r"(\d+(?:\.\d+)?)\s*%", cell)     # first percentage = headline VAT
        if not m:
            continue
        out[norm(st)] = (st, float(m.group(1)) / 100)
    return out


def match_vat(ms_key, vat):
    """Exact match, else a VAT entry whose name starts with the state (Table 8.17
    splits some states, e.g. 'Maharashtra - Mumbai...' / 'Maharashtra (Rest)')."""
    if ms_key in vat:
        return vat[ms_key]
    cands = sorted((k for k in vat if k.startswith(ms_key)), key=len)
    return vat[cands[0]] if cands else None


def main():
    ms, vat = load_ms(), load_vat()
    matched = {k: match_vat(k, vat) for k in ms}
    keys = sorted(k for k, v in matched.items() if v)
    vat_of = {k: matched[k] for k in keys}
    vat_per_l = {k: vat_of[k][1] * PRE_VAT_BASE for k in keys}  # ₹/L state VAT
    sgst_per_l_eth = ETHANOL_PRICE * GST_ETHANOL * SGST_SHARE   # ₹/L SGST on ethanol

    # per-state results for each blend scenario
    scen_rows = {b: [] for b in BLENDS}
    for b, frac in BLENDS.items():
        for k in keys:
            name, ms_l = ms[k]
            eth_l = ms_l * frac                       # petrol displaced by ethanol (= ethanol vol)
            vat_lost = eth_l * vat_per_l[k] / CR      # ₹ cr
            sgst_gain = eth_l * sgst_per_l_eth / CR   # ₹ cr
            net = vat_lost - sgst_gain
            scen_rows[b].append({
                "state": name, "vat_pct": round(vat_of[k][1]*100, 2),
                "ms_bnL": round(ms_l/1e9, 2), "ethanol_bnL": round(eth_l/1e9, 2),
                "vat_lost_cr": round(vat_lost), "sgst_gain_cr": round(sgst_gain),
                "net_state_loss_cr": round(net),
            })
        scen_rows[b].sort(key=lambda r: -r["net_state_loss_cr"])

    # write per-scenario CSV
    for b in BLENDS:
        with (OUT / f"statewise_tax_{b}.csv").open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(scen_rows[b][0].keys()))
            w.writeheader(); w.writerows(scen_rows[b])

    def tot(b, key): return sum(r[key] for r in scen_rows[b])

    # national central-excise context (all-India MS 40 MMT blended)
    natl_ms_l = 40.0 * 1e6 / DENS_MS * 1000    # 40 MMT -> L  (=54.05 bn L)

    # markdown
    L = []
    L.append("# State-wise tax revenue foregone from ethanol displacing petrol\n")
    L.append("When ethanol (5% GST) replaces petrol in the blend, each displaced litre no longer bears "
             "the state's petrol **VAT** — the state instead gets only its SGST share of 5% on the "
             "ethanol. This nets out the state revenue foregone, per state, at E20/E25/E30. Petrol "
             "volumes: PPAC RR Table 6.4(B) (FY24-25); VAT rates: RR Table 8.17 (headline rate).\n")
    L.append(f"Assumptions (editable): VAT charged on ₹{PRE_VAT_BASE:.0f}/L pre-VAT base; ethanol ₹{ETHANOL_PRICE:.0f}/L; "
             f"ethanol GST {GST_ETHANOL*100:.0f}% (SGST half); {len(keys)} states matched.\n")

    # national totals per scenario
    L.append("## 1. National state-VAT impact by blend\n")
    L.append("| Blend | Ethanol displacing petrol | State VAT foregone | SGST gained | **Net state loss** |")
    L.append("|---|--:|--:|--:|--:|")
    for b in BLENDS:
        L.append(f"| {b} | {sum(r['ethanol_bnL'] for r in scen_rows[b]):.1f} bn L | "
                 f"₹{tot(b,'vat_lost_cr'):,} cr | ₹{tot(b,'sgst_gain_cr'):,} cr | "
                 f"**₹{tot(b,'net_state_loss_cr'):,} cr** |")
    L.append("")
    L.append(f"> For context, the **centre** also forgoes excise ≈ ₹{EXCISE_PETROL:.0f}/L on the displaced "
             f"petrol: at E20 that is ~₹{round(natl_ms_l*0.20*EXCISE_PETROL/CR):,} cr/yr of central excise "
             "(net of CGST on ethanol) — larger than the state VAT loss, but borne by the Union, not states.\n")

    # top states at E20
    L.append("## 2. Top 15 states by net VAT foregone (E20)\n")
    L.append("| State | Petrol VAT | Petrol (bn L) | Ethanol (bn L) | VAT foregone (₹ cr) | net state loss (₹ cr) |")
    L.append("|---|--:|--:|--:|--:|--:|")
    for r in scen_rows["E20"][:15]:
        L.append(f"| {r['state']} | {r['vat_pct']}% | {r['ms_bnL']} | {r['ethanol_bnL']} "
                 f"| {r['vat_lost_cr']:,} | {r['net_state_loss_cr']:,} |")
    L.append("")
    L.append("Two forces set a state's loss: **VAT rate** (Kerala, Karnataka, AP, MP, Rajasthan sit high) "
             "and **petrol volume** (UP, Maharashtra, Tamil Nadu, Gujarat are big markets). States high on "
             "both lose most.\n")

    # E20 vs E30 for the top few
    L.append("## 3. How the loss scales E20 → E30 (top 8 states)\n")
    L.append("| State | E20 net (₹ cr) | E25 net (₹ cr) | E30 net (₹ cr) |")
    L.append("|---|--:|--:|--:|")
    idx = {r["state"]: r for r in scen_rows["E20"][:8]}
    e25 = {r["state"]: r for r in scen_rows["E25"]}
    e30 = {r["state"]: r for r in scen_rows["E30"]}
    for st in idx:
        L.append(f"| {st} | {idx[st]['net_state_loss_cr']:,} | {e25[st]['net_state_loss_cr']:,} "
                 f"| {e30[st]['net_state_loss_cr']:,} |")
    L.append("")

    L.append("## 4. Caveats\n")
    L.append("- **Framing:** this is the counterfactual revenue-foregone (petrol-vs-ethanol tax "
             "differential), the standard policy view. At the pump the E20 blend is still sold as petrol "
             "at petrol VAT, so this is not a fall in pump VAT collection — it is the VAT the state would "
             "have collected had that volume been taxed as petrol rather than 5%-GST ethanol.")
    L.append("- **VAT = headline rate only.** Table 8.17 rates carry extra fixed cesses and "
             "'whichever-is-higher' ₹/L floors not modelled here, so true losses are modestly higher in "
             "several states. `PRE_VAT_BASE` and `ETHANOL_PRICE` are editable levers.")
    L.append("- Petrol (MS) volume is treated as the blended volume dispensed; ethanol displaced = "
             "blend% × MS (consistent with the OMC model). Central excise is the Union's loss, shown for "
             "context only.\n")
    L.append("---\n*Analytical estimate from PPAC data + editable assumptions; not a fiscal forecast.*\n")
    (OUT / "statewise_tax_impact.md").write_text("\n".join(L))

    print(f"Matched {len(keys)} states.")
    for b in BLENDS:
        print(f"{b}: net state VAT foregone ₹{tot(b,'net_state_loss_cr'):,} cr "
              f"(VAT lost ₹{tot(b,'vat_lost_cr'):,} - SGST ₹{tot(b,'sgst_gain_cr'):,})")
    print("\nTop 8 states by net loss (E20):")
    for r in scen_rows["E20"][:8]:
        print(f"  {r['state']:20s} VAT {r['vat_pct']:5.1f}%  petrol {r['ms_bnL']:5.2f} bnL  net ₹{r['net_state_loss_cr']:>6,} cr")
    print("Wrote outputs/statewise_tax_impact.md + statewise_tax_E20/E25/E30.csv")


if __name__ == "__main__":
    main()
