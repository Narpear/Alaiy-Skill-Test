import os
import json
import requests

# === CONFIG ===
METADATA_PATH = r"C:\Users\prerk\OneDrive\Desktop\Prerana\Projects\Alaiy-Skill-Test\Dataset_final\Chubbies\images\metadata.json"
SAVE_DIR = r"C:\Users\prerk\OneDrive\Desktop\Prerana\Projects\Alaiy-Skill-Test\Dataset_final\Chubbies\images\downloaded_images"

# Ensure the save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

# Load metadata
with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# Simple sequential counter for all products
product_counter = 1

# Download loop
for item in metadata:
    url = item["url"]
    image_url = item["image"]

    # Extract slug from product URL
    slug = url.split("/products/")[-1]

    filename = f"{product_counter}-{slug}.webp"
    filepath = os.path.join(SAVE_DIR, filename)

    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()

        with open(filepath, "wb") as img_file:
            img_file.write(response.content)

        print(f"[✓] Saved: {filename}")
        product_counter += 1
    except Exception as e:
        print(f"[✗] Failed to download {image_url} — {e}")
        # Still increment counter even if download fails to maintain sequence
        product_counter += 1
