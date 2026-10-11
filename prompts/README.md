# Home Credit LAP Voice Agent — System Prompt Specification

This directory contains the production-grade System Prompt for the **Home Credit Loan Against Property (LAP) AI Voice Agent**.

- **Prompt File:** [`home_credit_lap_system_prompt.txt`](./home_credit_lap_system_prompt.txt)

---

## 1. Runtime Variables Reference

The voice agent prompt leverages dynamic templating parameters populated at call initialization or on every turn.

| Variable Name | Description | Example Value |
|---|---|---|
| `{{company_name}}` | Originating lender/NBFC name | `Home Credit India` |
| `{{customer_name}}` | Registered primary customer name | `Rajesh Sharma` |
| `{{agent_name}}` | Name of the AI virtual agent | `Pooja` |
| `{{agent_gender}}` | Agent gender persona for grammatical agreement | `female` |
| `{{current_date}}` | Current calendar date | `October 11, 2026` |
| `{{current_day}}` | Day of the week | `Sunday` |
| `{{current_time}}` | Current local time | `2:30 PM IST` |
| `{{additional_context_from_rag}}` | Dynamic knowledge base snippets retrieved for borrower FAQ | Standard fees, documentation checklist, processing steps |
| `{{language_to_speak}}` | Primary conversational language | `English` or `Hindi` |
| `{{conversation_history}}` | Multi-turn transcript up to current turn | User/Agent turn history |
| `{{customer_utterance}}` | Most recent customer spoken transcript | `"It's a residential house in Noida."` |

---

## 2. Voice Platform Syntax Mapping

Different voice platforms use slightly different template bracket conventions:

| Platform | Variable Syntax Format | Mapping Note |
|---|---|---|
| **Retell AI** (Dynamic LLM / Custom LLM) | `{{variable_name}}` | Native double curly braces. Dynamic variables can be supplied in `retell_llm_dynamic_variables`. |
| **Retell AI** (Prompt-based Agent) | `{{variable_name}}` | Passed into Agent General Prompt or dynamic variables. |
| **Bolna** (Agent Prompts) | `{{variable_name}}` or `{variable_name}` | Configurable in task prompt parameters. |
| **OpenAI Responses / LangChain** | `{variable_name}` | Standard f-string or jinja formatting. |

The backend includes a converter function in `app.qualification.engine` and `app.voice.retell_adapter` that renders the prompt for whichever provider or local engine is engaged.

---

## 3. Core Business Policy Rules Enforced in Prompt

1. **Pre-Disclosure Verification:** Never pitch the LAP offer or disclose pre-approved eligibility before confirming that the speaker is `{{customer_name}}`.
2. **Busy Customer Flow:** Immediately pivot to capturing a callback timestamp without pushing the checklist.
3. **Existing Loan Balance Transfer:** If the borrower requests a balance transfer or EMI reduction for an existing property loan, immediately divert them to the specialized Loan Transfer desk.
4. **Mandatory Disqualifications (Immediate Exit):**
   - Agricultural property.
   - Original documents missing/untraceable.
   - Cash income mode.
   - Loan tenure < 3 years or > 15 years.
5. **Loan Cap Negotiation (₹75 Lakhs):**
   - Amounts up to ₹75,00,000 are approved for qualification.
   - Amounts exceeding ₹75,00,000 trigger a polite cap confirmation. If accepted, the amount is locked at ₹75 Lakhs; if refused, the call concludes respectfully.
6. **Senior Loan Expert Gate:** Handoff is only permissible when all 7 checklist fields have passed validation.
