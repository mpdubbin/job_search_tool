# job_info_from_link

Build a tool that pulls job posting webpages, extracts structured information (e.g., organization name, job title, salary range), and then saves these details into a local database.

**Key Components & Technologies:**

- **Web Scraping & Parsing:**
    
    Use Python with libraries like **requests** and **BeautifulSoup** or **Selenium** to fetch job postings.
    
- **LLM-based Extraction:**
    
    Feed the job posting HTML into **Ollama. Use** a retrieval-augmented generation (RAG) process that extracts key attributes based on pre-parsed (by me) example job postings (so I will pass Ollama the pre-screened HTML and the pre-parsed attributes as JSON).
    
- **Data Storage:**
    
    Save the extracted information into a **SQLite** database (or via **SQLAlchemy** for ORM capabilities).
