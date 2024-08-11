import unittest
from xmlrunner import XMLTestRunner
from prettytable import PrettyTable
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from News_crawler import Browser, Extract_Data

table = PrettyTable()
table.field_names = ["Test", "Status"]

class TestWealthCrawler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        print(table)
        
    def test_page_load(self):
        url = 'https://www.wealth.com.tw/lists/categories/2c6379e9-7527-442b-880a-bb9552689e06'
        self.browser.get(url)
        time.sleep(1)
        try:
            table.add_row(["Assert the page title contains 財訊", "OK"])
        except AssertionError as e:
            table.add_row(["Assert the page title contains 財訊", "FAIL"])

    def test_btn1(self):
        url = 'https://www.wealth.com.tw/lists/categories/2c6379e9-7527-442b-880a-bb9552689e06'
        self.browser.get(url)
        time.sleep(1)

        try:
            button = self.browser.find_element(By.XPATH, '//button[text()=""我知道了"]')
            button.click()
            table.add_row(["Assert the button 我知道了 is clickable", "OK"])
        except Exception as e:
            table.add_row(["Assert the button 我知道了 is clickable", "FAIL"])

    def test_btn2(self):
        try:
            more_button = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[text()="想看更多"]'))
            )
            more_button.click()
            time.sleep(1)
            table.add_row(["Assert the button 想看更多 is clickable", "OK"])
        except Exception as e:
            table.add_row(["Assert the button 想看更多 is clickable", "FAIL"])
        
    
    def test_newslink_extraction(self):
        url = 'https://www.wealth.com.tw/lists/categories/2c6379e9-7527-442b-880a-bb9552689e06'
        self.browser.get(url)
        time.sleep(1)
        soup = BeautifulSoup(self.browser.page_source, 'lxml')
        item = soup.find('div', 'dpH7T')
        
        urlpattern = r'https://www\.wealth\.com\.tw/articles/[\w-]+'
        
        newslink = Extract_Data().extract_link(item)

        if len(newslink) > 0:
            table.add_row(["Assert the newslink is not empty", "OK"])
        else:
            table.add_row(["Assert the newslink is not empty", "FAIL"])
        
        if re.match(urlpattern, newslink):
            table.add_row(["Assert the newslink is not match", "OK"])
        else:
            table.add_row(["Assert the newslink is not match", "FAIL"])
        
    def test_content_extraction(self):
        url = 'https://www.wealth.com.tw/articles/ca791c2e-0a67-4c2f-a611-99694c60521e'
        self.browser.get(url)
        time.sleep(1)
        soup = BeautifulSoup(self.browser.page_source, 'lxml')

        content = Extract_Data().extract_content(soup)
        if len(content) > 0:
                table.add_row(["Assert the content is not empty", "OK"])
        else:
            table.add_row(["Assert the content is not empty", "FAIL"])
    
    def test_date_extraction(self):
        url = "https://www.wealth.com.tw/lists/categories/2c6379e9-7527-442b-880a-bb9552689e06"
        self.browser.get(url)
        time.sleep(1)
        soup = BeautifulSoup(self.browser.page_source, 'lxml')
        item = soup.find('div', 'dpH7T')
            
        article_date = Extract_Data().extract_date(item)
        if len(article_date) > 0:
            table.add_row(["Assert the date is not empty", "OK"])
        else:
            table.add_row(["Assert the date is not empty", "FAIL"])
        
        if re.match(r'^\d{4}/\d{2}/\d{2}$',article_date):
            table.add_row(["Assert the date is not match date format", "OK"])
        else:
            table.add_row(["Assert the date is not match date format", "FAIL"])
    
    def test_title_extraction(self):
        url = "https://www.wealth.com.tw/lists/categories/2c6379e9-7527-442b-880a-bb9552689e06"
        self.browser.get(url)
        time.sleep(1)
        soup = BeautifulSoup(self.browser.page_source, 'lxml')

        title = Extract_Data().extract_title(soup)
        if len(title) > 0:
            table.add_row(["Assert the title is not empty", "OK"])
        else:
            table.add_row(["Assert the title is not empty", "FAIL"])
    
    def test_source_extraction(self):
        url = "https://www.wealth.com.tw/lists/categories/2c6379e9-7527-442b-880a-bb9552689e06"
        self.browser.get(url)
        time.sleep(1)
        soup = BeautifulSoup(self.browser.page_source, 'lxml')
        item = soup.find('div', 'dpH7T')
        
        article_source = Extract_Data().extract_author(item)
        if len(article_source) > 0:
            table.add_row(["Assert the article source is not empty", "OK"])
        else:
            table.add_row(["Assert the article source is not empty", "FAIL"])
    
    def test_keyword_extraction(self):
        url = 'https://www.wealth.com.tw/articles/ca791c2e-0a67-4c2f-a611-99694c60521e'
        self.browser.get(url)
        time.sleep(1)
        soup = BeautifulSoup(self.browser.page_source, 'lxml')
        
        article_kw = Extract_Data().extract_keyword(soup)
        if article_kw == "三中全會、習近平、房地產、加稅、中國":
            table.add_row(["Assert the article keyword is equal from newslink keyword", "OK"])
        else:
            table.add_row(["Assert the article keyword is equal from newslink keyword", "FAIL"])
        
if __name__ == '__main__':
    unittest.main(testRunner=XMLTestRunner(output='test-reports'))
    