import re
# import nltk
# nltk.download('stopwords')
from nltk.corpus import stopwords
import spacy, spacy.tokens
from wordfreq import zipf_frequency

# -------------------- GLOBAL VARIABLES ---------------------
# Load spaCy’s small English model
nlp = spacy.load("en_core_web_sm", disable=["parser","tagger","lemmatizer","attribute_ruler"])

# Pre-compile regex patterns
_REPLACE_SANDWICHED_NON_ALNUMS, _CLEAN_NON_ALNUMS, \
    _CLEAN_WORDS_WITH_DIGITS, _CLEAN_5_DIGIT_NUMS = (
    re.compile(r"(?<=\w)[^\w\s]+(?=\w)"),
    re.compile(r"[^\w\s]"),
    re.compile(r"[A-Za-z]+\d+[A-Za-z]*"),
    re.compile(r"[0-9]{5,}"),  # 5 or more digits
)

STOP_WORDS = set(stopwords.words("english")) | {"like"}
KNOWN_NAMES = {"olneyanum", "flora", "planta", "plant", "james", "herbarium", \
               "howells", "oregonenses", "texan"}
# COLL_YEAR = re.compile("^(1[6-9[]|20)[0-9]{2}$")


# ------------------------- CLEANING -------------------------
def is_common_english(token: str, threshold: float = 3.5) -> bool:
    """
    Check whether a word is "common." A log-scaled frequency of 3.5 is roughly
    words occurring around once per million words.

    Parameters
    ----------
    token : str
        A token to check for commonality
    threshold : float
        The threshold for how common each token should be

    Returns
    -------
    bool
        True if a word's frequency exceeds the threshold. False otherwise.
    """
    return zipf_frequency(token.lower(), "en") >= threshold


def should_keep(token: spacy.tokens.Token, min_length: int) -> bool:
    """
    Check if a token is "important" and should be kept. Criteria:
        - Has at least two numbers
        - String length greater than min_length
        - Contains named entities
        - Not a stopword
        - Is "common enough" (see is_common_english)
    
    Parameters
    ----------
    token : spacy.tokens.Token
        A token to check for importance
    threshold : float

    Returns
    -------
    bool
        True if the token passes any of the above criteria. False otherwise.
    """
    text = token.text.strip()
    
    if text.isnumeric() and len(text) >= 2:
        return True
    
    if len(text) < min_length:
        return False

    # Named-entity or explicit list of names
    if token.ent_type_ or text.lower() in KNOWN_NAMES:
        return True

    # Otherwise: not a stopword and common in English
    return text not in STOP_WORDS and is_common_english(text)


def normalize_doc(doc: spacy.tokens.Doc, min_length: int = 4) -> str:
    """
    Clean a phrase by removing unwanted words/characters:
        1) Strip out non-alphanumeric chars
        2) Remove words with digits
        3) Remove long digit strings
        4) Filter short/non-name/uncommon/stop words
    """
    kept = []
    for token in doc:
        if should_keep(token, min_length):
            kept.append(token.text.strip())

    return " ".join(kept)


def extract_phrases_from_text(
    text: str,
    exclude_phrases: set[str] = {"copyright", "reserved"},
) -> list[str]:
    """
    1) Check for named entities (original case)
    2) If not a name, reject gibberish
    3) Normalize and lowercase
    4) Exclude duplicates & unwanted
    """
    raw_phrases = []
    for line in text.splitlines():
        phrase = line.strip()
        if not phrase:
            continue
        # regex cleaning
        phrase = _REPLACE_SANDWICHED_NON_ALNUMS.sub(" ", phrase)
        phrase = _CLEAN_NON_ALNUMS.sub("", phrase)
        phrase = _CLEAN_WORDS_WITH_DIGITS.sub("", phrase)
        phrase = _CLEAN_5_DIGIT_NUMS.sub("", phrase)
        raw_phrases.append(phrase)

    cleaned_norms = []
    seen = set()
    for doc in nlp.pipe(raw_phrases):
        norm = normalize_doc(doc).lower()
        if not norm or norm in seen:
            continue
        if any(exc in norm for exc in exclude_phrases):
            continue
        seen.add(norm)
        cleaned_norms.append(norm)

    return cleaned_norms
