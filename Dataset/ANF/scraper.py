import time
import requests
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Define scraping targets
SCRAPE_TARGETS = [
    {"url": "https://www.abercrombie.com/shop/wd/womens-dresses-and-jumpsuits", "gender": "womens", "category": "dresses-and-jumpsuits", "limit": 20},
    {"url": "https://www.abercrombie.com/shop/wd/womens-tops--1", "gender": "womens", "category": "tops", "limit": 50},
    {"url": "https://www.abercrombie.com/shop/wd/womens-bottoms--1", "gender": "womens", "category": "bottoms", "limit": 40},
    {"url": "https://www.abercrombie.com/shop/wd/womens-coats-and-jackets", "gender": "womens", "category": "coats-and-jackets", "limit": 20},
    {"url": "https://www.abercrombie.com/shop/wd/womens-sleep-and-intimates", "gender": "womens", "category": "sleep-and-intimates", "limit": 20},
    {"url": "https://www.abercrombie.com/shop/wd/womens-shoes", "gender": "womens", "category": "shoes", "limit": 20},
    {"url": "https://www.abercrombie.com/shop/wd/womens-activewear", "gender": "womens", "category": "activewear", "limit": 20},
    {"url": "https://www.abercrombie.com/shop/wd/mens-tops--1", "gender": "mens", "category": "tops", "limit": 50},
    {"url": "https://www.abercrombie.com/shop/wd/mens-bottoms--1", "gender": "mens", "category": "bottoms", "limit": 30},
    {"url": "https://www.abercrombie.com/shop/wd/mens-coats-and-jackets", "gender": "mens", "category": "coats-and-jackets", "limit": 30},
    {"url": "https://www.abercrombie.com/shop/wd/mens-suits", "gender": "mens", "category": "suits", "limit": 20},
    {"url": "https://www.abercrombie.com/shop/wd/mens-activewear", "gender": "mens", "category": "activewear", "limit": 20},
    {"url": "https://www.abercrombie.com/shop/wd/mens-underwear", "gender": "mens", "category": "underwear", "limit": 10},
    {"url": "https://www.abercrombie.com/shop/wd/mens-swim", "gender": "mens", "category": "swim", "limit": 20}  
]


def scrape_abercrombie_images():
    metadata = []
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        for item in SCRAPE_TARGETS:
            url = item["url"]
            gender = item["gender"]
            category = item["category"]
            limit = item["limit"]

            print(f"\n🔍 Scraping {gender}/{category} ({limit} images)")
            folder_path = os.path.join("images", gender, category)
            os.makedirs(folder_path, exist_ok=True)

            driver.get(url)
            time.sleep(10)

            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)

            images = driver.find_elements(By.CSS_SELECTOR, "img.catalog-productCard-module__productCardImage_1")

            count = 0
            for img in images:
                if count >= limit:
                    break

                src = img.get_attribute("src")
                alt = img.get_attribute("alt")
                if not src or not alt:
                    continue

                try:
                    response = requests.get(src, timeout=10)
                    if response.status_code == 200:
                        count += 1
                        img_filename = f"{gender}_{category}_{count}.jpg"
                        img_filepath = os.path.join(folder_path, img_filename)

                        with open(img_filepath, 'wb') as f:
                            f.write(response.content)

                        desc = alt.split(",")[0].strip()
                        metadata.append({
                            "image": img_filename,
                            "description": desc
                        })

                        print(f"✅ {img_filename}")
                        time.sleep(3)

                except Exception as e:
                    print(f"Error downloading: {e}")
                    time.sleep(3)

    finally:
        driver.quit()

    os.makedirs("images", exist_ok=True)
    metadata_path = os.path.join("images", "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

    print("\n🎉 Download complete. Metadata saved to images/metadata.json.")

if __name__ == "__main__":
    scrape_abercrombie_images()
