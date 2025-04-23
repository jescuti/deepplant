import os
import requests

def fetch_and_download_images(batch_size=100):
    start = 0
    while True:
        api_url = (
            "https://repository.library.brown.edu/api/search/"
            "?q=rel_is_member_of_collection_ssim:bdr:nz9qn2kb"
            f"&start={start}&rows={batch_size}&wt=json"
        )
        response = requests.get(api_url).json()
        docs = response.get("response", {}).get("docs", [])
        if not docs:
            break

        for item in docs:
            pid = item.get("pid")
            collector = item.get("dwc_recorded_by_ssi", "Unknown_Collector").replace("/", "_").replace(" ", "_")
            title = item.get("primary_title", "Untitled").replace("/", "_").replace(" ", "_")

            # Construct image viewer URL
            image_url = f"https://repository.library.brown.edu/viewers/image/zoom/{pid}"

            # Prepare directory and filepath
            os.makedirs(collector, exist_ok=True)
            file_path = os.path.join(collector, f"{title}_{pid.replace(':', '_')}.html")

            # Save the viewer page URL as an .html link file
            with open(file_path, 'w') as f:
                f.write(f'<meta http-equiv="refresh" content="0; url={image_url}">')

            print(f"Saved redirect file for {title} to {file_path}")

        start += batch_size
        if start >= response["response"].get("numFound", 0):
            break