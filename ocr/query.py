import json
import pprint
from ocr_cleaning import normalize_phrase
from build_token_db import OCR_image, read_image_and_preprocess, DATABASE_FILENAME
from search_db import search_by_phrase, search_by_image


with open(DATABASE_FILENAME, "rb") as f:
    database = json.load(f)

def query_by_label(text_label):
    """
    given text label, clean label, find images that match
    """
    text_label = "new mexico plants"

    norm = normalize_phrase(text_label)
    output = search_by_phrase(text_label, database)
    pprint.pprint(output)
    
    
def query_by_image(file_path):
    """
    given image, extract label, match
    """
    # Read in input image
    img = read_image_and_preprocess(file_path)

    # Run SAM on input image and get a list of labels
    pass
    segmented_labels = []

    # Run OCR on recognized labels and get a list of phrases
    pass
    input_phrases = []

    # Search database and get a list of paths
    list_of_paths = search_by_image(input_phrases, database)
