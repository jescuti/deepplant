import re
import nltk
from nltk.corpus import stopwords
import spacy
from functools import lru_cache
from typing import Set

'''
NOTE: Install language models: 
    python -m spacy download en_core_web_sm 
    python -m spacy download fr_core_news_sm
'''

_CLEAN_NON_ALNUM         = re.compile(r"[^A-Za-z0-9\s]+")
_CLEAN_WORDS_WITH_DIGITS = re.compile(r"[A-Za-z]+\d+[A-Za-z]*")
_CLEAN_8_DIGIT_NUMS      = re.compile(r"[0-9]{8,}")
_CLEAN_EDGES             = re.compile(r"^[\s\.',]+|[\s\.',]+$")

nlp = spacy.load("en_core_web_sm")
NAMED_ENTITY_TYPES = {"PERSON", "ORG", "GPE", "LOC"}
KNOWN_NAMES = {"Olneyanum"}

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


def has_named_entity(phrase: str, extra_names: set[str] = KNOWN_NAMES) -> bool:
    """
    Returns True if `phrase` contains:
      - any hard-coded name in `extra_names`, or
      - any spaCy-detected PERSON, ORG, GPE, LOC entity.
    """
    phrase = phrase.strip()
    if not phrase:
        return False

    # quick check for any “special” names
    if any(name in phrase for name in extra_names):
        return True

    # spaCy NER
    doc = nlp(phrase)
    return any(ent.label_ in NAMED_ENTITY_TYPES for ent in doc.ents)


def is_mostly_gibberish(
    phrase: str,
    threshold: float = 0.5,
    vocab_langs: tuple[str, ...] = ("en", "fr",)
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


def is_useful_phrase(phrase: str) -> bool:
    """
    Apply smart filters to phrase, return True if the phrase:
        - has named entities
        - is mostly gibberish (having a lot of words not in the English vocab)
    """
    phrase = phrase.strip()
    if not phrase:
        return False
    if has_named_entity(phrase):
        return True
    if is_mostly_gibberish(phrase):
        return False
    
    return True


# def remove_stopwords(phrase: str) -> str:
#     stop_words = set(stopwords.words("english"))
#     stop_words.update(["like"])
#     word_tokens = word_tokenize(phrase)


def normalize_phrase(
    phrase: str,
    min_length: int = 3,
    vocab_langs: tuple[str, ...] = ("en", "fr")
) -> str:
    """
    Edit a phrase by removing unwanted words/characters
        1. Strip out non-alphanumeric chars
        2. Remove any word that has digits in it
        3. Split, then drop words that are too short or (if len==3) not in the vocab
        4. Clean up leftover edge punctuation/spaces
    """
    vocab = load_vocab(vocab_langs)

    # 1) remove unwanted characters
    phrase = _CLEAN_NON_ALNUM.sub("", phrase)
    # 2) drop words with digits
    phrase = _CLEAN_WORDS_WITH_DIGITS.sub("", phrase)
    # 3) drop numbers with more than 8 digits (barcode)
    phrase = _CLEAN_8_DIGIT_NUMS.sub("", phrase)

    # 4) split, filter on each word, and re-join
    stop_words = set(stopwords.words("english"))
    stop_words.update(["like"])
    words = phrase.split()
    filtered = [
        w for w in words
        if not (
            len(w) < min_length
            or (len(w) == min_length and w.lower() not in vocab)
            or w.lower() in stop_words  # filter out stop words
        )
    ]
    phrase = " ".join(filtered)

    # 5) strip leftover punctuation/spaces
    phrase = _CLEAN_EDGES.sub("", phrase)
    return phrase


def extract_phrases_from_text(
    text: str,
    exclude_phrases: list[str],
    vocab_langs: tuple[str, ...] = ("en", "fr",)
) -> list[str]:
    """
    Split text into lines, normalize each “useful” phrase, return lowercased.
    Leave phrases that are in the list of excluded phrases.
    """
    phrases: list[str] = []
    for line in text.splitlines():
        if is_useful_phrase(line):
            norm = normalize_phrase(line, vocab_langs=vocab_langs).lower()
            if norm and norm not in phrases and not any(exc in norm for exc in exclude_phrases):
                phrases.append(norm)
    return phrases


def main():
    pass
    # print(has_named_entity(': 2 x Z : : Herbarium Olneyanum,'))
    # print(is_mostly_gibberish(': 2 x Z : : Herbarium Olneyanum,'))

if __name__ == "__main__":
    main()