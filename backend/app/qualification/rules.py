from typing import Optional, Tuple
from backend.app.models.qualification import (
    PropertyType,
    OwnershipType,
    DocumentStatus,
    OccupationType,
    IncomeMode,
    DisqualificationReason,
    ChecklistItemKey,
)

MAX_LOAN_AMOUNT = 75_00_000  # ₹75 Lakhs
MIN_TENURE_YEARS = 3
MAX_TENURE_YEARS = 15

CHECKLIST_SEQUENCE = [
    ChecklistItemKey.PROPERTY_TYPE,
    ChecklistItemKey.OWNERSHIP_STATUS,
    ChecklistItemKey.ORIGINAL_DOCUMENTS,
    ChecklistItemKey.REQUESTED_AMOUNT,
    ChecklistItemKey.OCCUPATION_AND_INCOME_MODE,
    ChecklistItemKey.MARKET_VALUE,
    ChecklistItemKey.TENURE,
]


def check_disqualification_property_type(prop_type: PropertyType) -> Optional[Tuple[DisqualificationReason, str]]:
    if prop_type == PropertyType.AGRICULTURAL:
        return (
            DisqualificationReason.AGRICULTURAL_PROPERTY,
            "Agricultural property is not eligible for this Loan Against Property offer.",
        )
    return None


def check_disqualification_documents(doc_status: DocumentStatus) -> Optional[Tuple[DisqualificationReason, str]]:
    if doc_status == DocumentStatus.UNAVAILABLE:
        return (
            DisqualificationReason.ORIGINAL_DOCS_UNAVAILABLE,
            "Original property documents are mandatory for verification under this offer.",
        )
    return None


def check_disqualification_income(income_mode: IncomeMode) -> Optional[Tuple[DisqualificationReason, str]]:
    if income_mode == IncomeMode.CASH:
        return (
            DisqualificationReason.CASH_INCOME,
            "Income must be received through bank credit/deposits. Cash income is not eligible.",
        )
    return None


def check_disqualification_tenure(tenure: Optional[int]) -> Optional[Tuple[DisqualificationReason, str]]:
    if tenure is not None:
        if tenure < MIN_TENURE_YEARS or tenure > MAX_TENURE_YEARS:
            return (
                DisqualificationReason.TENURE_OUT_OF_RANGE,
                f"Requested tenure of {tenure} years is outside permitted range of {MIN_TENURE_YEARS} to {MAX_TENURE_YEARS} years.",
            )
    return None
