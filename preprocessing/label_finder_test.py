import label_finder
from skimage import io
import matplotlib.pyplot as plt
import cv2
import torch
import torchvision
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry, SamPredictor

sam_checkpoint = "sam_vit_h_4b8939.pth"
model_type = "vit_h"
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

print("Setting up SAM!")
sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)

print("Setting up automatic mask generation!")
mask_generator = SamAutomaticMaskGenerator(
    model=sam,
    points_per_side=32,
    pred_iou_thresh=0.86,
    stability_score_offset=0.9,
    crop_n_layers=1,
    crop_n_points_downscale_factor=2,
    min_mask_region_area=100
    )

lobelia = cv2.imread('test-images/lobelia.jpg')
label = label_finder.segment_labels_sam(lobelia, mask_generator)

erigeron = cv2.imread('test-images/erigeron.jpg')
label = label_finder.segment_labels_sam(erigeron, mask_generator)

acer = cv2.imread('test-images/acer.jpg')
label = label_finder.segment_labels_sam(acer, mask_generator)

lycopodium = cv2.imread('test-images/lycopodium.jpg')
label = label_finder.segment_labels_sam(lycopodium, mask_generator)