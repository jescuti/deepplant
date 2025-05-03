import os
import numpy as np
from typing import Any, Literal
import cv2
import pytesseract
import json
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
ROOTDIR = "../image_download/herbarium_random_500"  # TODO: make this invariant
EXCLUDE_PHRASES = ["copyright", "reserved"]
DATABASE_FILENAME = "label_phrases_db.json"

def OCR_image(image: np.ndarray, output_mode: Literal["txt", "dct"] = "txt") -> Any:
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

def main():
    # Database of image path to text tokens and phrase
    label_db: dict[str, list[str]] = {}
    first_entry = True

    with open(DATABASE_FILENAME, "w", encoding="utf-8", buffering=1) as f:
        f.write("{\n")
        # Recursively search all subdirectories for files
        # If just one parent folder, use os.listdir
        for dirpath, _, files in os.walk(ROOTDIR):
            for file in files:
                file_path = os.path.join(dirpath, file)
                if not (os.path.isfile(file_path) and "DS_Store" not in file_path):
                    continue

                img = cv2.imread(file_path)
                gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # TODO: if more steps, put into preprocessing
                
                # OCR + extract phrases
                raw_text = OCR_image(gray_img)
                phrases = extract_phrases_from_text(raw_text, EXCLUDE_PHRASES)
                label_db[file_path] = phrases
                
                # Stream database to a JSON file
                if first_entry:
                    first_entry = False
                else:
                    f.write(",\n")
                f.write(
                    f"  {json.dumps(file_path)}: "
                    f"{json.dumps(phrases, ensure_ascii=False)}"
                )
        f.write("\n}\n")

if __name__ == "__main__":
    main()