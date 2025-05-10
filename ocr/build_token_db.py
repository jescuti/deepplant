import os
from tqdm import tqdm
import cv2
import json
from ocr import run_clean_ocr


ROOTDIR = "../image_download/db_labels"  
DATABASE_FILENAME = os.path.join("databases", "db_labels.json")

def read_image_and_preprocess(file_path):
    image = cv2.imread(file_path)
    if image is None:
        return None
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    return gray_image


def main():
    # Populate a database of image path to text tokens and phrase
    label_db: dict[str, list[str]] = {}
    first_entry = True
    
    print(f"Writing to {DATABASE_FILENAME}...")
    
    with open(DATABASE_FILENAME, "w", encoding="utf-8", buffering=1) as f:
        f.write("{\n")

        # Recursively search all subdirectories for files       
        # If just one parent folder, use os.listdir
        for file in tqdm(os.listdir(ROOTDIR)):
            file_path = os.path.join(ROOTDIR, file)
        # for dirpath, _, files in os.walk(ROOTDIR):
        #     for file in tqdm(files):
        #         file_path = os.path.join(dirpath, file)
            if not (os.path.isfile(file_path) and file.endswith(('.jpg', '.jpeg', '.png'))):
                print(f"ERROR: Could not load image at {file_path!r}")
                continue

            img = read_image_and_preprocess(file_path)
            if img is None:
                continue
            
            # Run OCR
            phrases = run_clean_ocr(img)
            label_db[file] = phrases
            
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


if __name__ == "__main__":
    main()
