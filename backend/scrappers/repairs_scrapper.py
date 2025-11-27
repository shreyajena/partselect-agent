import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ACCESS_DENIED_MARKER = "Access Denied"
POPUP_KEYWORDS = ("decline", "close", "continue")


def extract_section_text(section_div):
    """Extract <p> and list text from the left column."""
    left_col = section_div.select_one("div.col-lg-6")
    if not left_col:
        left_col = section_div

    text_parts = []
    for p in left_col.find_all("p"):
        content = p.get_text(" ", strip=True)
        if content:
            text_parts.append(content)

    for ol in left_col.find_all("ol"):
        for li in ol.find_all("li"):
            content = li.get_text(" ", strip=True)
            if content:
                text_parts.append(f"• {content}")

    return "\n".join(text_parts).strip()


def setup_driver():
    """Configure Chrome for scraping with anti-detection options."""
    options = Options()
    user_agent = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--accept-language=en-US,en;q=0.9")
    options.add_argument(
        "--accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    )
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    import tempfile
    import os

    temp_dir = os.path.join(tempfile.gettempdir(), f"chrome_temp_{os.getpid()}")
    options.add_argument(f"--user-data-dir={temp_dir}")
    options.page_load_strategy = "normal"

    driver = webdriver.Chrome(options=options)
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
    driver.set_script_timeout(30)
    driver.implicitly_wait(20)
    return driver


def dismiss_popup(driver):
    """Close marketing popups such as email capture dialogs."""
    try:
        controls = driver.find_elements(By.XPATH, "//button | //a")
        for control in controls:
            try:
                label = control.text.strip().lower()
                if label and any(keyword in label for keyword in POPUP_KEYWORDS):
                    if control.is_displayed():
                        control.click()
                        time.sleep(1)
                        return
            except Exception:
                continue
    except Exception:
        pass


def load_page(driver, url, max_retries=3, cooldown=8):
    """Navigate to a repair page with retries when Akamai blocks us."""
    for attempt in range(1, max_retries + 1):
        driver.get(url)
        time.sleep(3)
        page_source = driver.page_source
        if ACCESS_DENIED_MARKER not in page_source:
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
                )
            except Exception:
                pass
            dismiss_popup(driver)
            return True

        print(f"Access denied detected (attempt {attempt}/{max_retries}). Retrying after cooldown...")
        time.sleep(cooldown)
    return False


def scrape_repair_page(driver, url, appliance_type, symptom_name):
    """Scrape a single repair article."""
    if not load_page(driver, url):
        raise RuntimeError("Failed to load repair page due to access denial.")

    soup = BeautifulSoup(driver.page_source, "html.parser")

    result = {
        "appliance": appliance_type,
        "symptom": symptom_name,
        "url": url,
        "title": "",
        "difficulty": "",
        "description": "",
        "sections": [],
    }

    h1 = soup.select_one("h1")
    result["title"] = h1.text.strip() if h1 else symptom_name

    diff_li = soup.select_one("ul.list-disc li")
    if diff_li:
        result["difficulty"] = diff_li.text.replace("Rated as", "").strip()

    intro = soup.select_one("div.repair__intro p")
    result["description"] = intro.text.strip() if intro else ""

    # Primary layout: h2.section-title + content
    section_titles = soup.select("h2.section-title")
    if section_titles:
        for heading in section_titles:
            sec_title = heading.text.strip()
            desc_block = heading.find_next_sibling("div", class_="symptom-list__desc")
            if not desc_block:
                continue
            text = extract_section_text(desc_block)
            result["sections"].append({"title": sec_title, "text": text})
    else:
        # Fallback layout: repair__cause blocks
        causes = soup.select("div.repair__cause")
        for section in causes:
            sec_title_el = section.select_one("h3")
            sec_title = sec_title_el.text.strip() if sec_title_el else "Unknown Section"
            paragraphs = section.select("p")
            full_text = "\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
            result["sections"].append({"title": sec_title, "text": full_text})

    return result


def scrape_multiple_repairs(driver, repair_urls, appliance_type):
    results = []
    for url, symptom in repair_urls:
        print(f"Scraping: {symptom} → {url}")
        try:
            data = scrape_repair_page(driver, url, appliance_type, symptom)
            results.append(data)
            time.sleep(1)
        except Exception as exc:
            print("Error:", exc)
    return results


if __name__ == "__main__":

    #For Dishwasher
#     REPAIR_URLS = [
#         ("https://www.partselect.com/Repair/Dishwasher/Noisy/", "Noisy"),
#         ("https://www.partselect.com/Repair/Dishwasher/Leaking/", "Leaking"),
#         ("https://www.partselect.com/Repair/Dishwasher/Will-Not-Start/", "Will_Not_Start"),
#         ("https://www.partselect.com/Repair/Dishwasher/Door-Latch-Failure/","Door-Latch-Failure"),
#         ("https://www.partselect.com/Repair/Dishwasher/Not-Cleaning-Properly/", "Not_Cleaning_Properly"),
#         ("https://www.partselect.com/Repair/Dishwasher/Not-Draining/", "Not_Draining"),
#         ("https://www.partselect.com/Repair/Dishwasher/Will-Not-Fill-Water/", "Will_Not_Fill_Water"),
#         ("https://www.partselect.com/Repair/Dishwasher/Will-Not-Dispense-Detergent/", "Will_Not_Dispense_Detergent"),
#         ("https://www.partselect.com/Repair/Dishwasher/Not-Drying-Properly/", "Not_Drying_Properly")
# ]
    # appliance_type = "Dishwasher"

    REPAIR_URLS = [
    ("https://www.partselect.com/Repair/Refrigerator/Noisy/", "Noisy"),
    ("https://www.partselect.com/Repair/Refrigerator/Leaking/", "Leaking"),
    ("https://www.partselect.com/Repair/Refrigerator/Will-Not-Start/", "Will_Not_Start"),
    ("https://www.partselect.com/Repair/Refrigerator/Not-Making-Ice/", "Not_Making_Ice"),
    ("https://www.partselect.com/Repair/Refrigerator/Refrigerator-Too-Warm/", "Refrigerator_Too_Warm"),
    ("https://www.partselect.com/Repair/Refrigerator/Not-Dispensing-Water/", "Not_Dispensing_Water"),
    ("https://www.partselect.com/Repair/Refrigerator/Refrigerator-Freezer-Too-Warm/", "Freezer_Too_Warm"),
    ("https://www.partselect.com/Repair/Refrigerator/Door-Sweating/", "Door_Sweating"),
    ("https://www.partselect.com/Repair/Refrigerator/Light-Not-Working/", "Light_Not_Working"),
    ("https://www.partselect.com/Repair/Refrigerator/Refrigerator-Too-Cold/", "Refrigerator_Too_Cold"),
    ("https://www.partselect.com/Repair/Refrigerator/Running-Too-Long/", "Running_Too_Long"),
    ("https://www.partselect.com/Repair/Refrigerator/Freezer-Too-Cold/", "Freezer_Too_Cold")
]
    appliance_type = "Refrigerator"

    driver = setup_driver()
    try:
        data = scrape_multiple_repairs(driver, REPAIR_URLS, appliance_type)
        time.sleep(3)
    finally:
        driver.quit()

    with open("Refrigerator_repair_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("\nSaved to Refrigerator_repair_data.json")
