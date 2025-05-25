import sys
sys.path.append('../clustering')
sys.path.append('../ocr')
import model
import query as querySearch
import json
import re
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from io import BytesIO
import base64
from PIL import Image
import model  
import tempfile
import os
import requests
import numpy as np
import urllib.parse
from flask import send_file
import generate_output
import uuid
from flask_cors import cross_origin
import base64

app = Flask(__name__)
CORS(app, 
     resources={r"/*": {"origins": "*"}}, 
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
     methods=["GET", "POST", "OPTIONS", "HEAD", "DELETE"])

clustered_dataset = model.load_clustered_model("../clustering/datasets")

generated_pdfs = {}

PDF_DIRECTORY = "generated_pdfs"
if not os.path.exists(PDF_DIRECTORY):
    os.makedirs(PDF_DIRECTORY)

BDR_API_BASE = "https://repository.library.brown.edu/api/search/"

def fetch_catalog_metadata(bdr_code):
    """Fetch catalog metadata using the direct BDR API endpoint for the item"""
    metadata = {"dwc_catalog_number_ssi": f"PBRU {bdr_code}"}
    
    try:
        # API endpoint for the item
        api_url = f"https://repository.library.brown.edu/api/items/bdr:{bdr_code}/"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            
            if "dwc_catalog_number_ssi" in data:
                metadata["dwc_catalog_number_ssi"] = data["dwc_catalog_number_ssi"]
            
            # scientific name
            if "dwc_accepted_name_usage_ssi" in data:
                metadata["dwc_accepted_name_usage_ssi"] = data["dwc_accepted_name_usage_ssi"]
            elif "dwc_scientific_name_ssi" in data:
                scientific_name = data["dwc_scientific_name_ssi"]
                if "dwc_scientific_name_authorship_ssi" in data:
                    scientific_name += " " + data["dwc_scientific_name_authorship_ssi"]
                metadata["dwc_accepted_name_usage_ssi"] = scientific_name
            
            # get year
            if "dwc_year_ssi" in data:
                metadata["dwc_year_ssi"] = data["dwc_year_ssi"]
            
            # get collector info
            if "dwc_recorded_by_ssi" in data:
                metadata["dwc_recorded_by_ssi"] = data["dwc_recorded_by_ssi"]
            
            if data.get("iiif_resource_bsi", False):
                metadata["iiif_url"] = f"https://repository.library.brown.edu/iiif/image/bdr:{bdr_code}/info.json"
    
    except Exception as e:
        print(f"Error fetching metadata for BDR:{bdr_code} from API: {e}")

    if "dwc_accepted_name_usage_ssi" not in metadata:
        metadata["dwc_accepted_name_usage_ssi"] = f"Specimen {bdr_code}"
        
    return metadata

def generate_and_save_pdf(matched_img_paths, similarity_scores, search_type, image_dir=""):
    """Generate PDF and return the filename and URL"""
    pdf_filename = f"search_results_{uuid.uuid4()}.pdf"
    pdf_path = os.path.join(PDF_DIRECTORY, pdf_filename)
    
    generate_output.generate_pdf(matched_img_paths, similarity_scores, pdf_path, image_dir)

    with open(pdf_path, "rb") as pdf_file:
        encoded_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
    
    return pdf_path, encoded_pdf
    
@app.route("/api/search/text", methods=["POST", "OPTIONS"])
def search_text():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({'error': 'No query provided'}), 400
        
        query = data["query"].strip().lower()

        # load the token DB
        with open("../ocr/token_db_6719.json", "r") as f:
            label_db = json.load(f)

        # search text
        matched_paths, similarity_scores = querySearch.search_text_phrase(query, label_db)

        results = []
        image_directory = "segmented_images/"
        
        # full paths for PDF gen
        full_matched_paths = []
        normalized_similarity_scores = []
        
        for path, score in zip(matched_paths, similarity_scores):
            try:
                full_path = os.path.join(image_directory, path)
                full_matched_paths.append(full_path)
                normalized_similarity_scores.append(score / 100)
                
                if not os.path.exists(full_path):
                    print(f"File not found: {full_path}")
                    continue 
                
                with Image.open(full_path) as img:
                    buffered = BytesIO()
                    img.save(buffered, format = "JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()

                filename = os.path.basename(full_path)
                bdr_match = re.search(r"(\d+)", filename)
                bdr_code = bdr_match.group(1) if bdr_match else "000000"
                website_url = f"https://repository.library.brown.edu/studio/item/bdr:{bdr_code}/"

                metadata = fetch_catalog_metadata(bdr_code)
                if not metadata.get("dwc_catalog_number_ssi"):
                    metadata["dwc_catalog_number_ssi"] = f"PBRU {bdr_code}"
                
                if not metadata.get("dwc_accepted_name_usage_ssi"):
                    name_parts = filename.split("_")
                    if len(name_parts) >= 2:
                        metadata["dwc_accepted_name_usage_ssi"] = " ".join(name_parts[1:]).replace(".jpg", "").title()
                    else:
                        metadata["dwc_accepted_name_usage_ssi"] = filename.replace(".jpg", "").title()

                results.append({
                    "image": img_str,
                    "filepath": full_path,
                    "websiteUrl": website_url,
                    "similarity": score / 100,
                    "metadata": metadata
                })

            except Exception as img_err:
                print(f"Error processing {full_path}: {img_err}")


        pdf_path, pdf_base64 = generate_and_save_pdf(
            full_matched_paths,
            normalized_similarity_scores,
            "text",
            image_directory
        )

        return jsonify({
            "results": results,
            "pdf" : pdf_base64
        })

    except Exception as e:
        print("Text search error:", e)
        return jsonify({'error': str(e)}), 500
    
@app.route("/api/search", methods = ["POST"])
def search():
    try:
        # get uploaded image
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        image_file = request.files['image']
        k = int(request.form.get('k', 100))

        # save img temporarily
        with tempfile.NamedTemporaryFile(delete = False, suffix = ".jpg") as tmp:
            image_path = tmp.name
            image_file.save(image_path)

        # query top k images
        similar_images, similarity_scores = model.query_image(image_path, clustered_dataset, k)

        results = []
        sample_ids = clustered_dataset.values("id")
        sorted_indices = np.argsort(similarity_scores)[::-1][:k]

        top_samples = [clustered_dataset[sample_ids[i]] for i in sorted_indices]
        top_scores = similarity_scores[sorted_indices]
        
        # filepaths for PDF generation
        matched_img_paths = []

        for i, (sample, sim_score) in enumerate(zip(top_samples, top_scores)):
            filepath = sample.filepath if hasattr(sample, "filepath") else "/unknown.jpg"
            filename = os.path.basename(filepath)
            matched_img_paths.append(filepath)

            # convert img
            buffered = BytesIO()
            similar_images[i].save(buffered, format = "JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # extract bdr code
            code_match = re.search(r"(\d+)", filename)
            bdr_code = code_match.group(1) if code_match else "000000"
            website_url = f"https://repository.library.brown.edu/studio/item/bdr:{bdr_code}/"

            metadata = fetch_catalog_metadata(bdr_code)
            if not metadata.get("dwc_catalog_number_ssi"):
                metadata["dwc_catalog_number_ssi"] = f"PBRU {bdr_code}"

            if not metadata.get("dwc_accepted_name_usage_ssi"):
                name_parts = filename.split("_")
                if len(name_parts) >= 2:
                    metadata["dwc_accepted_name_usage_ssi"] = " ".join(name_parts[1:]).replace(".jpg", "").title()
                else:
                    metadata["dwc_accepted_name_usage_ssi"] = filename.replace(".jpg", "").title()

            results.append({
                "image": img_str,
                "similarity": float(sim_score),
                "filepath": filepath,
                "websiteUrl": website_url,
                "metadata": metadata,
            })

        os.remove(image_path)

        pdf_filename, pdf = generate_and_save_pdf(
            matched_img_paths,
            [float(score) for score in top_scores], 
            "image"
        )

        # print(pdf); 

        return jsonify({
            "results": results,
            "pdf": pdf,
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 5000)