from typing import Optional, Tuple, List
from backend.app.models.qualification import (
    QualificationState,
    ChecklistItemKey,
    ItemState,
    PropertyType,
    OwnershipType,
    DocumentStatus,
    OccupationType,
    IncomeMode,
    TransferIntent,
    ConversationStage,
    CallOutcome,
    DisqualificationReason,
    VerificationStatus,
    AvailabilityStatus,
)
from backend.app.qualification.rules import (
    MAX_LOAN_AMOUNT,
    MIN_TENURE_YEARS,
    MAX_TENURE_YEARS,
    CHECKLIST_SEQUENCE,
    check_disqualification_property_type,
    check_disqualification_documents,
    check_disqualification_income,
    check_disqualification_tenure,
)


class QualificationEngine:
    """
    Deterministic eligibility and business-rules engine for Home Credit LAP.
    Enforces strict business rules without depending on LLM output.
    """

    @staticmethod
    def evaluate_state(state: QualificationState) -> QualificationState:
        """Evaluates checklist fields, disqualification rules, transfer routing, and handoff gate."""
        if state.is_terminal:
            return state

        # 1. Check Transfer Intent (precedence over fresh-loan flow)
        if state.transfer_intent in [TransferIntent.TRANSFER_REQUESTED, TransferIntent.EMI_REDUCTION_REQUESTED]:
            state.stage = ConversationStage.SPECIALIST_TRANSFER
            state.outcome = CallOutcome.ROUTED_TRANSFER_SPECIALIST
            state.is_terminal = True
            return state

        # 2. Check Verification and Greeting status
        if state.verification_status == VerificationStatus.WRONG_PERSON:
            state.stage = ConversationStage.WRONG_PERSON_EXIT
            state.outcome = CallOutcome.WRONG_PERSON
            state.is_terminal = True
            return state

        if state.verification_status == VerificationStatus.DECLINED:
            state.stage = ConversationStage.DECLINED_EXIT
            state.outcome = CallOutcome.CUSTOMER_DECLINED
            state.is_terminal = True
            return state

        if state.verification_status == VerificationStatus.DND:
            state.stage = ConversationStage.DECLINED_EXIT
            state.outcome = CallOutcome.DND_REQUESTED
            state.is_terminal = True
            return state

        if state.availability_status == AvailabilityStatus.BUSY:
            state.stage = ConversationStage.CALLBACK_FLOW
            state.outcome = CallOutcome.BUSY_CALLBACK_SCHEDULED
            state.is_terminal = True
            return state

        if state.availability_status == AvailabilityStatus.DECLINED or state.offer_accepted is False:
            state.stage = ConversationStage.DECLINED_EXIT
            state.outcome = CallOutcome.CUSTOMER_DECLINED
            state.is_terminal = True
            return state

        # 3. Disqualification Checks (Immediate Exits)
        # 3a. Agricultural Property
        prop_disq = check_disqualification_property_type(state.property_type)
        if prop_disq:
            reason, detail = prop_disq
            state.disqualification_reason = reason
            state.disqualification_detail = detail
            state.stage = ConversationStage.DISQUALIFIED_EXIT
            state.outcome = CallOutcome.DISQUALIFIED
            state.is_terminal = True
            state.get_checklist_item(ChecklistItemKey.PROPERTY_TYPE).state = ItemState.DISQUALIFIED
            return state

        # 3b. Missing Original Documents
        doc_disq = check_disqualification_documents(state.document_status)
        if doc_disq:
            reason, detail = doc_disq
            state.disqualification_reason = reason
            state.disqualification_detail = detail
            state.stage = ConversationStage.DISQUALIFIED_EXIT
            state.outcome = CallOutcome.DISQUALIFIED
            state.is_terminal = True
            state.get_checklist_item(ChecklistItemKey.ORIGINAL_DOCUMENTS).state = ItemState.DISQUALIFIED
            return state

        # 3c. Cash Income
        income_disq = check_disqualification_income(state.income_mode)
        if income_disq:
            reason, detail = income_disq
            state.disqualification_reason = reason
            state.disqualification_detail = detail
            state.stage = ConversationStage.DISQUALIFIED_EXIT
            state.outcome = CallOutcome.DISQUALIFIED
            state.is_terminal = True
            state.get_checklist_item(ChecklistItemKey.OCCUPATION_AND_INCOME_MODE).state = ItemState.DISQUALIFIED
            return state

        # 3d. Tenure Out of Range (<3 or >15)
        tenure_disq = check_disqualification_tenure(state.tenure_years)
        if tenure_disq:
            reason, detail = tenure_disq
            state.disqualification_reason = reason
            state.disqualification_detail = detail
            state.stage = ConversationStage.DISQUALIFIED_EXIT
            state.outcome = CallOutcome.DISQUALIFIED
            state.is_terminal = True
            state.get_checklist_item(ChecklistItemKey.TENURE).state = ItemState.DISQUALIFIED
            return state

        # 3e. Loan Amount > ₹75L cap check
        if state.raw_requested_amount is not None and state.raw_requested_amount > MAX_LOAN_AMOUNT:
            if state.amount_cap_accepted is False:
                state.disqualification_reason = DisqualificationReason.AMOUNT_CAP_DECLINED
                state.disqualification_detail = f"Customer requested ₹{state.raw_requested_amount:,} and declined maximum offer limit of ₹{MAX_LOAN_AMOUNT:,}."
                state.stage = ConversationStage.DISQUALIFIED_EXIT
                state.outcome = CallOutcome.AMOUNT_CAP_REJECTED
                state.is_terminal = True
                state.get_checklist_item(ChecklistItemKey.REQUESTED_AMOUNT).state = ItemState.DISQUALIFIED
                return state
            elif state.amount_cap_accepted is True:
                state.requested_amount = MAX_LOAN_AMOUNT
                item = state.get_checklist_item(ChecklistItemKey.REQUESTED_AMOUNT)
                item.state = ItemState.ANSWERED
                item.value = MAX_LOAN_AMOUNT
            elif state.amount_cap_accepted is None:
                # Requires customer agreement to cap
                state.stage = ConversationStage.AMOUNT_CAP_CONFIRMATION
                item = state.get_checklist_item(ChecklistItemKey.REQUESTED_AMOUNT)
                item.state = ItemState.PENDING_CONFIRMATION
                item.value = state.raw_requested_amount
                return state

        # 4. Synchronize Checklist Item States
        QualificationEngine._sync_checklist_states(state)

        # 5. Check Final Handoff Gate
        if QualificationEngine.check_handoff_gate(state):
            state.stage = ConversationStage.SENIOR_EXPERT_HANDOFF
            state.outcome = CallOutcome.QUALIFIED_HANDOFF
            state.is_terminal = True
            state.handoff_gate_passed = True
            return state

        # If in qualification flow, ensure stage is checklist
        if state.verification_status == VerificationStatus.VERIFIED and state.offer_accepted is True:
            state.stage = ConversationStage.ELIGIBILITY_CHECKLIST

        return state

    @staticmethod
    def _sync_checklist_states(state: QualificationState) -> None:
        """Syncs the status of all 7 checklist items based on raw fields."""
        # 1. Property Type
        item = state.get_checklist_item(ChecklistItemKey.PROPERTY_TYPE)
        if state.property_type in [PropertyType.RESIDENTIAL, PropertyType.COMMERCIAL, PropertyType.INDUSTRIAL]:
            item.state = ItemState.ANSWERED
            item.value = state.property_type.value
        elif state.property_type == PropertyType.AGRICULTURAL:
            item.state = ItemState.DISQUALIFIED
            item.value = state.property_type.value
        else:
            item.state = ItemState.UNKNOWN

        # 2. Ownership Status
        item = state.get_checklist_item(ChecklistItemKey.OWNERSHIP_STATUS)
        if state.ownership_type in [OwnershipType.SOLE, OwnershipType.JOINT]:
            item.state = ItemState.ANSWERED
            item.value = state.ownership_type.value
        else:
            item.state = ItemState.UNKNOWN

        # 3. Original Documents
        item = state.get_checklist_item(ChecklistItemKey.ORIGINAL_DOCUMENTS)
        if state.document_status == DocumentStatus.AVAILABLE:
            item.state = ItemState.ANSWERED
            item.value = state.document_status.value
        elif state.document_status == DocumentStatus.UNAVAILABLE:
            item.state = ItemState.DISQUALIFIED
            item.value = state.document_status.value
        elif state.document_status == DocumentStatus.UNCERTAIN:
            item.state = ItemState.NEEDS_CLARIFICATION
            item.clarification_note = "Customer uncertain about original title document availability"
        else:
            item.state = ItemState.UNKNOWN

        # 4. Requested Amount
        item = state.get_checklist_item(ChecklistItemKey.REQUESTED_AMOUNT)
        if state.requested_amount is not None and state.requested_amount <= MAX_LOAN_AMOUNT:
            item.state = ItemState.ANSWERED
            item.value = state.requested_amount
        elif state.raw_requested_amount is not None and state.raw_requested_amount > MAX_LOAN_AMOUNT:
            if state.amount_cap_accepted is True:
                item.state = ItemState.ANSWERED
                item.value = MAX_LOAN_AMOUNT
            elif state.amount_cap_accepted is False:
                item.state = ItemState.DISQUALIFIED
            else:
                item.state = ItemState.PENDING_CONFIRMATION

        # 5. Occupation & Income Mode (Both are required for checklist item 5)
        item = state.get_checklist_item(ChecklistItemKey.OCCUPATION_AND_INCOME_MODE)
        has_occ = state.occupation in [OccupationType.SALARIED, OccupationType.SELF_EMPLOYED]
        has_bank = state.income_mode == IncomeMode.BANK
        if has_occ and has_bank:
            item.state = ItemState.ANSWERED
            item.value = {"occupation": state.occupation.value, "income_mode": state.income_mode.value}
        elif state.income_mode == IncomeMode.CASH:
            item.state = ItemState.DISQUALIFIED
            item.value = {"occupation": state.occupation.value, "income_mode": state.income_mode.value}
        elif state.income_mode == IncomeMode.MIXED:
            item.state = ItemState.NEEDS_CLARIFICATION
            item.clarification_note = "Income is mixed cash/bank; clarify verifiable bank deposit amount."
        elif has_occ and not has_bank:
            item.state = ItemState.NEEDS_CLARIFICATION
            item.clarification_note = "Occupation provided; income credit mode (bank vs cash) missing."
        elif not has_occ and has_bank:
            item.state = ItemState.NEEDS_CLARIFICATION
            item.clarification_note = "Bank income confirmed; occupation (salaried vs self-employed) missing."
        else:
            item.state = ItemState.UNKNOWN

        # 6. Market Value
        item = state.get_checklist_item(ChecklistItemKey.MARKET_VALUE)
        if state.market_value is not None and state.market_value > 0:
            item.state = ItemState.ANSWERED
            item.value = state.market_value
        else:
            item.state = ItemState.UNKNOWN

        # 7. Tenure
        item = state.get_checklist_item(ChecklistItemKey.TENURE)
        if state.tenure_years is not None:
            if MIN_TENURE_YEARS <= state.tenure_years <= MAX_TENURE_YEARS:
                item.state = ItemState.ANSWERED
                item.value = state.tenure_years
            else:
                item.state = ItemState.DISQUALIFIED
                item.value = state.tenure_years
        else:
            item.state = ItemState.UNKNOWN

    @staticmethod
    def get_next_checklist_item(state: QualificationState) -> Optional[ChecklistItemKey]:
        """Returns the earliest unanswered or clarification-needed checklist item from the sequence."""
        if state.is_terminal:
            return None

        for key in CHECKLIST_SEQUENCE:
            item = state.get_checklist_item(key)
            if item.state in [ItemState.UNKNOWN, ItemState.NEEDS_CLARIFICATION, ItemState.PENDING_CONFIRMATION]:
                return key

        return None

    @staticmethod
    def check_handoff_gate(state: QualificationState) -> bool:
        """
        Final Handoff Gate:
        The customer may reach the fresh-loan handoff only when:
        1. Customer verified.
        2. Customer agreed to continue.
        3. All 7 checklist items have passed.
        4. Amount is within limit (or agreed to 75L).
        5. No disqualifying condition.
        6. No loan-transfer branch triggered.
        """
        if state.verification_status != VerificationStatus.VERIFIED:
            return False
        if state.offer_accepted is not True:
            return False
        if state.transfer_intent != TransferIntent.NONE:
            return False
        if state.disqualification_reason is not None:
            return False

        # All 7 checklist items must be ANSWERED
        for key in CHECKLIST_SEQUENCE:
            item = state.get_checklist_item(key)
            if item.state != ItemState.ANSWERED:
                return False

        return True
