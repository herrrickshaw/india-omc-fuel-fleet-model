# TradeStat DGCIS HSN Code Query Guide

## Objective
Extract FY25 segment-level trade data for 12 technical textile segments using 315 official HSN codes.

## Data Availability

### What We Have
- ✅ **Chapter-level (2-digit) data**: FY2018-26, complete via JSON export
- ❌ **HSN-level (8-digit) data**: Available only via TradeStat web interface (not exportable to JSON in bulk)

### Why HSN-Level Data Matters
The 12 technical textile segments are defined by specific HSN codes. Chapter-level data aggregates across many use cases; HSN codes let us isolate:
- **Packtech** (specific packaging textiles): Ch 63 includes furnishings, apparel, etc.
- **Mobiltech** (automotive textiles): Ch 56/59 includes industrial nonwovens, etc.
- **Indutech** (industrial use): Scattered across multiple chapters

## Step-by-Step Query Process

### 1. Log Into TradeStat DGCIS
Go to: **https://tradestat.commerce.gov.in/eidb**

### 2. Prepare HSN Code List
Use the master list from `textile_data/raw/hsn_codes_12segments.xlsx`:
- 315 codes organized by segment
- Focus on high-volume chapters: **39, 54, 55, 56, 59, 63**

### 3. Query per Chapter or HSN Range

**Option A: Chapter-focused queries (recommended for FY25)**
1. Select **Commodity Level**: "8-Digit HSN Code"
2. Select **Report Type**: "Commodity-wise Export" and "Commodity-wise Import"
3. Enter HSN code range (e.g., `39xxxx00` for Chapter 39)
4. Set Fiscal Year: **2024-25**
5. Download as CSV

**Option B: Segment-focused queries (if HSN range not supported)**
1. Query individual HSN codes from your segment's list
2. Batch them: 20-30 codes per query
3. Combine results in Excel

### 4. Critical Chapters to Query (Priority Order)

| Chapter | Segment Priority | Key HSN Codes | Expected Volume |
|---------|------------------|---|---|
| **39** | Feedstock (Indutech, Mobiltech) | 39219027, 39219010-090 | ~$22bn imports |
| **54** | Indutech, Protech | 54021910, 54023010 | ~$1.5bn imports |
| **55** | Indutech, Clothtech | 55010010-090 | ~$0.8bn imports |
| **56** | Agrotech, Indutech, Mobiltech | 56071010-090, 56075010 | ~$0.5bn imports |
| **59** | Buildtech, Mobiltech, Hometech | 59050010-090, 59070011 | ~$0.8bn imports |
| **63** | **Packtech** (surplus!) | 63051010-070 | ~$5.5bn exports |

### 5. Data Import Process

Once you have HSN-level CSV data:

```bash
# 1. Place CSV in textile_data/raw/
cp tradestat_fy25_ch39_hsn.csv textile_data/raw/

# 2. Create master aggregator
python3 textile_data/analysis/segment_trade_extractor.py

# 3. Output: textile_data/processed/segment_trade_fy25.csv
```

## Expected Outputs

### FY25 Segment-Level Summary (After HSN Query)
```
Segment              Exports    Imports      Net    Status
Packtech           $6,103M     $636M      +$5,467M  Surplus
Cotton             $6,334M     $1,419M    +$4,915M  Surplus
Apparel (woven)    $8,303M     $912M      +$7,391M  Surplus
Apparel (knit)     $7,704M     $731M      +$6,973M  Surplus
─────────────────────────────────────────────────────
Plastics (Ch 39)   $8,158M     $22,116M   -$13,958M  DEFICIT
Chapter 29 (monomers) $20,121M $26,591M   -$6,470M   DEFICIT
```

### Gap Analysis
- **Feedstock Gap (Ch 39 polymers)**: $14bn → Target for local MMF via petrochemical pathways
- **Upstream Chemicals (Ch 29)**: $6.5bn → Addressable via C2-ethylene integration
- **Specialty Composites**: $1–2bn (estimate, needs HSN breakdown)

## TradeStat Web Interface Tips

### Session Management
- TradeStat uses **Livewire/Laravel sessions**
- Plain GET requests return 405 (Method Not Allowed)
- You must:
  1. Visit the search page first to establish session cookie
  2. Include CSRF token in POST requests
  3. Maintain session for multiple queries

### Query Parameters (from successful 2026-07-18 extraction)
```
POST /eidb
Form Data:
  comType: "all" (for all commodities)
  EidbComLevelCwe: "2" (2=chapter, "3"=4-digit, "8"=8-digit HSN)
  Eidb_ReportCwe: "2" (exports), "1" (imports)
  year: "2024-25"
```

### Known Limitations
1. **No bulk HSN export**: Must query individually or by chapter
2. **Session timeout**: ~30 min inactivity
3. **Rate limiting**: Safe to query ~1 chapter per 2 seconds
4. **Data lag**: Updated mid-May (data as of 19 May 2026)

## Validation Checklist

After extracting HSN data:

- [ ] FY25 total exports match chapter-level total (~$437.7bn)
- [ ] FY25 total imports match chapter-level total (~$721.2bn)
- [ ] All 315 HSN codes assigned to segments (or documented as out-of-scope)
- [ ] Segment totals reconcile with chapter-level sums
- [ ] Top 5 export segments align with our earlier analysis (Apparel, Cotton, Carpets, Packtech)
- [ ] Top 5 import segments align with feedstock (Ch 39) and chemicals (Ch 29)

## Output Files

After completing this process:

```
textile_data/processed/
├── segment_trade_fy25.csv          # Main output: 12-segment trade
├── chapter_trade_fy25.csv          # Chapter-level baseline (complete)
├── hsn_codes_matched_fy25.json     # 315 codes + matched FY25 trade data
└── hsn_codes_unmatched.csv         # Codes in TradeStat but not in 12-segment mapping
```

## Next Steps (Phase 2)

Once segment-level data is locked:

1. **Import-dependency matrix**: Which segments rely on which feedstock chapters?
2. **Substitution analysis**: Where can domestic MMF feedstock replace imports?
3. **Policy alignment**: Map to National Fibre Mission 2030-31 MMF production targets
4. **Petrochemical loop**: Quantify ethanol-freed naphtha → polymer feedstock potential

---

**Last Updated**: 2026-07-27  
**Status**: Awaiting HSN-level data from TradeStat query  
**Data Source**: DGCIS/TradeStat EIDB (FY2018-26, updated 19 May 2026)
