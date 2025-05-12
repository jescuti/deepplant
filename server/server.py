import sys
sys.path.append('../clustering')
import model
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from io import BytesIO
import base64
from PIL import Image
import model  
import tempfile
import os

app = Flask(__name__)
CORS(app)  

clustered_dataset = model.load_clustered_model("../clustering/datasets")

@app.route("/api/search", methods = ["POST"])
def search():
    try:
        # get uploaded image
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        image_file = request.files['image']
        k = int(request.form.get('k', 100))

        # save img temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            image_path = tmp.name
            image_file.save(image_path)

        # query top k images
        similar_images, similarity_scores = model.query_image(image_path, clustered_dataset, k)

        BDR_CODE_PATTERN = r"bdr[0-9]{6,}"

        results = []
        BDR_CODE_PATTERN = r"bdr[0-9]{6,}"

        for sim_img, sim_score, sample in zip(similar_images, similarity_scores, clustered_dataset):
            # convert img
            buffered = BytesIO()
            sim_img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            # get filepath
            filepath = sample.filepath if hasattr(sample, "filepath") else "unknown.jpg"
            
            # extract bdr code
            code_match = re.search(BDR_CODE_PATTERN, filepath)
            bdr_code = code_match.group(0).replace("bdr", "") if code_match else "000000"
            website_url = f"https://repository.library.brown.edu/studio/item/bdr:{bdr_code}/"

            results.append({
                "image": img_str,
                "similarity": float(sim_score),
                "filepath": filepath,
                "websiteUrl": website_url
            })

        os.remove(image_path)

        return jsonify({"results": results})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
