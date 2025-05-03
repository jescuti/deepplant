import cv2

def draw_boxes(original_img, data) -> None:
    '''
    Draw green boxes around detected text in the original image 
        based on tesseract DICT data.

    Parameters
    ----------
    original_img
        The image to draw the boxes on, assumed to have been read in by cv2.imread()
    data : pytesseract.Output.DICT
        The output of running pytesseract.image_to_data()

    Returns
    -------
    None
    '''
    # data = pytesseract.image_to_data(ocr_img, config=myconfig, output_type=Output.DICT)

    num_boxes = len(data['text'])
    for i in range(num_boxes):
        if float(data['conf'][i]) > 20:
            print("Char:", data['text'][i], " ; Conf:", data['conf'][i])
            (x, y, width, height) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            original_img = cv2.rectangle(original_img, (x,y), (x+width, y+height), (0,255,0), 2)

    cv2.imshow("img", original_img)
    cv2.waitKey(0)