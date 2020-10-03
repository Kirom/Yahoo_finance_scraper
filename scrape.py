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
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import Future

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

class Crawler:
    def __init__(self, company_name):
        self.company_name = company_name

    def run(self):
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(f"https://finance.yahoo.com/quote/{self.company_name}")
        # Checks if company not found
        if "Symbol Lookup" in driver.title:
            driver.close()
        else:
            # summary_csv_file = open(f"{self.company_name}_summary.csv", "w", newline="")
            #
            # summary_csv_file = open(os.path.join(Path(__file__).resolve().parent,
            #                                      'results', f'{self.company_name}_summary.csv'),
            #                         'w', newline="")
            # writer = csv.DictWriter(summary_csv_file, fieldnames=fieldnames)
            # writer.writeheader()

            wait_for_nine_news = WebDriverWait(driver, 10).until(
                lambda d: d.find_element_by_css_selector(
                    "#quoteNewsStream-0-Stream > ul > li:nth-child(10)"
                )
            )
            news_list = driver.find_elements_by_css_selector('[data-test-locator="mega"]')

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
            driver.close()


with ProcessPoolExecutor(max_workers=4) as executor:
    start = time()
    futures = [executor.submit(Crawler(company).run) for company in company_names]
    results = []
    for result in concurrent.futures.as_completed(futures):
        results.append(result)
    end = time()
    print(end - start)
    print(results)

# print(f'Начало - {time()}')
# for company_name in company_names:
#     driver.get(f"https://finance.yahoo.com/quote/{company_name}")
#
#     # Checks if company not found
#     if "Symbol Lookup" in driver.title:
#         continue
#
#     fieldnames = ["Link", "Title"]
#     summary_csv_file = open(os.path.join(Path(__file__).resolve().parent,
#                                          'results', f'{company_name}_summary.csv'),
#                             'w', newline="")
#     writer = csv.DictWriter(summary_csv_file, fieldnames=fieldnames)
#     writer.writeheader()
#
#     wait_for_nine_news = WebDriverWait(driver, 10).until(
#         lambda d: d.find_element_by_css_selector(
#             "#quoteNewsStream-0-Stream > ul > li:nth-child(10)"
#         )
#     )
#     news_list = driver.find_elements_by_css_selector('[data-test-locator="mega"]')
#
#     for news in news_list:
#         title = news.find_element_by_tag_name("a").text
#         link = news.find_element_by_tag_name("a").get_attribute("href")
#         row = {"Link": link, "Title": title}
#         writer.writerow(row)
#     summary_csv_file.close()
#
#     historical_data_btn = driver.find_element_by_css_selector(
#         "#quote-nav > ul > li:nth-child(6) > a"
#     )
#     driver.get(historical_data_btn.get_attribute("href"))
#
#     try:
#         date_range_btn = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CLASS_NAME, "dateRangeBtn"))
#         )
#         date_range_btn.click()
#     except MaxRetryError as exc:
#         print(exc)
#
#     max_date_btn = driver.find_element_by_css_selector('[data-value="MAX"]').click()
#     download_btn = driver.find_element_by_css_selector(
#         f'[download="{company_name}.csv"]'
#     )
#     download_link = download_btn.get_attribute("href")
#
#     r = requests.get(download_link)
#
#     csv_writer = CsvWriter(r.text, company_name)
#     csv_writer.run()
#
# driver.close()
# print(f'Конец - {time()}')
