from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import json
import time

def scrape_description_selenium(url):
    """
    Use Selenium to extract product description and image URL from og meta tags.
    Returns a dictionary with url, description, and image.
    """
    options = Options()
    options.add_argument("--headless")  # Run in background
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(3)  # Allow the page to fully load

        # Extract og:description
        try:
            description_meta = driver.find_element(By.XPATH, "//meta[@property='og:description']")
            description = description_meta.get_attribute("content")
        except NoSuchElementException:
            print(f"No og:description meta tag found for {url}")
            description = None

        # Extract og:image
        try:
            image_meta = driver.find_element(By.XPATH, "//meta[@property='og:image']")
            image_url = image_meta.get_attribute("content")
        except NoSuchElementException:
            print(f"No og:image meta tag found for {url}")
            image_url = None

        return {
            "url": url,
            "description": description,
            "image": image_url
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {
            "url": url,
            "description": None,
            "image": None
        }
    finally:
        driver.quit()

# # Usage
# url = "https://www.abercrombie.com/shop/wd/p/dipped-waist-bubble-hem-midi-dress-59928323?cate"
# product_data = scrape_description_selenium(url)

# if product_data:
#     print("PRODUCT DETAILS")
#     print("=" * 60)
#     print("URL:", product_data["url"])
#     print("Description:", product_data["description"])
    
#     # Save to file
#     with open('product_description.json', 'w', encoding='utf-8') as f:
#         json.dump(product_data, f, indent=2, ensure_ascii=False)
#     print("\nSaved to product_description.json")
# else:
#     print("Could not extract description")
