import re

def clean_ocr_tokens(tokens: list[str]) -> tuple[list[str], str]:
    '''
    Clean OCR tokens from Tesseract output.

    Parameters
    ----------
    tokens : list[str]
        List of uncleaned tokens from Tesseract.

    Returns
    -------
    cleaned : list[str]
        List of cleaned lowercase tokens.
    phrase : str
        Joined normalized phrase for fuzzy matching.
    '''
    cleaned = []
    for t in tokens:
        t = t.strip()
        t = re.sub(r'[^a-zA-Z0-9.\-]', '', t)  # Keep letters, numbers, dot, hyphen
        if len(t) > 1 or t.isnumeric():
            cleaned.append(t.lower())
    # Join into normalized phrase for fuzzy matching
    phrase = " ".join(cleaned)

    return cleaned, phrase
