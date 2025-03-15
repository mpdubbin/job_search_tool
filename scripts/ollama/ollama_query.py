from dotenv import load_dotenv
from module_ollama_query import * 
import ollama
import os


# Load environment variables
load_dotenv()
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# Test url, for testing purposes
test_url = "https://elderresearch.hrmdirect.com/employment/job-opening.php?req=3176662&req_loc=351584&&#job"
html = webpage_call(test_url, LINKEDIN_USERNAME, LINKEDIN_PASSWORD)


with open('scripts/ollama/query_context.txt', 'r') as f:
    context = f.read()


response = ollama.chat(
    model="llama3.2:latest",
    messages=[
        {'role': 'system', 'content': "You are an AI specialized in extracting job details from HTML content."},
        {'role': 'system', 'content': context},
        {'role': 'user', 'content': f"I am providing the HTML from a webpage for a job listing. Return the company name, job title, salary floor, salary ceiling, office status (in-office, hybrid, or remote), and job location in JSON format. Before you output your findings, ensure that what you found is actually present in the HTML. {html}"}
        ],
    format=JobDetails.model_json_schema(),
    options={'temperature': 0}
)


print(response['message']['content'])

    
