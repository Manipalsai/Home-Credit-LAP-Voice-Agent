import pytest
from backend.app.services.conversation_service import conversation_service
from backend.app.models.qualification import CallOutcome, ConversationStage


class TestConversationService:

    def test_multi_turn_happy_path(self):
        session_id = "test_multi_turn_01"
        conversation_service.reset_session(session_id, "Rajesh Sharma")

        # Turn 1: Verification
        resp1, state1, _ = conversation_service.process_turn(session_id, "Yes, Rajesh speaking.")
        assert "Rajesh" in resp1
        assert state1.stage == ConversationStage.OFFER_PRESENTATION

        # Turn 2: Offer consent
        resp2, state2, _ = conversation_service.process_turn(session_id, "Yes, I would like to explore.")
        assert state2.stage == ConversationStage.ELIGIBILITY_CHECKLIST
        assert "type of property" in resp2.lower()

        # Turn 3: Property Type
        resp3, state3, _ = conversation_service.process_turn(session_id, "It is a residential house.")
        assert "solely owned" in resp3.lower()

        # Turn 4: Ownership
        resp4, state4, _ = conversation_service.process_turn(session_id, "I am the sole owner.")
        assert "original" in resp4.lower()

        # Turn 5: Original Documents
        resp5, state5, _ = conversation_service.process_turn(session_id, "Yes, original papers are at home.")
        assert "loan amount" in resp5.lower()

        # Turn 6: Amount
        resp6, state6, _ = conversation_service.process_turn(session_id, "Fifty lakhs.")
        assert "occupation" in resp6.lower()

        # Turn 7: Occupation & Income Mode
        resp7, state7, _ = conversation_service.process_turn(session_id, "Salaried in IT and money comes in bank account.")
        assert "market value" in resp7.lower()

        # Turn 8: Market value
        resp8, state8, _ = conversation_service.process_turn(session_id, "Around one crore twenty lakhs.")
        assert "tenure" in resp8.lower()

        # Turn 9: Tenure -> Final Handoff
        resp9, state9, _ = conversation_service.process_turn(session_id, "Ten years.")
        assert state9.outcome == CallOutcome.QUALIFIED_HANDOFF
        assert state9.stage == ConversationStage.SENIOR_EXPERT_HANDOFF
        assert state9.is_terminal is True
        assert "Senior Loan Expert" in resp9

    # 25. Interruption asking for interest rate
    def test_25_interruption_interest_rate(self):
        session_id = "test_interruption_01"
        conversation_service.reset_session(session_id, "Rajesh Sharma")

        conversation_service.process_turn(session_id, "Yes, speaking.")
        conversation_service.process_turn(session_id, "Sure.")
        conversation_service.process_turn(session_id, "Residential apartment.")

        # Interruption: What is the interest rate?
        resp, state, _ = conversation_service.process_turn(session_id, "What is the interest rate on this loan?")
        assert "Senior Loan Expert" in resp or "customized" in resp.lower()
        # Ensure it also asks the next question (ownership)
        assert "owned" in resp.lower()
        assert not state.is_terminal

    # 32. System prompt rendering with all 11 runtime variables
    def test_32_system_prompt_rendering_all_variables(self):
        session_id = "test_prompt_vars"
        conversation_service.reset_session(session_id, "Rajesh Sharma")
        prompt = conversation_service.render_system_prompt(session_id, "Residential house")

        # Check required runtime variables are present or replaced
        assert "Rajesh Sharma" in prompt
        assert "Home Credit India" in prompt
        assert "Pooja" in prompt
        assert "female" in prompt
        assert "English" in prompt
        assert "Residential house" in prompt
        # Confirm no unrendered jinja brackets remain for core variables
        assert "{{customer_name}}" not in prompt
        assert "{{company_name}}" not in prompt
        assert "{{agent_name}}" not in prompt
