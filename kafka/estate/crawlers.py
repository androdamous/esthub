# human_verified_crawler.py
# -*- coding: utf-8 -*-
import os, time
from typing import List, Optional
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---- your Kafka producer ----
from producers import StorageEventProducer, StorageEvent

BASE_URL = "https://batdongsan.com.vn"
CITIES: List[str] = ["ha-noi", "bac-ninh", "bac-giang", "hai-phong"]
OUT_DIR = os.path.join(".", "data", "batdongsan.com.vn")
LISTING_SELECTORS = [".re__card", ".js__product-list", ".re__list-box", "article a[href*='/ban-']"]

def build_driver(headless: bool, user_agent: Optional[str], chrome_user_data_dir: Optional[str]) -> webdriver.Chrome:
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1366,768")
    if user_agent:
        opts.add_argument(f"--user-agent={user_agent}")
    # Reuse your real Chrome profile so Cloudflare’s cookie sticks
    if chrome_user_data_dir:
        opts.add_argument(f"--user-data-dir={chrome_user_data_dir}")
    # Slightly reduce obvious automation signals
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    drv = webdriver.Chrome(options=opts)  # Selenium Manager fetches chromedriver
    drv.set_page_load_timeout(90)
    return drv

def wait_until_human_verified(drv: webdriver.Chrome, timeout: int = 120) -> None:
    """
    Wait while Cloudflare challenge is present. You complete it manually once.
    We poll until common challenge markers disappear or timeout passes.
    """
    start = time.time()
    while time.time() - start < timeout:
        html = drv.page_source.lower()
        blocked = ("challenges.cloudflare.com" in html or
                   "checking your browser" in html or
                   "vui lòng bỏ chặn" in html)
        if not blocked:
            return
        time.sleep(2)
    raise TimeoutException("Cloudflare verification not completed within timeout.")

def save_html(city: str, html: str) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.abspath(os.path.join(OUT_DIR, f"{city}.html"))
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(html)
    return path

def fetch_city(drv: webdriver.Chrome, city: str, wait_selector_timeout: int = 40) -> str:
    url = f"{BASE_URL}/nha-dat-ban-{city}"
    print(f"[HUMAN] -> {url}")
    drv.get(url)

    # If challenge shows up mid-navigation, wait for you to pass it once
    try:
        wait_until_human_verified(drv, timeout=120)
    except TimeoutException:
        print("[WARN] Challenge likely still active; saving whatever loaded.")

    # Light lazy-load scroll
    for _ in range(6):
        drv.execute_script("window.scrollBy(0, document.body.scrollHeight * 0.5);"); time.sleep(0.3)

    # Try to see a listing node (optional)
    w = WebDriverWait(drv, wait_selector_timeout)
    for sel in LISTING_SELECTORS:
        try:
            w.until(EC.visibility_of_element_located((By.CSS_SELECTOR, sel))); break
        except TimeoutException:
            continue

    path = save_html(city, drv.page_source)
    print(f"[HUMAN] Saved -> {path}")
    return path

def main():
    # >>>> IMPORTANT (Mac example): set your Chrome profile path for the FIRST run (headless=False),
    # solve Cloudflare once, then you can switch headless=True next runs.
    # Mac default example: "/Users/<you>/Library/Application Support/Google/Chrome"
    CHROME_PROFILE_DIR = os.path.expanduser("~/Library/Application Support/Google/Chrome")  # adjust for your OS
    HEADLESS_FIRST_RUN = False  # keep False so you can solve the challenge

    producer = StorageEventProducer(kafka_server="0.0.0.0:9092", topic="test")
    drv = None
    try:
        drv = build_driver(HEADLESS_FIRST_RUN, None, CHROME_PROFILE_DIR)
        # Warm-up home page (often sets cookies)
        drv.get(BASE_URL + "/"); time.sleep(1.0)
        # If the home page shows the banner, solve it once here:
        try:
            wait_until_human_verified(drv, timeout=120)
        except TimeoutException:
            print("[WARN] Could not confirm verification on home page; continuing.")

        for city in CITIES:
            path = fetch_city(drv, city)
            producer.send_event(StorageEvent(path=path))
            time.sleep(1.0)

        print("Done.")
    except WebDriverException as e:
        print(f"[ERR] WebDriver: {e}")
    finally:
        if drv:
            try: drv.quit()
            except Exception: pass
        if hasattr(producer, "close"):
            try: producer.close()  # type: ignore[attr-defined]
            except Exception: pass

if __name__ == "__main__":
    main()