# from rapidfuzz import fuzz
# from build_token_db import OCR_image
# from ocr_cleaning import extract_phrases_from_text
# import os
# import nltk
# from tqdm import tqdm
# import cv2
# from nltk.tokenize import word_tokenize
# nltk.download('punkt_tab')

# print(ocr_image("./db_labels/Trifolium tridentatum_bdr_702466.jpg"))

# print(fuzz.partial_ratio(
#     "James Bennett", 
#     "oregon coll ann 1871 presented", score_cutoff=50))

### RUN OCR ON DIRECTORY IN IMAGE_DOWNLOAD
# ROOTDIR = "../image_download/sam"
# for file in tqdm(os.listdir(ROOTDIR)):
#     file_path = os.path.join(ROOTDIR, file)
#     if os.path.isfile(file_path):
#         print(file_path)
#         img = cv2.imread(file_path)
#         gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#         raw_text = OCR_image(gray_img)
#         print("raw text:", raw_text)
#         clean_phrases = extract_phrases_from_text(raw_text)
#         print("clean text:", clean_phrases)

# GENERATE PDF
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 5, txt="Hello, world!", ln=1, align="L")
pdf.image("./db_labels/Carex vesicaria_bdr_760491.jpg", x=pdf.get_x(), y=pdf.get_y(), h=40, w=200)
pdf.ln(50)
pdf.cell(200, 5, txt="Hello, world!", ln=1, align="L")
pdf.image("./db_labels/Echites difformis_bdr_755459.jpg", x=pdf.get_x(), y=pdf.get_y(), h=40, w=200)
pdf.ln(50)
pdf.cell(200, 5, txt="Hello, world!", ln=1, align="L")
pdf.image("./db_labels/Echites difformis_bdr_755459.jpg", x=pdf.get_x(), y=pdf.get_y(), h=40, w=200)
pdf.output("simple_pdf.pdf")