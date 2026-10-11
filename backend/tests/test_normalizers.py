import pytest
from backend.app.qualification.normalizers import (
    parse_indian_currency,
    normalize_property_type,
    normalize_ownership_type,
    normalize_document_status,
    normalize_occupation,
    normalize_income_mode,
    parse_tenure_years,
    detect_transfer_intent,
)
from backend.app.models.qualification import (
    PropertyType,
    OwnershipType,
    DocumentStatus,
    OccupationType,
    IncomeMode,
    TransferIntent,
)


class TestNormalizers:

    @pytest.mark.parametrize(
        "input_text,expected",
        [
            ("sixty lakhs", 60_00_000),
            ("60 lakh", 60_00_000),
            ("50 lac", 50_00_000),
            ("75 lacs", 75_00_000),
            ("₹75,00,000", 75_00_000),
            ("7500000", 75_00_000),
            ("1.5 crore", 1_50_00_000),
            ("2 cr", 2_00_00_000),
            ("one crore twenty lakh", 1_20_00_000),
            ("roughly one crore twenty", 1_20_00_000),
            ("fifty thousand", 50_000),
            ("50k", 50_000),
        ],
    )
    def test_parse_indian_currency(self, input_text, expected):
        assert parse_indian_currency(input_text) == expected

    @pytest.mark.parametrize(
        "input_text,expected",
        [
            ("residential house", PropertyType.RESIDENTIAL),
            ("flat in Noida", PropertyType.RESIDENTIAL),
            ("commercial office", PropertyType.COMMERCIAL),
            ("shop in market", PropertyType.COMMERCIAL),
            ("industrial manufacturing shed", PropertyType.INDUSTRIAL),
            ("factory unit", PropertyType.INDUSTRIAL),
            ("agricultural farmland", PropertyType.AGRICULTURAL),
            ("khet in village", PropertyType.AGRICULTURAL),
            ("unknown random word", PropertyType.UNKNOWN),
        ],
    )
    def test_normalize_property_type(self, input_text, expected):
        assert normalize_property_type(input_text) == expected

    @pytest.mark.parametrize(
        "input_text,expected",
        [
            ("sole owner", OwnershipType.SOLE),
            ("only mine", OwnershipType.SOLE),
            ("it's my house", OwnershipType.SOLE),
            ("jointly with my wife", OwnershipType.JOINT),
            ("me and my brother", OwnershipType.JOINT),
            ("co-owned with partner", OwnershipType.JOINT),
        ],
    )
    def test_normalize_ownership_type(self, input_text, expected):
        assert normalize_ownership_type(input_text) == expected

    @pytest.mark.parametrize(
        "input_text,expected",
        [
            ("original papers are available at home", DocumentStatus.AVAILABLE),
            ("yes in locker", DocumentStatus.AVAILABLE),
            ("papers are lost and unavailable", DocumentStatus.UNAVAILABLE),
            ("no original documents", DocumentStatus.UNAVAILABLE),
            ("not sure will check", DocumentStatus.UNCERTAIN),
        ],
    )
    def test_normalize_document_status(self, input_text, expected):
        assert normalize_document_status(input_text) == expected

    def test_normalize_occupation(self):
        assert normalize_occupation("salaried employee in MNC") == OccupationType.SALARIED
        assert normalize_occupation("I run a business") == OccupationType.SELF_EMPLOYED
        assert normalize_occupation("trader and shop owner") == OccupationType.SELF_EMPLOYED

    def test_normalize_income_mode(self):
        assert normalize_income_mode("credited into my bank account") == IncomeMode.BANK
        assert normalize_income_mode("cash in hand") == IncomeMode.CASH
        assert normalize_income_mode("both cash and bank transfers") == IncomeMode.MIXED

    @pytest.mark.parametrize(
        "input_text,expected",
        [
            ("ten years", 10),
            ("10 years", 10),
            ("3 years", 3),
            ("15 years", 15),
            ("120 months", 10),
            ("Ten years, actually make that twelve", 12),
            ("make it 5 years", 5),
        ],
    )
    def test_parse_tenure_years(self, input_text, expected):
        assert parse_tenure_years(input_text) == expected

    def test_detect_transfer_intent(self):
        intent, _ = detect_transfer_intent("I want to transfer my existing property loan to you")
        assert intent == TransferIntent.TRANSFER_REQUESTED

        intent, _ = detect_transfer_intent("Can I reduce EMI on my current home loan?")
        assert intent == TransferIntent.EMI_REDUCTION_REQUESTED

        # Unrelated personal loan should NOT trigger property transfer
        intent, _ = detect_transfer_intent("I already have a personal loan from HDFC")
        assert intent == TransferIntent.NONE
