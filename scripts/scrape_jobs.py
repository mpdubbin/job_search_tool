from playwright.sync_api import sync_playwright

from dotenv import load_dotenv
from module_scrape import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# Load environment variables
load_dotenv()
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")




# Load job posting URLs from file
with open("data/rag/job_urls.txt", "r") as f:
    job_urls = [line.strip() for line in f.readlines()]

# Create directory to store raw HTML
os.makedirs("data/rag/raw_html", exist_ok=True)


# Scrape n' Save each URL
for idx, url in enumerate(job_urls):
    if 'linkedin' in url:
        html_content = get_full_page_url_linkedin(url, LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
        with open(f"data/rag/raw_html/job_{idx}.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Saved: {url}")
        time.sleep(10)
    else:
        html_content = get_full_page_html(url)
        with open(f"data/rag/raw_html/job_{idx}.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Saved: {url}")
        time.sleep(10) 
