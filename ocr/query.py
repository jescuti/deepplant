import json
import pprint
from ocr_cleaning import normalize_phrase
from build_token_db import OCR_image, read_image_and_preprocess, DATABASE_FILENAME
from search_db import search_by_phrase, search_by_image

def generate_pdf(list_of_paths):
    """
    Generate a PDF file that contains the cropped out labels and URLs to matched images.

    URL format: https://repository.library.brown.edu/iiif/image/bdr:597562/full/full/0/default.jpg
    """
    
    


def query_by_label(text_label, database):
    """
    Given a text label, clean label, and find images that match.
    """
    norm = normalize_phrase(text_label)
    list_of_paths = search_by_phrase(norm, database)
    
    # Generate pdf
    return list_of_paths
    

def query_by_image(file_path, database):
    """
    Given an image, segment label, extract texts, and find images that match.
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


def main():
    with open("databases/500_random_db.json", "rb") as f:
    # with open(DATABASE_FILENAME, "rb") as f:
        database = json.load(f)
        print(len(database))
    # text_label = "new mexico plants"
    # pprint.pprint(search_by_phrase(text_label, database))

if __name__ == "__main__":
    main()