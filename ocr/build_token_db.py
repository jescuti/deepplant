import cv2
import os
import pytesseract
from pytesseract import Output
import PIL.Image
import pprint
import json
from matching.label_matcher import match_query_to_labels
from ocr_cleaning import clean_dict_tokens, extract_phrases_from_text


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

'''
create txt.file with file names: auto create links to bdr
match handwriting styles + printed labels
or PDF: segmented labels that match with a BPR link on it -> helpful

segmentation for stamp

frontend: text in label or picture of label

match exactly the strings; 

weighting matches: brown university herbarium; herb; herbarium; xex; flora of

OCR for herbaria in general around the world; skeletal/skeleton; harvard; smithsonian
'''

myconfig = r"--psm 6 --oem 3"
# images/Lolium arvense_bdr_819079.jpg
# images/Parnassia_bdr_398482.png
# images/Uraria lagopodioides_bdr_758039.png
# "images/Saxifraga biflora_bdr_853535.jpg"
# "images/Trifolium tridentatum_bdr_702466.jpg"
# "images/Mertensia alpina_bdr_754912.jpg"
# FILENAME = "preprocessing/images/Mertensia alpina_bdr_754912.jpg"

def draw_boxes(ocr_img, original_img) -> None:
    '''
    Draw green boxes around tesseract-detected text in the original image.

    Parameters
    ----------
    ocr_image
        The image to perform tesseract OCR on for bounding box boundaries.
    original_image
        The image to draw the boxes on

    Returns
    -------
    None
    '''
    data = pytesseract.image_to_data(ocr_img, config=myconfig, output_type=Output.DICT)
    print(data['text'])
    num_boxes = len(data['text'])
    for i in range(num_boxes):
        if float(data['conf'][i]) > 20:
            print("Char:", data['text'][i], " ; Conf:", data['conf'][i])
            (x, y, width, height) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            img = cv2.rectangle(original_img, (x,y), (x+width, y+height), (0,255,0), 2)

    cv2.imshow("img", original_img)
    cv2.waitKey(0)


def main():
    folder_path = "./images"
    
    # Database of image path to text tokens and phrase
    label_db = {}

    # Iterate through all test images
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if os.path.isfile(file_path):
            img = cv2.imread(file_path)
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Run tesseract for text extraction
            text = pytesseract.image_to_string(gray_img, config=myconfig)
            # print(text)
            # data = pytesseract.image_to_data(gray_img, config=myconfig, output_type=Output.DICT)
            # tokens, phrase = clean_dict_tokens(data['text'])
            # draw_boxes(gray_img, gray_img)

            # Build tokens database
            label_db[file_path] = extract_phrases_from_text(text)

    # pprint.pprint(label_db, indent=2)
    with open('label_phrases_db.json', 'w') as f:
        json.dump(label_db, f, indent=2)

if __name__ == "__main__":
    main()