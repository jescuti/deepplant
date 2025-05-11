import argparse
import os
import time
from ocr import run_clean_ocr
from build_db import build_db
from query import query_by_image, query_by_label

# Arguments for build_db
LABEL_DIR         = "../image_download/db_labels"  
DATABASE_FILENAME = "./databases/db_labels.json"

def main():
    """
    DeepPlant OCR Pipeline.
    Central place to run different OCR-related tasks.

    Command line usage:
    - python3 main.py -t build_db
    - python3 main.py -t ocr -i ./images/label_1.jpg
    - python3 main.py -t query (--image ./images/label_1.jpg | --text "label name")

    Arguments:
    -t | --task   : Required. One of ['ocr', 'build_db', 'query']
    -i | --image  : Required for 'ocr'. Optional for 'query' if --text is provided.
    --text        : Required for 'query' if --image is not provided.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--task",
                        required=True,
                        choices=['ocr', 'build_db', 'query'],
                        help="Task to run: 'ocr', 'build_db', or 'query'")

    parser.add_argument("-i", "--image", help="Path to image to query")
    parser.add_argument("--text", help="Text string to query")

    args = parser.parse_args()

    # Argument validation
    if args.task == 'ocr':
        if not args.image:
            parser.error("--image is required for OCR task")

    elif args.task == 'query':
        if not args.image and not args.text:
            parser.error("For 'query' task, you must provide either --image or --text")
        if args.image and args.text:
            parser.error("For 'query' task, provide only one of --image or --text, not both")

    # Task execution logic
    # if ocr
    if args.task == 'ocr':
        # if specified path does not exist
        if not os.path.exists(args.image):
            print('The file path you specified: ' + args.image + ' does not exist. Try running something like: '
                  '\n python3 main.py -t ocr -i ./images/label_1.jpg')
            return
        # if path does exist, run OCR
        else:
            print(f'Running OCR on image: {args.image}')
            run_clean_ocr(args.image, True)
            print(f'Finished OCR')

    # if build database
    elif args.task == 'build_db':
        print(f'Building text database. Writing to {DATABASE_FILENAME}...')
        logic_start = time.time()
        num_images = build_db(LABEL_DIR, DATABASE_FILENAME)
        logic_end = time.time()
        print('Finished building text database. Average runtime per image out of ' 
              f'{num_images} images: {(logic_end - logic_start) / num_images:.5f}')
    
    # if query
    elif args.task == 'query':
        if args.image:
            # if specified path does not exist
            if not os.path.exists(args.image):
                print(f'The file path you specified: {args.image} does not exist. '
                      'Try running something like: python3 main.py -t ocr -i ./images/label_1.jpg')
                return
            # if path does exist, query image for those with similar labels
            else:
                print(f'Querying using image: {args.image}')
                query_start = time.time()
                num_images = query_by_image(args.image)
                query_end = time.time()
        else:
            print(f'Querying using text: {args.text}')
            query_start = time.time()
            num_images = query_by_label(args.text)
            query_end = time.time()
        print(f"Finished querying. Number of images found: {num_images}.")
        print(f"Average runtime over {num_images} images: "
              f"{query_end - query_start/num_images:.5f} seconds")

    # user didn't specify whether running ocr, building db, or querying
    else:
        print("You must specify what OCR task you are performing (either 'ocr', 'build_db' or 'query')"
              " for e.g. try running: \n python3 main.py -t ocr -i ./images/label_1.jpg")
        return


if __name__ == '__main__':
    main()
