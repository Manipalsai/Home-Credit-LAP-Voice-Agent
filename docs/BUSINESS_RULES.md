# Home Credit LAP Voice Agent — Business Rules Specification

This document details the exact qualification criteria, precedence rules, and disqualification gates implemented in the **Home Credit Loan Against Property (LAP)** engine.

---

## 1. Stage Precedence & Global Rules

| Rule Key | Condition | Precedence / Action | Terminal Status |
|---|---|---|---|
| **Identity Verification** | Customer identity unverified or wrong person answers | Immediately apologize and conclude. Never disclose pre-approved terms. | `wrong_person` (Terminal) |
| **Customer Availability** | Borrower is busy (driving, meeting, etc.) | Collect callback preference, confirm timestamp, and end call. Do not push checklist. | `busy_callback_scheduled` (Terminal) |
| **Existing Property Loan Transfer** | Borrower requests balance transfer or EMI reduction on existing property loan | Stop fresh-loan checklist immediately. Route to dedicated Loan Transfer Desk. | `routed_transfer_specialist` (Terminal) |
| **Immediate Disqualification** | Any disqualifying condition detected at any turn | Immediately inform customer respectfully and terminate active checklist. | `disqualified` (Terminal) |
| **Cap Negotiation (₹75L)** | Customer requests > ₹75,00,000 | Inquire if they agree to proceed with ₹75L. If Yes: lock ₹75L. If No: terminate politely. | `amount_cap_rejected` if declined |

> **Note on Existing Loans:** An unrelated personal loan, auto loan, or credit card debt does NOT trigger transfer routing. Transfer routing is strictly for loans secured against the property or mortgage refinancing requests.

---

## 2. The 7-Point Qualification Checklist

| Item # | Checklist Attribute | Eligible Criteria | Ineligible Criteria / Action |
|---|---|---|---|
| **1** | **Property Type** | Residential, Commercial, Industrial | **Agricultural property is strictly ineligible.** Immediate termination. |
| **2** | **Ownership Status** | Sole ownership OR Joint ownership | Both are eligible. Joint ownership with spouse/family is never rejected. |
| **3** | **Original Documents** | Original title deeds must be available for legal audit | If documents are missing, lost, or disputed -> Immediate disqualification. |
| **4** | **Requested Loan Amount** | ≤ ₹75,00,000 (75 Lakhs) | > ₹75L requires explicit customer agreement to the ₹75L cap. Silent adjustments are forbidden. |
| **5** | **Occupation & Income Mode** | Salaried OR Self-employed WITH direct Bank credit | **Cash income is strictly ineligible.** Immediate disqualification. Both occupation and income mode must be captured. |
| **6** | **Current Market Value** | Customer's estimate in INR | No arbitrary minimum valuation threshold. Clarify if ambiguous. |
| **7** | **Repayment Tenure** | 3 to 15 years inclusive (36 to 180 months) | Tenures < 3 years or > 15 years -> Immediate disqualification. |

---

## 3. Disqualification Rules Matrix

When a disqualification rule fires, the agent provides a polite, specific explanation and halts the fresh-loan qualification sequence:

1. **Agricultural Property:**
   - *Message:* `"Thank you for sharing that. Unfortunately, under this specific offer, agricultural properties are not eligible at this time. Thank you for your time with Home Credit India."`
   - *Reason Code:* `agricultural_property`
2. **Missing Original Title Deeds:**
   - *Message:* `"Under our policy, original property documents are mandatory for verification. Since they are not currently available, we cannot proceed with this offer today. Thank you for your time."`
   - *Reason Code:* `original_docs_unavailable`
3. **Cash Income Mode:**
   - *Message:* `"To qualify for this offer, income must be routed through bank account deposits. Since your income is cash-based, we are unable to process this application at this time. Thank you for your time."`
   - *Reason Code:* `cash_income`
4. **Tenure Out of Bounds (< 3 or > 15 Years):**
   - *Message:* `"Our repayment tenure for this program is between 3 and 15 years. Since your requested tenure falls outside this range, we are unable to proceed with this offer. Thank you for your time."`
   - *Reason Code:* `tenure_out_of_range`
5. **Declined ₹75 Lakh Ceiling:**
   - *Message:* `"I understand your requirement is higher than our offer limit. Since this specific program is capped at ₹75 Lakhs, we cannot proceed today, but we will notify you if higher limits become available. Thank you for your time."`
   - *Reason Code:* `amount_cap_declined`

---

## 4. Senior Loan Expert Handoff Gate

A customer may **ONLY** pass the gate to Senior Loan Expert handoff when all 7 checklist items have reached status `ANSWERED` and satisfy the criteria below:

```python
def check_handoff_gate(state: QualificationState) -> bool:
    return (
        state.verification_status == VerificationStatus.VERIFIED
        and state.offer_accepted is True
        and state.transfer_intent == TransferIntent.NONE
        and state.disqualification_reason is None
        and state.property_type in [PropertyType.RESIDENTIAL, PropertyType.COMMERCIAL, PropertyType.INDUSTRIAL]
        and state.ownership_type in [OwnershipType.SOLE, OwnershipType.JOINT]
        and state.document_status == DocumentStatus.AVAILABLE
        and (state.requested_amount is not None and state.requested_amount <= 75_00_000)
        and state.occupation in [OccupationType.SALARIED, OccupationType.SELF_EMPLOYED]
        and state.income_mode == IncomeMode.BANK
        and (state.market_value is not None and state.market_value > 0)
        and (state.tenure_years is not None and 3 <= state.tenure_years <= 15)
    )
```

Premature handoff or bypass of this gate is strictly prevented by the deterministic backend engine.
