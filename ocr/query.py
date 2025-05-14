import json
from rapidfuzz import fuzz
import os
from ocr import run_clean_ocr
from generate_output import generate_pdf

DATABASE_FILENAME = "./past_db/db_labels.json"
OUTPUT_DIR = "./"
IMAGE_DIR = "../image_download/db_labels"

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
def search_text_phrase(
        query: str, 
        label_db: dict[str, list[str]], 
        threshold=70
    ) -> tuple[list[str], list[float]]:
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
    tuple (matched_paths, similarity_scores)
    """
    search_output = dict()  # K-V pair: (matched_path, similarity_score)

    for image_path, phrases in label_db.items():
        for phrase in phrases:
            if query in phrase:  # Substring match
                search_output[image_path] = 100
                break
            else:
                similarity_score = fuzz.ratio(query, phrase) 
                if similarity_score >= threshold:  # Fuzzy match with threshold
                    search_output[image_path] = similarity_score
                    break

    return list(search_output.keys()), list(search_output.values())


def search_image_phrase(
        input_phrases: list[str], 
        label_db: dict[str, list[str]],
        threshold=70
    ) -> tuple[list[str], list[float]]:
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
    tuple (matched_paths, similarity_scores)
        A list of matched paths with a corresponding list of similarity scores
    """
    search_output = dict()

    joined_input_phrase = " ".join(input_phrases)

    for image_path, image_phrases in label_db.items():
        joined_item_phrase = " ".join(image_phrases)
        similarity_score = fuzz.ratio(joined_input_phrase, joined_item_phrase, score_cutoff=70)
        if similarity_score >= threshold:
            search_output[image_path] = similarity_score
            break

    return list(search_output.keys()), list(search_output.values())


def query_by_label(text_label: str) -> tuple[list[str], list[float]]:
    """
    Given a text label, clean label, find images that match along with 
    similarity scores, and render results in a PDF. 

    Returns
    -------
    tuple (matched_paths, similarity_scores)
        A list of matched paths with a corresponding list of similarity scores
    """
    # Load text database
    with open(DATABASE_FILENAME, "rb") as f:
        database = json.load(f)

    # Search database and get a list of paths
    cleaned_label = text_label.strip().lower()
    matched_paths, similarity_scores = search_text_phrase(cleaned_label, database)
    
    # Generate PDf
    query = text_label.replace(" ", "_")
    output_filename = os.path.join(OUTPUT_DIR, "output", f"{query}.pdf")
    print(f"Generating output PDF at {output_filename}...")
    generate_pdf(matched_paths, similarity_scores, output_filename, IMAGE_DIR)
    
    return matched_paths, similarity_scores
    

def query_by_image(file_path: str) -> tuple[list[str], list[float]]:
    """
    Given a label image, extract texts, find images that match along with 
    similarity scores, and render results in a PDF. 

    Returns
    -------
    tuple (matched_paths, similarity_scores)
        A list of matched paths with a corresponding list of similarity scores
    """
    # Load text database
    with open(DATABASE_FILENAME, "rb") as f:
        database = json.load(f)

    # Run OCR on recognized labels and get a list of phrases
    input_phrases = run_clean_ocr(file_path)
    if input_phrases is None:
        raise FileNotFoundError(f"Could not load image at {file_path!r}")

    # Search database and get a list of paths
    matched_paths, similarity_scores = search_image_phrase(input_phrases, database)

    # Generate PDF
    query, _ = os.path.splitext(os.path.basename(file_path))
    output_filename = os.path.join(OUTPUT_DIR, "output", f"{query}.pdf")
    print(f"Generating output PDF at {output_filename}...")
    generate_pdf(matched_paths, similarity_scores, output_filename, IMAGE_DIR)

    return matched_paths, similarity_scores
