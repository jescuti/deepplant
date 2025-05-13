import os
import random
import shutil

# Define the source and destination directories
source_dir = '/content/drive/MyDrive/segmented_images'
destination_dir = '/content/drive/MyDrive/test_images'

def copy_random_100(source_dir, destination_dir):
    # Create destination directory if it doesn't exist
    os.makedirs(destination_dir, exist_ok=True)

    # Get a list of image files in the source directory
    image_files = [f for f in os.listdir(source_dir)
                if os.path.isfile(os.path.join(source_dir, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

    # Check if there are at least 100 images
    if len(image_files) < 100:
        raise ValueError("Not enough images in the source directory to select 100.")

    # Randomly select 100 images
    selected_images = random.sample(image_files, 100)

    # Copy the selected images to the destination directory
    for image in selected_images:
        src_path = os.path.join(source_dir, image)
        dst_path = os.path.join(destination_dir, image)
        shutil.copy2(src_path, dst_path)

    print("100 random images copied to 'test_images'.")