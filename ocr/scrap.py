from rapidfuzz import fuzz
from build_token_db import read_image_and_preprocess
from ocr_cleaning import extract_phrases_from_text
from ocr import _raw_ocr, run_clean_ocr
import os
from tqdm import tqdm
import cv2

def enhance_for_ocr(gray):
    # Compute metrics:
    c = (gray.max() - gray.min())/(gray.max()+1e-5)
    s = cv2.Laplacian(gray, cv2.CV_64F).var()

    out = gray.copy()
    # 2a) boost contrast if too low
    if c < 0.3:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        out = clahe.apply(out)

    # 2b) sharpen if too soft
    if s < 50:
        # simple unsharp mask
        blur = cv2.GaussianBlur(out, (0,0), sigmaX=3)
        out = cv2.addWeighted(out, 1.5, blur, -0.5, 0)

    # 2c) denoise (optional)
    out = cv2.fastNlMeansDenoising(out, None, h=10)

    # 2d) binarize
    _, out = cv2.threshold(out, 0, 255,
                          cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return out

#  deepplant/image_download/db_labels/bdr_755459_1.jpg
#  deepplant/image_download/db_labels/Lolium arvense_bdr_819079 copy.jpg
#  Onosmodium molle_bdr_747661.png
# Mertensia alpina_bdr_754912.jpg
# gray = read_image_and_preprocess("../image_download/db_labels/Onosmodium molle_bdr_747661.png")
# gray = read_image_and_preprocess("../image_download/db_labels/Lolium arvense_bdr_819079 copy.jpg")
# gray = read_image_and_preprocess("../image_download/db_labels/Mertensia alpina_bdr_754912.jpg")
# img = cv2.GaussianBlur(img, (3,3), 0)
# # Define alpha (contrast) and beta (brightness) values
# alpha = 0.5 # Contrast control (1.0 means no change)
# beta = 0   # Brightness control (0 means no change)

# Adjust the contrast and brightness
# img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

# ret, img = cv2.threshold(img, 130, 255, 0)

# img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
#             cv2.THRESH_BINARY,11,2)
# (T, img) = cv2.threshold(img, 0, 255,
# 	cv2.THRESH_BINARY | cv2.THRESH_OTSU)
# img = cv2.adaptiveThreshold(img, 255,
# 	cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 25, 11)
# check if enhancement is needed
# contrast = (gray.max() - gray.min())/(gray.max()+1e-5)
# sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

# if contrast < 0.3 or sharpness < 50:
#     proc = enhance_for_ocr(gray)
# else:
#     proc = gray
# # img = enhance_for_ocr(img)

# cv2.imshow("preprocessing", proc)
# cv2.waitKey(0)
# raw = _raw_ocr(proc)
# print("raw:", raw)
# print("clean:", extract_phrases_from_text(raw))

# print(fuzz.partial_ratio(
#     "James Bennett", 
#     "oregon coll ann 1871 presented", score_cutoff=50))



### RUN OCR ON DIRECTORY IN IMAGE_DOWNLOAD
print("WITH ADAPTIVE THRESHOLD")
ROOTDIR = "../image_download/db_labels"
for file in os.listdir(ROOTDIR):
    file_path = os.path.join(ROOTDIR, file)
    if os.path.isfile(file_path) and "DS_Store" not in file_path:
        print(file_path)
        img = cv2.imread(file_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # NAH: gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        
        # contrast = (gray.max() - gray.min())/(gray.max()+1e-5)
        # sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

        # if contrast < 0.3 or sharpness < 50:
        #     proc = enhance_for_ocr(gray)
        # else:
        #     proc = gray
        
        # thresh = cv2.adaptiveThreshold(gray_img, 255,
	    #     cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 25, 11)
        raw_text = _raw_ocr(gray)
        print("raw text:", raw_text)
        clean_phrases = extract_phrases_from_text(raw_text)
        print()
        print("clean text:", clean_phrases)

# GENERATE PDF
# from fpdf import FPDF

# pdf = FPDF()
# pdf.add_page()
# pdf.set_font("Arial", size=12, style="U")
# pdf.set_text_color(0, 0, 255)

# for _ in range(3):
#     pdf.cell(200, 5, txt="https://repository.library.brown.edu/iiif/image/bdr:739461/full/full/0/default.jpg", ln=1, align="L", \
#             link="https://repository.library.brown.edu/iiif/image/bdr:739461/full/full/0/default.jpg")
#     pdf.image("./test_labels/Gerardia divaricata_bdr_742487.jpg", x=pdf.get_x(), y=pdf.get_y(), h=40, w=200)
#     pdf.ln(50)


# pdf.output("simple_pdf.pdf")


"""
BUILD TOKEN DB
# Recursively search all subdirectories for files
# If just one parent folder, use os.listdir
for file in tqdm(os.listdir(ROOTDIR)):
    file_path = os.path.join(ROOTDIR, file)


with open(DATABASE_FILENAME, "w", encoding="utf-8", buffering=1) as f:
    f.write("{\n")
    
    for dirpath, _, files in os.walk(ROOTDIR):
        for file in tqdm(files):
            file_path = os.path.join(dirpath, file)
            if not (os.path.isfile(file_path) and "DS_Store" not in file_path):
                continue

            img = read_image_and_preprocess(file_path)
            
            # Run OCR
            phrases = run_clean_ocr(img)
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
print(f"Finished writing to {DATABASE_FILENAME}.")


for dirpath, _, files in tqdm(os.walk(ROOTDIR)):
        for file in files:
            file_path = os.path.join(dirpath, file)
            if not (os.path.isfile(file_path) and "DS_Store" not in file_path):
                continue

            img = read_image_and_preprocess(file_path)
            
            # Run OCR
            phrases = run_clean_ocr(img)
            label_db[file_path] = phrases
            
    with open(DATABASE_FILENAME, "w", encoding="utf-8", buffering=1) as f:
        f.write(json.dumps(f))
        
    print(f"Finished writing to {DATABASE_FILENAME}.")
"""