from rapidfuzz import fuzz
from build_token_db import ocr_image
import os

# print(ocr_image("./db_labels/Trifolium tridentatum_bdr_702466.jpg"))

# print(fuzz.partial_ratio(
#     "James Bennett", 
#     "oregon coll ann 1871 presented", score_cutoff=50))
rootdir = "../image_download/herbarium_random_500"
for dirpath, dirnames, files in os.walk(rootdir):
    for file in files:
        file_path = os.path.join(dirpath, file)
        if os.path.isfile(file_path):
            print(file_path)