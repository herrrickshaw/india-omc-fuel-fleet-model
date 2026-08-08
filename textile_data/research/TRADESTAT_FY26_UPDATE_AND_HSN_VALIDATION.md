# TradeStat FY2025-26 Update & DPIIT Ministry-Mapping Validation

**Date**: 2026-08-03
**Sources**:
- DGCIS TradeStat, Eidb Commodity-wise reports (8-digit HSN, value in USD Million), report generated 30/07/2026, covering FY2024-25 and FY2025-26 — user-supplied, more granular than the prior chapter-level `tradestat_hsn_2018-26.json` (which was chapter-level only, pulled 2026-07-18)
- DPIIT "Guidebook on Mapping of Harmonized System of Nomenclature (HSN) Codes" (December 2025, revised 16.12.2025) — official ministry-ownership mapping for 12,174 HS codes across 31 Ministries/Departments

## Part 1: What changed vs. the existing repo data

New files added to `raw/tradestat_fy26_source/` (export/import value and quantity, FY24-25 vs FY25-26, 8-digit HSN, ~11,500 export lines / ~10,850 import lines each — full commodity-wise detail, not just chapter totals).

New processed outputs:
- `processed/chapter_trade_fy26.csv` — chapter-level FY25 vs FY26 trade, replaces the single-year `chapter_trade_fy25.csv`
- `processed/segment_trade_fy26.csv` — 18-label technical-textile segment trade (matched against `raw/hsn_codes_12segments.xlsx`, 314 codes, 261 matched in TradeStat)
- `processed/textile_hsn8_detail_fy26.csv` — 3,349 individual 8-digit HSN lines across Chapters 29, 39, 50-63, with FY25→FY26 export/import/net and net-change
- `raw/tradestat_textile_hsn8_fy26.json` — raw chapter aggregates snapshot

### Chapter-level trade, FY2024-25 → FY2025-26 (USD million)

| Chapter | Name | Net FY25 | Net FY26 | Change | Import growth |
|---|---|---|---|---|---|
| 29 | Organic chemicals (monomers) | -6,469.8 | -5,001.9 | **+1,467.9 (improved)** | -4.4% |
| 39 | Plastics & polymer feedstock | -13,957.7 | -14,637.2 | -679.5 (worse) | +0.5% |
| 54 | Man-made filaments | +255.2 | **-337.4** | **-592.6 (flipped to deficit)** | +29.3% |
| 59 | Impregnated/coated textiles | -305.1 | -501.2 | -196.1 (worse) | +16.0% |
| 60 | Knitted fabrics | -303.2 | -455.5 | -152.3 (worse) | +6.3% |
| 70 | Glass & glassware | -1,055.0 | -1,953.3 | -898.3 (worse) | **+42.1%** |
| 52 | Cotton | +4,915.4 | +3,854.7 | -1,060.7 (surplus shrank) | **+50.1%** |
| 50 | Silk | -14.2 | +49.0 | +63.2 (flipped to surplus) | — |
| 53 | Vegetable textile fibres | -62.6 | +341.0 | +403.6 (flipped to surplus) | -19.6% |

**Two headline findings not visible in the prior (FY25-only) data:**
1. **Chapter 29's deficit actually narrowed** by $1.47bn in FY26 (imports down 4.4%) — a genuine improvement the previously-published article (based on FY21-25 data) could not show, since that run ended at FY25.
2. **Chapter 54 (man-made filaments) flipped from a $255M surplus to a $337M deficit** — import growth of 29.3% in a single year. This is a new, sharper signal on the MMF-import-dependency story than the FY21-25 trend data captured, and directly reinforces the "specialty-MMF deficit" argument in the Fuel-to-Fibre article.

### Top individual HSN-8 import lines in textile-relevant chapters, FY2025-26

| HSN | Chapter | Commodity | Import FY26 | Import FY25 |
|---|---|---|---|---|
| 52010024 | 52 | Cotton, other than Indian (staple ≥ threshold) | $1,637.3M | $917.1M |
| 39041020 | 39 | Suspension grade PVC resin | $1,632.5M | $2,124.9M |
| 29173600 | 29 | Terephthalic acid (PTA) and salts | $1,469.2M | $1,598.3M |
| 39021000 | 39 | Polypropylene | $1,372.0M | $1,152.4M |
| 39269099 | 39 | Other plastic articles NES | $1,228.5M | $1,064.0M |
| 29025000 | 29 | Styrene | $1,133.8M | $1,314.3M |
| 29051100 | 29 | Methanol | $1,085.8M | $917.6M |
| 39012000 | 39 | Polyethylene (density ≥0.94) | $938.6M | $1,151.2M |
| 29024300 | 29 | Paraxylene | $720.8M | $942.1M |
| 29053100 | 29 | Ethylene glycol (MEG) | $649.6M | $619.0M |

These are exactly the feedstock lines named in the Fuel-to-Fibre article's petrochemical-loop table (PTA/paraxylene → polyester, PE/PP → fibre-grade resins, MEG → polyester) — the HSN-level data confirms the article's framing at the individual-code level, not just the chapter aggregate.

### Biggest single-line deficit deteriorations, FY25→FY26

Cotton (52010024, -$736.7M), Polypropylene (39021000, -$356.4M), Textured polyester yarn (54023300, -$283.1M), and **Linear Low-Density Polyethylene (39014010, -$181.4M — the exact LLDPE line the BPCL Bina investment case targets)** all worsened materially in FY26.

## Part 2: Validation against the DPIIT Ministry-Mapping Guidebook

The DPIIT Guidebook (Dec 2025) assigns each of 12,174 HS codes to one lead Ministry/Department. Cross-checking the 314-code technical-textile segment list (`raw/hsn_codes_12segments.xlsx`) against the Guidebook's "M/o TEXTILES" section (2,176 codes, communicated via Ministry of Textiles OM No. 12015/10/2024-TTP, 30 Aug 2024):

- **261 of 314 codes (83%) are confirmed under Ministry of Textiles ownership.**
- **53 of 314 codes (17%) are NOT listed under M/o Textiles** in the Guidebook — spread across Chapter 30 (medical dressings — likely M/o Health/Pharmaceuticals territory), Chapter 39 (plastics — Chemicals), Chapter 56/57/59/63 (technical nonwovens/coated fabrics, some assigned elsewhere), and a handful of codes not found in the Guidebook's searchable text at all (possibly in the 495-code "residual" category, or a chapter-30/70 boundary product).

**The more consequential finding, directly relevant to the just-published Fuel-to-Fibre article:**

| Chapter | Codes under M/o Textiles | Codes under D/o Chemicals & Petro-Chemicals |
|---|---|---|
| 39 (Plastics/polymers) | **4** | **421** |
| 29 (Organic chemicals) | **0** | **694** |

**The $20.4bn Chapter 39+29 "textile feedstock deficit" cited in the article is, administratively, almost entirely owned by the Department of Chemicals & Petrochemicals, not the Ministry of Textiles.** This doesn't weaken the economic argument — PTA, MEG, polypropylene and acrylonitrile genuinely become polyester, PP fibre and acrylic regardless of which ministry's HS-code list they sit on — but it is an important governance-structure caveat: closing this deficit requires a **Chemicals & Petrochemicals-led capacity build (BPCL Bina LLDPE, RIL O2C, IOCL aromatics)** feeding into a **Textiles-led demand pull (PM MITRA, PLI, National Fibre Mission)**. The two ministries own different halves of the same supply chain — which is arguably the article's central point, now with an official administrative record confirming the split.

## Part 3: Segment-level trade (18 official technical-textile segments), FY2025-26

| Segment | Net FY26 (USD M) | Balance |
|---|---|---|
| Packtech | +1,212.1 | Surplus (largest) |
| Specialty Fibers & Composites | -395.5 | **Deficit (largest)** |
| Indutech | -324.8 | Deficit |
| Mobile Textiles | -309.6 | Deficit |
| Hometech | +96.1 | Surplus |
| Sports Textiles | +65.5 | Surplus |
| Meditech | +55.7 | Surplus |
| Agro-textiles | +61.0 | Surplus |
| Medical/Hygiene Textiles | +21.1 | Surplus |
| Clothtech | -23.0 | Deficit |
| Defence Textile | -14.9 | Deficit |

This segment-level match (using the official 314-code list, 261 codes found in TradeStat) is directionally consistent with the Ministry's own published FY22 trade table cited in the Fuel-to-Fibre article — Packtech remains the dominant surplus segment; Indutech, Mobile/Mobiltech, and Specialty Fibres remain the persistent deficit segments needing the petrochemical-feedstock pathway.

## Caveats

- FY2025-26 in the new TradeStat files is a **complete fiscal year** (report generated 30 July 2026, after FY26 close on 31 March 2026) — not provisional, unlike the repo's prior JSON snapshot pulled mid-year.
- Segment matching only covers 261/314 official codes found in the TradeStat commodity list; 53 codes returned no match (likely reclassified, discontinued, or below reporting threshold — not investigated line-by-line here).
- The DPIIT Guidebook's ministry assignment is an administrative/policy-ownership mapping, not a trade-value or import-dependency measure — a code being "owned" by Chemicals or Textiles says nothing about deficit size, only about which ministry is nominally responsible for sectoral policy on it.
