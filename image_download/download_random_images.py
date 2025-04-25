import os
import requests
import re
import time
import random
from tqdm import tqdm
from bs4 import BeautifulSoup

def create_filename(name):
    # create a valid filename
    return "".join(c if c.isalnum() or c in " ._-" else "_" for c in name).strip()

def extract_image_url_from_html(html_content):
    """
    extract the actual image URL from the HTML content
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        # IIIF => web address with the image, metadata, 
        # and the image "web viewer"
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string and 'tileSources' in script.string:
                # extract URL using regex
                match = re.search(r'"(https://repository\.library\.brown\.edu/iiif/image/bdr:[^/]+/info\.json)"', script.string)
                if match:
                    iiif_info_url = match.group(1)
                    # convert info.json URL to full image URL
                    return iiif_info_url.replace('/info.json', '/full/full/0/default.jpg')
        return None
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return None

def download_image(url, filepath):
    """
    download an image from the URL and save to filepath
    """
    try:
        response = requests.get(url, stream = True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)
                
        if os.path.getsize(filepath) == 0:
            print(f"WARNING: Downloaded file is empty: {filepath}")
            return False
        return True
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False

def get_total_item_count():
    """
    get the total number of items in the collection
    """
    api_url = (
        "https://repository.library.brown.edu/api/search/"
        "?q=rel_is_member_of_collection_ssim:bdr:nz9qn2kb"
        "&rows=1&wt=json"
    )
    try:
        response = requests.get(api_url).json()
        return response.get("response", {}).get("numFound", 0)
    except Exception as e:
        print(f"Error getting total item count: {e}")
        return 0

def fetch_random_sample(sample_size = 100, min_index = 4401, base_dir = "herbarium_images"):
    """
    fetch a random sample of herbarium images 
    and save them to folders

    starts at 4,401 because we already downloaded all 
    the images before that #
    """
    os.makedirs(base_dir, exist_ok = True)
    
    total_items = get_total_item_count()
    if total_items == 0:
        print("ERROR: couldn't determine the total number of items in the collection.")
        return 0, 0
    
    print(f"collection has {total_items} TOTAL items")
    
    # calculate available range for random sampling
    available_range = total_items - min_index
    if available_range <= 0:
        print("no more items available for sampling")
        return 0, 0
    
    # generate random indices
    if sample_size > available_range:
        print(f"Requested sample size {sample_size} exceeds available items {available_range}.")
        sample_size = available_range
    
    random_indices = random.sample(range(min_index, total_items), sample_size)
    
    total_processed = 0
    total_errors = 0
    
    # process each random index
    for index in tqdm(random_indices, desc = "Processing random samples"):
        # fetch single item at the random index
        api_url = (
            "https://repository.library.brown.edu/api/search/"
            "?q=rel_is_member_of_collection_ssim:bdr:nz9qn2kb"
            f"&start={index}&rows=1&wt=json"
        )
        
        try:
            response = requests.get(api_url).json()
            docs = response.get("response", {}).get("docs", [])
            
            if not docs:
                print(f"no item found at INDEX: {index}")
                continue
                
            # process item
            item = docs[0]
            pid = item.get("pid")
            if not pid:
                continue
            
            # get collector name / unknown if not available
            collector = item.get("dwc_recorded_by_ssi", "Unknown_Collector")
            collector = create_filename(collector)
            
            # scientific name for image name, if available
            scientific_name = item.get("dwc_scientific_name_ssi", "")
            scientific_name = create_filename(scientific_name) if scientific_name else ""
            
            # make title for file name
            title = item.get("primary_title", "Untitled")
            title = create_filename(title)
            
            # ceate folder for that collector
            collector_dir = os.path.join(base_dir, collector)
            os.makedirs(collector_dir, exist_ok = True)
            
            # make the image filename
            if scientific_name:
                filename = f"{scientific_name}_{pid.replace(':', '_')}.jpg"
            else:
                filename = f"{title}_{pid.replace(':', '_')}.jpg"
            
            filepath = os.path.join(collector_dir, filename)
            
            # SKIP if file exists
            if os.path.exists(filepath):
                print(f"File already exists: {filepath}")
                continue
            
            # create URL to open the image view => then, fetch the HTML
            viewer_url = f"https://repository.library.brown.edu/viewers/image/zoom/{pid}"
            try:
                print(f"Fetching HTML from {viewer_url}")
                html_response = requests.get(viewer_url)
                html_response.raise_for_status()
                
                # extract image URL from HTML
                image_url = extract_image_url_from_html(html_response.text)
                if not image_url:
                    # direct IIIF URL
                    image_url = f"https://repository.library.brown.edu/iiif/image/{pid}/full/full/0/default.jpg"
                    print(f"Using alternative URL: {image_url}")
                
                # download actual image as JPG
                if download_image(image_url, filepath):
                    print(f"Successfully downloaded {filename} to {collector_dir}")
                    total_processed += 1
                else:
                    print(f"Failed to download image for {pid}")
                    total_errors += 1
                    
            except Exception as e:
                print(f"Error processing {pid}: {e}")
                total_errors += 1
            
            # don't overwhelm server
            time.sleep(0.5)
                
        except Exception as e:
            print(f"Error fetching item at index {index}: {e}")
            total_errors += 1
            time.sleep(5)
    
    print(f"Successfully processed {total_processed} images with ERRORS: {total_errors}")
    return total_processed, total_errors

if __name__ == "__main__":
    # download 500 random samples from the remaining items (after index 4400)
    fetch_random_sample(sample_size = 500, min_index = 4401, base_dir = "herbarium_images")
