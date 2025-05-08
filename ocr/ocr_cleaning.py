import re
import nltk
from nltk.corpus import stopwords
import spacy
from functools import lru_cache
from typing import Set
from wordfreq import zipf_frequency

# ---------------- LOADING VOCABULARIES ------------------
'''
NOTE: Install language models: 
    python -m spacy download en_core_web_sm 
    python -m spacy download fr_core_news_sm
'''

@lru_cache(maxsize=1)
def load_vocab(langs: tuple[str, ...] = ("en",)) -> Set[str]:
    """
    Returns a set of valid words for the given languages.
    Caches on first call.
    """
    vocab: Set[str] = set()

    if "en" in langs:
        nltk.download("words", quiet=True)
        from nltk.corpus import words
        vocab |= set(words.words())

    if "fr" in langs:
        nlp_fr = spacy.load("fr_core_news_sm", disable=["parser","ner","tagger"])
        # take every alphabetical lexeme (lower-cased) in the model’s vocab
        vocab |= {
            lex.lower_ 
            for lex in nlp_fr.vocab 
            if lex.is_alpha
        }

    return vocab

# -------------------- GLOBAL VARIABLES ---------------------
# Load spaCy’s small English model
nlp = spacy.load("en_core_web_sm", disable=["parser","tagger","lemmatizer","attribute_ruler"])
STOP_WORDS = set(stopwords.words("english")) | {"like"}
VOCAB = load_vocab(("en",))

# Pre-compile regex patterns
_CLEAN_NON_ALNUM, _CLEAN_WORDS_WITH_DIGITS, _CLEAN_6_DIGIT_NUMS, _CLEAN_EDGES = (
    re.compile(r"[^A-Za-z0-9\s]+"),
    re.compile(r"[A-Za-z]+\d+[A-Za-z]*"),
    re.compile(r"[0-9]{6,}"),  # 6 or more digits
    re.compile(r"^[\s\.',]+|[\s\.',]+$")
)
_COLLECTION_YEAR = re.compile(r"(1[7-9[]|20)[0-9]{2}")
MONTHS = [
    "january", "february", "march", "april", "may", "june", "july", \
    "august", "september", "october", "november", "december", \
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sept", "oct", "nov", "dec"
]

NAMED_ENTITY_TYPES = {"PERSON", "ORG", "GPE", "LOC"}
KNOWN_NAMES = {"olneyanum", "flora", "planta", "plant", "james", "herbarium", \
               "howells", "oregonenses", "texan"}


# ------------------------- CLEANING -------------------------
@lru_cache(maxsize=1024)
def has_named_entity(phrase: str) -> bool:
    """
    Returns True if `phrase` contains:
      - any hard-coded name in `KNOWN_NAMES`, or
      - any spaCy-detected PERSON, ORG, GPE, LOC entity.
    """
    if any(name in phrase.lower() for name in KNOWN_NAMES):
        return True
    doc = nlp(phrase)
    return any(ent.label_ in NAMED_ENTITY_TYPES for ent in doc.ents)


def is_mostly_gibberish(
    phrase: str,
    threshold: float = 0.5,
    vocab_langs: tuple[str, ...] = ("en",)
) -> bool:
    """
    Returns True if fewer than `threshold` fraction of words are in English vocab.
    """
    tokens = [tok.lower() for tok in phrase.split()]
    if not tokens:
        return True

    vocab = load_vocab(vocab_langs)
    valid = sum(tok in vocab for tok in tokens)
    return (valid / len(tokens)) < threshold


def has_month_and_year(phrase: str):
    if re.search(_COLLECTION_YEAR, phrase) or any(month in phrase for month in MONTHS):
        return True


# def normalize_phrase(phrase: str, min_length: int = 3) -> str:
#     """
#     Edit a phrase by removing unwanted words/characters:
#         1) Strip out non-alphanumeric chars
#         2) Remove words with digits
#         3) Remove long digit strings
#         4) Filter short/stop words
#         5) Clean up leftover edges
#     """

#     # 1–3) regex cleaning
#     # phrase = _CLEAN_NON_ALNUM.sub("", phrase)
#     phrase = _CLEAN_WORDS_WITH_DIGITS.sub("", phrase)
#     phrase = _CLEAN_6_DIGIT_NUMS.sub("", phrase)

#     # 4) split & filter
#     words = phrase.split()
#     filtered = []
#     for w in words:
#         lw = w.lower()
#         if (
#             len(w) > min_length
#             and (len(w) != min_length or lw in VOCAB)
#             and lw not in STOP_WORDS
#         ):
#             filtered.append(w)
#     # 5) strip leftover punctuation/spaces
#     return _CLEAN_EDGES.sub("", " ".join(filtered))

def is_common_english(token: str, threshold: float = 3.5) -> bool:
    """
    zipf_frequency returns a log-scaled frequency (1-7);
    3.0 is roughly words occurring ~ once per million words.
    """
    return zipf_frequency(token.lower(), "en") >= threshold

def normalize_phrase(phrase: str, min_length: int = 4) -> str:
    """
    Edit a phrase by removing unwanted words/characters:
        1) Strip out non-alphanumeric chars
        2) Remove words with digits
        3) Remove long digit strings
        4) Filter short/stop words
        5) Clean up leftover edges
    """

    # 1–3) regex cleaning
    phrase = _CLEAN_NON_ALNUM.sub("", phrase)
    phrase = _CLEAN_WORDS_WITH_DIGITS.sub("", phrase)
    phrase = _CLEAN_6_DIGIT_NUMS.sub("", phrase)

    # 4) split & filter
    doc = nlp(phrase)
    kept = []
    for token in doc:
        text = token.text.strip()
        # Keep it if ANY of:
        #  - spaCy thinks it’s part of a named entity
        #  - it’s a “common English” word by frequency
        if len(text) >= min_length:
            if token.ent_type_ or text.lower() in KNOWN_NAMES:
                kept.append(text)
            elif text not in STOP_WORDS and is_common_english(text):
                kept.append(text)

    return " ".join(kept)


def extract_phrases_from_text(
    text: str,
    exclude_phrases: list[str] = ["copyright", "reserved"],
) -> list[str]:
    """
    1) Check for named entities (original case)
    2) If not a name, reject gibberish
    3) Normalize and lowercase
    4) Exclude duplicates & unwanted
    """
    result: list[str] = []
    for line in text.splitlines():
        phrase = line.strip()
        if not phrase:
            continue

        # 1) named-entity check
        # phrase = _CLEAN_NON_ALNUM.sub("", phrase)
        # if has_named_entity(phrase) or has_month_and_year(phrase):
        #     pass
        # else:
        #     # 2) gibberish check
        #     if is_mostly_gibberish(phrase):
        #         continue
        # 3) normalization
        norm = normalize_phrase(phrase).lower()
        # 4) exclude
        if not norm or norm in result:
            continue
        if any(exc in norm for exc in exclude_phrases):
            continue
        result.append(norm)

    return result

def main():
    first = _CLEAN_NON_ALNUM.sub("", "HERBARIUM CF JAMES L. BENNETT.")
    print(first)
    print(has_named_entity(first))
    print(is_mostly_gibberish(first))
    pass

if __name__ == "__main__":
    main()