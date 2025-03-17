from bs4 import BeautifulSoup
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from pydantic import BaseModel
from typing import List
import os


# Environment variables
load_dotenv()
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")


class JobTitle(BaseModel):
    """Schema for the job title"""
    job_title: str

class CompanyName(BaseModel):
    """Schema for the company name"""
    company_name: str

class SalaryFloor(BaseModel):
    """Schema for the salary floor"""
    salary_floor: int  

class SalaryCeiling(BaseModel):
    """Schema for the salary ceiling"""
    salary_ceiling: int    

class OfficeStatus(BaseModel):
    """Schema for the office status"""
    office_status: str

class Location(BaseModel):
    """Schema for the location"""
    location: str



def extract_all_content(html: str) -> str:
    """Extract all HTML tags and their content."""
    soup = BeautifulSoup(html, "html.parser")
    
    # Return the entire HTML including all tags
    return str(soup)


def extract_targeted_content(html):
    """Extracts job title-related content from HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Get job title candidates from <title>, <h1>, and <h2>
    title_tags = [tag.get_text(strip=True) for tag in soup.find_all(['title', 'h1', 'h2', 'p', 'li', 'tr', 'td'])]
    
    # Join extracted content into a clean format
    cleaned_text = "\n".join(title_tags)
    return cleaned_text


def get_full_page_html(url: str) -> str:
    """Scrape specified elements from a single webpage."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Must be false for Cloudflare
        page = browser.new_page()
        page.goto(url, wait_until="load")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(5000)
        
        filtered_content = extract_targeted_content(page.content())
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
        
        filtered_content = extract_targeted_content(page.content())
        browser.close()
        
        return filtered_content


def webpage_call(url: str, LINKEDIN_USERNAME: str, LINKED_PASSWORD: str) -> str:
    if 'linkedin' in url:
        html_content = get_full_page_url_linkedin(url, LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
        return html_content
    else:
        html_content = get_full_page_html(url)
        return html_content