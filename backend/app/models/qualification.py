from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class PropertyType(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    AGRICULTURAL = "agricultural"
    UNKNOWN = "unknown"


class OwnershipType(str, Enum):
    SOLE = "sole"
    JOINT = "joint"
    UNKNOWN = "unknown"


class DocumentStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNCERTAIN = "uncertain"
    UNKNOWN = "unknown"


class OccupationType(str, Enum):
    SALARIED = "salaried"
    SELF_EMPLOYED = "self_employed"
    UNKNOWN = "unknown"


class IncomeMode(str, Enum):
    BANK = "bank"
    CASH = "cash"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class VerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    WRONG_PERSON = "wrong_person"
    DECLINED = "declined"
    DND = "dnd"


class AvailabilityStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    DECLINED = "declined"
    UNKNOWN = "unknown"


class TransferIntent(str, Enum):
    NONE = "none"
    TRANSFER_REQUESTED = "transfer_requested"
    EMI_REDUCTION_REQUESTED = "emi_reduction_requested"


class ConversationStage(str, Enum):
    GREETING_VERIFICATION = "greeting_verification"
    CALLBACK_FLOW = "callback_flow"
    WRONG_PERSON_EXIT = "wrong_person_exit"
    DECLINED_EXIT = "declined_exit"
    OFFER_PRESENTATION = "offer_presentation"
    ELIGIBILITY_CHECKLIST = "eligibility_checklist"
    AMOUNT_CAP_CONFIRMATION = "amount_cap_confirmation"
    SPECIALIST_TRANSFER = "specialist_transfer"
    DISQUALIFIED_EXIT = "disqualified_exit"
    SENIOR_EXPERT_HANDOFF = "senior_expert_handoff"


class ChecklistItemKey(str, Enum):
    PROPERTY_TYPE = "property_type"
    OWNERSHIP_STATUS = "ownership_status"
    ORIGINAL_DOCUMENTS = "original_documents"
    REQUESTED_AMOUNT = "requested_amount"
    OCCUPATION_AND_INCOME_MODE = "occupation_and_income_mode"
    MARKET_VALUE = "market_value"
    TENURE = "tenure"


class ItemState(str, Enum):
    UNKNOWN = "UNKNOWN"
    ANSWERED = "ANSWERED"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    DISQUALIFIED = "DISQUALIFIED"
    PENDING_CONFIRMATION = "PENDING_CONFIRMATION"


class DisqualificationReason(str, Enum):
    AGRICULTURAL_PROPERTY = "agricultural_property"
    ORIGINAL_DOCS_UNAVAILABLE = "original_docs_unavailable"
    CASH_INCOME = "cash_income"
    TENURE_OUT_OF_RANGE = "tenure_out_of_range"
    AMOUNT_CAP_DECLINED = "amount_cap_declined"


class CallOutcome(str, Enum):
    IN_PROGRESS = "in_progress"
    QUALIFIED_HANDOFF = "qualified_handoff"
    DISQUALIFIED = "disqualified"
    ROUTED_TRANSFER_SPECIALIST = "routed_transfer_specialist"
    BUSY_CALLBACK_SCHEDULED = "busy_callback_scheduled"
    WRONG_PERSON = "wrong_person"
    CUSTOMER_DECLINED = "customer_declined"
    AMOUNT_CAP_REJECTED = "amount_cap_rejected"
    DND_REQUESTED = "dnd_requested"


class ChecklistItem(BaseModel):
    key: ChecklistItemKey
    label: str
    state: ItemState = ItemState.UNKNOWN
    value: Any = None
    clarification_note: Optional[str] = None


class QualificationState(BaseModel):
    session_id: str
    customer_name: str
    company_name: str = "Home Credit India"
    agent_name: str = "Pooja"
    agent_gender: str = "female"
    language: str = "English"

    # Stage and outcome tracking
    stage: ConversationStage = ConversationStage.GREETING_VERIFICATION
    outcome: CallOutcome = CallOutcome.IN_PROGRESS
    is_terminal: bool = False

    # Identity and call state
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    availability_status: AvailabilityStatus = AvailabilityStatus.UNKNOWN
    callback_preference: Optional[str] = None
    offer_accepted: Optional[bool] = None

    # Transfer detection
    transfer_intent: TransferIntent = TransferIntent.NONE
    transfer_reason: Optional[str] = None

    # Eligibility fields
    property_type: PropertyType = PropertyType.UNKNOWN
    ownership_type: OwnershipType = OwnershipType.UNKNOWN
    document_status: DocumentStatus = DocumentStatus.UNKNOWN
    requested_amount: Optional[int] = None  # in INR integer
    raw_requested_amount: Optional[int] = None
    amount_cap_accepted: Optional[bool] = None
    occupation: OccupationType = OccupationType.UNKNOWN
    income_mode: IncomeMode = IncomeMode.UNKNOWN
    market_value: Optional[int] = None  # in INR integer
    tenure_years: Optional[int] = None

    # Disqualification info
    disqualification_reason: Optional[DisqualificationReason] = None
    disqualification_detail: Optional[str] = None

    # Checklist progress (ordered 1 to 7)
    checklist: Dict[ChecklistItemKey, ChecklistItem] = Field(default_factory=dict)

    # Next prompt or question to ask
    current_prompt: Optional[str] = None
    last_customer_utterance: Optional[str] = None
    handoff_gate_passed: bool = False

    def get_checklist_item(self, key: ChecklistItemKey) -> ChecklistItem:
        if key not in self.checklist:
            labels = {
                ChecklistItemKey.PROPERTY_TYPE: "Property Type",
                ChecklistItemKey.OWNERSHIP_STATUS: "Ownership Status",
                ChecklistItemKey.ORIGINAL_DOCUMENTS: "Original Property Documents",
                ChecklistItemKey.REQUESTED_AMOUNT: "Requested Loan Amount",
                ChecklistItemKey.OCCUPATION_AND_INCOME_MODE: "Occupation and Income Mode",
                ChecklistItemKey.MARKET_VALUE: "Estimated Current Market Value",
                ChecklistItemKey.TENURE: "Desired Repayment Tenure",
            }
            self.checklist[key] = ChecklistItem(key=key, label=labels.get(key, key.value))
        return self.checklist[key]
