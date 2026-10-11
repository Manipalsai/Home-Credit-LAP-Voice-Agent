import re
from typing import Optional, Tuple
from backend.app.models.qualification import (
    PropertyType,
    OwnershipType,
    DocumentStatus,
    OccupationType,
    IncomeMode,
    TransferIntent,
)

# Number word lookup
NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90,
}


def _words_to_small_num(text: str) -> Optional[float]:
    """Helper to convert strings like 'one point two' or 'seventy five' to float/int."""
    text = text.lower().strip()
    if "point" in text:
        parts = text.split("point")
        whole = _words_to_small_num(parts[0]) or 0.0
        frac_words = parts[1].strip().split()
        frac_digits = ""
        for w in frac_words:
            if w in NUMBER_WORDS:
                frac_digits += str(NUMBER_WORDS[w])
            elif w.isdigit():
                frac_digits += w
        if frac_digits:
            return whole + float("0." + frac_digits)
        return whole

    words = text.split()
    total = 0.0
    current = 0.0
    found = False
    for word in words:
        if word in NUMBER_WORDS:
            current += NUMBER_WORDS[word]
            found = True
        elif word.isdigit():
            current += float(word)
            found = True
    if found:
        return total + current
    return None


def parse_indian_currency(text: str) -> Optional[int]:
    """
    Parses natural language or numerical Indian currency strings into integer Rupees.
    Supports formats:
      - '₹75,00,000', '7500000', '75 lakhs', '60 lakh', '50 lac', '50 lacs'
      - '1.5 crore', 'one crore twenty lakh', 'roughly one crore twenty', '1.2 cr'
      - 'twenty five thousand', '50k'
    """
    if not text:
        return None

    cleaned = text.lower().replace(",", "").replace("₹", "").replace("rs.", "").replace("inr", "").strip()

    # Case 1: Pure number (e.g. '7500000' or '50000')
    pure_num_match = re.search(r'\b\d{5,12}\b', cleaned)
    if pure_num_match and not any(term in cleaned for term in ["lakh", "lac", "crore", "cr", "k", "thousand"]):
        return int(pure_num_match.group(0))

    # Case 2: Crores + Lakhs compound (e.g. '1 crore 20 lakh', 'one crore twenty', '1 cr 20 l')
    compound_cr_lakh = re.search(
        r'(\d+(?:\.\d+)?|[a-z\s]+?)\s*(?:crore|crores|cr)\s*(?:and\s*)?(\d+(?:\.\d+)?|[a-z\s]+?)\s*(?:lakh|lakhs|lac|lacs)?\b',
        cleaned
    )
    if compound_cr_lakh:
        cr_part_str = compound_cr_lakh.group(1).strip()
        lakh_part_str = compound_cr_lakh.group(2).strip()

        try:
            cr_val = float(cr_part_str)
        except ValueError:
            cr_val = _words_to_small_num(cr_part_str) or 0.0

        try:
            lakh_val = float(lakh_part_str)
        except ValueError:
            lakh_val = _words_to_small_num(lakh_part_str) or 0.0

        if cr_val > 0 or lakh_val > 0:
            return int((cr_val * 10000000) + (lakh_val * 100000))

    # Case 3: Simple Crores (e.g. '1.5 crore', 'one point two crore', '2 cr')
    cr_match = re.search(r'(\d+(?:\.\d+)?|[a-z\s]+?)\s*(?:crore|crores|cr)\b', cleaned)
    if cr_match:
        val_str = cr_match.group(1).strip()
        try:
            cr_val = float(val_str)
        except ValueError:
            cr_val = _words_to_small_num(val_str)
        if cr_val is not None:
            return int(cr_val * 10000000)

    # Case 4: Lakhs (e.g. '60 lakh', 'seventy five lakhs', '50 lac', '75 lacs')
    lakh_match = re.search(r'(\d+(?:\.\d+)?|[a-z\s]+?)\s*(?:lakh|lakhs|lac|lacs|l)\b', cleaned)
    if lakh_match:
        val_str = lakh_match.group(1).strip()
        try:
            lakh_val = float(val_str)
        except ValueError:
            lakh_val = _words_to_small_num(val_str)
        if lakh_val is not None:
            return int(lakh_val * 100000)

    # Case 5: Thousands / k (e.g. '500k', 'fifty thousand')
    k_match = re.search(r'(\d+(?:\.\d+)?|[a-z\s]+?)\s*(?:thousand|k)\b', cleaned)
    if k_match:
        val_str = k_match.group(1).strip()
        try:
            k_val = float(val_str)
        except ValueError:
            k_val = _words_to_small_num(val_str)
        if k_val is not None:
            return int(k_val * 1000)

    # Case 6: Word numbers alone without explicit suffix if in context of lakhs
    num_val = _words_to_small_num(cleaned)
    if num_val is not None:
        if num_val <= 100:
            return int(num_val * 100000)
        return int(num_val)

    return None


def normalize_property_type(text: str) -> PropertyType:
    """Normalizes property type from customer speech."""
    t = text.lower().strip()
    if re.search(r'\b(agri|agriculture|agricultural|farm|farmland|khet|krishi|village land)\b', t):
        return PropertyType.AGRICULTURAL
    if re.search(r'\b(industrial|factory|plant|warehouse|shed|manufacturing|workshop)\b', t):
        return PropertyType.INDUSTRIAL
    if re.search(r'\b(commercial|shop|office|showroom|retail|complex|business property)\b', t):
        return PropertyType.COMMERCIAL
    if re.search(r'\b(residential|house|flat|apartment|villa|builder floor|home|makaan|independent floor|bungalow)\b', t):
        return PropertyType.RESIDENTIAL
    return PropertyType.UNKNOWN


def normalize_ownership_type(text: str) -> OwnershipType:
    """Normalizes ownership type (Sole or Joint)."""
    t = text.lower().strip()
    if re.search(r'\b(joint|jointly|co-owned|co owned|partner|brother|sister|father|mother|wife|husband|spouse|son|daughter)\b', t):
        return OwnershipType.JOINT
    if re.search(r'\b(my (?:residential |commercial |industrial )?(?:house|home|flat|apartment|bungalow|property)|sole|solely|single|only mine|my own|individual|myself only|sole owner|mine only|it\'s my house|my house)\b', t):
        return OwnershipType.SOLE
    return OwnershipType.UNKNOWN


def normalize_document_status(text: str, is_document_turn: bool = False) -> DocumentStatus:
    """
    Normalizes whether original title deeds are available for verification.
    Avoids false positives from generic words like 'yes' unless in direct document turn.
    """
    t = text.lower().strip()
    if re.search(r'\b(not available|unavailable|lost|missing|don\'t have|no original|only photocopy|disputed|court case|cannot provide)\b', t):
        return DocumentStatus.UNAVAILABLE
    if re.search(r'\b(original\s*(?:papers|documents|deeds|files)?\s*(?:are\s*)?available|at home|in locker|bank locker|have original|have papers|kept at home|originals are with me|originals are available|in my custody|in my possession)\b', t):
        return DocumentStatus.AVAILABLE
    if is_document_turn and re.search(r'\b(yes|available|sure|i have them|yes available|yes they are)\b', t):
        return DocumentStatus.AVAILABLE
    if re.search(r'\b(not sure|maybe|have to check|uncertain|will check)\b', t):
        return DocumentStatus.UNCERTAIN
    return DocumentStatus.UNKNOWN


def normalize_occupation(text: str) -> OccupationType:
    """Normalizes occupation into Salaried or Self-Employed."""
    t = text.lower().strip()
    if re.search(r'\b(salaried|job|employee|mnc|private limited|working|service|employed|govt|government|it firm)\b', t):
        return OccupationType.SALARIED
    if re.search(r'\b(self employed|self-employed|business|businessman|shopkeeper|business owner|shop owner|trading|firm|proprietorship|freelance|contractor|consultant)\b', t):
        return OccupationType.SELF_EMPLOYED
    return OccupationType.UNKNOWN


def normalize_income_mode(text: str) -> IncomeMode:
    """Normalizes mode of income into Bank, Cash, or Mixed."""
    t = text.lower().strip()
    has_cash = bool(re.search(r'\b(cash|in hand|naqad|rokh)\b', t))
    has_bank = bool(re.search(r'\b(bank|account|cheque|direct deposit|neft|rtgs|transfer|online|salary account|direct credit|receipts)\b', t))

    if has_cash and has_bank:
        return IncomeMode.MIXED
    if has_cash:
        return IncomeMode.CASH
    if has_bank:
        return IncomeMode.BANK
    return IncomeMode.UNKNOWN


def parse_tenure_years(text: str, is_tenure_turn: bool = False) -> Optional[int]:
    """
    Parses requested loan repayment tenure in years.
    Handles 'ten years', '10 years', '12 yrs', '120 months', 'Ten years, actually make that twelve'.
    Avoids mistaking currency amounts ('thirty lakhs', 'two crore') for tenure years.
    """
    if not text:
        return None
    t = text.lower().strip()

    # Look for corrections like "Ten years, actually make that twelve" or "make it 12"
    correction_match = re.search(
        r'(?:actually|instead)\s*(?:make that|make it|change to|change it to)?\s*(\d+|[a-z]+)',
        t
    ) or re.search(
        r'(?:make that|make it|change to|change it to)\s*(\d+|[a-z]+)',
        t
    )
    if correction_match:
        val_str = correction_match.group(1).strip()
        if val_str.isdigit():
            return int(val_str)
        if val_str in NUMBER_WORDS:
            return NUMBER_WORDS[val_str]

    # Check for months format: e.g. "60 months", "120 months"
    month_match = re.search(r'(\d+)\s*(?:months|month)\b', t)
    if month_match:
        months = int(month_match.group(1))
        return max(1, round(months / 12))

    # Standard years format: e.g. "10 years", "12 yrs", "5 saal"
    year_match = re.search(r'(\d+)\s*(?:years|year|yrs|yr|saal)\b', t)
    if year_match:
        return int(year_match.group(1))

    # Word years: e.g. "ten years", "fifteen years", "three years"
    word_year_match = re.search(r'([a-z]+)\s*(?:years|year|yrs|yr|saal)\b', t)
    if word_year_match:
        word = word_year_match.group(1).strip()
        if word in NUMBER_WORDS:
            return NUMBER_WORDS[word]

    # If currency words are in the utterance, do not parse currency numbers as tenure!
    if any(c in t for c in ["lakh", "lac", "crore", "cr", "thousand", "k", "rs", "₹", "inr"]):
        return None

    # If this is specifically a tenure turn (or pure number answering tenure):
    if is_tenure_turn or re.search(r'\b(tenure|repayment|period|years?)\b', t):
        plain_num_match = re.search(r'\b(\d{1,2})\b', t)
        if plain_num_match:
            val = int(plain_num_match.group(1))
            if 1 <= val <= 30:
                return val

        for w in t.split():
            if w in NUMBER_WORDS:
                val = NUMBER_WORDS[w]
                if 1 <= val <= 30:
                    return val

    # Plain standalone word or number like "three", "ten", "twelve", "10" if length of utterance is short (< 4 words)
    words = t.split()
    if len(words) <= 3:
        if words[0].isdigit():
            val = int(words[0])
            if 1 <= val <= 30:
                return val
        if words[0] in NUMBER_WORDS:
            val = NUMBER_WORDS[words[0]]
            if 1 <= val <= 30:
                return val

    return None


def detect_transfer_intent(text: str) -> Tuple[TransferIntent, Optional[str]]:
    """
    Detects if the customer wants to transfer or refinance an existing property/home loan,
    or reduce EMI on an existing property loan.
    Ignores unrelated personal loans, auto loans, or credit cards.
    """
    t = text.lower().strip()

    # Unrelated loans explicitly mentioned without property link
    has_unrelated_only = bool(re.search(r'\b(personal loan|car loan|auto loan|bike loan|credit card loan)\b', t))
    has_property_or_home_loan = bool(re.search(r'\b(property loan|home loan|housing loan|loan against property|lap|mortgage)\b', t))

    if has_unrelated_only and not has_property_or_home_loan:
        return TransferIntent.NONE, None

    # Check EMI reduction on property loan
    if re.search(r'\b(reduce emi|lower emi|decrease emi|cut emi|less emi)\b', t) and (has_property_or_home_loan or "existing loan" in t or "current loan" in t):
        return TransferIntent.EMI_REDUCTION_REQUESTED, "Customer requested EMI reduction on existing property loan"

    # Check transfer / refinance / balance transfer on property loan
    if re.search(r'\b(transfer|balance transfer|refinance|shift|takeover|switch)\b', t) and (has_property_or_home_loan or "existing loan" in t or "current loan" in t or "already have a loan on this property" in t or "running loan on this property" in t):
        return TransferIntent.TRANSFER_REQUESTED, "Customer requested balance transfer/refinance of existing property loan"

    # Direct phrases like "already have a loan against this property"
    if "loan against" in t and ("already" in t or "existing" in t or "running" in t):
        return TransferIntent.TRANSFER_REQUESTED, "Customer reported existing loan secured on property"

    return TransferIntent.NONE, None
