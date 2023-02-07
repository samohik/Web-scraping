import time
import uuid
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

# unique_id = uuid.uuid4()
# 👉️ 011963c3-7fa3-4963-8599-a302f9aefe7d


def test():
    driver = webdriver.Chrome()
    url = 'https://www.truckscout24.com/vans/used/refrigerated-truck/renault'
    driver.get(url)
    time.sleep(3)
    element = driver.find_element(By.CLASS_NAME, 'ls-arrow')
    element.click()
    time.sleep(3)
    html = driver.page_source
    driver.close()
    return html


class Parser:
    def __init__(self):
        self.url = 'https://www.truckscout24.ru/transporter/gebraucht/kuehl-iso-frischdienst/renault'

    def get_response(self):
        response = requests.get(self.url).content
        return response

    def scraping(self, content):
        soup = BeautifulSoup(content, 'lxml')
        items = soup.find_all('div', class_='ls-elem ls-elem-gap')
        for item in items:
            title = item.find('h2', class_='ls-makemodel sc-font-bold sc-ellipsis').text
            price = item.find('div', class_='ls-data-price').text
            mileage = item.find('div', class_='ls-data-additional').div.text

            # color = item.find('div', class_='detail-container')
            # hidden
            detail_info = item.find_all('li')
            """class_='sc-font-bold'"""
            for val in detail_info:
                print(val)
                if 'Colour' == val.string:
                    print(val.previous_sibling.string)
                    print(val.next_sibling.string)
            # print(title, price, mileage)
            break

    def main(self):
        self.scraping(content=test())


if __name__ == '__main__':
    # test()
    a = Parser()
    a.main()
