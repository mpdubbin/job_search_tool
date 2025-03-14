from module_scrape_targeted import *
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")


def webpage_call(url: str, LINKEDIN_USERNAME: str, LINKED_PASSWORD: str) -> str:
    if 'linkedin' in url:
        html_content = get_full_page_url_linkedin(url, LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
        return html_content
    else:
        html_content = get_full_page_html(url)
        return html_content