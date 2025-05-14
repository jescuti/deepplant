import pytesseract
import cv2
from typing import Any
from ocr_cleaning import extract_phrases_from_text

'''
Page segmentation modes (PSM):
    0|osd_only                Orientation and script detection (OSD) only.
    1|auto_osd                Automatic page segmentation with OSD.
    2|auto_only               Automatic page segmentation, but no OSD, or OCR. (not implemented)
    3|auto                    Fully automatic page segmentation, but no OSD. (Default)
    4|single_column           Assume a single column of text of variable sizes.
    5|single_block_vert_text  Assume a single uniform block of vertically aligned text.
    6|single_block            Assume a single uniform block of text.
    7|single_line             Treat the image as a single text line.
    8|single_word             Treat the image as a single word.
    9|circle_word             Treat the image as a single word in a circle.
  10|single_char             Treat the image as a single character.
  11|sparse_text             Sparse text. Find as much text as possible in no particular order.
  12|sparse_text_osd         Sparse text with OSD.
  13|raw_line                Raw line. Treat the image as a single text line,
                            bypassing hacks that are Tesseract-specific.
'''

'''
OCR Engine modes (OEM):
    0|tesseract_only          Legacy engine only.
    1|lstm_only               Neural nets LSTM engine only.
    2|tesseract_lstm_combined Legacy + LSTM engines.
    3|default                 Default, based on what is available.
'''

MYCONFIG = r"--psm 6 --oem 3"

def read_image_and_preprocess(file_path):
    """
    Read and preprocess image.
    """
    image = cv2.imread(file_path)
    if image is None:
        return None
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    return gray_image


def run_clean_ocr(file_path: str, print_text: bool = False) -> Any:
    """
    Run tesseract OCR on the input image and return a list of cleaned text phrases
    """
    image = read_image_and_preprocess(file_path)
    if image is None:
        print(f"ERROR: Could not load image at {file_path!r}")
        return None
    raw = pytesseract.image_to_string(image, config=MYCONFIG)
    cleaned_phrases = extract_phrases_from_text(raw)
    if print_text:
        print("Raw text detected by OCR:\n", raw)
        print("Cleaned extracted text:\n", cleaned_phrases)
    return cleaned_phrases