# State-wise tax revenue foregone from ethanol displacing petrol

When ethanol (5% GST) replaces petrol in the blend, each displaced litre no longer bears the state's petrol **VAT** — the state instead gets only its SGST share of 5% on the ethanol. This nets out the state revenue foregone, per state, at E20/E25/E30. Petrol volumes: PPAC RR Table 6.4(B) (FY24-25); VAT rates: RR Table 8.17 (headline rate).

Assumptions (editable): VAT charged on ₹78/L pre-VAT base; ethanol ₹60/L; ethanol GST 5% (SGST half); 36 states matched.

## 1. National state-VAT impact by blend

| Blend | Ethanol displacing petrol | State VAT foregone | SGST gained | **Net state loss** |
|---|--:|--:|--:|--:|
| E20 | 10.8 bn L | ₹19,485 cr | ₹1,622 cr | **₹17,865 cr** |
| E25 | 13.5 bn L | ₹24,358 cr | ₹2,025 cr | **₹22,331 cr** |
| E30 | 16.2 bn L | ₹29,229 cr | ₹2,434 cr | **₹26,792 cr** |

> For context, the **centre** also forgoes excise ≈ ₹20/L on the displaced petrol: at E20 that is ~₹21,514 cr/yr of central excise (net of CGST on ethanol) — larger than the state VAT loss, but borne by the Union, not states.

## 2. Top 15 states by net VAT foregone (E20)

| State | Petrol VAT | Petrol (bn L) | Ethanol (bn L) | VAT foregone (₹ cr) | net state loss (₹ cr) |
|---|--:|--:|--:|--:|--:|
| Maharashtra | 25.0% | 5.91 | 1.18 | 2,303 | 2,126 |
| Karnataka | 29.84% | 4.13 | 0.83 | 1,921 | 1,798 |
| UttarPradesh | 19.36% | 6.53 | 1.31 | 1,972 | 1,776 |
| Telangana | 35.2% | 2.43 | 0.49 | 1,337 | 1,264 |
| Rajasthan | 29.04% | 2.75 | 0.55 | 1,246 | 1,164 |
| Kerala | 30.08% | 2.54 | 0.51 | 1,192 | 1,116 |
| MadhyaPradesh | 29.0% | 2.64 | 0.53 | 1,195 | 1,116 |
| AndhraPradesh | 31.0% | 2.2 | 0.44 | 1,063 | 997 |
| TamilNadu | 13.0% | 4.78 | 0.96 | 968 | 825 |
| Gujarat | 13.7% | 3.65 | 0.73 | 780 | 671 |
| WestBengal | 25.0% | 1.86 | 0.37 | 727 | 671 |
| Odisha | 28.0% | 1.56 | 0.31 | 683 | 636 |
| Bihar | 23.58% | 1.57 | 0.31 | 577 | 530 |
| Haryana | 18.2% | 1.93 | 0.39 | 549 | 491 |
| Chhattisgarh | 24.0% | 1.19 | 0.24 | 446 | 410 |

Two forces set a state's loss: **VAT rate** (Kerala, Karnataka, AP, MP, Rajasthan sit high) and **petrol volume** (UP, Maharashtra, Tamil Nadu, Gujarat are big markets). States high on both lose most.

## 3. How the loss scales E20 → E30 (top 8 states)

| State | E20 net (₹ cr) | E25 net (₹ cr) | E30 net (₹ cr) |
|---|--:|--:|--:|
| Maharashtra | 2,126 | 2,658 | 3,189 |
| Karnataka | 1,798 | 2,247 | 2,696 |
| UttarPradesh | 1,776 | 2,221 | 2,665 |
| Telangana | 1,264 | 1,579 | 1,895 |
| Rajasthan | 1,164 | 1,455 | 1,746 |
| Kerala | 1,116 | 1,394 | 1,673 |
| MadhyaPradesh | 1,116 | 1,395 | 1,674 |
| AndhraPradesh | 997 | 1,247 | 1,496 |

## 4. Caveats

- **Framing:** this is the counterfactual revenue-foregone (petrol-vs-ethanol tax differential), the standard policy view. At the pump the E20 blend is still sold as petrol at petrol VAT, so this is not a fall in pump VAT collection — it is the VAT the state would have collected had that volume been taxed as petrol rather than 5%-GST ethanol.
- **VAT = headline rate only.** Table 8.17 rates carry extra fixed cesses and 'whichever-is-higher' ₹/L floors not modelled here, so true losses are modestly higher in several states. `PRE_VAT_BASE` and `ETHANOL_PRICE` are editable levers.
- Petrol (MS) volume is treated as the blended volume dispensed; ethanol displaced = blend% × MS (consistent with the OMC model). Central excise is the Union's loss, shown for context only.

---
*Analytical estimate from PPAC data + editable assumptions; not a fiscal forecast.*
