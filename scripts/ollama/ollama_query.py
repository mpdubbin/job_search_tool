from dotenv import load_dotenv
from module_ollama_query import * 

import os

test_url = "https://arkeabio.bamboohr.com/careers/48"

env_variables = load_env_variables()

ATTRIBUTES_DICT = {
    'job_title': JobTitle,
    'company_name': CompanyName,
    'salary_floor': SalaryFloor,
    'salary_ceiling': SalaryCeiling,
    'office_status': OfficeStatus,
    'location': Location
}

html = webpage_call(test_url, env_variables['linkedin_username'], env_variables['linkedin_password'])

for key, value in ATTRIBUTES_DICT.items():
    print(ollama_chat(env_variables, key, value, html))