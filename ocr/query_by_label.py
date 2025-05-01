# given text label, clean label, find images that match

import json
import pprint
from ocr_cleaning import normalize_phrase
from build_token_db import ocr_image
from label_matcher import search_by_phrase


text_label = "James Bennett"

with open("label_phrases_db.json", "rb") as f:
    database = json.load(f)

norm = normalize_phrase(text_label)
output = search_by_phrase(text_label, database)
pprint.pprint(output)
    