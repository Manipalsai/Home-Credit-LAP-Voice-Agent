import pytest
from backend.app.models.qualification import (
    QualificationState,
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
    ChecklistItemKey,
    ItemState,
)
from backend.app.qualification.engine import QualificationEngine


def create_base_verified_state() -> QualificationState:
    state = QualificationState(
        session_id="test_sess_01",
        customer_name="Rajesh Sharma",
        stage=ConversationStage.ELIGIBILITY_CHECKLIST,
        verification_status=VerificationStatus.VERIFIED,
        availability_status=AvailabilityStatus.AVAILABLE,
        offer_accepted=True,
    )
    # Initialize checklist keys
    for key in [
        ChecklistItemKey.PROPERTY_TYPE,
        ChecklistItemKey.OWNERSHIP_STATUS,
        ChecklistItemKey.ORIGINAL_DOCUMENTS,
        ChecklistItemKey.REQUESTED_AMOUNT,
        ChecklistItemKey.OCCUPATION_AND_INCOME_MODE,
        ChecklistItemKey.MARKET_VALUE,
        ChecklistItemKey.TENURE,
    ]:
        state.get_checklist_item(key)
    return state


class TestQualificationEngine:

    # 1. Standard residential qualification
    def test_01_standard_residential_qualification(self):
        state = create_base_verified_state()
        state.property_type = PropertyType.RESIDENTIAL
        state.ownership_type = OwnershipType.SOLE
        state.document_status = DocumentStatus.AVAILABLE
        state.requested_amount = 50_00_000
        state.occupation = OccupationType.SALARIED
        state.income_mode = IncomeMode.BANK
        state.market_value = 1_00_00_000
        state.tenure_years = 10

        QualificationEngine.evaluate_state(state)

        assert state.outcome == CallOutcome.QUALIFIED_HANDOFF
        assert state.stage == ConversationStage.SENIOR_EXPERT_HANDOFF
        assert state.is_terminal is True
        assert state.handoff_gate_passed is True

    # 2. Commercial property qualification
    def test_02_commercial_property_eligible(self):
        state = create_base_verified_state()
        state.property_type = PropertyType.COMMERCIAL
        state.ownership_type = OwnershipType.SOLE
        state.document_status = DocumentStatus.AVAILABLE
        state.requested_amount = 40_00_000
        state.occupation = OccupationType.SELF_EMPLOYED
        state.income_mode = IncomeMode.BANK
        state.market_value = 1_50_00_000
        state.tenure_years = 7

        QualificationEngine.evaluate_state(state)
        assert state.outcome == CallOutcome.QUALIFIED_HANDOFF

    # 3. Industrial property qualification
    def test_03_industrial_property_eligible(self):
        state = create_base_verified_state()
        state.property_type = PropertyType.INDUSTRIAL
        state.ownership_type = OwnershipType.SOLE
        state.document_status = DocumentStatus.AVAILABLE
        state.requested_amount = 60_00_000
        state.occupation = OccupationType.SELF_EMPLOYED
        state.income_mode = IncomeMode.BANK
        state.market_value = 2_00_00_000
        state.tenure_years = 5

        QualificationEngine.evaluate_state(state)
        assert state.outcome == CallOutcome.QUALIFIED_HANDOFF

    # 4. Joint ownership remains eligible
    def test_04_joint_ownership_remains_eligible(self):
        state = create_base_verified_state()
        state.property_type = PropertyType.RESIDENTIAL
        state.ownership_type = OwnershipType.JOINT
        state.document_status = DocumentStatus.AVAILABLE
        state.requested_amount = 50_00_000
        state.occupation = OccupationType.SALARIED
        state.income_mode = IncomeMode.BANK
        state.market_value = 1_00_00_000
        state.tenure_years = 10

        QualificationEngine.evaluate_state(state)
        assert state.outcome == CallOutcome.QUALIFIED_HANDOFF
        assert state.get_checklist_item(ChecklistItemKey.OWNERSHIP_STATUS).state == ItemState.ANSWERED

    # 5. Loan amount exactly ₹75 lakh
    def test_05_loan_amount_exactly_75_lakh(self):
        state = create_base_verified_state()
        state.property_type = PropertyType.RESIDENTIAL
        state.ownership_type = OwnershipType.SOLE
        state.document_status = DocumentStatus.AVAILABLE
        state.requested_amount = 75_00_000
        state.occupation = OccupationType.SALARIED
        state.income_mode = IncomeMode.BANK
        state.market_value = 1_50_00_000
        state.tenure_years = 10

        QualificationEngine.evaluate_state(state)
        assert state.outcome == CallOutcome.QUALIFIED_HANDOFF
        assert state.requested_amount == 75_00_000

    # 6. Tenure exactly 3 years
    def test_06_tenure_exactly_3_years(self):
        state = create_base_verified_state()
        state.property_type = PropertyType.RESIDENTIAL
        state.ownership_type = OwnershipType.SOLE
        state.document_status = DocumentStatus.AVAILABLE
        state.requested_amount = 30_00_000
        state.occupation = OccupationType.SALARIED
        state.income_mode = IncomeMode.BANK
        state.market_value = 80_00_000
        state.tenure_years = 3

        QualificationEngine.evaluate_state(state)
        assert state.outcome == CallOutcome.QUALIFIED_HANDOFF

    # 7. Tenure exactly 15 years
    def test_07_tenure_exactly_15_years(self):
        state = create_base_verified_state()
        state.property_type = PropertyType.RESIDENTIAL
        state.ownership_type = OwnershipType.SOLE
        state.document_status = DocumentStatus.AVAILABLE
        state.requested_amount = 50_00_000
        state.occupation = OccupationType.SALARIED
        state.income_mode = IncomeMode.BANK
        state.market_value = 1_00_00_000
        state.tenure_years = 15

        QualificationEngine.evaluate_state(state)
        assert state.outcome == CallOutcome.QUALIFIED_HANDOFF

    # 8. Agricultural property -> immediate termination
    def test_08_agricultural_property_disqualification(self):
        state = create_base_verified_state()
        state.property_type = PropertyType.AGRICULTURAL

        QualificationEngine.evaluate_state(state)
        assert state.outcome == CallOutcome.DISQUALIFIED
        assert state.stage == ConversationStage.DISQUALIFIED_EXIT
        assert state.disqualification_reason == DisqualificationReason.AGRICULTURAL_PROPERTY
        assert state.is_terminal is True
        assert QualificationEngine.get_next_checklist_item(state) is None

    # 9. Original documents unavailable -> immediate termination
    def test_09_documents_unavailable_disqualification(self):
        state = create_base_verified_state()
        state.property_type = PropertyType.RESIDENTIAL
        state.document_status = DocumentStatus.UNAVAILABLE

        QualificationEngine.evaluate_state(state)
        assert state.outcome == CallOutcome.DISQUALIFIED
        assert state.disqualification_reason == DisqualificationReason.ORIGINAL_DOCS_UNAVAILABLE
        assert state.is_terminal is True
        assert QualificationEngine.get_next_checklist_item(state) is None

    # 10. Cash income -> immediate termination
    def test_10_cash_income_disqualification(self):
        state = create_base_verified_state()
        state.property_type = PropertyType.COMMERCIAL
        state.document_status = DocumentStatus.AVAILABLE
        state.income_mode = IncomeMode.CASH

        QualificationEngine.evaluate_state(state)
        assert state.outcome == CallOutcome.DISQUALIFIED
        assert state.disqualification_reason == DisqualificationReason.CASH_INCOME
        assert state.is_terminal is True

    # 11. Two-year tenure -> immediate termination
    def test_11_two_year_tenure_disqualification(self):
        state = create_base_verified_state()
        state.tenure_years = 2

        QualificationEngine.evaluate_state(state)
        assert state.outcome == CallOutcome.DISQUALIFIED
        assert state.disqualification_reason == DisqualificationReason.TENURE_OUT_OF_RANGE
        assert state.is_terminal is True

    # 12. Sixteen-year tenure -> immediate termination
    def test_12_sixteen_year_tenure_disqualification(self):
        state = create_base_verified_state()
        state.tenure_years = 16

        QualificationEngine.evaluate_state(state)
        assert state.outcome == CallOutcome.DISQUALIFIED
        assert state.disqualification_reason == DisqualificationReason.TENURE_OUT_OF_RANGE
        assert state.is_terminal is True

    # 13. Loan alternative: 90L requested, accepts 75L
    def test_13_loan_amount_accepts_75l_cap(self):
        state = create_base_verified_state()
        state.raw_requested_amount = 90_00_000
        state.amount_cap_accepted = True
        state.property_type = PropertyType.RESIDENTIAL
        state.ownership_type = OwnershipType.SOLE
        state.document_status = DocumentStatus.AVAILABLE
        state.occupation = OccupationType.SALARIED
        state.income_mode = IncomeMode.BANK
        state.market_value = 1_50_00_000
        state.tenure_years = 10

        QualificationEngine.evaluate_state(state)
        assert state.requested_amount == 75_00_000
        assert state.outcome == CallOutcome.QUALIFIED_HANDOFF

    # 14. Loan alternative: 90L requested, declines 75L
    def test_14_loan_amount_declines_75l_cap(self):
        state = create_base_verified_state()
        state.raw_requested_amount = 90_00_000
        state.amount_cap_accepted = False

        QualificationEngine.evaluate_state(state)
        assert state.outcome == CallOutcome.AMOUNT_CAP_REJECTED
        assert state.stage == ConversationStage.DISQUALIFIED_EXIT
        assert state.is_terminal is True

    # 17 & 18. Transfer Intent Specialist Routing
    def test_17_18_transfer_intent_routing(self):
        state = create_base_verified_state()
        state.transfer_intent = TransferIntent.TRANSFER_REQUESTED
        QualificationEngine.evaluate_state(state)
        assert state.outcome == CallOutcome.ROUTED_TRANSFER_SPECIALIST
        assert state.stage == ConversationStage.SPECIALIST_TRANSFER
        assert state.is_terminal is True

    # 33. Premature handoff rejected if fields missing
    def test_33_premature_handoff_rejected(self):
        state = create_base_verified_state()
        state.property_type = PropertyType.RESIDENTIAL
        # missing other 6 items
        assert QualificationEngine.check_handoff_gate(state) is False
        QualificationEngine.evaluate_state(state)
        assert state.outcome == CallOutcome.IN_PROGRESS
        assert state.stage == ConversationStage.ELIGIBILITY_CHECKLIST

    # 34. Previously answered fields are not asked again
    def test_34_next_checklist_item_skips_answered(self):
        state = create_base_verified_state()
        state.property_type = PropertyType.RESIDENTIAL
        QualificationEngine.evaluate_state(state)
        next_item = QualificationEngine.get_next_checklist_item(state)
        assert next_item == ChecklistItemKey.OWNERSHIP_STATUS

    # 35. Unknown answers never count as eligible
    def test_35_unknown_answers_never_eligible(self):
        state = create_base_verified_state()
        state.property_type = PropertyType.UNKNOWN
        state.document_status = DocumentStatus.UNKNOWN
        assert QualificationEngine.check_handoff_gate(state) is False
