import time
import requests
import os
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scrape_description import scrape_description_selenium

# Define scraping targets
SCRAPE_TARGETS = [
    {"url": "https://www.abercrombie.com/shop/wd/womens-dresses-and-jumpsuits", "gender": "womens", "category": "dresses-and-jumpsuits", "limit": 5},
    {"url": "https://www.abercrombie.com/shop/wd/womens-tops--1", "gender": "womens", "category": "tops", "limit": 15},
    {"url": "https://www.abercrombie.com/shop/wd/womens-bottoms--1", "gender": "womens", "category": "bottoms", "limit": 10},
    {"url": "https://www.abercrombie.com/shop/wd/womens-coats-and-jackets", "gender": "womens", "category": "coats-and-jackets", "limit": 5},
    {"url": "https://www.abercrombie.com/shop/wd/womens-sleep-and-intimates", "gender": "womens", "category": "sleep-and-intimates", "limit": 5},
    {"url": "https://www.abercrombie.com/shop/wd/womens-shoes", "gender": "womens", "category": "shoes", "limit": 5},
    {"url": "https://www.abercrombie.com/shop/wd/womens-activewear", "gender": "womens", "category": "activewear", "limit": 5},
    {"url": "https://www.abercrombie.com/shop/wd/mens-tops--1", "gender": "mens", "category": "tops", "limit": 15},
    {"url": "https://www.abercrombie.com/shop/wd/mens-bottoms--1", "gender": "mens", "category": "bottoms", "limit": 10},
    {"url": "https://www.abercrombie.com/shop/wd/mens-coats-and-jackets", "gender": "mens", "category": "coats-and-jackets", "limit": 5},
    {"url": "https://www.abercrombie.com/shop/wd/mens-suits", "gender": "mens", "category": "suits", "limit": 5},
    {"url": "https://www.abercrombie.com/shop/wd/mens-activewear", "gender": "mens", "category": "activewear", "limit": 5},
    {"url": "https://www.abercrombie.com/shop/wd/mens-underwear", "gender": "mens", "category": "underwear", "limit": 2},
    {"url": "https://www.abercrombie.com/shop/wd/mens-swim", "gender": "mens", "category": "swim", "limit": 3}
]

def scrape_abercrombie_images():
    metadata = []
    BASE_URL = "https://www.abercrombie.com"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=options)

    try:
        for item in SCRAPE_TARGETS:
            url = item["url"]
            gender = item["gender"]
            category = item["category"]
            limit = item["limit"]

            print(f"\n🔍 Finding {gender}/{category} ({limit} links)")
            driver.get(url)
            time.sleep(10)

            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)

            images = driver.find_elements(By.CSS_SELECTOR, "img.catalog-productCard-module__productCardImage_1")

            count = 0
            seen = set()

            for img in images:
                if count >= limit:
                    break

                try:
                    parent_a = img.find_element(By.XPATH, "ancestor::a")
                    href = parent_a.get_attribute("href")

                    if not href:
                        continue
                    if href.startswith("/"):
                        href = BASE_URL + href
                    if href in seen:
                        continue
                    seen.add(href)

                    count += 1
                    print(f"🔗 Found: {href}")
                    
                    # Scrape product description
                    try:
                        product_data = scrape_description_selenium(href)
                        if product_data and isinstance(product_data, dict):
                            metadata.append(product_data)
                            print(f"✅ Scraped and saved: {href}")
                        else:
                            # Fallback if description scraping fails
                            metadata.append({"url": href, "description": None})
                            print(f"⚠️ Scraped URL only: {href}")
                    except Exception as e:
                        print(f"❌ Error scraping description for {href}: {e}")
                        metadata.append({"url": href, "description": None})

                    time.sleep(1)

                except Exception as e:
                    print(f"Error processing image: {e}")
                    time.sleep(1)

    finally:
        driver.quit()

    os.makedirs("images", exist_ok=True)
    metadata_path = os.path.join("images", "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

    # Print summary
    total_products = len(metadata)
    products_with_descriptions = sum(1 for item in metadata if item.get("description"))
    
    print(f"\n🎉 Link scraping complete. Metadata saved to images/metadata.json.")
    print(f"📊 Summary: {total_products} products found, {products_with_descriptions} with descriptions")

if __name__ == "__main__":
    # Run either step depending on what you've already done:
    scrape_abercrombie_images()       # Step 1: Collect URLs