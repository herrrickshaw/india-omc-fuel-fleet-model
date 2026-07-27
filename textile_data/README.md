# Textile Import-Export Analysis

Dedicated branch for comprehensive technical textiles import/export data and analysis.

## Directory Structure

```
textile_data/
├── README.md                          # This file
├── raw/                              # Raw data from DGCIS TradeStat
│   ├── tradestat_hsn_*.json          # Chapter/HSN-level trade data FY2018-26
│   └── hsn_codes_12segments.xlsx     # Official 315 HSN codes for 12 segments
├── processed/                        # Aggregated & cleaned data
│   ├── segment_trade_fy24_fy25.csv   # Segment-wise FY24 vs FY25
│   ├── chapter_trade_fy24_fy25.csv   # Chapter-level summary
│   └── hsn_mapping_complete.csv      # 315-code master list
└── analysis/                         # Analytical outputs
    ├── segment_analysis/             # Per-segment trade flows
    ├── import_dependency/            # Import gap analysis
    ├── hsn_coverage/                 # HSN code validation vs trade data
    └── reports/                      # Summary reports & visualizations
```

## Data Sources

### Live Databases
- **TradeStat DGCIS**: https://tradestat.commerce.gov.in/
- **India Trade Data Analysis repo**: `india-trade-data-analysis/data/tradestat_*.json`

### Official HSN Mappings
- **Export-Import Bank Annexure**: 157 codes (9 segments)
- **Complete HSN List**: 315 codes (12 segments) — see `raw/hsn_codes_12segments.xlsx`

### Policy Documents
- **National Fibre Mission 2030-31**: MMF targets, feedstock mandate
- **NTTM Compendium 2024**: Segment definitions, FY24 trade baseline
- **Ministry of Textiles Annual Report 2024-25**: FY25 headline figures

## Key Segments (12 Total)

| Segment | Definition | Key HSN Codes | Trade Status FY25 |
|---------|-----------|---|---|
| Agrotech | Agricultural nets, mulch | 56075010, 56081110 | Surplus |
| Buildtech | Construction textiles | 39219027, 59050010, 63061200 | Deficit (needs mapping) |
| Clothtech | Apparel components | 58071010, 58071090 | Small net |
| Geotech | Geosynthetics | 63051080, 63051090 | Surplus |
| Hometech | Home furnishings | 59070011, 53050010-030 | Deficit |
| Indutech | Industrial textiles | 54021910, 56071010 (80+ codes) | Deficit |
| Meditech | Medical/hygiene | 30051010, 56012110 | Surplus |
| Mobiltech | Automotive textiles | 87089500, 56075020-030 | Deficit |
| Packtech | Packaging textiles | 63051010-070 | **SURPLUS +$5.5bn** |
| Protech | Protective textiles | 62011100, 62104010 | Surplus |
| Sportech | Sports textiles | 54071011, 63061200 | Surplus |
| Specialty Fibres & Composites | Carbon, glass, aramid | 68151100, 70191100-900 | Heavy deficit |

## FY25 Trade Summary (Chapter-Level, USD Mn)

| Chapter | Category | Exports | Imports | Net | Growth |
|---------|----------|---------|---------|-----|--------|
| 39 | Plastics (feedstock) | 8,158 | 22,116 | −13,958 | +10.5% |
| 54 | Man-made filaments | 1,770 | 1,515 | +255 | +0.5% |
| 55 | Man-made staple | 1,613 | 840 | +773 | −1.6% |
| 56 | Wadding/nonwoven | 666 | 475 | +192 | +15.9% |
| 59 | Impregnated/coated | 504 | 809 | −305 | +5.0% |
| 63 | Made-up articles | 6,103 | 636 | +5,468 | +9.3% |
| **TOTAL** | **TECH TEXTILES** | **18,814** | **26,389** | **−7,575** | **+8.0%** |

## Analysis Checklist

- [ ] Pull segment-wise FY25 data from TradeStat using 315-code mapping
- [ ] Validate HSN coverage: TradeStat data vs official 315-code list
- [ ] Identify missing codes: chapters in trade data but not in HSN mapping
- [ ] Build import-dependency matrix: feedstock imports vs end-use textiles
- [ ] Compare FY24 vs FY25 growth by segment (15 segments tracked vs 12 official)
- [ ] Map deficit segments (Hometech, Mobiltech, Specialty) to petrochemical feedstock needs
- [ ] Document data quality gaps & recommendations for next phase

## Related Branches

- **feat/textile-petrochemicals-loop**: Fuel-to-fibre opportunity analysis (merged insights welcome)
- **india-trade-data-analysis**: TradeStat historical database (2018-26)

---

**Last Updated:** 2026-07-27  
**Maintainer:** Claude Code  
**Data Currency:** TradeStat DGCIS (19 May 2026)
