from playwright.sync_api import sync_playwright

def get_full_page_html(url):
    with sync_playwright() as p:
        # Launch browser (set headless=False to see it working)
        browser = p.chromium.launch(headless=False)  
        page = browser.new_page()

        # Navigate to the URL
        page.goto(url, wait_until="load")  # Wait for full page load

        # Optional: Scroll to trigger lazy loading (if needed)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        # Wait for additional content to load
        page.wait_for_timeout(5000)  # Adjust timeout as needed

        # Get the full page HTML
        full_html = page.content()

        # Save to file (optional)
        with open("full_page.html", "w", encoding="utf-8") as f:
            f.write(full_html)

        print("✅ Page saved successfully!")
        browser.close()

        return full_html

# URL to scrape
url = "https://careers.guitarcenter.com/jobs/15485512-senior-data-analyst"

# Get full HTML
html = get_full_page_html(url)

with open(f"scripts/guitarcenter.html", "w", encoding="utf-8") as f:
        f.write(html)