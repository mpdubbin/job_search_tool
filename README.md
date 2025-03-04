# job_search_tool

**Overview:**

Build a tool that scrapes job posting webpages, extracts structured information (e.g., organization name, job title, salary range), and then saves these details into a local database.

### **1. Web Scraping & Parsing**

- Use **`requests` + `BeautifulSoup`** for simple static pages.
- Use **Selenium** if you need to interact with JavaScript-heavy sites.
- Implement a **scraping pipeline** that extracts job posting URLs, then fetches and parses the HTML content.

### **2. LLM-based Extraction (Ollama + RAG)**

- Store **pre-parsed example job postings** (HTML → JSON) in a local vector database (e.g., **FAISS or ChromaDB**).
- Pass scraped job postings into **Ollama**, retrieving the closest pre-parsed example as context for structured extraction.
- Use **Pydantic** or a JSON schema to validate extracted attributes (e.g., `organization_name`, `job_title`, `salary_range`).

### **3. Data Storage**

- Store extracted job data in **SQLite** (or PostgreSQL if scaling).
- Use **SQLAlchemy ORM** for easy querying & manipulation.
- Implement **CRUD operations** to modify job entries manually.

### **4. Data Visualization**

- Use **Python Shiny** (simpler) or **Dash** (more control).
- Display a **table** of extracted jobs with filtering, sorting, and CRUD operations.
- Add **simple analytics**, like job counts by company or average salary ranges.

Future Features:

- Add a networking feature:
    - Contact A recommended Job A
    - Contact B connected me with Contact C who recommended Job B
