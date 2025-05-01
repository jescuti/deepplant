import re
import spacy
import nltk

# NOTE: Run to download the english model: python -m spacy download en_core_web_sm 
nlp = spacy.load("en_core_web_sm")
_english_vocab = None

def load_english_vocab():
    # TODO: add French vocab
    global _english_vocab
    if _english_vocab is None: 
        nltk.download('words', quiet=True)
        from nltk.corpus import words
        _english_vocab = set(words.words())

def has_named_entity(phrase: str) -> bool:
    '''
    Filter to check if a phrase contains named entities.
        - PERSON: person's name
        - ORG: organizations
        - GPE: geopolitical entities, e.g. everything with a governing body like cities and countries
        - LOC: locations
    
    Returns
    -------
    bool
        Indicates if the phrase has named entities.
    '''
    known_names = ["Olneyanum"]
    mask = [True for name in known_names if name in phrase]
    if sum(mask) > 0:
        return True
    doc = nlp(phrase)
    return any(ent.label_ in {"PERSON", "ORG", "GPE", "LOC"} for ent in doc.ents)


def is_mostly_gibberish(phrase: str, threshold: float = 0.5) -> bool:
    '''
    Filter to check if a phrase is mostly gibberish (contains few real English words).
    Parameters
    ----------
    phrase : str
        The phrase to check against.
    threshold : float
        The threshold for the proportion of invalid, gibberish words.

    Returns
    -------
    bool
        Indicates if the phrase is mostly gibberish.
    '''
    load_english_vocab()
    tokens = phrase.lower().split()
    if not tokens:
        return True
    valid_count = sum(1 for t in tokens if t in _english_vocab)
    return (valid_count / len(tokens)) < threshold


# def looks_like_junk(phrase: str) -> bool:
#     '''
#     Filter out words that have weird spacing and heavy alphanumeric mixes, e.g. "No44e"
#     '''
#     words = phrase.split()
#     for 
#     # TODO: add filter for 'y F . s'
#     # Too many non-letters (e.g., digits or weird caps)
#     if re.fullmatch(r'[A-Z0-9\s\.\-]{1,}', phrase) and len(phrase.split()) > 2:
#         return True
#     # Mix of digits and letters in short phrase
#     if re.search(r'\d', phrase) and len(phrase.split()) <= 2:
#         return True
#     return False

def is_useful_phrase(phrase: str) -> bool:
    phrase = phrase.strip()
    if not phrase:
        return False
    if has_named_entity(phrase):
        return True
    # if looks_like_junk(phrase):
    #     return False
    if is_mostly_gibberish(phrase):
        return False
    
    return True


def normalize_phrase(phrase: str) -> str:
    load_english_vocab()
    # print("before", phrase)
    phrase = re.sub(r'[^a-zA-Z0-9&\ \-\']', '', phrase)
    phrase = re.sub(r'[a-zA-Z]+\d+[a-zA-Z]*', '', phrase)
    phrase = phrase.strip()
    print("before", phrase)
    if phrase:
        words = phrase.split()
        cleaned = []
        for word in words:
            # print(word)
            # if not ((len(word) == 1) or ((len(word) == 2) and (word.lower() not in _english_vocab))):
            if not (len(word) <= 2 or (len(word) == 3 and word.lower() not in _english_vocab)):
                cleaned.append(word)
        phrase = " ". join(cleaned).strip()
        # print("after", phrase)
    # Clean beginning and end
    phrase = re.sub(r'^[.,\ \']+', '', phrase)
    phrase = re.sub(r'[\ .,]+$', '', phrase)
    print("after", phrase)
    return phrase


def extract_phrases_from_text(text: str) -> list[str]:
    lines = text.splitlines()
    phrases = []
    for line in lines:
        if is_useful_phrase(line):
            normalized = normalize_phrase(line)
            if normalized:
                phrases.append(normalized.lower())
                
    return phrases


def clean_dict_tokens(tokens: list[str]) -> tuple[list[str], str]:
    '''
    Clean OCR tokens from Tesseract dictionary output.

    Parameters
    ----------
    tokens : list[str]
        List of uncleaned tokens from Tesseract.

    Returns
    -------
    cleaned : list[str]
        List of cleaned lowercase tokens.
    phrase : str
        A joined phrase of all tokens for fuzzy matching.
    '''
    cleaned = []
    print(tokens)
    for t in tokens:
        t = t.strip()
        '''
        NOTE: This cleaning is not robust. For example,
        Input: ['', '', '', '', '“Rocky', 'Mountain', 'Flora,', 'Lat.', '39°41".', '', 'No44e', '', 'Gs', 'Cnn', 'Lon', '', '', '|', 'E.HALL', '&', 'J.', 'P.', 'HARBOUR,', 'Colls.', '1862.', '', '', '4']
        Output: ['rocky', 'mountain', 'flora', 'lat.', '3941.', 'no44e', 'gs', 'cnn', 'lon', 'e.hall', 'j.', 'p.', 'harbour', 'colls.', '1862.', '4']
        -> Need to deal with nonsense words like no44e or single numbers like 4
        '''
        t = re.sub(r'[^a-zA-Z0-9.\-]', '', t)  # Keep letters, numbers, dot, hyphen
        if len(t) > 1 or t.isnumeric():
            cleaned.append(t.lower())
    # Join into normalized phrase for fuzzy matching
    phrase = " ".join(cleaned)

    return cleaned, phrase

def main():
    # phrase = "S Cnn Lon"
    # if re.fullmatch(r'[A-Z0-9\s\.\-]{1,}', phrase) and len(phrase.split()) > 2:
    #     print("yes")
    print(has_named_entity(': 2 x Z : : Herbarium Olneyanum,'))
    # print(has_named_entity('Oregon coll. Exigv Haut, ann. 1871. Presented to'))
    # print(is_mostly_gibberish(': 2 x Z : : Herbarium Olneyanum,'))
    # print(is_mostly_gibberish('Oregon coll. Exigv Haut, ann. 1871. Presented to'))

if __name__ == "__main__":
    main()