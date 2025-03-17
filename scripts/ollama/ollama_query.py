from dotenv import load_dotenv
from module_ollama_query import * 
import ollama
import os


# Load environment variables
load_dotenv()
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# Test url, for testing purposes
test_url = "https://jobs.ashbyhq.com/equip/2f34e681-461b-47ef-a86a-182e3ffc39a8?src=LinkedIn+Posting"
html = webpage_call(test_url, LINKEDIN_USERNAME, LINKEDIN_PASSWORD)

# Job Title
with open('scripts/ollama/query_context_jobtitle.txt', 'r') as f:
    context_job_title = f.read()


response_job_title = ollama.chat(
    model="llama3.2",
    messages=[
        {'role': 'system', 'content': "You are an AI specialized in extracting job details from HTML content."},
        {'role': 'system', 'content': f"This context contains examples of HTML and JSON output for the job title: {context_job_title}."},
        {'role': 'user', 'content': f"I am providing the HTML from a webpage for a job listing. Please return only the job title and it must be in JSON format. {html}"}
        ],
    format=JobTitle.model_json_schema(),
    options={'temperature': 0}
)

job_title = response_job_title['message']['content']

    
# Company Name
with open('scripts/ollama/query_context_companyname.txt', 'r') as f:
    context_company_name = f.read()


response_company_name = ollama.chat(
    model="llama3.2",
    messages=[
        {'role': 'system', 'content': "You are an AI specialized in extracting job details from HTML content."},
        {'role': 'system', 'content': f"This context contains examples of HTML and JSON output for the company name: {context_company_name}."},
        {'role': 'user', 'content': f"I am providing the HTML from a webpage for a job listing. Please return only the company name and it must be in JSON format. {html}"}
        ],
    format=CompanyName.model_json_schema(),
    options={'temperature': 0}
)

company_name = response_company_name['message']['content']


# Salary Floor
with open('scripts/ollama/query_context_salaryfloor.txt', 'r') as f:
    context_salary_floor = f.read()


response_salary_floor = ollama.chat(
    model="llama3.2",
    messages=[
        {'role': 'system', 'content': "You are an AI specialized in extracting job details from HTML content."},
        {'role': 'system', 'content': f"This context contains examples of HTML and JSON output for the salary floor: {context_salary_floor}."},
        {'role': 'user', 'content': f"I am providing the HTML from a webpage for a job listing. Please return only the salary floor and it must be in JSON format. If salary information is not available or is missing, return null in the JSON; salary information typically begins with a `$` dollar sign. Convert the salary to an integer value with the format 90,000. If the information is the format '$90K', convert to 90000. {html}"}
        ],
    format=SalaryFloor.model_json_schema(),
    options={'temperature': 0}
)

salary_floor = response_salary_floor['message']['content']


# Salary Ceiling
with open('scripts/ollama/query_context_salaryceiling.txt', 'r') as f:
    context_salary_ceiling = f.read()


response_salary_ceiling = ollama.chat(
    model="llama3.2",
    messages=[
        {'role': 'system', 'content': "You are an AI specialized in extracting job details from HTML content."},
        {'role': 'system', 'content': f"This context contains examples of HTML and JSON output for the salary ceiling: {context_salary_ceiling}."},
        {'role': 'user', 'content': f"I am providing the HTML from a webpage for a job listing. Please return only the salary ceiling and it must be in JSON format. If salary information is not available or is missing, return null in the JSON; salary information typically begins with a `$` dollar sign. Convert the salary to an integer value with the format 90,000. If the information is the format '$90K', convert to 90000. {html}"}
        ],
    format=SalaryCeiling.model_json_schema(),
    options={'temperature': 0}
)

salary_ceiling = response_salary_ceiling['message']['content']


# Office Status

with open('scripts/ollama/query_context_officestatus.txt', 'r') as f:
    context_office_status = f.read()


response_office_status= ollama.chat(
    model="llama3.2",
    messages=[
        {'role': 'system', 'content': "You are an AI specialized in extracting job details from HTML content."},
        {'role': 'system', 'content': f"This context contains examples of HTML and JSON output for the office status: {context_office_status}."},
        {'role': 'user', 'content': f"I am providing the HTML from a webpage for a job listing. Please return only the office status. {html}"}
        ],
    format=OfficeStatus.model_json_schema(),
    options={'temperature': 0}
)

office_status = response_office_status['message']['content']


# Office Location
with open('scripts/ollama/query_context_location.txt', 'r') as f:
    context_location = f.read()


response_location= ollama.chat(
    model="llama3.2",
    messages=[
        {'role': 'system', 'content': "You are an AI specialized in extracting job details from HTML content."},
        {'role': 'system', 'content': f"This context contains examples of HTML and JSON output for the location: {context_location}."},
        {'role': 'user', 'content': f"I am providing the HTML from a webpage for a job listing. Please return only the location. If the office_status is remote, then you should return the location as null; here is the office_status: {office_status}. Here is the job posting: {html}"}
        ],
    format=Location.model_json_schema(),
    options={'temperature': 0}
)

location = response_location['message']['content']



print(job_title, company_name, salary_floor, salary_ceiling, office_status, location)


