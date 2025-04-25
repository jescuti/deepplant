import os
import requests
import re
import time
from tqdm import tqdm
from bs4 import BeautifulSoup

def create_filename(name):
    # create a valid filename
    return "".join(c if c.isalnum() or c in " ._-" else "_" for c in name).strip()

# image download it creating HTML, so the image needs to be
# selected from the HTML
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
        print(f"error parsing HTML: {e}")
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
            print(f"WARNING: downloaded file is empty: {filepath}")
            return False
        return True
    except Exception as e:
        print(f"error downloading image: {e}")
        return False

def fetch_and_download_images(batch_size = 100, base_dir = "herbarium_images"):
    """
    fetch herbarium images and download them to folders;
    that are organized by the collector's name for us to
    run the classification algorithms on later
    """
    # create base directory to store all the folders
    os.makedirs(base_dir, exist_ok = True)
    
    # tracking progress!
    start = 4401
    total_processed = 0
    total_errors = 0
    
    print("Starting herbarium image download!")
    
    while True:
        # construct API URL (with pagination by iterating the 
        # start + row values so we get more than 500 results, the API
        # return limit amount)
        api_url = (
            "https://repository.library.brown.edu/api/search/"
            "?q=rel_is_member_of_collection_ssim:bdr:nz9qn2kb"
            f"&start={start}&rows={batch_size}&wt=json"
        )
        
        # fetch batch of items (~100 images at a time)
        print(f"Fetching items {start} to {start+batch_size}...")
        try:
            response = requests.get(api_url).json()
            docs = response.get("response", {}).get("docs", [])
            
            if not docs:
                print("No more items to process!")
                break
                
            total_items = response["response"].get("numFound", 0)
            print(f"Found {len(docs)} items (total in collection: {total_items})")
            
            # process each item in the batch
            for item in tqdm(docs, desc=f"Processing batch starting at {start}"):
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
                
                # create folder for that collector
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
                
                # avoid overwhelming the server
                time.sleep(0.5)
            
            # next batch
            start += batch_size
            if start >= total_items:
                print("reached end of collection!")
                break
                
            # pause between batches
            time.sleep(1)
            
        except Exception as e:
            print(f"Error fetching batch: {e}")
            time.sleep(5) # wait b4 retrying
    
    # summary
    print(f"Download complete! Successfully processed {total_processed} images with {total_errors} errors.")
    return total_processed, total_errors

if __name__ == "__main__":
    fetch_and_download_images(batch_size = 100)