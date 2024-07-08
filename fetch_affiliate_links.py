import requests
from bs4 import BeautifulSoup
import csv
import os
import time
import psutil
from urllib.parse import urljoin
from selenium import webdriver

# Path to your Chrome profile, PUT YOUR USER NAME
chrome_profile_path = r'C:\Users\<YOUR USERNAME>\AppData\Local\Google\Chrome\User Data'

# Ensure all Chrome instances are closed
def close_chrome_instances():
    for process in psutil.process_iter():
        if process.name() == "chrome.exe":
            process.kill()

close_chrome_instances()

# Set up Chrome options to use your primary profile
options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={chrome_profile_path}")
options.add_argument("profile-directory=Default")

# Initialize WebDriver for Chrome with options
driver = webdriver.Chrome(options=options)

def get_affiliate_link(product_url):
    try:
        print(f"Fetching affiliate link for {product_url}...")
        response = requests.get(product_url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')

        affiliate_link_element = soup.find('input', {'id': 'amzn-ss-text-shortlink-textarea'})
        if affiliate_link_element:
            affiliate_link = affiliate_link_element['value']
            print(f"Affiliate link: {affiliate_link}")
            return affiliate_link
        else:
            print("Affiliate link element not found.")
            return None
    except Exception as e:
        print(f"Error while getting affiliate link: {e}")
        return None

def scrape_amazon_product(url):
    try:
        print(f"Scraping product data from: {url}")
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')

        title_element = soup.find('span', {'id': 'productTitle'})
        title = title_element.text.strip() if title_element else None

        price_element = soup.find('span', {'class': 'a-offscreen'})
        price = price_element.text.strip() if price_element else None

        image_element = soup.find('img', {'id': 'landingImage'})
        image = image_element['src'] if image_element else None

        product_data = {'title': title, 'price': price, 'image': image}
        print(f"Scraped product data: {product_data}")
        return product_data
    except Exception as e:
        print(f"Error while scraping product data: {e}")
        return None

def get_top_selling_products():
    try:
        print("Fetching top selling products...")
        best_sellers_url = 'https://www.amazon.com/gp/movers-and-shakers'
        response = requests.get(best_sellers_url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')

        product_links = soup.find_all('a', {'class': 'a-link-normal'})
        product_urls = [urljoin(best_sellers_url, link.get('href')) for link in product_links if '/dp/' in link.get('href')]

        print(f"Top selling product URLs: {product_urls}")
        return product_urls
    except Exception as e:
        print(f"Error while fetching top selling products: {e}")
        return []

print("Starting the process...")
top_selling_product_urls = get_top_selling_products()

# Prepare the CSV file AND PUT IT IN DESKTOP
csv_file_path = os.path.join(r'C:\Users\<YOUR USERNAME\Desktop', 'amazon_products.csv')
csv_columns = ['Title', 'Price', 'Image', 'Affiliate Link']

with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
    writer.writeheader()

    for product_url in top_selling_product_urls:
        product_info = scrape_amazon_product(product_url)
        if product_info:
            affiliate_link = get_affiliate_link(product_url)
            if affiliate_link:
                product_info['Affiliate Link'] = affiliate_link
                writer.writerow(product_info)
                print('Product Info written to CSV:', product_info)
            else:
                print("Failed to get affiliate link for:", product_url)
        else:
            print("Failed to scrape product info for:", product_url)

print("Process complete. Closing the browser.")
driver.quit()