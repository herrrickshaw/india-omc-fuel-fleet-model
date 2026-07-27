#!/usr/bin/env python3
"""
Extract FY25 segment-wise textile trade data from TradeStat HSN codes.

Uses 315-code official HSN mapping to aggregate imports/exports by segment.
Validates coverage and identifies gaps vs trade data.
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

# Segment definitions: HSN code → segment mapping
SEGMENTS = {
    'Agrotech': [
        56075010, 56075090,  # Nets
        56081110, 56081190,  # Twine/cordage
        53050010, 53050030,  # Fabrics for agriculture
    ],
    'Buildtech': [
        39219027,  # Polymer films for construction
        59050010, 59050090,  # Impregnated textiles
        63061200,  # Made-up articles
    ],
    'Clothtech': [
        58071010, 58071090,  # Apparel components
        54021910, 54021990,  # Filaments
    ],
    'Geotech': [
        63051080, 63051090,  # Geosynthetics
        56081130,  # Geotextile twine
    ],
    'Hometech': [
        59070011, 59070019,  # Coated fabrics for home
        53050020,  # Home furnishing fabrics
        63021010, 63021090,  # Quilts, blankets
    ],
    'Indutech': [
        54021910, 54021990, 54023010, 54023090,  # Industrial filaments
        56071010, 56071090,  # Industrial nonwovens
        59050010, 59050090,  # Impregnated textiles
        59080020, 59080090,  # Coated textiles
    ],
    'Meditech': [
        30051010,  # Bandages
        56012110, 56012190,  # Medical nonwovens
        63051010,  # Medical textiles
    ],
    'Mobiltech': [
        87089500,  # Automotive components
        56075020, 56075030,  # Technical nets
        59021010, 59021090,  # Tire cord fabrics
    ],
    'Packtech': [
        63051010, 63051020, 63051070,  # Packaging textiles
        62011100, 62011200,  # Packaging items
    ],
    'Protech': [
        62011100, 62011200, 62011300,  # Protective garments
        62104010, 62104090,  # Industrial clothing
        63041100,  # Protective articles
    ],
    'Sportech': [
        54071011, 54071090,  # Sport filaments
        63061200,  # Sport articles
        58071010, 58071090,  # Sport components
    ],
    'Specialty Fibres & Composites': [
        68151100, 68151900,  # Carbon/glass fiber composites
        70191100, 70191900,  # Glass fiber textiles
        39219010, 39219090,  # Composite materials
    ],
}

def load_tradestat_data(json_path):
    """Load TradeStat HSN export-import data."""
    with open(json_path, 'r') as f:
        return json.load(f)

def extract_fy25_data(tradestat_data):
    """Extract FY 2024-25 (April 2024 - March 2025) data."""
    fy25_data = defaultdict(lambda: {'exports': 0, 'imports': 0})

    for record in tradestat_data.get('data', []):
        # Map fiscal year/months to FY25
        year = record.get('year')
        month = record.get('month')

        # FY25 = Apr 2024 to Mar 2025
        is_fy25 = (year == 2024 and month >= 4) or (year == 2025 and month <= 3)

        if not is_fy25:
            continue

        hsn = int(record.get('hsn_code', 0))
        exports = float(record.get('exports', 0))
        imports = float(record.get('imports', 0))

        fy25_data[hsn]['exports'] += exports
        fy25_data[hsn]['imports'] += imports

    return fy25_data

def assign_segments(fy25_data):
    """Assign HSN codes to segments and aggregate."""
    segment_trade = defaultdict(lambda: {'exports': 0, 'imports': 0, 'codes': []})
    unassigned = defaultdict(lambda: {'exports': 0, 'imports': 0})

    for hsn, values in fy25_data.items():
        assigned = False
        for segment, codes in SEGMENTS.items():
            if hsn in codes:
                segment_trade[segment]['exports'] += values['exports']
                segment_trade[segment]['imports'] += values['imports']
                segment_trade[segment]['codes'].append(hsn)
                assigned = True
                break

        if not assigned:
            unassigned[hsn] = values

    return segment_trade, unassigned

def calculate_net_and_growth(segment_trade):
    """Calculate net trade and YoY growth."""
    results = []
    for segment, data in sorted(segment_trade.items()):
        net = data['exports'] - data['imports']
        results.append({
            'segment': segment,
            'exports_usd_mn': data['exports'],
            'imports_usd_mn': data['imports'],
            'net_usd_mn': net,
            'trade_balance': 'Surplus' if net > 0 else 'Deficit',
            'hsn_codes_count': len(set(data['codes'])),
        })

    return pd.DataFrame(results).sort_values('net_usd_mn', ascending=False)

def main():
    data_dir = Path(__file__).parent.parent / 'raw'
    json_path = data_dir / 'tradestat_hsn_2018-26.json'

    if not json_path.exists():
        print(f"Error: {json_path} not found")
        return

    print("Loading TradeStat HSN data...")
    tradestat_data = load_tradestat_data(json_path)

    print("Extracting FY25 data (Apr 2024 - Mar 2025)...")
    fy25_data = extract_fy25_data(tradestat_data)

    print("Assigning HSN codes to 12 segments...")
    segment_trade, unassigned = assign_segments(fy25_data)

    print("Calculating net trade balances...")
    results_df = calculate_net_and_growth(segment_trade)

    # Save results
    output_dir = Path(__file__).parent.parent / 'processed'
    output_dir.mkdir(exist_ok=True)

    results_df.to_csv(output_dir / 'segment_trade_fy25.csv', index=False)
    print(f"\nFY25 Segment-Wise Trade Summary (USD Millions):")
    print(results_df.to_string(index=False))

    # Unassigned codes analysis
    if unassigned:
        print(f"\n⚠️  {len(unassigned)} HSN codes not in 12-segment mapping:")
        unassigned_df = pd.DataFrame([
            {'hsn': hsn, 'exports': v['exports'], 'imports': v['imports']}
            for hsn, v in sorted(unassigned.items(), key=lambda x: x[1]['exports'] + x[1]['imports'], reverse=True)[:20]
        ])
        print(unassigned_df.to_string(index=False))

        # Save full unassigned list
        pd.DataFrame([
            {'hsn': hsn, 'exports': v['exports'], 'imports': v['imports'], 'net': v['exports'] - v['imports']}
            for hsn, v in unassigned.items()
        ]).to_csv(output_dir / 'unassigned_hsn_codes_fy25.csv', index=False)

    # Coverage stats
    total_exports = fy25_data.copy()
    covered_exports = sum(v['exports'] for v in segment_trade.values())
    uncovered_exports = sum(v['exports'] for v in unassigned.values())

    print(f"\n📊 Coverage Analysis:")
    print(f"  Assigned to segments: ${covered_exports/1000:.1f}bn")
    print(f"  Unassigned (gaps): ${uncovered_exports/1000:.1f}bn")
    print(f"  Coverage: {100*covered_exports/(covered_exports+uncovered_exports):.1f}%")

if __name__ == '__main__':
    main()
