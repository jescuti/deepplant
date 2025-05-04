from rapidfuzz import fuzz
import cv2
from build_token_db import read_image_and_preprocess

"""
TOKENS DATABASE STRUCTURE EXAMPLE

label_db = {
  "./images/Mertensia alpina_bdr_754912.jpg": [
    "rocky mountain flora lat 3941",
    "ehall harbour colls 1862"
  ],
  ...
}
"""
def search_phrase(input_phrase: str, label_db: dict[str, list[str]]) -> list[str]:
    """
    Given an input_phrase, search the label database for images that contain that phrase.

    Parameters
    ----------
    input_phrase : str
        The input phrase
    label_db : dict[str, list[str]]
        The dictionary database that stores pairs of (image_path, list_of_phrases)
        
    Returns
    -------
    A list of image paths whose labels contain the search phrase.
    """
    output : list[str] = []

    for image_path, phrases in label_db.items():
        for phrase in phrases:
            if fuzz.partial_ratio(input_phrase, phrase, score_cutoff=70):
                if image_path not in output:
                    output.append(image_path)
    return output


def search_list_of_phrases(input_phrases: list[str], label_db: dict[str, list[str]]) -> list[str]:
    """
    Given a list of phrases from an input image label, search the label database 
        for images that contain those phrases. 
    
    Approach: Join all phrases in the input list, fuzzy match against joined phrases
        in each database image
    
    Parameters
    ----------
    input_phrases : list[str]
        A list of input phrases, extracted by OCR from the input image
    label_db : dict[str, list[str]]
        The dictionary database that stores pairs of (image_path, list_of_phrases)
        
    Returns
    -------
    A list of image paths whose labels contain the search phrases.
    """
    output : list[str] = []

    joined_input_phrase = " ".join(input_phrases)

    for image_path, image_phrases in label_db.items():
        joined_item_phrase = " ".join(image_phrases)
        if fuzz.partial_ratio(joined_input_phrase, joined_item_phrase, score_cutoff=70):
            if image_path not in output:
                output.append(image_path)
    return output