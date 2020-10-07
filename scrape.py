"""Scrapes finance.yahoo.com for historical data and latest news."""

import csv
import os
from time import time

from csv_writer import CsvWriter

import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from urllib3.exceptions import MaxRetryError

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager, IEDriverManager
from webdriver_manager.opera import OperaDriverManager
from webdriver_manager.utils import ChromeType

import concurrent
from concurrent.futures import ProcessPoolExecutor

company_names = ["PD", "ZUO", "PINS", "ZM", "PVTL", "DOCU", "CLDR", "RUN"]


# For Chrome browser
# driver = webdriver.Chrome(ChromeDriverManager().install())


# For Chromium browser
# driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())

# For FireFox browser
# driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())

# For Internet Explorer browser
# driver = webdriver.Ie(IEDriverManager().install())

# For Edge browser
# driver = webdriver.Edge(EdgeChromiumDriverManager().install())

# For Opera browser
# driver = webdriver.Opera(executable_path=OperaDriverManager().install())

def get_news_list(driver):
    wait_for_nine_news = WebDriverWait(driver, 10).until(
        lambda d: d.find_element_by_css_selector(
            "#quoteNewsStream-0-Stream > ul > li:nth-child(10)"
        )
    )
    news_list = driver.find_elements_by_css_selector('[data-test-locator="mega"]')
    return news_list


class Crawler:
    def __init__(self, company_name):
        self.company_name = company_name

    def write_csv_summary_file(self, news_list):
        fieldnames = ["Link", "Title"]
        file_name = f"{self.company_name}_summary.csv"
        if not os.path.exists('results'):
            os.mkdir('results')
        with open(f"results/{file_name}", "w", newline="") as csv_summary_file:
            writer = csv.DictWriter(csv_summary_file, fieldnames=fieldnames)
            writer.writeheader()
            for news in news_list:
                title = news.find_element_by_tag_name("a").text
                link = news.find_element_by_tag_name("a").get_attribute("href")
                row = {"Link": link, "Title": title}
                writer.writerow(row)

    def write_csv_file(self, driver):
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
            f'[download="{self.company_name}.csv"]'
        )
        download_link = download_btn.get_attribute("href")

        r = requests.get(download_link)

        csv_writer = CsvWriter(r.text, self.company_name)
        csv_writer.run()

    def run(self):
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(f"https://finance.yahoo.com/quote/{self.company_name}")
        # Checks if company not found
        if "Symbol Lookup" in driver.title:
            driver.close()
        else:
            news_list = get_news_list(driver)
            self.write_csv_summary_file(news_list)
            self.write_csv_file(driver)
            driver.close()


if __name__ == '__main__':
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(Crawler(company).run) for company in company_names]
        results = []
        for result in concurrent.futures.as_completed(futures):
            results.append(result)
