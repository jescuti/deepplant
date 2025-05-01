import cv2; 

def segment_labels(img):
    # blur and threshold repeatedly to isolate label
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #black_pixels_mask = gray_img < 150
    #gray_img[black_pixels_mask] = 200
    cv2.imshow("Image", gray_img)
    cv2.waitKey(0)
    thresh = cv2.adaptiveThreshold(gray_img, 255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,11,2)
    cv2.imshow("Image", thresh)
    cv2.waitKey(0)

    blurred = cv2.GaussianBlur(thresh, (51, 51), 1000)
    cv2.imshow("Image", blurred)
    cv2.waitKey(0)
    ret, thresh2 = ret,thresh = cv2.threshold(blurred,230,255,0)
    cv2.imshow("Image", thresh2)
    cv2.waitKey(0)

    #find contours
    contours, hierarchy = cv2.findContours(thresh2, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    if hierarchy is not None:
        for i in range(len(contours)):
            #draws in red if an open shape is detected
            if hierarchy[0][i][2] == -1:
                cv2.drawContours(img, [contours[i]], -1, (0, 0, 255), 2)
    
    #determine which contours are labels
    label = 0
    for cnt in contours:
        x1,y1 = cnt[0][0]
        x, y, w, h = cv2.boundingRect(cnt)
            #only return contours of a certain size
        if w > 10 or h > 10:
            cv2.putText(img, 'Rectangle', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            label = cnt

    cv2.imshow("Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return label

