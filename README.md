# DeepPlant

## Project Description
Our project's main goal is to assist the Brown Herbarium in reading and transcribing labels (typed and handwritten) for plant specimens in Rhode Island and New England collections dated from the late 1800s. Our client, Professor Kartzinel, has an extensive collection of images of preserved plant specimens with various labels about the collector, date, plant type, etc. Professor Kartzinel described to us that the herbarium has encountered issues understanding what the handwriting says, but over the years have learned to decipher some of the lettering. In an ideal world, she would have a software that could categorize the images into clusters with similar handwriting or machine-printed labels. Essentially there are two tasks: 

1. For machine pre-printed labels: Find images with almost exact similar labels; the colors could be different, but contents would be the same
2. For hand-written labels: Match a segment of a label, typically a signature, with images with similar handwriting or containing that signature

## Running the Project
In one terminal:
[1] `cd frontend`
[2] `npm install`
[3] `npm start`

In another terminal:
[1] `cd server`
[2] `python server.py`

## Data
After scraping data by calling the API for the Brown Digital Repository, we successfully downloaded over 6,000 images totaling nearly 9.5GB. Due to GitHub's size constraints, these images couldn't be uploaded directly to the repository. However, they have been made available for download on Google Drive: 

[1] [**Segmented Images**](https://drive.google.com/drive/folders/1hV1xIqXvEzKdtaawIy-H4K-9SbmWZwoy?usp=drive_link)

[2] [**Herbarium Plant Specimen Images**](https://drive.google.com/drive/folders/1AemR3uG3RSOLiDwFROlHL0qzPpQfJSvL?usp=drive_link)

## Architecture Overview
<img width="585" alt="image" src="https://github.com/user-attachments/assets/a1f2ceb2-dd66-4e83-986b-5ae57d37c49c" />

**Pipeline Steps**

[1] Images were webscraped using the `webscraping/download_all_images`

[2] Images were preprocessed & segmented using `preprocessing/segmentation.ipynb`

[3] Text-inputs are processed using `ocr/query.py` and the OCR database was created using `ocr/build_db.py`

[4] Image-inputs are processed by comparing against clusters which are found in `clustering/model.py`

[5] Front-End was developed which can be found in `frontend/src`

[6] The front and back end were connected with a Flask server found in `server/server.py`


