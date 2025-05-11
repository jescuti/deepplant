from typing import Any, Literal
import numpy as np
import pytesseract
import cv2
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
    image = cv2.imread(file_path)
    if image is None:
        return None
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    return gray_image


def _raw_ocr(image: np.ndarray, output_mode: Literal["txt", "dct"] = "txt") -> Any:
    """
    Run OCR on the input image using a specific output mode.

    Parameters
    ----------
        image : np.ndarray
            The image to run OCR on.
        output_mode: Literal["txt", "dct"]
            An output mode that belongs to the specified list. Default: "txt".
    
    Returns
    -------
    The OCR output in the specified format.
    """
    # Run tesseract OCR for text extraction
    if output_mode == "txt":
        out = pytesseract.image_to_string(image, config=MYCONFIG)
    elif output_mode == "dct":
        out = pytesseract.image_to_data(image, config=MYCONFIG, output_type=pytesseract.Output.DICT)

    return out


def run_clean_ocr(file_path: str, output_mode: Literal["txt", "dct"] = "txt") -> Any:
    """
    Run tesseract OCR on the input image and return a list of cleaned text phrases
    """
    image = read_image_and_preprocess(file_path)
    if image is None:
        print(f"ERROR: Could not load image at {file_path!r}")
        return None
    if output_mode:
        raw = _raw_ocr(image, output_mode)
    else:
        raw = _raw_ocr(image)
    print("Raw text detected by OCR:\n", raw)
    
    cleaned_phrases = extract_phrases_from_text(raw)
    print("Cleaned extracted text:\n", cleaned_phrases)
    return cleaned_phrases