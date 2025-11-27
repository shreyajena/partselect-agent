import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup
import tempfile


# ----------------------------------------------------------
# SETUP DRIVER
# ----------------------------------------------------------

def setup_driver():
    """Set up a Chrome WebDriver with appropriate options."""
    print("Setting up Chrome WebDriver...")
    
    chrome_options = Options()
    user_agent = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(f"--user-agent={user_agent}")
    chrome_options.add_argument("--accept-language=en-US,en;q=0.9")
    chrome_options.add_argument(
        "--accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    )
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    temp_dir = tempfile.mkdtemp(prefix="blog_chrome_")
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")
    print(f"Using temporary directory: {temp_dir}")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_cdp_cmd(
            "Network.setUserAgentOverride", {"userAgent": user_agent}
        )
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """
            },
        )
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(20)
        print("Chrome WebDriver setup successful")
        return driver
    except Exception as e:
        print(f"Error setting up Chrome WebDriver: {e}")
        return None


# ----------------------------------------------------------
# NAVIGATION + HELPERS
# ----------------------------------------------------------

def safe_navigate(driver, url, max_retries=3):
    """Safely navigate with retry and anti-access-denied logic."""
    for attempt in range(max_retries):
        try:
            print(f"Navigating to {url} (attempt {attempt+1}/{max_retries})")
            driver.get(url)

            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            if "Access Denied" in driver.title or "Forbidden" in driver.title:
                print("Access denied, retrying...")
                time.sleep(random.uniform(5, 10))
                continue

            time.sleep(3)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            return True

        except Exception as e:
            print(f"Navigation error: {e}")
            time.sleep(random.uniform(2, 5))

    return False


# ----------------------------------------------------------
# SCRAPE SELECTED BLOGS
# ----------------------------------------------------------

def extract_sections(soup):
    container = soup.select_one("div.blog__article-page__content")
    if not container:
        return []

    sections = []
    current = None
    heading_tags = {"h2", "h3", "h4"}

    for child in container.children:
        tag = getattr(child, "name", None)
        if tag in heading_tags:
            if current and current["text"].strip():
                sections.append(current)
            current = {"heading": child.get_text(strip=True), "text": ""}
        elif current and hasattr(child, "get_text"):
            text = child.get_text(" ", strip=True)
            if text:
                if current["text"]:
                    current["text"] += " "
                current["text"] += text

    if current and current["text"].strip():
        sections.append(current)

    if not sections:
        sections.append(
            {
                "heading": "Summary",
                "text": container.get_text(" ", strip=True),
            }
        )

    return sections


def scrape_single_blog(driver, url):
    """Navigate to a provided blog URL and extract structured sections."""
    if not safe_navigate(driver, url):
        print(f"Skipping {url} due to navigation failure.")
        return None

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    soup = None
    try:
        soup = BeautifulSoup(driver.page_source, "html.parser")
    except Exception as e:
        print(f"Failed to parse HTML for {url}: {e}")

    title = url
    if soup:
        header = soup.find("h1")
        if header:
            title = header.get_text(strip=True)

    sections = extract_sections(soup) if soup else []
    slug = url.rstrip("/").split("/")[-1] or "blog"
    blog_id = f"blog_{slug}"

    return {"id": blog_id, "title": title, "url": url, "sections": sections}


def scrape_selected_blogs(blog_urls):
    results = []
    driver = setup_driver()

    if not driver:
        print("WebDriver setup failed.")
        return results

    try:
        for idx, url in enumerate(blog_urls, 1):
            print(f"\nScraping blog {idx}/{len(blog_urls)}: {url}")
            data = scrape_single_blog(driver, url)
            if data:
                results.append(data)
            time.sleep(random.uniform(2, 4))
    finally:
        driver.quit()

    return results


# ----------------------------------------------------------
# SAVE RESULTS
# ----------------------------------------------------------

def save_to_json(blogs, filename):
    if not blogs:
        print("No blogs to save.")
        return

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(blogs, f, indent=2)

    print(f"\nSaved {len(blogs)} blogs to {filename}")


# ----------------------------------------------------------
# MAIN
# ----------------------------------------------------------

if __name__ == "__main__":
    BLOG_URLS = {
        "dishwasher": [
            "https://www.partselect.com/blog/dishwasher-cycle-guide/",
            "https://www.partselect.com/blog/how-to-reset-a-bosch-dishwasher/",
            "https://www.partselect.com/blog/how-to-clean-a-bosch-dishwasher/",
            "https://www.partselect.com/blog/why-dishwasher-stops-mid-cycle/",
            "https://www.partselect.com/blog/how-to-fix-frigidaire-dishwasher-not-draining/",
            "https://www.partselect.com/blog/how-to-clean-whirlpool-dishwasher-filter/",
            "https://www.partselect.com/blog/bosch-dishwasher-e22-error-code/",
            "https://www.partselect.com/blog/what-does-samsung-dishwasher-blinking-heavy-mean/",

        ],
        "refrigerator": [
            "https://www.partselect.com/blog/proper-fridge-temperature/",
            "https://www.partselect.com/blog/how-to-use-power-cool-on-a-samsung-fridge/",
            "https://www.partselect.com/blog/how-to-reset-a-frigidaire-refrigerator/",
            "https://www.partselect.com/blog/how-to-fix-a-torn-refrigerator-door-seal/",
            "https://www.partselect.com/blog/how-to-replace-lg-refrigerator-water-filter/",
            "https://www.partselect.com/blog/bosch-ice-maker-not-working/",
            "https://www.partselect.com/blog/refrigerator-tripping-breaker/",
            "https://www.partselect.com/blog/repair-or-replace-refrigerator-shelf/",
            "https://www.partselect.com/blog/ge-refrigerator-tf-tc-code/"
        ],
    }

    print("\nStarting PartSelect blog scraper (selected URLs)...\n")

    for category, urls in BLOG_URLS.items():
        print(f"\nProcessing {category} blogs...")
        blogs = scrape_selected_blogs(urls)
        if blogs:
            output_file = f"{category}_blogs.json"
            print(f"\nTotal blogs collected for {category}: {len(blogs)}")
            save_to_json(blogs, output_file)
        else:
            print(f"No blogs collected for {category}.")
