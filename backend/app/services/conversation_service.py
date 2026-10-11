from typing import Dict, Any, Optional, Tuple
import os
from datetime import datetime
from jinja2 import Template

from backend.app.models.qualification import (
    QualificationState,
    ConversationStage,
    CallOutcome,
    ChecklistItemKey,
    ItemState,
    VerificationStatus,
    AvailabilityStatus,
    TransferIntent,
    DisqualificationReason,
    PropertyType,
    OwnershipType,
    DocumentStatus,
    OccupationType,
    IncomeMode,
)
from backend.app.models.conversation import Message, MessageSender, ConversationSession
from backend.app.qualification.engine import QualificationEngine
from backend.app.qualification.extractor import ConversationalExtractor
from backend.app.services.rag_service import RAGKnowledgeService
from backend.app.config import settings


class ConversationService:
    """
    Orchestrates the multi-turn conversational voice flow, state transitions,
    and response generation adhering to all business rules.
    """

    def __init__(self):
        self._sessions: Dict[str, QualificationState] = {}
        self._session_histories: Dict[str, ConversationSession] = {}
        self._system_prompt_template = self._load_system_prompt_template()

    def _load_system_prompt_template(self) -> str:
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "prompts", "home_credit_lap_system_prompt.txt")
        norm_path = os.path.abspath(prompt_path)
        if os.path.exists(norm_path):
            with open(norm_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def get_or_create_session(self, session_id: str, customer_name: str = "Rajesh Sharma") -> QualificationState:
        if session_id not in self._sessions:
            state = QualificationState(
                session_id=session_id,
                customer_name=customer_name,
                company_name=settings.COMPANY_NAME,
                agent_name=settings.AGENT_NAME,
                agent_gender=settings.AGENT_GENDER,
                language=settings.DEFAULT_LANGUAGE,
                stage=ConversationStage.GREETING_VERIFICATION,
                outcome=CallOutcome.IN_PROGRESS,
            )
            # Initialize checklist items 1-7
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

            self._sessions[session_id] = state
            self._session_histories[session_id] = ConversationSession(
                session_id=session_id,
                customer_name=customer_name,
            )
        return self._sessions[session_id]

    def reset_session(self, session_id: str, customer_name: str = "Rajesh Sharma") -> QualificationState:
        if session_id in self._sessions:
            del self._sessions[session_id]
        if session_id in self._session_histories:
            del self._session_histories[session_id]
        return self.get_or_create_session(session_id, customer_name)

    def process_turn(self, session_id: str, customer_utterance: str) -> Tuple[str, QualificationState, Dict[str, Any]]:
        state = self.get_or_create_session(session_id)
        history = self._session_histories[session_id]

        # Record customer message
        history.messages.append(
            Message(
                id=f"msg_{len(history.messages) + 1}",
                sender=MessageSender.USER,
                text=customer_utterance,
            )
        )
        state.last_customer_utterance = customer_utterance

        # If call is already terminal, do not ask further questions
        if state.is_terminal:
            farewell = "Thank you. Our call has concluded. Have a good day."
            return farewell, state, {}

        # 1. Check for interruptions / product questions first
        rag_answer = RAGKnowledgeService.answer_query(customer_utterance)

        # 2. Extract structured facts from customer utterance
        current_item = QualificationEngine.get_next_checklist_item(state)
        extracted_facts = ConversationalExtractor.extract_facts(
            customer_utterance,
            state.stage,
            current_checklist_item=current_item,
        )

        # 3. Apply extracted facts to state
        self._apply_facts_to_state(state, extracted_facts)

        # 4. Run deterministic qualification engine
        QualificationEngine.evaluate_state(state)

        # 5. Determine the next agent response
        agent_response, next_question = self._generate_agent_response(state, rag_answer)

        # Record agent message
        history.messages.append(
            Message(
                id=f"msg_{len(history.messages) + 1}",
                sender=MessageSender.AGENT,
                text=agent_response,
                metadata={"stage": state.stage.value, "outcome": state.outcome.value, "next_question": next_question},
            )
        )

        state.current_prompt = next_question
        return agent_response, state, extracted_facts

    def _apply_facts_to_state(self, state: QualificationState, facts: Dict[str, Any]) -> None:
        if "transfer_intent" in facts:
            state.transfer_intent = facts["transfer_intent"]
            state.transfer_reason = facts.get("transfer_reason")

        if "verification_status" in facts:
            state.verification_status = facts["verification_status"]

        if "availability_status" in facts:
            state.availability_status = facts["availability_status"]

        if "callback_preference" in facts:
            state.callback_preference = facts["callback_preference"]

        if "offer_accepted" in facts:
            state.offer_accepted = facts["offer_accepted"]

        if "amount_cap_accepted" in facts:
            state.amount_cap_accepted = facts["amount_cap_accepted"]

        if "property_type" in facts:
            state.property_type = facts["property_type"]

        if "ownership_type" in facts:
            state.ownership_type = facts["ownership_type"]

        if "document_status" in facts:
            state.document_status = facts["document_status"]

        if "raw_requested_amount" in facts:
            state.raw_requested_amount = facts["raw_requested_amount"]
        if "requested_amount" in facts:
            state.requested_amount = facts["requested_amount"]

        if "occupation" in facts:
            state.occupation = facts["occupation"]

        if "income_mode" in facts:
            state.income_mode = facts["income_mode"]

        if "market_value" in facts:
            state.market_value = facts["market_value"]

        if "tenure_years" in facts:
            state.tenure_years = facts["tenure_years"]

    def _generate_agent_response(self, state: QualificationState, rag_answer: Optional[str]) -> Tuple[str, Optional[str]]:
        """Generates natural, policy-compliant response based on state."""
        # 1. Terminal Outcomes
        if state.outcome == CallOutcome.ROUTED_TRANSFER_SPECIALIST:
            return (
                "I understand you are looking to transfer your existing property loan for better terms. "
                "Our dedicated Loan Transfer team handles this directly. A specialist will call you shortly to assist with your transfer. "
                "Thank you for your time!",
                None,
            )

        if state.outcome == CallOutcome.WRONG_PERSON:
            return "I apologize for the disturbance. Have a great day.", None

        if state.outcome == CallOutcome.CUSTOMER_DECLINED:
            return "I completely understand and respect your decision. Thank you for your time, and have a good day.", None

        if state.outcome == CallOutcome.DND_REQUESTED:
            return "We have noted your preference and will update our records not to contact you. Thank you and have a good day.", None

        if state.outcome == CallOutcome.BUSY_CALLBACK_SCHEDULED:
            time_pref = state.callback_preference or "a later time"
            return (
                f"I completely understand you are busy right now. We will call you back at {time_pref}. "
                "Thank you, and have a wonderful day!",
                None,
            )

        if state.outcome == CallOutcome.DISQUALIFIED:
            if state.disqualification_reason == DisqualificationReason.AGRICULTURAL_PROPERTY:
                return (
                    "Thank you for sharing that. Unfortunately, under this specific offer, agricultural properties "
                    f"are not eligible at this time. Thank you for your time with {state.company_name}.",
                    None,
                )
            if state.disqualification_reason == DisqualificationReason.ORIGINAL_DOCS_UNAVAILABLE:
                return (
                    "Under our policy, original property documents are mandatory for verification. "
                    "Since they are not currently available, we cannot proceed with this offer today. Thank you for your time.",
                    None,
                )
            if state.disqualification_reason == DisqualificationReason.CASH_INCOME:
                return (
                    "To qualify for this offer, income must be routed through bank account deposits. "
                    "Since your income is cash-based, we are unable to process this application at this time. Thank you for your time.",
                    None,
                )
            if state.disqualification_reason == DisqualificationReason.TENURE_OUT_OF_RANGE:
                return (
                    f"Our repayment tenure for this program is between 3 and 15 years. Since your requested tenure of {state.tenure_years} years "
                    "falls outside this range, we are unable to proceed with this offer. Thank you for your time.",
                    None,
                )

        if state.outcome == CallOutcome.AMOUNT_CAP_REJECTED:
            return (
                "I understand your requirement is higher than our offer limit. Since this specific program is capped at ₹75 Lakhs, "
                "we cannot proceed today, but we will notify you if higher limits become available. Thank you for your time.",
                None,
            )

        if state.outcome == CallOutcome.QUALIFIED_HANDOFF:
            return (
                f"Congratulations, {state.customer_name}! Based on your details, your profile meets all criteria for our Loan Against Property offer. "
                f"A Senior Loan Expert from {state.company_name} will contact you shortly to review your documentation and share your customized interest rate and terms. "
                "Thank you for your time, and have a wonderful day!",
                None,
            )

        # 2. Stage-based transitions
        if state.stage == ConversationStage.GREETING_VERIFICATION:
            if state.verification_status == VerificationStatus.UNVERIFIED:
                return f"Hello, am I speaking with {state.customer_name}?", "Verification"
            else:
                # Transition to offer presentation
                state.stage = ConversationStage.OFFER_PRESENTATION
                return (
                    f"Thank you, {state.customer_name}. As a valued customer of {state.company_name}, you may be eligible for a special Loan Against Property offer of up to ₹75 Lakhs. "
                    "May I ask a few quick questions to assess your eligibility?",
                    "Offer Consent",
                )

        if state.stage == ConversationStage.OFFER_PRESENTATION:
            if state.offer_accepted is True:
                state.stage = ConversationStage.ELIGIBILITY_CHECKLIST
            else:
                return (
                    f"Would you like to explore this pre-approved Loan Against Property offer of up to ₹75 Lakhs?",
                    "Offer Consent",
                )

        if state.stage == ConversationStage.AMOUNT_CAP_CONFIRMATION:
            return (
                "Under this pre-approved program, the maximum loan amount we can offer is ₹75 Lakhs. "
                "Would you like to proceed with ₹75 Lakhs?",
                "Amount Cap Consent",
            )

        # 3. Eligibility Checklist Questions
        next_item = QualificationEngine.get_next_checklist_item(state)
        question_text = self._get_question_for_item(next_item, state)

        # If user asked a question (e.g. interest rate), answer it first then append next checklist item
        if rag_answer:
            full_response = f"{rag_answer} {question_text}"
        else:
            full_response = question_text

        return full_response, str(next_item.value if next_item else None)

    def _get_question_for_item(self, item_key: Optional[ChecklistItemKey], state: QualificationState) -> str:
        if item_key == ChecklistItemKey.PROPERTY_TYPE:
            return "Could you tell me what type of property this is—residential, commercial, or industrial?"

        if item_key == ChecklistItemKey.OWNERSHIP_STATUS:
            return "Is the property solely owned by you, or is it jointly owned with family?"

        if item_key == ChecklistItemKey.ORIGINAL_DOCUMENTS:
            return "Are the original property title documents available for verification?"

        if item_key == ChecklistItemKey.REQUESTED_AMOUNT:
            return "What loan amount are you looking for?"

        if item_key == ChecklistItemKey.OCCUPATION_AND_INCOME_MODE:
            item = state.get_checklist_item(ChecklistItemKey.OCCUPATION_AND_INCOME_MODE)
            has_occ = state.occupation in [OccupationType.SALARIED, OccupationType.SELF_EMPLOYED]
            has_bank = state.income_mode in [IncomeMode.BANK, IncomeMode.CASH, IncomeMode.MIXED]
            if has_occ and not has_bank:
                return "Understood. And is your income received directly into your bank account, or is it cash?"
            if not has_occ and has_bank:
                return "Got it. And are you salaried or self-employed?"
            return "What is your current occupation, and is your income received through a bank account?"

        if item_key == ChecklistItemKey.MARKET_VALUE:
            return "What is your estimated current market value of the property?"

        if item_key == ChecklistItemKey.TENURE:
            return "What repayment tenure are you looking for, between 3 and 15 years?"

        return "Could you provide any additional details?"

    def get_initial_greeting(self, session_id: str, customer_name: str = "Rajesh Sharma") -> str:
        state = self.get_or_create_session(session_id, customer_name)
        return f"Hello, am I speaking with {state.customer_name}?"

    def get_history(self, session_id: str) -> Optional[ConversationSession]:
        return self._session_histories.get(session_id)

    def render_system_prompt(self, session_id: str, current_utterance: str = "") -> str:
        """Renders the complete System Prompt with all 11 required variables."""
        state = self.get_or_create_session(session_id)
        history = self._session_histories.get(session_id)
        conv_history_str = ""
        if history:
            for m in history.messages:
                conv_history_str += f"{m.sender.value.capitalize()}: {m.text}\n"

        now = datetime.now()
        context_rag = RAGKnowledgeService.get_context_summary()

        template = Template(self._system_prompt_template)
        rendered = template.render(
            company_name=state.company_name,
            customer_name=state.customer_name,
            agent_name=state.agent_name,
            agent_gender=state.agent_gender,
            current_date=now.strftime("%B %d, %Y"),
            current_day=now.strftime("%A"),
            current_time=now.strftime("%I:%M %p"),
            additional_context_from_rag=context_rag,
            language_to_speak=state.language,
            conversation_history=conv_history_str or "None yet.",
            customer_utterance=current_utterance or state.last_customer_utterance or "",
        )
        return rendered


conversation_service = ConversationService()
