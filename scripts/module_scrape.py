from playwright.sync_api import sync_playwright

def get_full_page_html(url: str, LINKEDIN_USERNAME: str, LINKEDIN_PASSWORD, str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) # Must be false for cloudflare
        page = browser.new_page()

        # Navigate to the URL
        page.goto(url, wait_until="load")  # Wait for full page load

        # Scroll to trigger lazy loading
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        # Wait for additional content to load
        page.wait_for_timeout(5000) 

        full_html = page.content()

        browser.close()

        return full_html
    

def get_full_page_url_linkedin(url: str, linkedin_username: str, linkedin_password: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Must be False for Cloudflare
        page = browser.new_page()

        # Navigate to LinkedIn login page
        page.goto("https://www.linkedin.com/login", wait_until="load")

        # Ensure the login form is visible
        page.wait_for_selector("input#username")

        # Fill in login credentials
        page.fill("input#username", linkedin_username)
        page.fill("input#password", linkedin_password)

        # Press Enter to submit login form
        page.keyboard.press("Enter")

        # Wait for login to complete (redirects to feed or another page)
        page.wait_for_timeout(5000)  # Adjust as necessary

        # Navigate to the target URL
        page.goto(url, wait_until="load")

        # Scroll to trigger lazy loading
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        # Wait for additional content to load
        page.wait_for_timeout(5000)

        # Get full HTML content
        full_html = page.content()

        browser.close()

        return full_html
