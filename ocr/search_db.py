from rapidfuzz import fuzz
import cv2
from build_token_db import read_image_and_preprocess

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
    Given an input_phrase, search the label database for images that contain the input phrase

    Parameters
    ----------
    input_phrase : str
        The input phrase
    label_db : dict[str, list[str]]
        The dictionary database that stores pairs of (image_path, list_of_phrases)
        
    Returns
    -------
    A list of image paths 
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
    Given an input_phrase, search the label database for images that contain the input phrase.
    Approach: Since we're matching a whole label, fuzzy match all JOINED phrases in the input image and 
        those for each database image
    """
    output : list[str] = [] 

    # Read in input image
    img = read_image_and_preprocess(file_path)

    # Run SAM on input image and get a list of labels
    pass
    segmented_labels = []

    # Run OCR on recognized labels
    pass
    input_phrases = []

    # Matching: a list of phrases
    joined_input_phrase = " ".join(input_phrases)

    for image_path, image_phrases in label_db.items():
        joined_item_phrase = " ".join(image_phrases)
        if fuzz.partial_ratio(joined_input_phrase, joined_item_phrase, score_cutoff=70):
            if image_path not in output:
                output.append(image_path)
    return output