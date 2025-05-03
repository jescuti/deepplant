from rapidfuzz import fuzz
from build_token_db import OCR_image
import os
import nltk
import cv2
from nltk.tokenize import word_tokenize
nltk.download('punkt_tab')

# print(ocr_image("./db_labels/Trifolium tridentatum_bdr_702466.jpg"))

# print(fuzz.partial_ratio(
#     "James Bennett", 
#     "oregon coll ann 1871 presented", score_cutoff=50))

# rootdir = "../image_download/herbarium_random_500"
# for dirpath, dirnames, files in os.walk(rootdir):
#     for file in files:
#         file_path = os.path.join(dirpath, file)
#         if os.path.isfile(file_path):
#             print(file_path)

file_path = "../image_download/samples/Pinus ponderosa_bdr_750802.jpg"
img = cv2.imread(file_path)
gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
print(OCR_image(gray_img))