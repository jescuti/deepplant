import os
import requests
import time
from urllib.parse import urlparse
from tqdm import tqdm

# URL that goes to the first 500 results of the collection
COLLECTION_URL = "https://repository.library.brown.edu/api/collections/bdr:nz9qn2kb/"
BASE_DIR = "bdr_by_collector"
os.makedirs(BASE_DIR, exist_ok = True)

def create_filename(name):
    return "".join(c if c.isalnum() or c in " ._-" else "_" for c in name).strip()

def fetch_json(url):
    try:
        response = requests.get(url, timeout = 10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"error fetching {url}: {e}")
        return None

def download_image(url, dest_path):
    try:
        r = requests.get(url, stream = True)
        r.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"failed to download {url}: {e}")
        return False

def get_collector(brief_data):
    # locate the collect name (at the bottom of the JSON result returned called "collector")
    if brief_data and "collector" in brief_data and brief_data["collector"]:
        return brief_data["collector"][0]
    return "No Collector"

def main():
    collection_data = fetch_json(COLLECTION_URL)
    if not collection_data:
        print("couldn't fetch collection data :/")
        return

    items = collection_data.get("items", {}).get("docs", [])
    print(f"Found {len(items)} items in collection.")

    # for item in tqdm(items, desc="Processing items"):
    #     # from the COLLECTION_URL JSON, each specimen has its own page
    #     # which is under "uri" or you can get that specimen's JSON with the 
    #     # "json_uri" -> so essentially this is going from the whole collection 
    #     # to that specific specimen's "page"
    #     json_uri = item.get("json_uri")
    #     if not json_uri:
    #         continue

    #     item_data = fetch_json(json_uri)
    #     if not item_data:
    #         continue

    #     pid = item_data.get("pid", "unknown").replace(":", "_")
    #     # once on that specimen's JSON page, the image can be downloaded from 
    #     # the link found under the key "primary_download_link"
    #     download_link = item_data.get("primary_download_link")
    #     if not download_link:
    #         print(f"no download link for {pid}")
    #         continue

    #     # get collector name (if there is one)
    #     brief_data = item_data.get("brief", {})
    #     collector = get_collector(brief_data)
        
    #     # create / add to a folder for the collector
    #     collector_folder = create_filename(collector)
    #     folder_path = os.path.join(BASE_DIR, collector_folder)
    #     os.makedirs(folder_path, exist_ok=True)

    #     # create filename w/ scientific name if available
    #     scientific_name = ""
    #     if "scientific name" in brief_data and brief_data["scientific name"]:
    #         scientific_name = brief_data["scientific name"][0].replace(" ", "_")
    #         filename = f"{scientific_name}_{pid}.jpg"
    #     else:
    #         filename = f"{pid}.jpg"
        
    #     filepath = os.path.join(folder_path, create_filename(filename))

    #     if os.path.exists(filepath):
    #         print(f"file already exists: {filepath}")
    #         continue 

    #     print(f"downloading {filename} to {collector_folder}/")
    #     success = download_image(download_link, filepath)
    #     if not success:
    #         print(f"retrying {filename}...")
    #         time.sleep(5)
    #         download_image(download_link, filepath)

if __name__ == "__main__":
    main()