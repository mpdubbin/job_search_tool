from playwright.sync_api import sync_playwright

from dotenv import load_dotenv
from module_ollama_query import * 
import ollama
import os


# Load environment variables
load_dotenv()
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")


# Test url, for testing purposes
test_url = "https://boards.greenhouse.io/capitaltg/jobs/4378843007"
query_html = webpage_call(test_url, LINKEDIN_USERNAME, LINKEDIN_PASSWORD)

# Queries
query_summary = f"""
Summarize the following job posting in a **concise and structured format**. Must include key details such as:
- Job title
- Company name
- Job responsibilities
- Required qualifications
- Salary range
- Work environment (Remote, Hybrid, or On-site)
- Work location (city, state, address)
- Any unique aspects of the role or company culture

If these details are not present in the supplied job posting, say so.

**Here is the job posting HTML: {query_html}**
"""

# Pass the context and query to Ollama
summary_response = ollama.chat(
    model="mistral",
    messages=[
        {"role": "system", "content": "You are an AI assistant helping with job webpage analysis."},
        {"role": "user", "content": f"{query_summary}"}
    ]
)

query_structured = f"""Using the following **job summary**, extract job details in **valid JSON format only**.

**Job Summary:**

{summary_response["message"]["content"]}


**Expected JSON Output Format:**
```json
{{
    "company": "Example Corp",
    "job_title": "Data Scientist",
    "salary_floor": 80000,
    "salary_ceiling": 120000,
    "office_status": "Hybrid",
    "office_location": ["Austin, TX", "San Francisco, CA"]
}}

Rules:

    If salary floor and ceiling are less than 100, assume they are hourly rates and multiply by 2080 to get annual salary.
    If salary data is missing, set it as null instead of 0 or incorrect values.
    Use consistent formatting for "office_status":
        "Remote" (fully remote)
        "Hybrid" (mix of remote & in-office)
        "On-site" (fully in-office)
    Use an array for "office_location", even if there's only one location.

DO NOT include any additional text, explanations, or formatting—ONLY return valid JSON. 
"""
