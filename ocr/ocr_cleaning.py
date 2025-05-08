import re
from nltk.corpus import stopwords
import spacy
from wordfreq import zipf_frequency

# -------------------- GLOBAL VARIABLES ---------------------
# Load spaCy’s small English model
nlp = spacy.load("en_core_web_sm", disable=["parser","tagger","lemmatizer","attribute_ruler"])

# Pre-compile regex patterns
_CLEAN_NON_ALNUM, _CLEAN_WORDS_WITH_DIGITS, _CLEAN_6_DIGIT_NUMS = (
    re.compile(r"[^A-Za-z0-9\s]+"),
    re.compile(r"[A-Za-z]+\d+[A-Za-z]*"),
    re.compile(r"[0-9]{6,}"),  # 6 or more digits
)

STOP_WORDS = set(stopwords.words("english")) | {"like"}
KNOWN_NAMES = {"olneyanum", "flora", "planta", "plant", "james", "herbarium", \
               "howells", "oregonenses", "texan"}


# ------------------------- CLEANING -------------------------
def is_common_english(token: str, threshold: float = 3.5) -> bool:
    """
    zipf_frequency returns a log-scaled frequency (1-7);
    3.0 is roughly words occurring around once per million words.
    """
    return zipf_frequency(token.lower(), "en") >= threshold


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
        text = token.text.strip()

        if len(text) >= min_length:
            if token.ent_type_ or text.lower() in KNOWN_NAMES:
                kept.append(text)
            elif text not in STOP_WORDS and is_common_english(text):
                kept.append(text)

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
        phrase = _CLEAN_NON_ALNUM.sub("", phrase)
        phrase = _CLEAN_WORDS_WITH_DIGITS.sub("", phrase)
        phrase = _CLEAN_6_DIGIT_NUMS.sub("", phrase)
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

def main():
    pass

if __name__ == "__main__":
    main()