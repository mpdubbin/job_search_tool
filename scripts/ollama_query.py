import json 
import ollama


def load_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# Load JSON Data
with open("data/rag/manual_parse.json", "r", encoding="utf-8") as file:
    job_data = json.load(file)


# Add full HTML to context
context = "\n\n".join([
    "Testing scripts/ollama_query.py\n\n\n"
    "Unique Job Posting\n"
    "---\n"
    f"Company: {job['company']} ; Job Title: {job['job_title']}; "
    f"Office Status: {job['office_status']} ; Location: {job['office_location']} ;"
    f"Salary Floor: {job['salary_floor']} ; Salary Ceiling {job['salary_ceiling']} ; \n"
    f"Job Webpage:\n{load_html(job['html'])}\n\n"
    "---"
    for job in job_data
])

with open('data/rag/context_test_output_multiple.txt', 'w') as f:
    f.write(context)

# # Example query
# query = "What is the highest salary among these job postings?"

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
