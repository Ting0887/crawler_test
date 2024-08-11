import os
import json
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class Browser:
    def __init__(self):
        self.driver = self.setup_browser()

    def setup_browser(self):
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--log-level=1")
        chrome_options.add_argument("--disable-3d-apis")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('blink-settings=imagesEnabled=false')
        chrome_options.add_argument("--disable-javascript")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--in-process-plugins")
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    def teardown_browser(self):
        self.driver.quit()

    def scroll_and_collect_data(self):
        js_down = 'window.scrollTo(0, document.body.scrollHeight)'
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            self.driver.execute_script(js_down)
            time.sleep(2.5)

            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            items = soup.find_all('div', 'dpH7T')

            for item in items:
                date_time = Extract_Data().extract_date(item)
                print(date_time)

            try:
                button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[text()="想看更多"]')))
                button.click()
            except Exception as e:
                print(f"An error occurred while clicking 'More': {e}")
                break

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

class Extract_Data:
    def extract_content(self, soup):
        content = []
        try:
            contents = soup.find_all('p', 'qdr-paragraph')
            for c in contents:
                text = c.get_text()
                cleaned_text = text.replace('\ufeff', '').strip()
                content.append(cleaned_text)
        except AttributeError as e:
            print(f"An error occurred: {e}")
        return '\n'.join(content)

    def extract_keyword(self, soup):
        keyword = ''
        try:
            keywords = soup.find_all('a', 'Vvwcb a0OGQ Dhqmu T_RGN lz9m3')
            keyword = '、'.join(k.text for k in keywords)
        except Exception as e:
            print(f"An error occurred while extracting keywords: {e}")
        return keyword

    def write_to_json(self, article, folder):
        folder_path = f'news_data/wealth/{folder}/{time.strftime("%Y-%m")}'
        os.makedirs(folder_path, exist_ok=True)
        filename = f'wealth_{folder}{time.strftime("%Y%m%d")}.json'
        file_path = os.path.join(folder_path, filename)

        with open(file_path, 'w', encoding='utf8') as jf:
            json.dump(article, jf, ensure_ascii=False, indent=2)

    def extract_title(self, item):
        try:
            return item.find('h2').text
        except AttributeError:
            return ''

    def extract_date(self, item):
        try:
            return item.find('span', 'g4jRc aDT8p pfH6t t1DSN rUO_L').text
        except AttributeError:
            return ''

    def extract_author(self, item):
        try:
            return item.find_all('span', 'g4jRc aDT8p pfH6t t1DSN rUO_L Pm9CI c_Ei3')[1].text
        except IndexError:
            return ''

    def extract_link(self, item):
        try:
            return 'https://www.wealth.com.tw' + item.select('a')[2]['href']
        except IndexError:
            return ''

class WealthNews:
    def __init__(self, browser):
        self.browser = browser

    def Wealth(self, label, label_id, folder, end_date):
        url = f'https://www.wealth.com.tw/lists/categories/{label_id}'
        self.browser.driver.get(url)

        time.sleep(2) 
        try:
            self.browser.driver.find_element(By.XPATH, '//button[text()="我知道了"]').click()
        except Exception as e:
            print(f"An error occurred while clicking 'I Know': {e}")

        self.browser.scroll_and_collect_data()

        article = []
        soup = BeautifulSoup(self.browser.driver.page_source, 'lxml')
        items = soup.find_all('div', 'dpH7T')

        for item in items:
            title = Extract_Data().extract_title(item)
            date_time = Extract_Data().extract_date(item)
            author = Extract_Data().extract_author(item)
            link = Extract_Data().extract_link(item)

            if date_time < end_date:
                break

            self.browser.driver.get(link)
            time.sleep(1)  
            soup = BeautifulSoup(self.browser.driver.page_source, 'lxml')
            content = Extract_Data().extract_content(soup)
            keyword = Extract_Data().extract_keyword(soup)

            post = {
                "title": title,
                "author": author,
                "date_time": date_time,
                "link": link,
                "label": label,
                "website": "財訊",
                "content": content,
                "keyword": keyword.rstrip('、')
            }
            print(post)
            article.append(post)
            time.sleep(1)  

        if article:
            Extract_Data().write_to_json(article, folder)

if __name__ == '__main__':
    browser = Browser()

    start_date = datetime.datetime.today()
    end_date = (start_date - datetime.timedelta(days=30)).strftime('%Y/%m/%d')

    categories = [
        ('國際', '2c6379e9-7527-442b-880a-bb9552689e06', 'global'),
        ('政經', '352be1d4-7ce8-42b8-9a84-0f491f7927ea', 'politics'),
        ('科技', '79c03f3f-d546-4551-a05f-c6d38e5579ca', 'tech'),
        ('財經', 'd1354fa3-82bf-42e6-84ad-9e36d7615892', 'finance'),
        ('生技醫療', 'dd2b5859-96aa-42bb-b5cc-08e6c7c8728e', 'biotech_medical')
    ]

    for label, label_id, folder in categories:
        WealthNews(browser).Wealth(label, label_id, folder, end_date)

    browser.teardown_browser()