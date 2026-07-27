#!/usr/bin/env python3
"""
Analyze FY25 textile trade at chapter level using TradeStat DGCIS data.

Identifies key textile chapters and their trade flows.
Prepares roadmap for 8-digit HSN code-level query via TradeStat web interface.
"""

import json
import pandas as pd
from pathlib import Path

# Key textile and feedstock chapters
TEXTILE_CHAPTERS = {
    '29': 'Organic chemicals (monomers for synthetics)',
    '39': 'Plastics & polymer feedstock (CRITICAL)',
    '41': 'Hides, skins (upstream)',
    '51': 'Wool, animal hair',
    '52': 'Cotton',
    '53': 'Vegetable textile fibers',
    '54': 'Man-made filaments (synthetic)',
    '55': 'Man-made staple fibers (MMF)',
    '56': 'Wadding, felt, nonwoven',
    '57': 'Carpets',
    '58': 'Special textiles',
    '59': 'Impregnated, coated textiles',
    '60': 'Knitted fabrics',
    '61': 'Apparel (knit)',
    '62': 'Apparel (woven)',
    '63': 'Made-up textile articles',
    '64': 'Footwear',
    '68': 'Glass/ceramic composites',
    '70': 'Glass & glass products',
}

def load_tradestat_data(json_path):
    """Load TradeStat data."""
    with open(json_path, 'r') as f:
        return json.load(f)

def extract_chapter_data(tradestat_data):
    """Extract chapter-level data and identify textile chapters."""
    textile_trade = {}

    export_data = tradestat_data.get('by_chapter', {}).get('export', {})
    import_data = tradestat_data.get('by_chapter', {}).get('import', {})

    fy25_exp_key = '2024 - 2025'
    fy25_imp_key = '2024 - 2025'

    for chapter, name in TEXTILE_CHAPTERS.items():
        exp = export_data.get(chapter, {}).get(fy25_exp_key, 0)
        imp = import_data.get(chapter, {}).get(fy25_imp_key, 0)

        textile_trade[chapter] = {
            'name': name,
            'exports': exp,
            'imports': imp,
            'net': exp - imp,
            'status': 'Surplus' if exp > imp else 'Deficit',
        }

    return textile_trade

def create_chapter_analysis(textile_trade):
    """Create analysis dataframe."""
    data = []
    for chapter, values in sorted(textile_trade.items()):
        data.append({
            'chapter': chapter,
            'name': values['name'],
            'exports_usd_mn': round(values['exports'], 1),
            'imports_usd_mn': round(values['imports'], 1),
            'net_usd_mn': round(values['net'], 1),
            'trade_balance': values['status'],
        })

    return pd.DataFrame(data)

def main():
    data_dir = Path(__file__).parent.parent / 'raw'
    json_path = data_dir / 'tradestat_hsn_2018-26.json'

    print("=" * 80)
    print("FY25 TEXTILE & FEEDSTOCK TRADE ANALYSIS (Chapter Level)")
    print("=" * 80)

    tradestat_data = load_tradestat_data(json_path)

    # Print metadata
    print(f"\nData Source: {tradestat_data.get('source')}")
    print(f"Retrieved: {tradestat_data.get('retrieved')}")
    print(f"Last Updated: {tradestat_data.get('years_covered')}")

    # Extract and analyze
    textile_trade = extract_chapter_data(tradestat_data)
    df = create_chapter_analysis(textile_trade)

    # Totals
    total_exp = df['exports_usd_mn'].sum()
    total_imp = df['imports_usd_mn'].sum()
    net_all = total_exp - total_imp

    print(f"\n📊 FY2024-25 TEXTILE TRADE SUMMARY")
    print(f"─" * 80)
    print(df.to_string(index=False))
    print(f"\n{'TOTAL':>10} {total_exp:>18.1f} {total_imp:>18.1f} {net_all:>18.1f}")

    # Key findings
    deficits = df[df['trade_balance'] == 'Deficit'].sort_values('net_usd_mn')
    surpluses = df[df['trade_balance'] == 'Surplus'].sort_values('net_usd_mn', ascending=False)

    print(f"\n🔴 IMPORT DEFICITS (Top 5 chapters):")
    for idx, row in deficits.head(5).iterrows():
        print(f"  Ch {row['chapter']:>2} | {row['name']:<40} | Gap: ${abs(row['net_usd_mn']):>8.1f}bn")

    print(f"\n🟢 EXPORT SURPLUSES (Top 5 chapters):")
    for idx, row in surpluses.head(5).iterrows():
        print(f"  Ch {row['chapter']:>2} | {row['name']:<40} | Net: ${row['net_usd_mn']:>8.1f}bn")

    # Feedstock gap analysis
    ch39 = textile_trade.get('39', {})
    print(f"\n🔑 CRITICAL FEEDSTOCK GAP (Chapter 39 - Polymers):")
    print(f"   Exports: ${ch39['exports']:.1f}bn | Imports: ${ch39['imports']:.1f}bn | Deficit: ${abs(ch39['net']):.1f}bn")
    print(f"   ⚠️  This represents the upstream polymer feedstock import dependency")
    print(f"   ⚠️  Target for local MMF feedstock via petrochemical pathways (Nat. Fibre Mission)")

    # Save to CSV
    output_dir = Path(__file__).parent.parent / 'processed'
    output_dir.mkdir(exist_ok=True)
    df.to_csv(output_dir / 'chapter_trade_fy25.csv', index=False)

    print(f"\n✅ Results saved to: {output_dir / 'chapter_trade_fy25.csv'}")

    # Next steps
    print(f"\n📋 NEXT STEPS FOR HSN CODE-LEVEL ANALYSIS:")
    print(f"   1. Query TradeStat DGCIS directly at: https://tradestat.commerce.gov.in/")
    print(f"   2. For each chapter, use 8-digit HSN codes from segment mapping (315 codes)")
    print(f"   3. Focus on Chapters 39, 54, 55, 56, 59 for MMF/polyester segments")
    print(f"   4. Export results as CSV, aggregate by segment using hsn_codes_12segments.xlsx")
    print(f"   5. Run segment_trade_extractor.py to finalize segment-level trade flows")

if __name__ == '__main__':
    main()
