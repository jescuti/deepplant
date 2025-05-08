import json
import pprint
from ocr_cleaning import normalize_doc
from ocr import run_clean_ocr
from build_token_db import read_image_and_preprocess, DATABASE_FILENAME
from search_db import search_phrase, search_list_of_phrases
from fpdf import FPDF
import re

_BDR_CODES = re.compile(r'([0-9]{6})')


def extract_bdr_code(list_of_paths: list[str]) -> list[str]:
    list_of_codes : list[str] = []
    for path in list_of_paths:
        code = re.search(_BDR_CODES, path)
        if code:
            list_of_codes.append(code.group(0))
    return list_of_codes


def generate_pdf(list_of_codes: list[str], list_of_paths: list[str]) -> None:
    """
    Generates a PDF file that contains the cropped out labels and their corresponding image URLs.

    URL format: https://repository.library.brown.edu/iiif/image/bdr:000000/full/full/0/default.jpg
    
    Parameters
    ----------
    list_of_paths : list[str]
        A list of image paths, assumed to be of format `bdr_000000.`

    Returns
    -------
    None
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12, style="U")
    pdf.set_text_color(0, 0, 255)
    pdf.set_auto_page_break(True)

    for (code, path) in zip(list_of_codes, list_of_paths):
        pdf.cell(
            200, 5, txt=f"https://repository.library.brown.edu/iiif/image/bdr:{code}/full/full/0/default.jpg", \
                ln=1, align="L", \
                link=f"https://repository.library.brown.edu/iiif/image/bdr:{code}/full/full/0/default.jpg")
        # pdf.image(path, x=pdf.get_x(), y=pdf.get_y(), h=40)
        pdf.ln(50)

    pdf.output("output.pdf")


def query_by_label(text_label, database):
    """
    Given a text label, clean label, and find images that match.
    """
    cleaned_label = text_label.strip().lower()
    list_of_paths = search_phrase(cleaned_label, database)
    
    # Generate pdf
    return list_of_paths
    

def query_by_image(file_path: str, database: dict[str, list[str]], labeled: bool=True):
    """
    Given an image, segment label (if needed), extract texts, and find images that match.
    TODO: 
    1. Add SAM for full picture
    2. Input format of image?
    """
    # Read in input image
    img = read_image_and_preprocess(file_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image at {file_path!r}")

    # Run SAM on input image and get a list of labels
    if not labeled:
        pass
        segmented_labels = []

    # Run OCR on recognized labels and get a list of phrases
    input_phrases = run_clean_ocr(img)

    # Search database and get a list of paths
    list_of_paths = search_list_of_phrases(input_phrases, database)
    return list_of_paths


def main():
    with open("databases/5k_db_1.json", "rb") as f:
    # with open(DATABASE_FILENAME, "rb") as f:
        database = json.load(f)
    
    ### TEST QUERY BY LABEL
    text_label = "rocky mountain flora"
    list_of_paths = query_by_label(text_label, database)
    print(f"Finished querying. Number of images found: {len(list_of_paths)}.")
    list_of_codes = extract_bdr_code(list_of_paths)
    print("Started generating PDF...")
    generate_pdf(list_of_codes, list_of_paths)
    print("Finished generating PDF!")

    # pprint.pprint(search_by_phrase(text_label, database))

    ### TEST QUERY BY IMAGE
    # image_path = "../image_download/db_labels/Mertensia alpina_bdr_754912.jpg"
    # list_of_paths = query_by_image(image_path, database)
    # list_of_codes = extract_bdr_code(list_of_paths)
    # generate_pdf(list_of_codes, list_of_paths)


if __name__ == "__main__":
    main()