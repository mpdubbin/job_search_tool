# job_search_tool

## Project Background  
In the flooded tech market of early 2025 (hopefully future me will look back and laugh at how quickly I landed a job during this time) I knew I had to apply to tens if not hundreds of jobs. My personal machine is a MacBook Pro, so I use a Numbers spreadsheet to track my job application and networking progress. I find a job posting then copy and paste attributes from that job posting into a Numbers table. It's tedious, though it's really not that tedious, but as [Perl author Larry Wall said](https://www.brainyquote.com/quotes/larry_wall_141510), "the three chief virtues of a programmer are: Laziness, Impatience and Hubris." And, while thinking about copying and pasting over and over again for the next few months, both that third attribute and this meme came to mind:

![programmer automation meme](assets/readme/0cm6yx27tez21.jpg)

This is the basic outline of the project.
![basic outline](assets/readme/Screenshot%202025-03-20%20at%2010.41.09 AM.png)

## Flow-of-Thought Walkthrough

My initial vision was a Numbers plug-in, where, when I pasted a job url into a cell in Numbers, the other fields (job title, company name, salary, etc.) would autopopulate. That way I keep the familiarity of Numbers and reduce the time spent copying and pasting (that meme is staring straight at me).   

I've used [openpyxl](https://pypi.org/project/openpyxl/) before for Microsoft Excel interaction, and looked up if something similar exists for Apple. I discovered [AppleScript](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/introduction/ASLR_intro.html) and a Python package [py-applescript](https://github.com/rdhyee/py-applescript) - as of March 10, 2025, `py-applescript` hasn't been updated in over two years. Ok, maybe it would be easier to make a simple [Shiny](https://shiny.posit.co/py/) or [Dash](https://pypi.org/project/dash/) application... 

But first, I need to get the actual data I want to input.

---
In my first brainstorming session I came up with the following steps:

#### **1. Web Scraping**

- Use **`requests` + `BeautifulSoup`** for simple static pages.
- If dynamically loaded, use Selenium (like my other repo `job_update`, where the page looked static but wasn't actually).
- Create a scraping pipeline that fetches and parses the HTML content from a URL input.

#### **2. Parsing and LLM-based Extraction (Ollama + RAG)**

- Pre-parse 10 job postings (manually extract the desired attributes) to use as context for Ollama, and store in JSON
```JSON
{
    "html": "<div class=\"job-title\">Donut Delicatessen</div><div class=\"company-name\">Dubbin's Delicious Donut Dispensary</div><div class=\"location\">Donutland, Delaware</div>",
    "job_title": "Donut Delicatessen",
    "company_name": "Dubbin's Delicious Donut Dispensary",
    "location": "Donutland, Delaware"
}
```

- Pass JSON job postings into Ollama as context

#### **3. Data Storage**

- Store extracted job data in SQLite -> need data to be in row-form no matter the output  

|job_title|company_name|location|
|---|---|---|
|Donut Delicatessen|Dubbin's Delicious Donut Dispensary|Donutland, Delaware|

#### **4. Data Visualization**

- Use Python Shiny? Maybe Dash? Maybe AppleScript?
- If Shiny or Dash: display a table of extracted jobs with filtering, sorting, and CRUD operations. Else, autopopulate Numbers table.
- Add simple analytics like job counts by company or average salary ranges.

## 1. Web Scraping & Parsing

To start, I looked at the [DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction) of 10 of the jobs that I applied to (links in `data/rag/job_urls.txt`, though by the time you're reading this they may be 404ed) to observe any pattern in attributes (job title company name) tags. I observed that some of the attribute locations across job sites were rather consistent:
- job titles in h1 or h2 tags
- job description in p tags

Some, though, were not:
- company names are all over the place. And some websites only had the company name in a logo (image, not text) with the in the description. 
- salary is sometimes at the top of the page in a table, sometimes at the bottom of the page, and, often, not listed at all

Therefore, for job title and job description, perhaps I could write a script that pulls all h1, h2 and p tags. But the other attributes would require some more advanced semantics. And what's good at that? [Artificial Intelligence](https://www.geeksforgeeks.org/semantic-networks-in-artificial-intelligence/)! 

<u>Question</u>: can I put the whole scraped HTML page in a local instance of Ollama as context? Can I put all 10 scraped HTML pages as context? I'm working with an M3 Pro chip and 18GB RAM. I have the llama3.2 model installed and asked it it's context window:

> My context window is 131k tokens.

Ok, time to scrape webpages and see how many tokens they contain.

### Selenium/Playwright

I wrote a simple script using [Selenium ](https://selenium-python.readthedocs.io/) that waited for the page to load and then pulled the whole webpage. This worked for a few of the job postings, but others, like LinkedIn, required a login, and still others were protected from scraping by security tools.

While I'm familiar with Selenium and used it to log in to websites before, I've never used [Playwright](https://playwright.dev/) before, and read that it is quite robust. 

After some tinkering I was able to successfully pull all job posting webpages (`scripts/module_scrape.py`) and saved them to `data/rag/raw_html`.

## 2. Parsing and LLM-based Extraction (Ollama + RAG)  

To answer the question above, I asked ChatGPT to give me the number of tokens in each HTML file:

| File | Token Count |
|---|---|
| job_0.html | 4036 |
| job_1.html | 12578 |
| job_2.html | 1645 |
| job_3.html | 39067 |
| job_4.html | 16577 |
| job_5.html | 4936 |
| job_6.html | 15259 |
| job_7.html | 7677 |
| job_8.html | 11704 |
| job_9.html | 9467 |

Resulting in a total token count of 122,946 which falls below the 151,000 maximum specified by Ollama, leaving room to spare for the structured JSON component. 

However, the following day I asked ChatGPT again how many tokens were in each file and it responded with these values:

| File | Token Count |
|---|---|
| job_0.html | 6302 |
| job_1.html | 153545 |
| job_2.html | 3908 |
| job_3.html | 72881 |
| job_4.html | 50431 |
| job_5.html | 6996 |
| job_6.html | 49313 |
| job_7.html | 22355 |
| job_8.html | 152252 |
| job_9.html | 18006 |

Well above the 151k maximum context window. The two LinkedIn postings, jobs 1 and 8, have the most tokens and can easily be parsed down - their HTML includes all of the sidebar:

![linkedin sidebar](assets/readme/Screenshot%202025-03-12%20at%2012.46.52 PM.png)

However, even with these two LinkedIn posts removed from the analysis, the total is still well above 151k (~230k). I can either: reduce the amount of jobs to bring into context, or spend a little more time figuring out patterns. As I am in exploratory mode, I chose option 2 and spent time in the DOM and .html files to figure out similarities, so that instead of pulling all of the webpage I can target attributes for lower token counts. 

I first looked at the LinkedIn posts and see that over half of the webpage is in \<meta>, \<script>, and \<link> tags, and manually checked to see if they contained any important information (they didn't). I wrote a Playwright script that pulled everything that isn't in one of those three tags. With the reduced .html files in hand I reasked ChatGPT to count the tokens in each file, resulting in: 

| File | Token Count |
|---|---|
| job_0.html | 3021 |
| job_1.html | 3629 |
| job_2.html | 1268 |
| job_3.html | 1193 |
| job_4.html | 15694 |
| job_5.html | 1933 |
| job_6.html | 8127 |
| job_7.html | 1420 |
| job_8.html | 3654 |
| job_9.html | 749 |

Ok, promising! 

### Manual Parsing

Next, I manually parsed each job listing into JSON format, as described in the section above (`data/rag/manual_parse.json`). This is intended to be model context to refine the model's ability to understand what I'm looking for: job title, company name, etc. There was a slight complexity in that a few positions listed hourly rates instead of yearly salary, so those I multiplied the ceiling and floor values by 2,080 (8 hours/day * 5 days/week * 52 weeks/year). I'll have to prompt Ollama that if values are <$100 to multiply by 2,080. Also, some jobs listed multiple locations (like the Disney job [job_6]) with multiple salary ranges, so those must be output as a list. Eventually, I can add user location or allow the user to input desired locations (like, I prefer New York or east coast opportunities).

After that I manually CMD + F'ing each file to see if the necessary information is present.

| File | Necessary Information? |
|---|---|
| job_0.html | 1 |
| job_1.html | 1 |
| job_2.html | 1 |
| job_3.html | 1 |
| job_4.html | 1 |
| job_5.html | 1 |
| job_6.html | 1 |
| job_7.html | 1 |
| job_8.html | 1 |
| job_9.html | 1 |

Even more promising!

## Passing Context to Ollama

I first tried this code to pass the context (JSON) and query:

```python
# Test url, for testing purposes
test_url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4182517296"
query_html = webpage_call(test_url, LINKEDIN_USERNAME, LINKEDIN_PASSWORD)


# Example query
query = f"With this HTML of a job posting as input, return the company name, job title, salary floor, salary ceiling, office status (in-office/hybrid/remote), and job location in table format, like so: |Company Name|Job Title|Salary Floor|Salary Ceiling|Office Status|Office Location|. If the salary floor and salary ceiling are less than $100, then please multiply those values bo 2080. If there are multiple locations, please output the values as a list, like |Austin, TX; San Francisco, CA|. If those different locations have different salaries, please format the same way as the location, in the same order, like so: |Austin, TX ; San Francisco, CA|80,000 ; 90,000|. Please only return a response in that table format. Here is the job posting: {query_html}"

# Pass the context and query to Ollama
response = ollama.chat(
    model="mistral",
    messages=[
        {"role": "system", "content": "You are an AI assistant helping with job webpage analysis."},
        {"role": "user", "content": f"Here is job data:\n{context}\n\n{query}"}
    ]
)
```
This was not successful. Both mistral and llama3.2 models returned responses explaining much more than I asked for, and also none of what I asked for. Here is the llama3.2 response:

```txt
This is a comprehensive overview of Siemens Healthineers, a leading medical technology company with over 125 years of experience. Here are some key takeaways:

**Company Overview**

* Siemens Healthineers is a global leader in healthcare technology, with over 71,000 employees in over 70 countries.
* The company's portfolio includes in vitro and in vivo diagnostics, image-guided therapy, and cancer care, which is crucial for clinical decision-making and treatment pathways.

**Diversity, Equity, and Inclusion**

* Siemens Healthineers strives to be an attractive employer for talented individuals regardless of their background or protected characteristics.
* The company aims to promote diversity, equity, and inclusion in its workforce and operations.

**Environmental Sustainability**

* Siemens Healthineers is committed to reducing its collective emissions along the value chain and driving decarbonization.
* The company aims to achieve net zero by promoting circularity in its products and processes.

**Social Impact**

* Siemens Healthineers focuses on making healthcare accessible and affordable for patients everywhere, especially in remote regions.
* The company contributes to addressing the workforce skills gap by providing education and training to healthcare professionals worldwide.

**Hiring Trends**

* Siemens Healthineers hires candidates from a variety of sources, including the FDA and University of Maryland.
* The company operates in a highly competitive medical technology landscape with key competitors like GE Healthcare, Medtronic, and Philips Healthcare.

**Insights into the Company's Commitments**

* Siemens Healthineers is committed to promoting diversity, equity, and inclusion in its workforce and operations.
* The company aims to reduce its environmental impact through decarbonization and circularity initiatives.
* Siemens Healthineers prioritizes social impact by making healthcare accessible and affordable for patients everywhere.

**Job Opportunities**

* Siemens Healthineers offers a range of job opportunities across various fields, including engineering, IT, and sales.
* The company's hiring trends suggest that it is actively seeking talented individuals to join its workforce.

Overall, Siemens Healthineers appears to be a committed and values-driven organization that prioritizes diversity, equity, inclusion, environmental sustainability, and social impact. If you're considering working for the company or applying for one of its job openings, this overview provides valuable insights into its culture and mission.
```

... After a few hours of prompt engineering, I discovered that the context I was giving Ollama was really confusing it. It kept giving answers that didn't contain any information, or incorrect information, or responded with a lot of extraneous information. So I removed all context (I'm leaving the context in the repo `data/context_obsolete` because it was a good exercise in figuring out which attributes were and weren't useful for containing relevant information) and simply asked llama3.2 to read the condensed HTML and summarize it:

```python
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

# Pass the context and query to Ollama
summary_response = ollama.chat(
    model="llama3.2",
    messages=[
        {"role": "system", "content": "You are an AI assistant helping with job webpage analysis."},
        {"role": "user", "content": f"{query_summary}"}
    ]
)

# Print the response
print(summary_response["message"]["content"])
"""
```
This worked great. And the response was more accurate, and quicker, with llama3.2 than with mistral. The next step is to pass that summary to another query, asking Ollama to structure the output into JSON (so I can convert it to a table for the future user interface).

### The Next Day
After quite a bit of testing and rewording the prompt, I discovered that there was real inconsistencies in what Ollama was returning: sometimes *most* of the attributes were pulled and structured correctly, but most of the time Ollama returned incorrect information or stated that information was missing when it was clearly present in the source. So after resonating with this poor fellow:

![prompt engineering meme](assets/readme/prompt_engineer.png)

I read [this resource](https://www.promptingguide.ai/) on prompt engineering techniques. Because I already put in the work for context, I gravitated towards [few-shot prompting](https://www.promptingguide.ai/techniques/fewshot). 

I went back through the raw job postings and listed out all of the tags that the information was contained in (`scripts/ollma/query_context.txt`). From this, I created the context with fewer, but specific, HTML tags and corresponding desired job details in JSON format. I returned to [the basics]((https://github.com/ollama/ollama-python/blob/main/examples/structured-outputs.py), instead of the ChatGPT monstrosity I created.

This is still producing inconsistent output. Will troubleshoot (3/15/2025).

After some more YouTube videos, articles, and conversations with developer friends, here are some ideas for improving the AI's response:
- ask for only 1 item at a time (rather than full Json, only 1 key. Then make a bunch of separate queries)
- put the instructions in the "system prompt" (rather than the user-prompt, so the overload of html doesn't confuse it, and it forgets what you want it to do)
- split the html into a few chunks, and it can answer with the answer or NULL. Then you piece it together in a for-loop

I will try those now.

Llama3.2 on my 18GB RAM machine is still getting confused with job postings with JavaScript-heavy elements and SVGs. I am going to revert back to pulling partial webapges instead of entire webpages and try the updated prompting methods.

**Final Prompting Update**
I provide the prompts located in `data/context` to ollama. I discovered that combining options 1 & 2 above gave the most accurate responses. There are still issues with the following two types of job postings:
1. job postings with multiple locations. This would require some additional prompt engineering.
2. Job postings with no salary listed. Llama3.2 defaults to the salary I provided in the context example. This would require some additional prompt engineering.

I decided to allow these errors for the first pass of this project, because in actuality I would use a more robust model's API (I input these raw html files into ChatGPT 4.o and it returned the job posting details flawlessly) rather than these small local models. In the GUI tool I plan to add a feature that, after Ollama pulls the job details, the user can edit the details before inserting it into the table. [Good Enough, Proceed On](https://www.lizardbrain.com/blog/2016/10/10/2016-10-10-gepo-and-fpo). 

## The GUI
The idea now is to create a tool where the user can input a url, press go, and have the job details there automically for a table, such as this:

|Organization|Role|Website|Salary Floor|Salary Ceiling|Office Status|Location|Application Status|
|---|---|---|---|---|---|---|--|
|Donut Delicatessen|Dubbin's Delicious Donut Dispensary|dubbinsdonuts.com|10000|20000|In-Office|Donutland, DE|Applied|
|Dorito's Devourer|Dubbin's Delicious Dorito's Dispensary|dubbinsoritos.com|20000|30000|Remote||Rejected|

I'm going with Python Shiny. 

I actually wrote out all of the jobs I've applied to (and have been rejected from) but don't want to put any companies on blast with their rejection of a great candidate. So I prepopulated the example table with random ones from ChatGPT, added it to a .csv file, and created the table in Shiny (with automatic filters) using that .csv file. I then reworked the ollama_chat() function for compatability with Shiny (i.e., change from an executable script to a straight-up function), to which I configured Shiny to output Ollama's response in the GUI for debugging purposes. Below is the current stage of the product, with the filterable data table and the Ollama output of a job listing.

![ollama output and example data table from .csv file](assets/readme/Screenshot%202025-03-20%20at%2011.15.53 AM.png)

Three main tasks left for the MVP:
1. Allow the user to edit the Ollama output (if Ollama returned incorrect information, for example if Ollama returned an incorrect salary_floor)
2. Add that information to a new line in the table
3. Turn the table and GUI into a CRUD app using SQLite

This took a little finagling with Shiny, but the Ollama output is now output into an editable textfield *prior* to being added in the database. The user enters the URL, waits for the Ollama response which is output in the text field, can edit the text field, and then adds the data to the database (and therefore the table) with the "Save to Table" button. I also added a search bar that searches the entire table for capital-agnostic text.

![table output](assets/readme/Screenshot%202025-03-20%20at%204.52.27 PM.png)

So main task 1 and 2 are complete. And half of 3 is complete: I still need to develop the **U** and **D** functionality, which is especially important for updating the application status.

README In Progress
---

## Future Features:

- User location or allow the user to input desired locations
    - Preference for a specific city or region
- Networking tracker:
    - Contact A recommended Job A
    - Contact B connected me with Contact C who recommended Job B