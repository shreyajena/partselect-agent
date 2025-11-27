import time
import csv
import json
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PAGE_LOAD_RETRIES = 3
RETRY_COOLDOWN = 8
ACCESS_DENIED_MARKER = "Access Denied"


def setup_driver():
    options = Options()
    user_agent = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"--user-agent={user_agent}")
    options.add_argument("--accept-language=en-US,en;q=0.9")
    options.add_argument(
        "--accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    temp_dir = tempfile.mkdtemp(prefix="parts_chrome_")
    options.add_argument(f"--user-data-dir={temp_dir}")

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent})
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
    return driver


def scroll(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/1.5);")
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)


def el(driver, selector):
    try:
        return driver.find_element(By.CSS_SELECTOR, selector)
    except:
        return None


def els(driver, selector):
    try:
        return driver.find_elements(By.CSS_SELECTOR, selector)
    except:
        return []


def load_cross_reference(driver):
    container = el(driver, "div.pd__crossref__list")
    if not container:
        return []

    last_count = 0
    stagnant_loops = 0
    while stagnant_loops < 3:
        rows = container.find_elements(By.CSS_SELECTOR, "div.row")
        if not rows:
            break
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", container)
        time.sleep(1)
        current_count = len(container.find_elements(By.CSS_SELECTOR, "div.row"))
        if current_count == last_count:
            stagnant_loops += 1
        else:
            stagnant_loops = 0
            last_count = current_count

    cross_refs = []
    for row in container.find_elements(By.CSS_SELECTOR, "div.row"):
        try:
            brand = row.find_element(By.CSS_SELECTOR, "div.col-6.col-md-3").text.strip()
        except Exception:
            brand = ""
        try:
            model_el = row.find_element(By.CSS_SELECTOR, "a.col-6.col-md-3.col-lg-2")
            model_number = model_el.text.strip()
            model_url = model_el.get_attribute("href")
        except Exception:
            model_number = ""
            model_url = ""
        try:
            desc = row.find_element(By.CSS_SELECTOR, "div.col.col-md-6.col-lg-7").text.strip()
        except Exception:
            desc = ""

        if brand or model_number or desc:
            cross_refs.append(
                {
                    "brand": brand,
                    "model_number": model_number,
                    "model_url": model_url,
                    "description": desc,
                }
            )
    return cross_refs


def dismiss_popup(driver):
    """Close marketing overlays/pop-ups if they appear."""
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//button|//a"))
        )
        controls = driver.find_elements(By.XPATH, "//button | //a")
        for control in controls:
            try:
                label = control.text.strip().lower()
                if any(k in label for k in ("decline", "close", "continue")):
                    if control.is_displayed():
                        control.click()
                        time.sleep(1)
                        return
            except:
                continue
    except:
        pass


def load_product_page(driver, url):
    """Navigate to the product page with retries if Access Denied is returned."""
    for attempt in range(1, PAGE_LOAD_RETRIES + 1):
        driver.get(url)
        time.sleep(3)

        if ACCESS_DENIED_MARKER not in driver.page_source:
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1[itemprop='name']"))
                )
            except:
                pass
            dismiss_popup(driver)
            return True

        print(f"Access denied (attempt {attempt}/{PAGE_LOAD_RETRIES}). Retrying...")
        time.sleep(RETRY_COOLDOWN)

    return False


def scrape_part(driver, url):
    if not load_product_page(driver, url):
        print("Unable to load product page after retries.")
        return {
            "name": "N/A",
            "price": "N/A",
            "partselect_number": "N/A",
            "model_number": "N/A",
            "brand": "N/A",
            "manufacturer_part_number": "N/A",
            "description": "N/A",

            "install_difficulty": "N/A",
            "install_time": "N/A",
            "availability": "N/A",

            "symptoms": "",
            "product_types": "",
            "replaceable_models": "",
            "model_cross_reference": "[]",
            "product_url": url
        }

    scroll(driver)

    data = {
        "name": "N/A",
        "price": "N/A",
        "partselect_number": "N/A",
        "model_number": "N/A",
        "official_oem": "N/A",
        "manufacturer_part_number": "N/A",
        "description": "N/A",

        # Newly restored fields
        "install_difficulty": "N/A",
        "install_time": "N/A",
        "availability": "N/A",

        # RAG-critical fields
        "symptoms": "",
        "product_types": "",
        "replaceable_models": "",
        "model_cross_reference": "[]",

        "product_url": url
    }

    # --------------------
    # BASIC FIELDS
    # --------------------

    title = el(driver, "h1[itemprop='name']")
    if title:
        data["name"] = title.text.strip()

    p = el(driver, "span.js-partPrice")
    if p:
        data["price"] = p.text.strip()

    ps = el(driver, "span[itemprop='productID']")
    if ps:
        data["partselect_number"] = ps.text.strip()

    mpn = el(driver, "span[itemprop='mpn']")
    if mpn:
        val = mpn.text.strip()
        data["manufacturer_part_number"] = val
        data["model_number"] = val

    oem = el(driver, "span[itemprop='brand'] span[itemprop='name']")
    if oem:
        data["official_oem"] = oem.text.strip()

    desc = el(driver, "div[itemprop='description'], div.pd__description")
    if desc:
        data["description"] = desc.text.strip()

    # --------------------
    # INSTALL DIFFICULTY / TIME
    # --------------------

    rating_container = el(driver, "div.pd__repair-rating__container")
    if rating_container:
        bolds = rating_container.find_elements(By.CSS_SELECTOR, "p.bold")
        if len(bolds) >= 1:
            data["install_difficulty"] = bolds[0].text.strip()     # "Very Easy"
        if len(bolds) >= 2:
            data["install_time"] = bolds[1].text.strip()           # "15 - 30 mins"


    # --------------------
    # AVAILABILITY
    # --------------------

    avail = el(driver, "span[itemprop='availability']")
    if avail:
        data["availability"] = avail.text.strip()

    # --------------------
    # TROUBLESHOOTING
    # --------------------

    symptoms = els(driver, "#Troubleshooting + div ul.list-disc li")
    data["symptoms"] = "; ".join([x.text.strip() for x in symptoms])

    prod_types = els(driver,
        "#Troubleshooting + div .col-md-6:nth-of-type(2) ul.list-disc li")
    data["product_types"] = "; ".join([x.text.strip() for x in prod_types])

    replace = el(driver,
        "#Troubleshooting + div div[data-collapse-container]")
    if replace:
        raw = replace.text.strip()
        data["replaceable_models"] = "; ".join([x.strip() for x in raw.split(",")])

    cross_refs = load_cross_reference(driver)
    if cross_refs:
        data["model_cross_reference"] = json.dumps(cross_refs)

    return data, cross_refs


def save_parts_csv(rows, filename):
    if not rows:
        print(f"No data to save for {filename}")
        return
    fieldnames = rows[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} parts → {filename}")


if __name__ == "__main__":
    PART_URLS = {
        "dishwasher": [
            "https://www.partselect.com/PS3406971-Whirlpool-W10195416-Lower-Dishrack-Wheel.htm?SourceCode=18",
            "https://www.partselect.com/PS10065979-Whirlpool-W10712395-Upper-Rack-Adjuster-Kit-White-Wheels-Left-and-Right-Sides.htm?SourceCode=18",
            "https://www.partselect.com/PS11756150-Whirlpool-WPW10546503-Dishwasher-Upper-Rack-Adjuster.htm?SourceCode=18",
            "https://www.partselect.com/PS11746591-Whirlpool-WP8565925-Dishwasher-Rack-Track-Stop.htm?SourceCode=18",
            "https://www.partselect.com/PS11750057-Whirlpool-WPW10195417-Lower-Dishrack-Wheel-Assembly.htm?SourceCode=18",
            "https://www.partselect.com/PS12585623-Frigidaire-5304517203-Lower-Spray-Arm.htm?SourceCode=18",
            "https://www.partselect.com/PS17137081-GE-WD22X33499-LOWER-SPRAY-ARM.htm?SourceCode=18",
            "https://www.partselect.com/PS16217024-GE-WD12X26146-Dishwasher-Lower-Rack-Roller.htm?SourceCode=18",
            "https://www.partselect.com/PS8260087-Whirlpool-W10518394-Dishwasher-Heating-Element.htm?SourceCode=18",
            "https://www.partselect.com/PS9495545-Frigidaire-809006501-Dishwasher-Bottom-Door-Gasket.htm?SourceCode=18"
        ],
        "refrigerator": [
            "https://www.partselect.com/PS12364199-Frigidaire-242126602-Refrigerator-Door-Shelf-Bin.htm?SourceCode=18",
            "https://www.partselect.com/PS11752778-Whirlpool-WPW10321304-Refrigerator-Door-Shelf-Bin.htm?SourceCode=18",
            "https://www.partselect.com/PS11701542-Whirlpool-EDR1RXD1-Refrigerator-Ice-and-Water-Filter.htm?SourceCode=18",
            "https://www.partselect.com/PS734935-Frigidaire-240534901-Door-Shelf-Retainer-Bar.htm?SourceCode=18",
            "https://www.partselect.com/PS734936-Frigidaire-240534701-Door-Shelf-Retainer-Bar.htm?SourceCode=18",
            "https://www.partselect.com/PS11739119-Whirlpool-WP2188656-Refrigerator-Crisper-Drawer-with-Humidity-Control.htm?SourceCode=18",
            "https://www.partselect.com/PS429868-Frigidaire-240337901-Refrigerator-Door-Shelf-Retainer-Bin.htm?SourceCode=18",
            "https://www.partselect.com/PS11739091-Whirlpool-WP2187172-Refrigerator-Door-Shelf-Bin-White.htm?SourceCode=18",
            "https://www.partselect.com/PS2358880-Frigidaire-241993101-Crisper-Cover-Support-Front.htm?SourceCode=18",
            "https://www.partselect.com/PS11757048-Whirlpool-WPW10671238-Refrigerator-Center-Crisper-Drawer-Slide-Rail-White.htm?SourceCode=18"
        ],
    }

    for category, urls in PART_URLS.items():
        if not urls:
            print(f"No URLs provided for {category}, skipping.")
            continue

        print(f"\nScraping {category} parts...")
        driver = setup_driver()
        output = []
        cross_refs_all = []
        try:
            for u in urls:
                print("Scraping:", u)
                part_data, cross_refs = scrape_part(driver, u)
                output.append(part_data)
                for entry in cross_refs:
                    cross_refs_all.append({
                        "partselect_number": part_data["partselect_number"],
                        "model_number": entry["model_number"],
                        "brand": entry["brand"],
                        "description": entry["description"],
                        "model_url": entry["model_url"],
                    })
                time.sleep(2)
        finally:
            driver.quit()

        save_parts_csv(output, f"{category}_parts.csv")
        if cross_refs_all:
            save_parts_csv(cross_refs_all, f"{category}_parts_crossref.csv")
