import requests
from bs4 import BeautifulSoup
import re
import json

def scrape_chubbies_product(url):
    """
    Scrape Chubbies Shorts product page for features
    
    Args:
        url (str): The product page URL
    
    Returns:
        dict: Contains description with features
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract description from product accordion panel
        description = ""
        
        # Look for the specific product accordion panel div
        accordion_panels = soup.find_all('div', class_=lambda x: x and 'product-accordion__panel' in x)
        
        for panel in accordion_panels:
            # Get all paragraph tags within this panel
            paragraphs = panel.find_all('p')
            panel_text = []
            
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 10:  # Only include substantial text
                    panel_text.append(text)
            
            if panel_text:
                description = " ".join(panel_text)
                break  # Use the first panel with content
        
        # Fallback: Look for other common description containers
        if not description:
            description_selectors = [
                '.product-description p',
                '.product__description p',
                '[class*="description"] p',
                '[class*="panel"] p',
                '.product-content p'
            ]
            
            for selector in description_selectors:
                elements = soup.select(selector)
                if elements:
                    desc_parts = []
                    for elem in elements:
                        text = elem.get_text().strip()
                        if text and len(text) > 10:
                            desc_parts.append(text)
                    if desc_parts:
                        description = " ".join(desc_parts)
                        break
        
        # If still no description, look for any substantial paragraph text
        if not description:
            all_paragraphs = soup.find_all('p')
            substantial_paragraphs = []
            
            for p in all_paragraphs:
                text = p.get_text().strip()
                # Look for product-related content (longer paragraphs with product keywords)
                if (len(text) > 50 and 
                    any(keyword in text.lower() for keyword in ['short', 'fabric', 'stretch', 'comfort', 'fit', 'feature', 'elastic', 'pocket'])):
                    substantial_paragraphs.append(text)
            
            if substantial_paragraphs:
                description = " ".join(substantial_paragraphs[:3])  # Take first 3 relevant paragraphs
        
        if not description:
            description = "No product description found"
        
        return {
            'description': description,
            'status': 'success'
        }
        
    except requests.RequestException as e:
        return {
            'description': f"Error fetching page: {str(e)}",
            'status': 'error'
        }
    except Exception as e:
        return {
            'description': f"Error parsing page: {str(e)}",
            'status': 'error'
        }

def debug_description_search(url):
    """
    Debug function to show description extraction process
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print("Product accordion panels found:")
    accordion_panels = soup.find_all('div', class_=lambda x: x and 'product-accordion__panel' in x)
    print(f"  Found {len(accordion_panels)} accordion panels")
    
    for i, panel in enumerate(accordion_panels, 1):
        paragraphs = panel.find_all('p')
        print(f"  Panel {i}: {len(paragraphs)} paragraphs")
        for j, p in enumerate(paragraphs, 1):
            text = p.get_text().strip()
            if text and len(text) > 10:
                print(f"    Paragraph {j}: {text[:100]}...")

# Example usage
if __name__ == "__main__":
    # Test URL
    url = "https://www.chubbiesshorts.com/products/the-khakinators-5-5"
    
    print("=== SCRAPING RESULT ===")
    result = scrape_chubbies_product(url)
    
    print(f"Status: {result['status']}")
    print(f"Description: {result['description']}")
    
    # print("\n=== DEBUG INFO ===")
    # debug_description_search(url)