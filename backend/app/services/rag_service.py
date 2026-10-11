import re
from typing import Optional, Tuple


class RAGKnowledgeService:
    """
    Supplies grounded information for borrower product inquiries without hallucinating.
    Adheres strictly to business rules:
      - Never fabricate interest rates, branch locations, or unconfirmed fees.
      - Always defer custom rates and fees to the Senior Loan Expert.
    """

    KNOWLEDGE_BASE = {
        "interest_rate": (
            "Our Loan Against Property interest rates are customized based on property valuation and borrower profile. "
            "Our Senior Loan Expert will share your exact rate and EMI schedule after this quick check."
        ),
        "processing_fee": (
            "Processing fees are nominal and depend on the sanction terms. "
            "The exact details will be provided transparently by our senior loan advisor."
        ),
        "disbursement_time": (
            "Preliminary sanction is evaluated immediately, and disbursement typically takes 3 to 5 business days "
            "following complete document verification."
        ),
        "required_documents": (
            "The primary documents required are original title deeds, KYC documents (Aadhaar & PAN), and the last 6 months' bank statements."
        ),
        "foreclosure": (
            "Prepayment and foreclosure policies follow standard RBI guidelines, which our Senior Loan Expert will detail during your consultation."
        ),
        "company_info": (
            "Home Credit India is a leading NBFC committed to transparent, customer-centric credit solutions."
        ),
    }

    @classmethod
    def get_context_summary(cls) -> str:
        """Returns the context string to inject into {{additional_context_from_rag}}."""
        return (
            "- Product: Home Credit Loan Against Property (LAP).\n"
            "- Maximum Cap: ₹75,00,000 (75 Lakhs).\n"
            "- Permitted Tenures: 3 to 15 years.\n"
            "- Eligible Properties: Residential, Commercial, Industrial (Agricultural strictly not eligible).\n"
            "- Income Requirement: Bank credit required; cash income not eligible.\n"
            "- Documents: Original title deeds must be available for verification.\n"
            "- Rates & Charges: Defer exact interest rate and processing fees to the Senior Loan Expert."
        )

    @classmethod
    def answer_query(cls, utterance: str) -> Optional[str]:
        """Detects if customer asked a question and returns a grounded 1-sentence answer."""
        t = utterance.lower()

        if re.search(r'\b(interest rate|rate of interest|roi|interest kitna|biyaj|interest percentage)\b', t):
            return cls.KNOWLEDGE_BASE["interest_rate"]

        if re.search(r'\b(processing fee|charges|hidden fee|login fee)\b', t):
            return cls.KNOWLEDGE_BASE["processing_fee"]

        if re.search(r'\b(time|how long|disburs|paisa kab milega|sanction time)\b', t):
            return cls.KNOWLEDGE_BASE["disbursement_time"]

        if re.search(r'\b(what documents|documents needed|kagaz|papers needed)\b', t):
            return cls.KNOWLEDGE_BASE["required_documents"]

        if re.search(r'\b(foreclose|prepayment|part payment|close early)\b', t):
            return cls.KNOWLEDGE_BASE["foreclosure"]

        if re.search(r'\b(who are you|about home credit|company details)\b', t):
            return cls.KNOWLEDGE_BASE["company_info"]

        return None
