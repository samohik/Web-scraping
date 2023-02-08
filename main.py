import json
import os
import time
import uuid
from typing import Tuple, Dict, List, Any

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Parser:
    def __init__(self, url):
        self.driver = webdriver.Chrome()
        self.url = url
        self.l_links = []
        self.data = {"ads": []}

    def get_html(self, url) -> str:
        """
        Gets full html with details after click on products.
        :return: str
        """
        self.driver.get(url)
        items = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//div[@class="ls-elem ls-elem-gap"]')
            )
        )
        for index, _ in enumerate(items):
            element = WebDriverWait(self.driver, 1).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f'//div[@data-container-id="{index}"]')
                )
            )
            action = ActionChains(self.driver)
            action.move_to_element(element).perform()
            self.driver.execute_script("arguments[0].click();", element)
        time.sleep(0.2)
        html = self.driver.page_source
        return html

    def get_pages(self) -> None:
        """
        Finds links to other pages.
        :return: None
        """
        self.driver.get(self.url)
        content = self.driver.page_source
        soup = BeautifulSoup(content, "lxml")
        links = soup.find("ul", class_="sc-pagination")
        links.findChildren("a", recursive=True)
        for link in links:
            link = link.find("a").get("href")
            if link and link not in self.l_links:
                self.l_links.append(link)

    def get_detail(self, item) -> Tuple[str, str]:
        """
        :return: color and power information
        """
        li_s = item.find("div", class_="detail-container").find_all("li")
        color: str | None = None
        power = None
        for elem in li_s:
            if color and power:
                break
            else:
                if elem.div.text == "Colour":
                    color = elem.div.findNext("div").text.strip()
                if elem.div.text == "Power":
                    power = elem.div.findNext("div").text.split(" (")[0]
        return color, power

    def scraping(self, content: str) -> None:
        """
        Getting all information from html.
        :param content: html
        :return: Dict
        """
        soup = BeautifulSoup(content, "lxml")
        items = soup.find_all("div", class_="ls-elem ls-elem-gap")

        for item in items:
            try:
                description: str = item.find("div", class_="short-description").text
            except AttributeError:
                print("If that's too fast, just add the time on line 42.")
                description = "Nothing!"
            href: str = item.find("a", {"data-item-name": "detail-page-link"})["href"]
            title: str = item.find(
                "h2", class_="ls-makemodel sc-font-bold sc-ellipsis"
            ).text.strip()
            price = (
                item.find("div", class_="ls-data-price").text.strip().replace("\n", "")
            )
            try:
                mileage = item.find("div", class_="ls-data-additional").div.text.strip()
            except AttributeError:
                mileage = "Nope"
            color, power = self.get_detail(item)
            self.data["ads"].append(
                {
                    "id": str(uuid.uuid4()),
                    "href": href,
                    "title": title,
                    "price": price,
                    "mileage": mileage,
                    "color": color,
                    "power": power,
                    "description": description,
                }
            )

    @classmethod
    def file_write(cls, data: Dict[str, List[Any]]) -> None:
        """
        Writing all information to data/data.json.
        :param data: product information
        :return: None
        """
        os.mkdir("data")
        with open("data/data.json", "w") as file:
            json_data = json.dumps(data)
            file.write(json_data)

    def main(self) -> None:
        """
        Executing function.
        :return: None
        """
        self.l_links.append(self.url)
        self.get_pages()
        for url in self.l_links:
            self.scraping(content=self.get_html(url))
        self.file_write(self.data)


if __name__ == "__main__":
    a = Parser("https://www.truckscout24.com/vans/used/refrigerated-truck/renault")
    a.main()
