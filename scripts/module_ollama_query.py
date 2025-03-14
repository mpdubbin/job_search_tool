from scripts.context_obsolete.module_scrape_targeted import *
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import os


# Environment variables
load_dotenv()
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")


def extract_relevant_content(html: str) -> str:
    """Extract text content from HTML while excluding specific tags."""
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove specified tags from the soup
    for tag in soup(["link", "meta", "script"]):
        tag.decompose()
    
    extracted_data = []
    
    # Extract all text content after exclusion
    for element in soup.find_all(text=True):
        parent = element.parent.name
        if parent not in ["link", "meta", "script"]:
            extracted_data.append(element.strip())
    
    return "\n".join(filter(None, extracted_data))



def get_full_page_html(url: str) -> str:
    """Scrape specified elements from a single webpage."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Must be false for Cloudflare
        page = browser.new_page()
        page.goto(url, wait_until="load")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(5000)
        
        filtered_content = extract_relevant_content(page.content())
        browser.close()
        
        return filtered_content


def get_full_page_url_linkedin(url: str, linkedin_username: str, linkedin_password: str) -> str:
    """Scrape specified elements from a single LinkedIn webpage."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Must be False for Cloudflare
        page = browser.new_page()
        
        page.goto("https://www.linkedin.com/login", wait_until="load")
        page.wait_for_selector("input#username")
        page.fill("input#username", linkedin_username)
        page.fill("input#password", linkedin_password)
        page.keyboard.press("Enter")
        page.wait_for_timeout(5000)  # Adjust as necessary
        
        page.goto(url, wait_until="load")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(5000)
        
        filtered_content = extract_relevant_content(page.content())
        browser.close()
        
        return filtered_content


def webpage_call(url: str, LINKEDIN_USERNAME: str, LINKED_PASSWORD: str) -> str:
    if 'linkedin' in url:
        html_content = get_full_page_url_linkedin(url, LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
        return html_content
    else:
        html_content = get_full_page_html(url)
        return html_content