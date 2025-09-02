import json
import time
import urllib
from telnetlib import EC

import requests
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from src.config.Logging import Log


from src.domain.types.LoopSearchDTO import LOOP_SEARCH_RESULT_MESSAGE, LoopSearchDTO
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

class ShoppingCompareService:
    def __init__(self, parent=None):
        self.driver = self.setup_driver()
        self.parent = parent
        self.keyword = ""
        self.mid = ""
        self.compareMid = 0
        self.option = None
        self.optionCategory = ""

    def setup_driver(self):
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--window-size=800x600')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--enable-fast-unload')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        Log.i("컴페어 크롬생성")
        return webdriver.Chrome(executable_path="./chromedriver", options=chrome_options)

    def click_option(self):
        url = f"https://search.shopping.naver.com/catalog/{self.mid}"
        self.driver.get(url)
        Log.i("원부 페이지이동", url)
        time.sleep(2)
        if self.option != 1:
            for i in range(1,4):
                try:
                    # XPath를 기반으로 n번째 옵션 선택
                    option_xpath = f"/html/body/div/div/div[2]/div[2]/div[2]/div[3]/div[3]/div[2]/div[3]/div[1]/a[{self.option}]"
                    #                /html/body/div/div/div[2]/div[2]/div[2]/div[3]/div[3]/div[2]/div[3]/div[1]/a[1]
                    option_element = self.driver.find_element(By.XPATH, option_xpath)

                    # 클릭 처리
                    action = ActionChains(self.driver)
                    action.move_to_element(option_element).click().perform()
                    time.sleep(2)
                    break
                except Exception as e:
                    Log.e(f"옵션 클릭 중 오류 발생: {e}")

    def search(self, page):
        loopSearchDTO = LoopSearchDTO()
        rankPage = page
        if page >= 12:
            page -= 9

        # 클릭 처리
        if page != 1:
            try:
                container_selector = "#section_price > div[class^='productList_seller_wrap'] > div[class^='pagination_pagination']"
                nth_anchor_selector = f"{container_selector} > a:nth-of-type({page})"
                nth_anchor = self.driver.find_element(By.CSS_SELECTOR, nth_anchor_selector)
                nth_anchor.click()
                time.sleep(1)  # 필요에 따라 시간 조정
            except Exception as e:
                # 예외 처리 및 메시지 설정
                # print(f"오류 발생: {e}")
                loopSearchDTO.message = LOOP_SEARCH_RESULT_MESSAGE.LIMIT
                loopSearchDTO.rank = -1
                return loopSearchDTO

        time.sleep(0.8)

        extracted_data = self.driver.execute_script("""
               const listItems = document.querySelectorAll('ul[class^="productList_list_seller"] > li');
               let results = [];

               listItems.forEach((item) => {
                   const dataI = item.querySelector('a[data-i]')?.getAttribute('data-i');
                   const title = item.querySelector('[class^="productList_title"]')?.textContent.trim();

                   if (dataI && title) {
                       results.push({ dataI, title });
                   }
               });

               return results;
           """)
        time.sleep(1)

        # Python으로 데이터를 받아 비교 및 반환 처리
        rank = (rankPage - 1) * 20  # 페이지 기반 순위 계산
        if extracted_data:
            for index, productData in enumerate(extracted_data):
                rank += 1

                dataI = productData.get("dataI")
                if dataI is not None and dataI == self.compareMid:
                    # 조건에 맞는 경우 반환
                    loopSearchDTO.message = LOOP_SEARCH_RESULT_MESSAGE.SUCCESS
                    loopSearchDTO.rank = rank
                    loopSearchDTO.name = productData.get("title", "Unknown Title")  # title 키가 없으면 기본값 설정
                    return loopSearchDTO

        loopSearchDTO.message = LOOP_SEARCH_RESULT_MESSAGE.SEARCHING
        loopSearchDTO.rank = -1
        return loopSearchDTO

    def close_driver(self):
        self.driver.quit()
