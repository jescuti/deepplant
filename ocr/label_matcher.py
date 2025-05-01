from rapidfuzz import fuzz
"""
TOKENS DATABASE STRUCTURE

label_db = {
  "./images/Mertensia alpina_bdr_754912.jpg": [
    "rocky mountain flora lat 3941",
    "ehall harbour colls 1862"
  ],
  ...
}
"""
def search_by_phrase(input_phrase: str, label_db: dict[str, list[str]]) -> list[str]:
    """
    Fuzzy matching
    """
    output : list[str] = []
    for image_path, phrases in label_db.items():
        for phrase in phrases:
            if fuzz.partial_ratio(input_phrase, phrase, score_cutoff=50):
                if image_path not in output:
                    output.append(image_path)
    return output

def match_query_to_labels(
        query_tokens: list[str], 
        query_phrase: str, 
        db, 
        top_k: int = 10
    ) -> list[tuple[str, float, float]]:
    '''
    Match a query label to the top-K most similar entries in the label database.

    Matches are scored using:
    - Token overlap (set intersection)
    - Fuzzy string matching on normalized phrase

    Parameters
    ----------
    query_tokens : List[str]
        A list of cleaned tokens from the OCR output of the query image.

    query_phrase : str
        A normalized, joined string from OCR tokens (for fuzzy matching).

    db : Dict[str, Dict]
        A dictionary mapping image paths (or IDs) to their label info.
        Each entry should have:
            - 'tokens': List[str]
            - 'phrase': str

    top_k : int, optional
        Number of top matches to return (default is 10).

    Returns
    -------
    List[Tuple[str, float, float]]
        A list of tuples, each containing:
            - image path (str)
            - token overlap score (float, 0-1)
            - fuzzy phrase match score (float, 0-1)
        Sorted in descending order of fuzzy match score.
    '''
    candidates = []
    for img, info in db.items():
        overlap = len(set(query_tokens) & info["tokens"])
        score = overlap / len(query_tokens)
        candidates.append((img, score))
    
    # Sort by score (descending order)
    top = sorted(candidates, key=lambda x: -x[1])[:top_k]

    # Refine using fuzzy string match
    from rapidfuzz import fuzz
    final = []
    for img, token_score in top:
        phrase_score = fuzz.partial_ratio(query_phrase, db[img]["phrase"]) / 100
        final.append((img, token_score, phrase_score))
    
    return sorted(final, key=lambda x: -x[2])