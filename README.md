# job_search_tool

## Project Background  
In the flooded tech market of early 2025 (hopefully future me will look back and laugh at how quickly I landed a job during this time) I knew I had to apply to tens if not hundreds of jobs. My personal machine is a MacBook Pro, so I use a Numbers spreadsheet to track my job application and networking progress. I find a job posting then copy and paste attributes from that job posting into a Numbers table. It's tedious, though it's really not that tedious, but as [Perl author Larry Wall said](https://www.brainyquote.com/quotes/larry_wall_141510), "the three chief virtues of a programmer are: Laziness, Impatience and Hubris." And, while thinking about copying and pasting over and over again for the next few months, both that third attribute and this meme came to mind:

![](assets/readme/0cm6yx27tez21.jpg)


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

Great, time to scrape webpages and see how many tokens they contain.

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

Well above the 151k maximum context window. The two LinkedIn postings, jobs 1 and 8, have the most tokens and can easily be parsed down - they HTML includes all of the sidebar:

![linkedin sidebar](assets/readme/Screenshot%202025-03-12%20at%2012.46.52 PM.png)

However, even with these two removed, the total is still well above 151k (~230k). I can either: reduce the amount of jobs to bring into context, or spend a little more time figuring out patterns. I chose option 2 spent some time in the DOM and .html files to figure out similarities, so that instead of pulling all of the webpage I can target attributes. 

I first looked at the LinkedIn posts and see that over half of the webpage is in \<meta>, \<script>, and \<link> tags, and manually checked to see if they contained any important information (they didn't). With the reduced .html files in hand, I reasked ChatGPT to count the tokens in each file, resulting in: 

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

Next, I manually parsed each job listing into JSON format, as described in the section above (`data/rag/manual_parse.json`). This is intended to be model context so refine the model's ability to understand what I'm looking for: job title, company name, etc. There was a slight complexity in that a few positions listed hourly rates instead of yearly salary, so those I multiplied the ceiling and floor values by 2,080 (8 hours/day * 5 days/week * 52 weeks/year). I'll have to prompt Ollama that if values are <$100 to multiply by 2,080. Also, some jobs listed multiple locations (like the Disney job [job_6]) with multiple salary ranges, so those must be output as a list. Eventually, I can add user location or allow the user to input desired locations (like, I prefer New York or east coast opportunities).

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


















README In Progress
---

## Future Features:

- User location or allow the user to input desired locations
    - Preference for a specific city or region
- Networking tracker:
    - Contact A recommended Job A
    - Contact B connected me with Contact C who recommended Job B