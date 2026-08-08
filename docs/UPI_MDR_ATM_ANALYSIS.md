# UPI, MDR and the fuel forecourt: what payments actually cost a petrol pump, and why the ATM is the hedge

*8 August 2026. Built from this machine's own verified data (PPAC price build-up via the
masaladeutsch fuel-pricing post; the OMC retail profitability model; the fuel-retail-outlets
repo's SSRI catalog and SBI Cash@PoS extraction) plus current literature on MDR and ATM
economics. Every number's source is named; what could not be verified is flagged.*

---

## 1. The premise, checked first

**"UPI payments are increasing costs of fuel in retail outlets" was legally false for six
years — and became prospectively live four days ago.**

- Since **1 January 2020**, Section 10A of the Payment and Settlement Systems Act mandated
  **zero MDR on UPI and RuPay debit** transactions. A fuel dealer paid *no* merchant
  discount rate on a UPI sale. Whatever UPI cost a pump in 2020–2026, it was not MDR.
- On **4 August 2026**, the Taxation and Other Laws (Amendment) Bill amended Section 10A:
  the blanket ban is replaced by a framework in which the government *notifies* which
  payment modes stay MDR-exempt — modes not notified may lawfully attract fees
  ([TechTimes on the amendment](https://www.techtimes.com/articles/322958/20260804/india-opens-door-upi-merchant-fees-parliament-amends-six-year-zero-mdr-law.htm);
  the user-supplied Hindu explainer "Will UPI remain free to use?" covers the same change —
  thehindu.com blocks automated retrieval, so it is cited here as supplied, not verified).
- Context for why: the **Payments Council of India** sought "urgent reconsideration" of
  zero-MDR in March 2025 on sustainability grounds, and the Budget 2025 incentive that
  compensated banks for free UPI was cut from **₹2,000 crore to ₹437 crore**
  ([StartupTalky](https://startuptalky.com/news/rupay-upi-incentive-reduced/)).
- Precedent that this fight is real at the pump: in **January 2017** petrol dealers
  threatened to stop accepting cards when banks moved to levy ~1% MDR on fuel
  ([Deccan Herald 1](https://www.deccanherald.com/india/petrol-pumps-not-accept-card-1985185),
  [2](https://www.deccanherald.com/india/customers-not-pay-card-transaction-1986335)).

So the correct frame is not "UPI has been raising costs" but: **the legal shield that made
UPI free at the pump has just been removed, and the fuel forecourt is the single most
margin-fragile merchant category the change touches.** Here is why, with this machine's
numbers.

## 2. Why the forecourt is uniquely exposed: the 26× leverage

From the PPAC price build-up (01.10.2025, already verified in the blog's fuel-pricing
post) and the OMC model's throughput figures:

| Quantity | Value | Source |
|---|---|---|
| Dealer commission, petrol | ₹4.40/L on ₹94.77 RSP (4.6%) | PPAC RR FY25-26 H1 |
| Dealer commission, diesel | ₹3.03/L on ₹87.67 RSP (3.5%) | PPAC RR FY25-26 H1 |
| Avg outlet throughput | ~45 KL/mo petrol + ~92 KL/mo diesel | OMC model / PPAC |
| Avg outlet monthly sales value | **₹1.23 crore** | computed |
| Avg outlet monthly gross commission | **₹4.77 lakh** | computed |
| Blended margin on ticket value | **3.87%** | computed |

The structural point: **an MDR is charged on the full ticket, but paid out of a 3.87%
margin — a 25.9× leverage.** Nearly the whole pump price is excise, VAT and the OMC's
product cost, none of which the dealer keeps; the fee applies to all of it.

**What an MDR would consume of the average outlet's gross fuel commission:**

| Digital share of sales | 0.25% MDR | 0.30% | 0.90% | 1.00% |
|---|---|---|---|---|
| 30% | 1.9% | 2.3% | 7.0% | 7.8% |
| 50% | 3.2% | 3.9% | 11.6% | 12.9% |
| 70% | 4.5% | 5.4% | 16.3% | 18.1% |
| 90% | 5.8% | 7.0% | 20.9% | 23.3% |

Even a "small" 0.25–0.30% MDR at realistic digital shares takes 2–5% of gross commission;
a card-style ~1% at high UPI shares takes a fifth of it. This is why the 2017 strike
threat happened at ~1%, and why any repeat lands harder now that digital share is higher.
(Gross commission also has to fund staff, power, evaporation losses and licence fees —
the hit to *net* dealer income is proportionally larger; that decomposition is not in
PPAC's tables, so it is not quantified here.)

**What UPI costs a pump today, with zero MDR still in force:** soundbox/PSP
subscriptions, reconciliation effort, and — where a customer pays by RuPay credit card
*via* UPI — credit-card MDR, from which large merchants are not exempt. Magnitudes for
these are not published anywhere authoritative and are left unquantified rather than
guessed.

## 3. The other side of the same counter: cash, and where the ATMs aren't

- India has roughly **2.58 lakh ATMs + cash recyclers** (Feb 2025), of which only about
  **20,000 are white-label ATMs** — the category that skews semi-urban/rural
  ([RBI FAQ](https://www.rbi.org.in/commonman/Upload/English/FAQs/PDFs/FAQATM04072025.pdf),
  [Angel One on the May 2025 fee revision](https://www.angelone.in/news/economy/rbi-approves-atm-interchange-fee-hike-for-financialnon-financial-transactions)).
- From **1 May 2025** the ATM interchange a card issuer pays the machine's owner is
  **₹19 per cash withdrawal** (₹7 non-financial), customer charge beyond free limits
  capped at ₹23 — raised, notably, *at the request of white-label operators* whose rural
  economics did not close at ₹17.
- India has **103,682 fuel retail outlets** (PPAC Snapshot July-26 Table 14, as on 01.07.2026; 29,684 rural — the analysis was first written on the 99,281 count of 01.10.2025) — a network reaching rural
  and highway India far more densely than the WLA fleet, with what an ATM host needs:
  power, lighting, security presence, 24×7 staffing, footfall, and — decisively — **a
  daily cash float from fuel sales**.
- The overlap today is tiny. This repo family's own extraction of SBI's **Cash@PoS**
  fuel-station list found **693 stations** against an SSRI catalog of **82,609 outlets —
  0.8% penetration** — and the outlet-level join showed the program's data is too poor to
  even say *which* outlets those are (18 of 693 confidently matched;
  `fuel-retail-outlets/ATM_OUTLET_JOIN_20260712.md`). The cash-at-pump idea exists in
  policy; it barely exists on the ground, and nobody can currently audit it.

## 4. The integration case: dispensing fees hedge acceptance fees

The two halves of this brief are one machine:

1. **The pump's cash float is the ATM's inventory.** Cash-in-transit and cash handling
   are the largest opex lines in rural ATM economics; a co-located ATM or cash recycler
   fed by the forecourt's own takings shortens or eliminates the CIT loop, and cuts the
   dealer's cash-deposit burden in the same stroke. (Constraint to state honestly: RBI's
   currency-fitness rules mean loose over-the-counter recycling needs a recycler machine
   and note-sorting compliance, not an informal drawer-to-dispenser loop.)
2. **Interchange is fee income where MDR is fee outgo.** At ₹19 per withdrawal, an
   on-site machine doing 50 / 100 / 150 withdrawals a day generates an interchange pool
   of **₹28k / ₹57k / ₹86k a month — 6% / 12% / 18% of the average outlet's entire fuel
   commission.** How that pool splits between the WLA operator and the host is
   commercial, but the host's rent-plus-share is bargained out of it, and it scales with
   exactly the rural, cash-preferring footfall that MDR-bearing digital sales do not
   capture. A dealer facing a 2–7% commission hit from a future MDR can plausibly recover
   it as an ATM host.
3. **For consumers, the arithmetic is availability, not price.** ₹23 is the capped cost
   of a beyond-free-limit withdrawal; the uncapped cost in rural India is the trip to a
   distant machine. Putting cash-out where fuel is bought uses a network 5× the WLA
   fleet's size that already exists on every highway and in every tehsil.
4. **The lighter version needs no ATM licence at all:** micro-ATM / AePS at the pump
   (dealer as business-correspondent agent) or the existing but moribund cash-at-PoS
   facility — which is what SBI's 693-station list was. The infrastructure gap is not
   technology; it is that nobody has made the dealer's business case, which rows 1–2
   above do.

## 5. What this analysis does not establish

- **UPI's actual share of fuel-retail payment value** — no authoritative split found;
  the scenario table spans 30–90% instead of pretending to know.
- **Whether an MDR on UPI will actually be notified, at what rate, or with a fuel/large-
  merchant carve-out** — the 4 Aug 2026 amendment creates the power, not the fee.
- **Rural ATM share precisely**, beyond RBI's statement that WLAs skew semi-urban/rural.
- **Whether PPAC's dealer-commission formula already imputes payment-acceptance costs**
  — the Ready Reckoner does not decompose the commission.
- **Which fuel outlets have ATMs today** — the outlet-level join failed on source data
  quality (2.6% match rate), documented in `ATM_OUTLET_JOIN_20260712.md`.
- The interchange split between WLA operator and site host — commercial, unpublished.

## Verdict

The brief's claim inverts once and then lands. UPI has not been raising fuel-retail
costs — the law forbade exactly that for six years. But the amendment of 4 August 2026
makes the fear forward-real, and the forecourt's 26× ticket-to-margin leverage makes it
the most exposed merchant category in the country. The ATM half of the brief is not a
separate idea; it is the hedge: the same forecourt that would pay fees on digital
acceptance can earn fees on cash dispensing, using a float it already holds and a
network five times the size of the white-label ATM fleet, in precisely the rural
geography where both cash access and ATM economics are thinnest today.
