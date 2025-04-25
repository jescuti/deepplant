# import os
# import requests

# def fetch_and_download_images(batch_size=100):
#     start = 0
#     while True:
#         api_url = (
#             "https://repository.library.brown.edu/api/search/"
#             "?q=rel_is_member_of_collection_ssim:bdr:nz9qn2kb"
#             f"&start={start}&rows={batch_size}&wt=json"
#         )
#         response = requests.get(api_url).json()
#         docs = response.get("response", {}).get("docs", [])
#         if not docs:
#             break

#         for item in docs:
#             pid = item.get("pid")
#             collector = item.get("dwc_recorded_by_ssi", "Unknown_Collector").replace("/", "_").replace(" ", "_")
#             title = item.get("primary_title", "Untitled").replace("/", "_").replace(" ", "_")

#             # Construct image viewer URL
#             image_url = f"https://repository.library.brown.edu/viewers/image/zoom/{pid}"

#             # Prepare directory and filepath
#             os.makedirs(collector, exist_ok=True)
#             file_path = os.path.join(collector, f"{title}_{pid.replace(':', '_')}.html")

#             # Save the viewer page URL as an .html link file
#             with open(file_path, 'w') as f:
#                 f.write(f'<meta http-equiv="refresh" content="0; url={image_url}">')

#             print(f"Saved redirect file for {title} to {file_path}")

#         start += batch_size
#         if start >= response["response"].get("numFound", 0):
#             break



import os
import requests
import re
import time
from tqdm import tqdm
from bs4 import BeautifulSoup

def create_filename(name):
    # Create a valid filename; replacing invalid characters with underscores
    return "".join(c if c.isalnum() or c in " ._-" else "_" for c in name).strip()

def extract_image_url_from_html(html_content):
    """
    Extract the actual image URL from the HTML content
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        # Look for the IIIF URL in the script tag
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string and 'tileSources' in script.string:
                # Extract URL using regex
                match = re.search(r'"(https://repository\.library\.brown\.edu/iiif/image/bdr:[^/]+/info\.json)"', script.string)
                if match:
                    iiif_info_url = match.group(1)
                    # Convert info.json URL to full image URL
                    return iiif_info_url.replace('/info.json', '/full/full/0/default.jpg')
        return None
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return None

def download_image(url, filepath):
    """
    Download an image from the URL and save to filepath
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)
                
        if os.path.getsize(filepath) == 0:
            print(f"Warning: Downloaded file is empty: {filepath}")
            return False
        return True
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False

def fetch_and_download_images(batch_size=100, base_dir="herbarium_images"):
    """
    Fetch herbarium images and download them to organized folders
    """
    # Create base directory
    os.makedirs(base_dir, exist_ok=True)
    
    # Keep track of progress
    start = 0
    total_processed = 0
    total_errors = 0
    
    print("Starting herbarium image download...")
    
    while True:
        # Construct API URL with pagination
        api_url = (
            "https://repository.library.brown.edu/api/search/"
            "?q=rel_is_member_of_collection_ssim:bdr:nz9qn2kb"
            f"&start={start}&rows={batch_size}&wt=json"
        )
        
        # Fetch batch of items
        print(f"Fetching items {start} to {start+batch_size}...")
        try:
            response = requests.get(api_url).json()
            docs = response.get("response", {}).get("docs", [])
            
            if not docs:
                print("No more items to process.")
                break
                
            total_items = response["response"].get("numFound", 0)
            print(f"Found {len(docs)} items (total in collection: {total_items})")
            
            # Process each item in the batch
            for item in tqdm(docs, desc=f"Processing batch starting at {start}"):
                pid = item.get("pid")
                if not pid:
                    continue
                
                # Get collector name, use default if not available
                collector = item.get("dwc_recorded_by_ssi", "Unknown_Collector")
                collector = create_filename(collector)
                
                # Get scientific name if available
                scientific_name = item.get("dwc_scientific_name_ssi", "")
                scientific_name = create_filename(scientific_name) if scientific_name else ""
                
                # Get title for filename
                title = item.get("primary_title", "Untitled")
                title = create_filename(title)
                
                # Create collector folder
                collector_dir = os.path.join(base_dir, collector)
                os.makedirs(collector_dir, exist_ok=True)
                
                # Construct image filename
                if scientific_name:
                    filename = f"{scientific_name}_{pid.replace(':', '_')}.jpg"
                else:
                    filename = f"{title}_{pid.replace(':', '_')}.jpg"
                
                filepath = os.path.join(collector_dir, filename)
                
                # Skip if file already exists
                if os.path.exists(filepath):
                    print(f"File already exists: {filepath}")
                    continue
                
                # Construct viewer URL and fetch HTML
                viewer_url = f"https://repository.library.brown.edu/viewers/image/zoom/{pid}"
                try:
                    print(f"Fetching HTML from {viewer_url}")
                    html_response = requests.get(viewer_url)
                    html_response.raise_for_status()
                    
                    # Extract image URL from HTML
                    image_url = extract_image_url_from_html(html_response.text)
                    if not image_url:
                        # Try alternative method - direct IIIF URL
                        image_url = f"https://repository.library.brown.edu/iiif/image/{pid}/full/full/0/default.jpg"
                        print(f"Using alternative URL: {image_url}")
                    
                    # Download actual image
                    if download_image(image_url, filepath):
                        print(f"Successfully downloaded {filename} to {collector_dir}")
                        total_processed += 1
                    else:
                        print(f"Failed to download image for {pid}")
                        total_errors += 1
                        
                except Exception as e:
                    print(f"Error processing {pid}: {e}")
                    total_errors += 1
                
                # Brief pause to avoid overwhelming the server
                time.sleep(0.5)
            
            # Move to next batch
            start += batch_size
            if start >= total_items:
                print("Reached end of collection.")
                break
                
            # Pause between batches
            time.sleep(1)
            
        except Exception as e:
            print(f"Error fetching batch: {e}")
            time.sleep(5)  # Wait longer before retrying
    
    # Print summary
    print(f"Download complete! Successfully processed {total_processed} images with {total_errors} errors.")
    return total_processed, total_errors

if __name__ == "__main__":
    fetch_and_download_images(batch_size=100)