import json
import re
import time
from fpdf import FPDF
from ocr import run_clean_ocr
from build_token_db import read_image_and_preprocess, DATABASE_FILENAME
from search_db import search_phrase, search_list_of_phrases

_BDR_CODES = re.compile(r'([0-9]{6})')
OUTPUT_FILENAME = "output.pdf"

def generate_pdf(list_of_paths: list[str]) -> None:
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

    for path in list_of_paths:
        code = re.search(_BDR_CODES, path).group(0)
        pdf.cell(
            200, 5, txt=f"https://repository.library.brown.edu/iiif/image/bdr:{code}/full/full/0/default.jpg", \
                ln=1, align="L", \
                link=f"https://repository.library.brown.edu/iiif/image/bdr:{code}/full/full/0/default.jpg")
        pdf.image(path, x=pdf.get_x(), y=pdf.get_y(), h=40)
        pdf.ln(50)

    pdf.output(OUTPUT_FILENAME)


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
    Given an image of a label, extract texts, and find images that match.
    """
    # Read in input image
    img = read_image_and_preprocess(file_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image at {file_path!r}")

    # Run OCR on recognized labels and get a list of phrases
    input_phrases = run_clean_ocr(img)

    # Search database and get a list of paths
    list_of_paths = search_list_of_phrases(input_phrases, database)
    return list_of_paths


def main():
    with open("databases/db_labels.json", "rb") as f:
    # with open(DATABASE_FILENAME, "rb") as f:
        database = json.load(f)
    
    ### TEST QUERY BY LABEL
    text_label = "rocky mountain flora lat 3941"
    logic_start = time.time()
    list_of_paths = query_by_label(text_label, database)
    num_images = len(list_of_paths)
    print(f"Finished querying. Number of images found: {num_images}.")
    print("Started generating PDF...")
    generate_pdf(list_of_paths)  # This step generally takes the longest
    logic_end = time.time()
    print("Finished generating PDF!")
    total_time = logic_end - logic_start
    print(f"Average runtime over {num_images} images: {total_time/num_images:.5f} seconds")

    ### TEST QUERY BY IMAGE
    # image_path = "../image_download/db_labels/Mertensia alpina_bdr_754912.jpg"
    # list_of_paths = query_by_image(image_path, database)
    # generate_pdf(list_of_paths)


if __name__ == "__main__":
    main()