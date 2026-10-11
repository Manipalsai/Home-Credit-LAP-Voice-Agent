import pytest
from backend.app.qualification.extractor import ConversationalExtractor
from backend.app.models.qualification import (
    ConversationStage,
    PropertyType,
    OwnershipType,
    DocumentStatus,
    OccupationType,
    IncomeMode,
    VerificationStatus,
    AvailabilityStatus,
)


class TestExtractor:

    # 23. Customer provides property type, ownership, and market value together
    def test_23_extract_multiple_facts_together(self):
        text = "It's my residential house worth about 1.5 crore"
        facts = ConversationalExtractor.extract_facts(text, ConversationStage.ELIGIBILITY_CHECKLIST)

        assert facts.get("property_type") == PropertyType.RESIDENTIAL
        assert facts.get("ownership_type") == OwnershipType.SOLE
        assert facts.get("market_value") == 1_50_00_000

    # 24. Out of order extraction (all 4 facts in one sentence)
    def test_24_out_of_order_extraction(self):
        text = "It's a residential house, jointly owned with my wife, worth about one crore, and I need sixty lakhs."
        facts = ConversationalExtractor.extract_facts(text, ConversationStage.ELIGIBILITY_CHECKLIST)

        assert facts.get("property_type") == PropertyType.RESIDENTIAL
        assert facts.get("ownership_type") == OwnershipType.JOINT
        assert facts.get("market_value") == 1_00_00_000
        assert facts.get("requested_amount") == 60_00_000

    # 26. Spoken correction handling
    def test_26_spoken_correction(self):
        text = "Ten years, actually make that twelve"
        facts = ConversationalExtractor.extract_facts(text, ConversationStage.ELIGIBILITY_CHECKLIST)
        assert facts.get("tenure_years") == 12

    # 27. Ambiguous document availability
    def test_27_ambiguous_documents(self):
        text = "I am not sure, will check"
        facts = ConversationalExtractor.extract_facts(text, ConversationStage.ELIGIBILITY_CHECKLIST)
        assert facts.get("document_status") == DocumentStatus.UNCERTAIN

    # 29. Occupation provided but income mode omitted
    def test_29_occupation_only(self):
        text = "I am salaried in an IT firm"
        facts = ConversationalExtractor.extract_facts(text, ConversationStage.ELIGIBILITY_CHECKLIST)
        assert facts.get("occupation") == OccupationType.SALARIED
        assert "income_mode" not in facts

    # 30. Income mode provided but occupation omitted
    def test_30_income_mode_only(self):
        text = "Everything comes directly into my bank account"
        facts = ConversationalExtractor.extract_facts(text, ConversationStage.ELIGIBILITY_CHECKLIST)
        assert facts.get("income_mode") == IncomeMode.BANK
        assert "occupation" not in facts

    # 20. Busy customer extraction
    def test_20_busy_customer(self):
        text = "I am busy in a meeting right now, please call me back tomorrow"
        facts = ConversationalExtractor.extract_facts(text, ConversationStage.GREETING_VERIFICATION)
        assert facts.get("availability_status") == AvailabilityStatus.BUSY
        assert "tomorrow" in facts.get("callback_preference", "").lower()

    # 21. Wrong person
    def test_21_wrong_person(self):
        text = "No, this is wrong number, not Rajesh here"
        facts = ConversationalExtractor.extract_facts(text, ConversationStage.GREETING_VERIFICATION)
        assert facts.get("verification_status") == VerificationStatus.WRONG_PERSON

    # 22. Customer declines
    def test_22_customer_declines(self):
        text = "I am not interested in taking any loan"
        facts = ConversationalExtractor.extract_facts(text, ConversationStage.OFFER_PRESENTATION)
        assert facts.get("offer_accepted") is False
