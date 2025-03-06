from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# Load job posting URLs from file
with open("data/rag/job_urls.txt", "r") as f:
    job_urls = [line.strip() for line in f.readlines()]

# Set up Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Create directory to store raw HTML
os.makedirs("data/rag/raw_html", exist_ok=True)

# Scrape each URL
for idx, url in enumerate(job_urls):
    driver.get(url)
    time.sleep(10) 
    
    html_content = driver.page_source

    # Save HTML file
    with open(f"data/rag/raw_html/job_{idx}.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Saved: data/rag/raw_html/job_{url}.html")

driver.quit()
