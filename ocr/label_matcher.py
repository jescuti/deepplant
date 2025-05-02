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
            if fuzz.partial_ratio(input_phrase, phrase, score_cutoff=70):
                if image_path not in output:
                    output.append(image_path)
    return output

def search_by_image(file_path, label_db: dict[str, list[str]]) -> list[str]:
    """
    Given a path to an image, return images that have the same label
    """