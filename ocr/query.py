import json
from rapidfuzz import fuzz
import re
import os
from fpdf import FPDF
from ocr import run_clean_ocr

_BDR_CODES = re.compile(r'([0-9]{6})')
DATABASE_FILENAME = "./databases/db_labels.json"

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

def generate_pdf(list_of_paths: list[str], query: str) -> None:
    """
    Generates a PDF file that contains the cropped out labels and their corresponding image URLs.

    URL format: https://repository.library.brown.edu/iiif/image/bdr:000000/full/full/0/default.jpg
    
    Parameters
    ----------
    list_of_paths : list[str]
        A list of image paths, assumed to contain the herbarium code `bdr_000000.`
    query :  str
        The input query, either a text label or a cleaned image path. 
    Returns
    -------
    None
    """
    output_filename = os.path.join("output", f"{query}.pdf")

    print(f"Generating output PDF at {output_filename}...")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12, style="U")
    pdf.set_text_color(0, 0, 255)
    pdf.set_auto_page_break(True)

    for path in list_of_paths:
        code = re.search(_BDR_CODES, path).group(0) # type: ignore
        pdf.cell(
            200, 5, 
            txt=f"https://repository.library.brown.edu/studio/item/bdr:{code}/", # type: ignore
            ln=1, align="L", 
            link=f"https://repository.library.brown.edu/studio/item/bdr:{code}/")
        pdf.image(path, x=pdf.get_x(), y=pdf.get_y(), h=40)
        pdf.ln(50)

    pdf.output(output_filename)


def search_text_phrase(query: str, label_db: dict[str, list[str]], threshold=70) -> list[str]:
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
    matched_paths = set()

    for image_path, phrases in label_db.items():
        for phrase in phrases:
            if query in phrase:  # Substring match
                matched_paths.add(image_path)
                break
            elif fuzz.ratio(query, phrase) >= threshold:  # Fuzzy match with threshold
                matched_paths.add(image_path)
                break

    return list(matched_paths)


def search_image_phrase(input_phrases: list[str], label_db: dict[str, list[str]]) -> list[str]:
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
    matched_paths = set()
    joined_input_phrase = " ".join(input_phrases)

    for image_path, image_phrases in label_db.items():
        joined_item_phrase = " ".join(image_phrases)
        if fuzz.ratio(joined_input_phrase, joined_item_phrase, score_cutoff=70):
            matched_paths.add(image_path)
            break

    return list(matched_paths)


def query_by_label(text_label: str) -> None:
    """
    Given a text label, clean label, and find images that match.
    """
    # Load text database
    with open(DATABASE_FILENAME, "rb") as f:
        database = json.load(f)

    # Search database and get a list of paths
    cleaned_label = text_label.strip().lower()
    list_of_paths = search_text_phrase(cleaned_label, database)
    
    # Generate PDf
    generate_pdf(list_of_paths, text_label)
    

def query_by_image(file_path: str) -> None:
    """
    Given a label image, extract texts, and find images that match.
    """
    # Load text database
    with open(DATABASE_FILENAME, "rb") as f:
        database = json.load(f)

    # Run OCR on recognized labels and get a list of phrases
    input_phrases = run_clean_ocr(file_path)
    if input_phrases is None:
        raise FileNotFoundError(f"Could not load image at {file_path!r}")

    # Search database and get a list of paths
    list_of_paths = search_image_phrase(input_phrases, database)
    cleaned_input_path, _ = os.path.splitext(os.path.basename(file_path))

    # Generate PDF
    generate_pdf(list_of_paths, cleaned_input_path)
