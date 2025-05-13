import json
from rapidfuzz import fuzz
import re
import os
from fpdf import FPDF
from ocr import run_clean_ocr

_BDR_CODES = re.compile(r'([0-9]{6})')
DATABASE_FILENAME = "./databases/db_labels.json"
OUTPUT_DIR = "./"
IMAGE_DIR = "./"

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
class PDFWithFooter(FPDF):
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Set font: Arial italic 8
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(0, 0, 0)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')
        
def generate_pdf(list_of_paths: list[str], output_filename: str) -> None:
    """
    Generates a PDF file that contains the cropped out labels and their corresponding image URLs.
    """
    pdf = PDFWithFooter()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12, style="U")
    pdf.set_text_color(0, 0, 255)
    pdf.set_auto_page_break(True, margin=10)

    image_height = 40
    spacing_after_image = 10

    for path in list_of_paths:
        if "/" not in path:
            path = os.path.join(IMAGE_DIR, path)

        code = re.search(_BDR_CODES, path).group(0) # type: ignore
        
        # Check remaining space on page
        current_y = pdf.get_y()
        if current_y + image_height + spacing_after_image > pdf.h - pdf.b_margin:
            pdf.add_page()

        # Add hyperlink text
        link_url = f"https://repository.library.brown.edu/studio/item/bdr:{code}/"
        pdf.cell(200, 5, txt=link_url, ln=1, align="L", link=link_url) # type: ignore
        
        # Add image
        pdf.image(path, x=pdf.get_x(), y=pdf.get_y(), h=image_height)
        pdf.ln(image_height + spacing_after_image)

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


def query_by_label(text_label: str) -> int:
    """
    Given a text label, clean label, and find images that match.

    Returns
    -------
    int
        The number of matched images.
    """
    # Load text database
    with open(DATABASE_FILENAME, "rb") as f:
        database = json.load(f)

    # Search database and get a list of paths
    cleaned_label = text_label.strip().lower()
    list_of_paths = search_text_phrase(cleaned_label, database)
    
    # Generate PDf
    query = text_label.replace(" ", "_")
    output_filename = os.path.join(OUTPUT_DIR, "output", f"{query}.pdf")
    print(f"Generating output PDF at {output_filename}...")
    generate_pdf(list_of_paths, output_filename)
    
    return len(list_of_paths)
    

def query_by_image(file_path: str) -> int:
    """
    Given a label image, extract texts, and find images that match.

    Returns
    -------
    int
        The number of matched images.
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

    # Generate PDF
    query, _ = os.path.splitext(os.path.basename(file_path))
    output_filename = os.path.join(OUTPUT_DIR, "output", f"{query}.pdf")
    print(f"Generating output PDF at {output_filename}...")
    generate_pdf(list_of_paths, output_filename)

    return len(list_of_paths)
