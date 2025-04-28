import cv2
import matplotlib.pyplot as plt

def segment_labels(filename):
    # Load image
    img = cv2.imread(filename)
    
    # Convert BGR to RGB for correct color display with matplotlib
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Convert to grayscale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Threshold the grayscale image
    ret, thresh = cv2.threshold(gray_img, 50, 255, 0)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Draw contours on the RGB image for visualization
    cv2.drawContours(img_rgb, contours, -1, (0, 255, 0), 3)
    
    # Plot using matplotlib
    plt.figure(figsize=(5, 5))
    plt.imshow(img_rgb)
    plt.axis('off')  # Hide axes
    plt.title('Contours Overlay')
    plt.show()

FILENAME = "../image_download/herbarium_images/C. C. Parry/Pyrola asarifolia_bdr_398017.jpg"

if __name__ == "__main__":
    segment_labels(FILENAME)

# for cnt in contours:
#     x1,y1 = cnt[0][0]
#     cv2.putText(img, 'Rectangle', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
#     img = cv2.drawContours(img, [cnt], -1, (0,255,0), 3)

#     # Determine which is the rectangle we want
#     label = cnt
#
# return label