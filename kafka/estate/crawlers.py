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
# from producers import StorageEventProducer, StorageEvent

BASE_URL = "https://batdongsan.com.vn"
CITIES: List[str] = ["ha-noi", "bac-ninh", "bac-giang", "hai-phong"]
OUT_DIR = os.path.join(".", "data", "batdongsan.com.vn")
LISTING_SELECTORS = [".re__card", ".js__product-list", ".re__list-box", "article a[href*='/ban-']"]

def main():
    driver = webdriver.Chrome()
    return driver
if __name__ == "__main__":
    driver = main()
    driver.get("https://onehousing.vn/bds/Can-1PN--toa-L1---Masteri-Lakeside.5DXNQC")

    driver.execute_script("document.body.style.zoom='50%'")

    page_source = driver.execute_script("return document.documentElement.outerHTML;")
    
    with open("page_source.html", "w", encoding="utf-8") as f:
        f.write(page_source)

    time.sleep(3)
    driver.save_screenshot("current_viewport.png")


    time.sleep(30)