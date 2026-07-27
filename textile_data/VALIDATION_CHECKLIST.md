# Data Validation Checklist

## Pre-Extraction

- [ ] TradeStat DGCIS accessible: https://tradestat.commerce.gov.in/eidb
- [ ] Session established (visit search page first, note CSRF token)
- [ ] HSN code list ready: `textile_data/raw/hsn_codes_12segments.xlsx`
- [ ] Python environment ready with pandas: `pip install pandas openpyxl`

## During HSN Extraction (Per-Chapter)

### Chapter 39 (Polymers - Critical)
- [ ] Query: HSN `3900xxxx` to `3999xxxx` (all polymer codes)
- [ ] FY25 exports: Should be ~$8.2bn (matches chapter-level)
- [ ] FY25 imports: Should be ~$22.1bn (matches chapter-level)
- [ ] Deficit: ~$14bn (primary feedstock gap)
- [ ] Sample validation: HSN 39219027 (film feedstock for Buildtech)

### Chapter 54 (Man-made Filaments)
- [ ] Query: HSN `5400xxxx` to `5499xxxx`
- [ ] FY25 exports: ~$1.77bn
- [ ] FY25 imports: ~$1.51bn
- [ ] Net: ~$255mn surplus
- [ ] Sample codes: 54021910 (polyester filaments for Indutech)

### Chapter 55 (Man-made Staple - MMF)
- [ ] Query: HSN `5500xxxx` to `5599xxxx`
- [ ] FY25 exports: ~$1.61bn
- [ ] FY25 imports: ~$840mn
- [ ] Net: ~$773mn surplus
- [ ] Sample codes: 55010010 (polyester staple)

### Chapter 56 (Wadding, Felt, Nonwoven)
- [ ] Query: HSN `5600xxxx` to `5699xxxx`
- [ ] FY25 exports: ~$666mn
- [ ] FY25 imports: ~$475mn
- [ ] Net: ~$192mn surplus
- [ ] Sample codes: 56071010 (industrial nonwovens for Indutech)

### Chapter 59 (Impregnated/Coated Textiles)
- [ ] Query: HSN `5900xxxx` to `5999xxxx`
- [ ] FY25 exports: ~$504mn
- [ ] FY25 imports: ~$809mn
- [ ] Net: ~$305mn deficit
- [ ] Sample codes: 59050010 (Buildtech construction textiles)

### Chapter 63 (Made-up Textile Articles)
- [ ] Query: HSN `6300xxxx` to `6399xxxx`
- [ ] FY25 exports: ~$6.1bn (PACKTECH SURPLUS!)
- [ ] FY25 imports: ~$636mn
- [ ] Net: ~$5.5bn surplus
- [ ] Sample codes: 63051010-070 (packaging textiles)

## Post-Extraction Aggregation

### File Preparation
- [ ] All CSV files placed in `textile_data/raw/tradestat_fy25_ch*.csv`
- [ ] Columns verified: `hsn_code`, `exports_usd_mn`, `imports_usd_mn`
- [ ] No null values in HSN or trade columns
- [ ] Fiscal year verified as FY2024-25 (Apr 2024 - Mar 2025)

### Aggregation Execution
```bash
cd ~/omc-retail-profitability-model
python3 textile_data/analysis/segment_trade_extractor.py
```

- [ ] Script runs without errors
- [ ] Output CSV created: `textile_data/processed/segment_trade_fy25.csv`
- [ ] Output CSV has 12 rows (one per segment) + header

### Data Quality Validation

#### Totals Reconciliation
- [ ] Sum of chapter exports from segment CSV = $18.8bn (±$50mn tolerance)
- [ ] Sum of chapter imports from segment CSV = $26.4bn (±$50mn tolerance)
- [ ] No duplicate HSN codes across segments
- [ ] All 315 HSN codes either assigned or documented as out-of-scope

#### Segment-Level Checks
| Segment | Expected Export | Expected Import | Note |
|---------|---|---|---|
| Packtech | $6.1bn | $636mn | Should be largest surplus |
| Apparel* | $15.9bn | $1.6bn | Ch 61+62 (check separately) |
| Cotton | $6.3bn | $1.4bn | Ch 52 (should have surplus) |
| Indutech | Mixed | $8-10bn | Scattered across Ch 54-56-59 |
| Buildtech | $500mn | $800-900mn | Ch 59+39 codes for construction |
| Mobiltech | $300-500mn | $500-700mn | Ch 56-59-87 codes |

*Note: Apparel chapters (61, 62) not in textile_data scope but included in totals

#### Coverage Analysis
- [ ] Coverage >= 95% of chapter-level trade data
- [ ] Unassigned codes < 5% by value
- [ ] Any gaps documented in `unassigned_hsn_codes_fy25.csv`

### Red Flags (Stop & Investigate)
- 🚩 Chapter 39 (polymers) differs from $22.1bn by >$1bn
- 🚩 Packtech or Indutech imports show as zero
- 🚩 Total fabric chapters (54-59) < $15bn (suggests data loss)
- 🚩 Any HSN code assigned to multiple segments (creates double-counting)
- 🚩 Exports + imports totals < $40bn (data incomplete)

## Policy Alignment Validation

### National Fibre Mission 2030-31 Targets
- [ ] MMF production (Ch 55): Current 75 lakh MT, target 130 lakh MT
- [ ] MMF imports (Ch 54-55): Current $2.35bn/year
- [ ] Feedstock gap (Ch 39): Identified as -$14bn/year
- [ ] Policy mandate: "Local MMF feedstock via petrochemical pathways" → matches fuel-to-fibre loop

### Cross-Check Against Prior Analysis
- [ ] Chapter 39 gap confirmed: $13.96bn vs $14bn estimate ✅
- [ ] Chapter 29 gap identified: $6.47bn (new finding from HSN query)
- [ ] Packtech surplus confirmed: $5.47bn (aligns with prior export strength)

## Export & Documentation

### Final Outputs
- [ ] `textile_data/processed/segment_trade_fy25.csv` — Main 12-segment analysis
- [ ] `textile_data/processed/chapter_trade_fy25.csv` — FY25 chapter baseline
- [ ] `textile_data/processed/unassigned_hsn_codes_fy25.csv` — Coverage gaps
- [ ] `textile_data/raw/hsn_codes_matched_fy25.json` — HSN + FY25 trade pairs

### Branch Readiness
- [ ] All analysis scripts documented and reproducible
- [ ] README updated with FY25 results
- [ ] TRADESTAT_HSN_QUERY_GUIDE updated with actual findings
- [ ] PR summary includes validation results
- [ ] Ready for merge to main once approved

---

## Notes

**Timestamp**: 2026-07-27
**Data Freshness**: TradeStat DGCIS, updated 19 May 2026 (FY25 provisional)
**Next Phase**: Import-dependency mapping (which segments rely on which feedstock chapters?)
