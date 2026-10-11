import re
from typing import Dict, Any, Optional, Tuple
from backend.app.models.qualification import (
    PropertyType,
    OwnershipType,
    DocumentStatus,
    OccupationType,
    IncomeMode,
    TransferIntent,
    VerificationStatus,
    AvailabilityStatus,
    ConversationStage,
    ChecklistItemKey,
)
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


class ConversationalExtractor:
    """
    Extracts structured facts from natural language customer utterances.
    Supports out-of-order facts, corrections, interruptions, and multi-fact statements.
    """

    @staticmethod
    def extract_facts(
        utterance: str,
        current_stage: ConversationStage,
        current_checklist_item: Optional[ChecklistItemKey] = None,
    ) -> Dict[str, Any]:
        """Extracts all facts present in the utterance regardless of the current stage."""
        facts: Dict[str, Any] = {}
        t = utterance.strip().lower()

        # 1. Transfer Intent Detection
        transfer_intent, transfer_reason = detect_transfer_intent(utterance)
        if transfer_intent != TransferIntent.NONE:
            facts["transfer_intent"] = transfer_intent
            facts["transfer_reason"] = transfer_reason

        # 2. Verification / Identity handling
        if current_stage == ConversationStage.GREETING_VERIFICATION:
            if re.search(r'\b(not him|wrong number|wrong person|no rajesh|not rajesh|wrong call|nobody here)\b', t):
                facts["verification_status"] = VerificationStatus.WRONG_PERSON
            elif re.search(r'\b(dont call|do not call|remove my number|stop calling|dnd|complaint)\b', t):
                facts["verification_status"] = VerificationStatus.DND
            elif re.search(r'\b(not interested|not now|busy|call later|dont want)\b', t):
                if re.search(r'\b(busy|call later|call back|driving|in a meeting|at work)\b', t):
                    facts["verification_status"] = VerificationStatus.VERIFIED
                    facts["availability_status"] = AvailabilityStatus.BUSY
                else:
                    facts["verification_status"] = VerificationStatus.DECLINED
            elif re.search(r'\b(yes|speaking|this is|yeah|haan|bol raha hu|bol rahi hu|i am|myself|sure|here)\b', t):
                facts["verification_status"] = VerificationStatus.VERIFIED
                facts["availability_status"] = AvailabilityStatus.AVAILABLE

        # 3. Callback Preference extraction (if busy)
        if re.search(r'\b(call (?:me )?(?:back |later )?(?:at |after |tomorrow |evening|morning|afternoon|in \d+|\d+ (?:pm|am|o\'?clock)))\b', t) or \
           re.search(r'\b(tomorrow|evening|after \d+|at \d+|5 pm|6 pm|next week)\b', t):
            cb_match = re.search(r'(?:call (?:me )?(?:back |later )?)?(at \d+(?:\s*[ap]m)?|\d+\s*[ap]m|tomorrow(?:\s*(?:morning|evening|afternoon))?|in the evening|after \d+ hours?)', t)
            facts["callback_preference"] = cb_match.group(0).strip() if cb_match else "Tomorrow"
            facts["availability_status"] = AvailabilityStatus.BUSY

        # 4. Offer Acceptance / Decline
        if current_stage == ConversationStage.OFFER_PRESENTATION:
            if re.search(r'\b(not interested|dont want|no thanks|nahi chahiye|no)\b', t):
                facts["offer_accepted"] = False
            elif re.search(r'\b(yes|sure|okay|ok|yeah|haan|tell me|proceed|go ahead|interested|please)\b', t):
                facts["offer_accepted"] = True

        # 5. Amount Cap Acceptance / Decline (when asked about ₹75 Lakh alternative)
        if current_stage == ConversationStage.AMOUNT_CAP_CONFIRMATION:
            if re.search(r'\b(yes|okay|ok|sure|fine|proceed with 75|75 is fine|agree|ready|let\'s proceed with 75)\b', t):
                facts["amount_cap_accepted"] = True
            elif re.search(r'\b(no|cannot|need more|reject|not enough|only want|cancel)\b', t):
                facts["amount_cap_accepted"] = False
            return facts

        # 6. Property Type extraction
        prop_type = normalize_property_type(utterance)
        if prop_type != PropertyType.UNKNOWN:
            facts["property_type"] = prop_type

        # 7. Ownership Type extraction
        ownership = normalize_ownership_type(utterance)
        if ownership != OwnershipType.UNKNOWN:
            facts["ownership_type"] = ownership

        # 8. Document Status extraction
        is_doc_turn = (current_checklist_item == ChecklistItemKey.ORIGINAL_DOCUMENTS)
        doc_status = normalize_document_status(utterance, is_document_turn=is_doc_turn)
        if doc_status != DocumentStatus.UNKNOWN:
            facts["document_status"] = doc_status

        # 9. Occupation & Income Mode extraction
        occ = normalize_occupation(utterance)
        if occ != OccupationType.UNKNOWN:
            facts["occupation"] = occ

        inc_mode = normalize_income_mode(utterance)
        if inc_mode != IncomeMode.UNKNOWN:
            facts["income_mode"] = inc_mode

        # 10. Loan Amount and Market Value extraction
        market_val_match = re.search(r'(?:worth|value|valued at|market value|cost|price|property is)\s*(?:roughly|about|around)?\s*([₹\d\w\s\.\,]+?)(?:and|for|but|,|$)', t)
        loan_amount_match = re.search(r'(?:need|want|looking for|require|loan of|amount of|get)\s*(?:around|about|roughly)?\s*([₹\d\w\s\.\,]+?)(?:and|for|worth|,|$)', t)

        if market_val_match:
            mv = parse_indian_currency(market_val_match.group(1))
            if mv and mv >= 100000:
                facts["market_value"] = mv

        if loan_amount_match:
            amt = parse_indian_currency(loan_amount_match.group(1))
            if amt and amt >= 10000:
                facts["raw_requested_amount"] = amt
                if amt <= 75_00_000:
                    facts["requested_amount"] = amt

        # Contextual currency extraction if neither marker was explicit:
        if "market_value" not in facts and "raw_requested_amount" not in facts:
            parsed_curr = parse_indian_currency(utterance)
            if parsed_curr is not None:
                if current_checklist_item == ChecklistItemKey.MARKET_VALUE:
                    facts["market_value"] = parsed_curr
                elif current_checklist_item == ChecklistItemKey.REQUESTED_AMOUNT:
                    facts["raw_requested_amount"] = parsed_curr
                    if parsed_curr <= 75_00_000:
                        facts["requested_amount"] = parsed_curr
                elif parsed_curr > 75_00_000:
                    facts["market_value"] = parsed_curr
                else:
                    facts["raw_requested_amount"] = parsed_curr
                    if parsed_curr <= 75_00_000:
                        facts["requested_amount"] = parsed_curr

        # 11. Tenure Extraction
        is_tenure_turn = (current_checklist_item == ChecklistItemKey.TENURE)
        tenure = parse_tenure_years(utterance, is_tenure_turn=is_tenure_turn)
        if tenure is not None:
            facts["tenure_years"] = tenure

        return facts
