import os
import json
import requests
from urllib.parse import urlparse

# Path to metadata.json
METADATA_PATH = r"C:\Users\prerk\OneDrive\Desktop\Prerana\Projects\Alaiy-Skill-Test\Dataset_final\ANF\images\metadata.json"

# Output directory for downloaded images
OUTPUT_DIR = os.path.join(os.path.dirname(METADATA_PATH), r"C:\Users\prerk\OneDrive\Desktop\Prerana\Projects\Alaiy-Skill-Test\Dataset_final\ANF\images\downloaded_images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_product_slug(url):
    """
    Extract product name slug from the URL
    e.g., "https://.../bra-free-everyday-skort-59596828?..." -> "bra-free-everyday-skort"
    """
    try:
        filename = urlparse(url).path.split("/")[-1]
        return "-".join(filename.split("-")[:-1])
    except Exception:
        return "unknown"

def download_images(metadata_path, output_dir):
    with open(metadata_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    for idx, product in enumerate(products, start=1):
        image_url = product.get("image")
        product_url = product.get("url")
        if not image_url or not product_url:
            print(f"Skipping item {idx} due to missing data.")
            continue

        product_name = extract_product_slug(product_url)
        filename = f"{idx}-{product_name}.jpg"
        filepath = os.path.join(output_dir, filename)

        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            with open(filepath, "wb") as img_file:
                img_file.write(response.content)
            print(f"✅ Saved: {filename}")
        except Exception as e:
            print(f"❌ Failed to download {filename}: {e}")

if __name__ == "__main__":
    download_images(METADATA_PATH, OUTPUT_DIR)
