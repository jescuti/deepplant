import cv2; 

def segment_labels(filename):
    img = cv2.imread(filename)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(gray_img, 50, 255, 0)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    
    for cnt in contours:
        x1,y1 = cnt[0][0]
        cv2.putText(img, 'Rectangle', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        img = cv2.drawContours(img, [cnt], -1, (0,255,0), 3)

        #determine which is the rectangle we want
        label = cnt
    
    return label

