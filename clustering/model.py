import fiftyone as fo
import fiftyone.brain as fob
from fiftyone import ViewField as F
import os
from PIL import Image
import clip # pip install git+https://github.com/openai/CLIP.git
import torch
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import numpy as np

# takes in a directory to the segmented labels
# returns clustered dataset
# RUN ON GPU
def cluster_dataset(segmented_labels_dir):
   image_files = [os.path.join(segmented_labels_dir, f) for f in os.listdir(segmented_labels_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
   dataset = fo.Dataset.from_images(image_files, name='labels_test', overwrite=True)
   session = fo.launch_app(dataset)
   # compute features
   res = fob.compute_visualization(
        dataset,
        model="clip-vit-base32-torch",
        embeddings="clip_embeddings",
        method="umap",
        brain_key="clip_vis",
        batch_size=10
    )
   dataset.set_values("clip_umap", res.current_points)
   return dataset

# load in a dataset from a file
def load_clustered_model(model_dir):
   name = "my-dataset"

   # Create the dataset
   dataset = fo.Dataset.from_dir(
      dataset_dir=model_dir,
      dataset_type=fo.types.FiftyOneDataset,
      name=name,
   )

   print(dataset)

   return dataset

# takes in a path to the search image and dataset, as well as k, the number of results to return
# returns top k similar images to the search image, as well as their similarity scores
def query_image(image_path, dataset, k):
   model_name = "ViT-B/32"
   device = "cuda" if torch.cuda.is_available() else "cpu"

   #get image embeddings
   model, preprocess = clip.load(model_name, device=device)
   image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
   with torch.no_grad():
      image_embedding = model.encode_image(image).cpu().numpy()

   #get dataset embeddings
   dataset_embeddings = dataset.values("clip_embeddings")
   sample_ids = dataset.values("id")

   #calculate similarity
   similarity_scores = cosine_similarity(image_embedding, np.array(dataset_embeddings))[0]

   #get top k most similar images
   sorted_indices = np.argsort(similarity_scores)[::-1]
   top_k_indices = sorted_indices[:k]

   top_similar_images = []
   top_similarity_scores = []
   for i in top_k_indices:
      sample = dataset[sample_ids[i]]
      img = Image.open(sample.filepath)
      top_similar_images.append(img)
      top_similarity_scores.append(similarity_scores[i])

   return top_similar_images, similarity_scores
