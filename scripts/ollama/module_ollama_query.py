# Models
from pydantic import BaseModel

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


def attributes_dict():
    return  {
        'job_title': JobTitle,
        'company_name': CompanyName,
        'salary_floor': SalaryFloor,
        'salary_ceiling': SalaryCeiling,
        'office_status': OfficeStatus,
        'location': Location
    }


# Webscraping
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import os


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


def webpage_call(url: str, linkedin_username: str, linkedin_password: str) -> str:
    if 'linkedin' in url:
        html_content = get_full_page_url_linkedin(url, linkedin_username, linkedin_password)
        return html_content
    else:
        html_content = get_full_page_html(url)
        return html_content
    

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
    

def load_env_variables():
    """Load environment variables."""
    load_dotenv()
    return {
        "linkedin_username": os.getenv("linkedin_username"),
        "linkedin_password": os.getenv("linkedin_username"),
        "model": os.getenv("MODEL")
    }


def read_txt_file(file_path):
    """Read query context from a given file."""
    with open(file_path, "r") as f:
        return f.read()



# Ollama
import json
import ollama


def ollama_chat(env_variables, attributes_dict_key, attributes_dict_value, html):

    context = read_txt_file(
        f'data/context/role_system/role_system_content_{attributes_dict_key}.txt').format(
            context=read_txt_file(
                f"data/context/query_context/query_context_{attributes_dict_key}.txt"
        ))
    
    query = read_txt_file(
        f'data/context/role_user/role_user_content_{attributes_dict_key}.txt').format(
            html=html
            )

    response = ollama.chat(
        model=env_variables['model'],
        messages=[
            {'role': 'system', 'content': read_txt_file('data/context/role_system/role_system_content.txt')},
            {'role': 'system', 'content': context},
            {'role': 'user', 'content': query}
            ],
        format=attributes_dict_value.model_json_schema(),
        options={'temperature': 0}
    )

    return response['message']['content'] 


def get_attributes(attributes_dict, env_variables, html):
    job_details = {}
    for key, value in attributes_dict.items():
        response = json.loads(ollama_chat(env_variables, key, value, html))
        job_details[key] = response[key] 

    return job_details