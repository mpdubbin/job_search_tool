from playwright.sync_api import sync_playwright

from dotenv import load_dotenv
from module_ollama_query import *
import json 
import ollama
import os
import time

# Load environment variables
load_dotenv()
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")


def load_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# Load JSON Data
with open("data/rag/manual_parse.json", "r", encoding="utf-8") as file:
    job_data = json.load(file)


# Add full HTML to context
context = "\n\n".join([
    "Unique Job Posting\n"
    "---\n"
    f"Company: {job['company']} ; Job Title: {job['job_title']}; "
    f"Office Status: {job['office_status']} ; Location: {job['office_location']} ;"
    f"Salary Floor: {job['salary_floor']} ; Salary Ceiling {job['salary_ceiling']} ; \n"
    f"Job Webpage:\n{load_html(job['html'])}\n\n"
    "---"
    for job in job_data
])

# Test url, for testing purposes
test_url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4039885789"
query_html = webpage_call(test_url, LINKEDIN_USERNAME, LINKEDIN_PASSWORD)


# Example query
query = f"With this HTML as input, please pull the job title, company name, in-office/hybrid/remote status, job location, salary floor, salary ceiling. {query_html}"

print(query)

# # Pass the context and query to Ollama
# response = ollama.chat(
#     model="mistral",
#     messages=[
#         {"role": "system", "content": "You are an AI assistant helping with job analysis."},
#         {"role": "user", "content": f"Here is job data:\n{context}\n\n{query}"}
#     ]
# )

# # Print the response
# print(response["message"]["content"])
