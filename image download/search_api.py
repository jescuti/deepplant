# import requests

# def count_herbarium_items_only(batch_size=500):
#     total_count = 0
#     start = 0
#     max_pages = 20  # ~10,000 items

#     while True:
#         api_url = (
#             "https://repository.library.brown.edu/api/search/"
#             "?q=rel_is_member_of_collection_ssim:bdr:nz9qn2kb"
#             f"&start={start}&rows={batch_size}&wt=json"
#         )
#         try:
#             response = requests.get(api_url)
#             response.raise_for_status()
#             data = response.json()
#         except Exception as e:
#             print(f"Failed at start={start}: {e}")
#             break

#         docs = data.get("response", {}).get("docs", [])
#         if not docs:
#             print("No more items returned.")
#             break

#         total_count += len(docs)
#         print(f"Fetched {len(docs)} items (start={start})")

#         start += batch_size
#         if start >= data["response"].get("numFound", 0):
#             break
#         if start // batch_size >= max_pages:
#             print("Reached max page limit.")
#             break

#     print(f"Total items scanned: {total_count}")
#     return total_count

# count_herbarium_items_only()

import os
import requests

def download_sample_images(page_number=100, page_size=10):
    start = page_number * page_size
    os.makedirs("sample_images", exist_ok=True)

    api_url = (
        "https://repository.library.brown.edu/api/search/"
        "?q=rel_is_member_of_collection_ssim:bdr:nz9qn2kb"
        f"&start={start}&rows={page_size}&wt=json"
    )

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Failed to fetch page {page_number}: {e}")
        return

    docs = data.get("response", {}).get("docs", [])
    if not docs:
        print(f"No items found on page {page_number}.")
        return

    for item in docs:
        pid = item.get("pid")
        title = item.get("primary_title", "Untitled").replace("/", "_").replace(" ", "_")

        if not pid:
            continue

        image_url = f"https://repository.library.brown.edu/viewers/image/zoom/{pid}"
        file_path = os.path.join("sample_images", f"{title}_{pid.replace(':', '_')}.html")

        try:
            with open(file_path, 'w') as f:
                f.write(f'<meta http-equiv="refresh" content="0; url={image_url}">')
            print(f"Saved link: {file_path}")
        except Exception as e:
            print(f"Failed to save file for {pid}: {e}")

download_sample_images()