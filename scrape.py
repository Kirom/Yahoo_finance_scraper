"""Scrapes finance.yahoo.com for historical data and latest news."""

import csv

from csv_writer import CsvWriter

import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from urllib3.exceptions import MaxRetryError

from webdriver_manager.chrome import ChromeDriverManager

company_names = ["PD", "ZUO", "PINS", "ZM", "PVTL", "DOCU", "CLDR", "RUN"]

driver = webdriver.Chrome(ChromeDriverManager().install())

for company_name in company_names:
    driver.get(f"https://finance.yahoo.com/quote/{company_name}")

    # Checks if company not found
    if "Symbol Lookup" in driver.title:
        continue

    fieldnames = ["Link", "Title"]
    summary_csv_file = open(f"{company_name}_summary.csv", "w", newline="")
    writer = csv.DictWriter(summary_csv_file, fieldnames=fieldnames)
    writer.writeheader()

    wait_for_nine_news = WebDriverWait(driver, 10).until(
        lambda d: d.find_element_by_css_selector(
            "#quoteNewsStream-0-Stream > ul > li:nth-child(10)"
        )
    )
    news_list = driver.find_elements_by_css_selector('[data-test-locator="mega"]')

    for news in news_list:
        title = news.find_element_by_tag_name("a").text
        link = news.find_element_by_tag_name("a").get_attribute("href")
        row = {"Link": link, "Title": title}
        writer.writerow(row)
    summary_csv_file.close()

    historical_data_btn = driver.find_element_by_css_selector(
        "#quote-nav > ul > li:nth-child(6) > a"
    )
    driver.get(historical_data_btn.get_attribute("href"))

    try:
        date_range_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dateRangeBtn"))
        )
        date_range_btn.click()
    except MaxRetryError as exc:
        print(exc)

    max_date_btn = driver.find_element_by_css_selector('[data-value="MAX"]').click()
    download_btn = driver.find_element_by_css_selector(
        f'[download="{company_name}.csv"]'
    )
    download_link = download_btn.get_attribute("href")

    r = requests.get(download_link)

    csv_writer = CsvWriter(r.text, company_name)
    csv_writer.run()

driver.close()
