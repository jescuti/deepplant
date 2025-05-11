import os
from tqdm import tqdm
import json
import time
from ocr import run_clean_ocr

def build_db(image_dir: str, db_filename: str) -> None:
    """
    Build a text database as a dictionary and stream to a JSON file.

    Parameters
    ----------
    image_dir : str
        Path to the label image folder
    db_filename : str
        Name of the JSON file to write the database to

    Returns
    -------
    None
    """
    first_entry = True  # marker for json formatting
    num_images = len(os.listdir(image_dir))
    
    print(f"Writing to {db_filename}...")
    logic_start = time.time()

    with open(db_filename, "w", encoding="utf-8", buffering=1) as f:
        f.write("{\n")

        # Recursively search all subdirectories for files       
        # If just one parent folder, use os.listdir
        for file in tqdm(os.listdir(image_dir)):
            file_path = os.path.join(image_dir, file)
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
            
            # Stream database pair to a JSON file
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
        f"{num_images} images: {(logic_end - logic_start)/num_images:.5f}")
