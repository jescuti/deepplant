import label_finder
from skimage import io
import matplotlib.pyplot as plt
import cv2;

lobelia = io.imread('test-images/lobelia.jpg')
label = label_finder.segment_labels(lobelia)

erigeron = io.imread('test-images/erigeron.jpg')
label = label_finder.segment_labels(erigeron)

acer = io.imread('test-images/acer.jpg')
label = label_finder.segment_labels(acer)

lycopodium = io.imread('test-images/lycopodium.jpg')
label = label_finder.segment_labels(lycopodium)