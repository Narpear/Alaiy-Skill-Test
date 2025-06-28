#!/usr/bin/env python3
"""
Chubbies Shorts Scraper using requests and BeautifulSoup
Scrapes product URLs and image URLs from multiple collection pages
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
from scrape_description import scrape_chubbies_product
import os

def scrape_chubbies_collection(url, target_count):
    """
    Scrapes product URLs and image URLs from the given Chubbie Shorts collection URL.

    Args:
        url (str): The URL of the Chubbie Shorts collection page.
        target_count (int): Number of products to scrape (after skipping first 6)

    Returns:
        list: A list of dictionaries, where each dictionary contains 'url' and 'image' for a product.
    """
    # Set up headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print(f"Fetching URL: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        print(f"Successfully fetched page (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Try multiple selectors to find product cards
    product_cards = []
    selectors_to_try = [
        'div._header_k20bi_1',
        'div[class*="product"]',
        'div[class*="card"]',
        'a[href*="/products/"]',
        'div[class*="item"]'
    ]
    
    for selector in selectors_to_try:
        product_cards = soup.select(selector)
        if product_cards:
            print(f"Found {len(product_cards)} product cards using selector: {selector}")
            break
    
    if not product_cards:
        print("No product cards found with any selector. Page structure might have changed.")
        # Let's see what's actually on the page
        print(f"Page title: {soup.title.string if soup.title else 'No title'}")
        # Save the HTML for debugging
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Saved page HTML to debug_page.html for inspection")
        return []
    
    scraped_data = []
    product_counter = 0  # Counter to track processed products
    saved_count = 0  # Counter for products actually saved
    
    for i, card in enumerate(product_cards, 1):
        # Stop if we've reached our target count
        if saved_count >= target_count:
            break
            
        try:
            # Try to find anchor tag with different approaches
            anchor_tag = None
            
            # Method 1: Look for specific class
            anchor_tag = card.find('a', class_="_imageWrapper_k20bi_22")
            
            # Method 2: If not found, look for any anchor with href containing /products/
            if not anchor_tag:
                anchor_tag = card.find('a', href=lambda x: x and '/products/' in x)
            
            # Method 3: If still not found, look for any anchor tag
            if not anchor_tag:
                anchor_tag = card.find('a')
            
            if anchor_tag:
                # Get the product URL
                product_href = anchor_tag.get('href')
                if product_href:
                    # Ensure the product URL is absolute
                    if product_href.startswith('/'):
                        product_url = f"https://www.chubbiesshorts.com{product_href}"
                    elif product_href.startswith('http'):
                        product_url = product_href
                    else:
                        product_url = f"https://www.chubbiesshorts.com/{product_href}"

                    # Get the image URL
                    img_tag = anchor_tag.find('img')
                    image_url = None
                    if img_tag:
                        image_url = img_tag.get('src') or img_tag.get('data-src')
                        # Handle relative image URLs
                        if image_url:
                            if image_url.startswith('//'):
                                image_url = f"https:{image_url}"
                            elif image_url.startswith('/'):
                                image_url = f"https://www.chubbiesshorts.com{image_url}"
                            elif not image_url.startswith('http'):
                                image_url = f"https://www.chubbiesshorts.com/{image_url}"

                    if product_url and image_url:
                        description = scrape_chubbies_product(product_url)["description"]
                        image_url = image_url.replace("width=100&height=133", "width=800&height=1067")
                        
                        product_counter += 1
                        
                        # Skip saving the first 6 products
                        if product_counter > 6:
                            scraped_data.append({
                                "url": product_url,
                                "image": image_url,
                                "description": description
                            })
                            saved_count += 1
                            print(f"Product {i} (saved #{saved_count}/{target_count}): {product_url}")
                        else:
                            print(f"Product {i} (skipped #{product_counter}): {product_url}")
                    else:
                        print(f"Product {i}: Missing URL or image")
                else:
                    print(f"Product {i}: No href found")
            else:
                print(f"Product {i}: No anchor tag found")
                
        except Exception as e:
            print(f"Error processing product {i}: {e}")
            continue

    return scraped_data

def save_to_json(data, filename="images/metadata.json"):
    """Save scraped data to JSON file"""
    try:
        # Create images directory if it doesn't exist
        os.makedirs("images", exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving to JSON: {e}")

def main():
    """Main function to run the scraper"""
    
    # Define the URLs and their target product counts
    url_targets = [
        ("https://www.chubbiesshorts.com/collections/the-casual-shorts", 10),
        ("https://www.chubbiesshorts.com/collections/the-sport-shorts", 10),
        ("https://www.chubbiesshorts.com/collections/the-swim-trunks", 10),
        ("https://www.chubbiesshorts.com/collections/the-sweat-shorts-loungers", 10),
        ("https://www.chubbiesshorts.com/collections/youth-swim-trunks", 5),
        ("https://www.chubbiesshorts.com/collections/kids-swim", 3),
        ("https://www.chubbiesshorts.com/collections/casual-pants", 6),
        ("https://www.chubbiesshorts.com/collections/the-polos", 5),
        ("https://www.chubbiesshorts.com/collections/button-ups", 5),
        ("https://www.chubbiesshorts.com/collections/t-shirts", 4),
        ("https://www.chubbiesshorts.com/collections/the-outerwear", 3),
        ("https://www.chubbiesshorts.com/collections/boys-short-sleeve-shirts", 3),
    ]
    
    print("🚀 Starting Chubbies Multi-Collection Scraper...")
    print("=" * 60)
    
    all_data = []
    total_products = 0
    
    for i, (url, target_count) in enumerate(url_targets, 1):
        print(f"\n📄 Processing Collection {i}/{len(url_targets)}: {url}")
        print(f"🎯 Target: {target_count} products (after skipping first 6)")
        print("-" * 60)
        
        data = scrape_chubbies_collection(url, target_count)
        
        if data:
            all_data.extend(data)
            total_products += len(data)
            print(f"✅ Successfully scraped {len(data)} products from this collection")
        else:
            print("❌ No data scraped from this collection")
        
        # Add a small delay between requests to be respectful
        if i < len(url_targets):
            print("⏳ Waiting 2 seconds before next collection...")
            time.sleep(2)

    if all_data:
        print(f"\n🎉 Successfully scraped {total_products} products total from all collections!")
        print("=" * 60)
        
        # Save data to files
        save_to_json(all_data)
        
        # Print summary
        print("\n📋 Summary of scraped data:")
        for i, (url, target_count) in enumerate(url_targets, 1):
            actual_count = len([item for item in all_data if any(url_part in item['url'] for url_part in url.split('/')[-2:])])
            print(f"Collection {i}: {actual_count}/{target_count} products")
        
        # Print first few results as preview
        print("\n📋 Preview of scraped data:")
        for i, item in enumerate(all_data[:5], 1):
            print(f"\nProduct {i}:")
            print(f"  URL: {item['url']}")
            print(f"  Image: {item['image']}")
        
        if len(all_data) > 5:
            print(f"\n... and {len(all_data) - 5} more products")
            
    else:
        print("❌ No data scraped from any collection. Check the debug_page.html file for page structure.")

if __name__ == "__main__":
    main()