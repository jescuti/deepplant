import os
from tqdm import tqdm
import json
import time
from ocr import run_clean_ocr

ROOTDIR           = "../image_download/db_labels"  
DATABASE_FILENAME = "./databases/db_labels.json"

def build_db():
    # Populate a database of image path to text tokens and phrase
    label_db: dict[str, list[str]] = {}
    first_entry = True
    
    print(f"Writing to {DATABASE_FILENAME}...")
    logic_start = time.time()
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
            
            # Run OCR
            phrases = run_clean_ocr(file_path)
            if phrases is None:
                continue
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
    logic_end = time.time()
    print("Finished building text database. Average runtime per image out of " 
        f"{len(label_db)} images: {(logic_end - logic_start)/len(label_db):.5f}")
