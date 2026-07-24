# DCPC validation of the petrochemical import figures

Source: **Department of Chemicals & Petrochemicals (DCPC), Ministry of Chemicals & Fertilizers —
"Indian Chemical & Petrochemical Statistics at a Glance 2025"**, Table 3.2 *"Products having Imports
more than Rs. 1,000 Cr (FY 2024-25)"* and the sector market-size table. This is the authoritative
source; it validates the aggregates here and corrects two individual products.

## Aggregate — validated

| Metric | This repo's figure | **DCPC (Statistics at a Glance 2025)** | Verdict |
|---|--:|--:|---|
| Total chem + petchem **imports** | ₹6.32 lakh cr (~$74 bn) | **₹6.00 lakh cr (~$70 bn)** | ✓ within ~5% |
| Petrochemical imports (>₹1,000 cr products) | ~₹1.25 lakh cr (~$15 bn) | **₹1.18 lakh cr (~$14 bn)** | ✓ within ~6% |
| Sector output / export | — | output ₹15.14 lakh cr · export ₹3.73 lakh cr | — |
| **Net chemical trade deficit** | — | **₹2.27 lakh cr (~$26 bn)** | new |

## Product-wise — DCPC authoritative values (FY2024-25, ₹ cr)

| Product | This repo | **DCPC** | Note |
|---|--:|--:|---|
| Polypropylene (inc. co-polymer) | 13,000 | **15,627** | largest single petchem import |
| **Purified Terephthalic Acid (PTA)** | ~5,000 | **13,501** | ⚠️ I understated — 2nd largest |
| High-Density Polyethylene | (in PE) | **12,187** | |
| Styrene | 10,150 | **11,105** | ✓ |
| **Paraxylene** | (in PX/PTA) | **7,965** | ⚠️ large, under-counted |
| Polycarbonate | 5,000 | **5,545** | ✓ |
| Mono-ethylene glycol (MEG) | 6,666 | **5,239** | ✓ (mine high) |
| Toluene | (feedstock) | **4,669** | TDI feedstock |
| **Poly Vinyl Chloride (PVC)** | 19,000 | **4,558** | ⚠️ I overstated ~2× |
| Linear Alkyl Benzene (LAB) | (indic.) | **3,670** | |
| Ethyl Vinyl Acetate (EVA) | (in VAM) | **3,601** | |
| Low-Density Polyethylene | (in PE) | **3,529** | |
| Styrene-Butadiene Rubber (SBR) | (in BD rubber) | **3,515** | |
| Polyester Filament Yarn | — | **3,072** | new |
| Vinyl Chloride Monomer (VCM) | (in PVC) | **2,987** | PVC feedstock |
| Poly Butadiene Rubber (PBR) | (in BD rubber) | **2,562** | |
| ABS Resin | 8,000 (w/ others) | **2,311** | |
| Acrylonitrile (ACN) | 3,000 | **2,283** | ✓ |
| Ortho-Xylene | 2,000 | **2,227** | ✓ |
| Linear Low-Density PE | (in PE) | **1,751** | |
| Ethylene Dichloride (EDC) | (in PVC) | **1,679** | PVC feedstock |
| Polystyrene | (in PS/ABS) | **1,646** | |
| Vinyl Acetate Monomer (VAM) | 2,000 | **1,598** | ✓ |
| Isopropanol | (indic.) | **1,516** | |
| Methanol | 7,524 | **7,755** | ✓ (chemical, gas-based) |

Reconciled groupings: **PE (HDPE 12,187 + LDPE 3,529 + LLDPE 1,751) = ₹17,467 cr** (I had 22,000 —
~25% high). **PVC chain (PVC 4,558 + VCM 2,987 + EDC 1,679) = ₹9,224 cr** (I had 19,000 — ~2× high).
**Polyester/PET chain (PTA 13,501 + PX 7,965 + PFY 3,072) = ₹24,538 cr** (I badly under-counted — it is
actually the *single biggest* substitutable cluster).

## What this changes

- **The thesis and headline numbers stand:** ~$70 bn chemical imports, ~$14-15 bn petroleum-linked
  substitutable, PLI case unchanged — DCPC confirms the aggregate.
- **The product mix shifts:** the biggest substitutable prize is the **polyester/PET chain (PX→PTA→PET,
  ~₹24,500 cr)** and **polyolefins (PP ₹15,627 + PE ₹17,467)**, not PVC. PVC is a smaller ~₹9,000 cr gap.
- **Priority list corrected:** PP, PTA/PX, HDPE, styrene lead by value; polycarbonate/MDI/ACN remain the
  high-*dependence* (~85-100%) engineering-plastics gap even if smaller by value.

*DCPC Statistics-at-a-Glance is the definitive product-wise trade source (built on DGCIS). Figures are
FY2024-25, ₹ crore; ₹→$ at ₹86.*
