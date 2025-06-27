import time
import requests
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Define scraping targets for Chubbies
SCRAPE_TARGETS = [
    {"url": "https://www.chubbiesshorts.com/en-in/collections/the-casual-shorts", "category": "casual-shorts", "limit": 300},
    {"url": "https://www.chubbiesshorts.com/en-in/collections/the-sport-shorts", "category": "sport-shorts", "limit": 300},
    {"url": "https://www.chubbiesshorts.com/en-in/collections/the-swim-trunks", "category": "swim-trunks", "limit": 300},
    {"url": "https://www.chubbiesshorts.com/en-in/collections/casual-pants", "category": "casual-pants", "limit": 200},
    {"url": "https://www.chubbiesshorts.com/en-in/collections/the-joggers", "category": "joggers", "limit": 200},
    {"url": "https://www.chubbiesshorts.com/en-in/collections/the-polos", "category": "polos", "limit": 70},
    {"url": "https://www.chubbiesshorts.com/en-in/collections/button-ups", "category": "button-ups", "limit": 70},
    {"url": "https://www.chubbiesshorts.com/en-in/collections/long-sleeve-shirts", "category": "long-sleeve-shirts", "limit": 70},
    {"url": "https://www.chubbiesshorts.com/en-in/collections/t-shirts", "category": "t-shirts", "limit": 70},
    {"url": "https://www.chubbiesshorts.com/en-in/collections/the-outerwear", "category": "outerwear", "limit": 70}
]


def scrape_chubbies_images():
    metadata = []
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    try:
        for item in SCRAPE_TARGETS:
            url = item["url"]
            category = item["category"]
            limit = item["limit"]

            print(f"\n🔍 Scraping {category} ({limit} images)")
            folder_path = os.path.join("images", category)
            os.makedirs(folder_path, exist_ok=True)

            driver.get(url)
            time.sleep(10)

            # Scroll to load more products
            for _ in range(4):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)

            # Find the grid container with all product cards
            print("🔍 Looking for the product grid container...")
            target_container = None
            
            # Look for the specific grid class that contains all product cards
            grid_selectors = [
                "div[class*='_grid_niz5w_1']",
                "div._grid_niz5w_1"
            ]
            
            for selector in grid_selectors:
                try:
                    containers = driver.find_elements(By.CSS_SELECTOR, selector)
                    if containers:
                        target_container = containers[0]  # Should only be one
                        print(f"✅ Found product grid container with selector: {selector}")
                        break
                except Exception as e:
                    print(f"❌ Error with selector {selector}: {e}")
                    continue
            
            if not target_container:
                print(f"❌ No target container found for {category}")
                continue

            # Debug: Print container info
            print(f"📊 Target container class: {target_container.get_attribute('class')}")
            
            # Now search for images ONLY within this container
            print("🔍 Searching for images within the target container...")
            
            # Try multiple selectors for product images within the container
            image_selectors = [
                "img",
                "img[class*='product']",
                "img[class*='card']", 
                "img[class*='grid']",
                "img[src*='products']",
                "img[alt*='shorts']",
                "img[alt*='shirt']"
            ]
            
            images = []
            for selector in image_selectors:
                try:
                    found_images = target_container.find_elements(By.CSS_SELECTOR, selector)
                    if found_images:
                        print(f"✅ Found {len(found_images)} images with selector: {selector}")
                        images = found_images
                        break
                except Exception as e:
                    print(f"❌ Error with selector {selector}: {e}")
                    continue
            
            if not images:
                print(f"❌ No product images found in target container for {category}")
                # Save container HTML for debugging
                try:
                    with open(f"debug_container_{category}.html", "w", encoding="utf-8") as f:
                        f.write(target_container.get_attribute('innerHTML'))
                    print(f"💾 Container HTML saved to debug_container_{category}.html")
                except:
                    pass
                continue

            print(f"📊 Processing {len(images)} images from target container...")
            
            count = 0
            for img in images:
                if count >= limit:
                    break

                src = img.get_attribute("src") or img.get_attribute("data-src")
                alt = img.get_attribute("alt") or ""
                
                if not src:
                    continue
                
                # Skip small images (thumbnails, color swatches)
                if any(size in src for size in ["_50x", "_100x", "_150x", "thumb", "small"]):
                    continue
                
                # Skip non-product images
                if any(skip in src.lower() for skip in ["logo", "icon", "banner", "badge"]):
                    continue
                
                # Ensure we get high-quality images
                if "_400x" in src:
                    src = src.replace("_400x", "_800x")
                elif "_300x" in src:
                    src = src.replace("_300x", "_800x")

                try:
                    response = requests.get(src, timeout=10)
                    if response.status_code == 200:
                        count += 1
                        img_filename = f"chubbies_{category}_{count}.jpg"
                        img_filepath = os.path.join(folder_path, img_filename)

                        with open(img_filepath, 'wb') as f:
                            f.write(response.content)

                        # Clean up description
                        desc = alt.split(",")[0].strip() if alt else f"Chubbies {category} item {count}"
                        metadata.append({
                            "image": img_filename,
                            "description": desc,
                            "category": category,
                            "brand": "chubbies"
                        })

                        print(f"✅ {img_filename}")
                        time.sleep(3)  # 3 second delay

                except Exception as e:
                    print(f"❌ Error downloading {category} image {count+1}: {e}")
                    time.sleep(3)

    finally:
        driver.quit()

    # Save metadata
    metadata_path = os.path.join("images", "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

    print(f"\n🎉 Download complete! {len(metadata)} images saved.")
    print(f"📊 Metadata saved to images/metadata.json")

if __name__ == "__main__":
    scrape_chubbies_images()

