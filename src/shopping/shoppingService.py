
from selenium.webdriver.common.by import By
import time
import json

from src.config.Logging import Log
from src.domain.types.LoopSearchDTO import LOOP_SEARCH_RESULT_MESSAGE

from selenium.webdriver.chrome.options import Options
from selenium import webdriver

class ShoppingService:
    def __init__(self):
        self.driver = self.setup_driver()
        self.keyword = ""
        self.input = ""
        self.page = 0
        self.category = ""
        self.cronNo = ""

    def setup_driver(self):
        chrome_options = Options()

        # 최신 User-Agent
        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36')

        # 자동화 감지 방지
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        # 기본 옵션들
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        Log.i("일반 크롬 생성")
        # 웹드라이버 감지 방지 스크립트
        # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # 네이버 접속
        from selenium.webdriver.chrome.service import Service
        service = Service(executable_path="./chromedriver")
        driver = webdriver.Chrome(executable_path="./chromedriver", options=chrome_options)

        driver.get("https://www.naver.com")
        time.sleep(2)

        # GLOBAL_NAVER_COOKIE 사용
        from src.config.util import GLOBAL_NAVER_COOKIE

        cookie_pairs = GLOBAL_NAVER_COOKIE.split('; ')
        for pair in cookie_pairs:
            if '=' in pair:
                name, value = pair.split('=', 1)
                try:
                    driver.add_cookie({"name": name, "value": value, "domain": ".naver.com"})
                except Exception as e:
                    Log.e(f"쿠키 추가 실패 ({name}): {e}")

        # CDPExecutor를 사용하여 요청 헤더 설정 (Chrome DevTools Protocol)
        try:
            driver.execute_cdp_cmd('Network.enable', {})
            driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {'headers': {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-encoding': 'gzip, deflate, br, zstd',
                'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
                'sec-ch-ua-arch': '"x86"',
                'sec-ch-ua-bitness': '"64"',
                'sec-ch-ua-form-factors': '"Desktop"',
                'sec-ch-ua-full-version-list': '"Chromium";v="136.0.7103.94", "Google Chrome";v="136.0.7103.94", "Not.A/Brand";v="99.0.0.0"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-model': '""',
                'sec-ch-ua-platform': '"Windows"',
                'sec-ch-ua-platform-version': '"15.0.0"',
                'sec-ch-ua-wow64': '?0',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1'
            }})
            Log.i("헤더 설정 완료")
        except Exception as e:
            Log.e(f"헤더 설정 실패: {e}")

        return driver

    def loop_single_search(self, start_page, last_page):
        for i in range(start_page, last_page + 1):
            result = self.single_search(i)
            if result["message"] == "LIMIT":
                return result
            if result["rank"] > 0:
                return result
        return {"message": "SEARCHING", "rank": -1}

    def scroll_to_end(self):
        """
        Scroll to the bottom of the page until no further content is loaded.
        """
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # 페이지 끝으로 스크롤
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.1)  # 페이지 로딩 대기 (필요 시 조정)

            # 새로운 높이 가져오기
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            # 더 이상 로드되는 내용이 없으면 종료
            if new_height == last_height:
                break
            last_height = new_height

    def process_element(self, element):
        """
        Extracts 'rank', 'id', and 'name' from the given element.
        Compares 'catalog_nv_mid' with self.input.
        """
        try:
            # data-shp-contents-dtl 속성을 가진 태그에서 값 추출
            test = element.get_attribute("outerHTML")
            data_shp_contents_dtl = element.get_attribute("data-shp-contents-dtl")

            if not data_shp_contents_dtl:
                return {"message": "NOT_data_shp_contents_dtl"}  # data-shp-contents-dtl 없으면 매치 실패

            # JSON 파싱
            shp_contents_json = json.loads(data_shp_contents_dtl.replace("&quot;", '"'))
            # 'ad_expose_order' 키가 존재하면 매치 실패
            if any(isinstance(item, dict) and item.get("key") == "ad_expose_order" for item in shp_contents_json):
                return {"message": "HAS_ad_expose_order"}

            organic_expose_order = next(
                (int(item.get("value")) for item in shp_contents_json if
                 isinstance(item, dict) and item.get("key") == "organic_expose_order"), None
            )
            catalog_nv_mid = next(
                (item.get("value") for item in shp_contents_json if
                 isinstance(item, dict) and item.get("key") == "catalog_nv_mid"), None
            )
            prod_nm = next(
                (item.get("value") for item in shp_contents_json if
                 isinstance(item, dict) and item.get("key") == "prod_nm"), None
            )

            # 필수 값 확인
            if organic_expose_order is None or catalog_nv_mid is None or prod_nm is None:
                return {"message": "NOT_NEED_OPTION"}  # 필요한 값이 없으면 매치 실패

            # self.input과 비교
            if str(catalog_nv_mid) == str(self.input):
                return {
                    "message": LOOP_SEARCH_RESULT_MESSAGE.SUCCESS,
                    "rank": organic_expose_order,
                    "id": catalog_nv_mid,
                    "name": prod_nm,
                }
            else:
                return {"message": "NOT_MATCHED"}

        except Exception as e:
            # 오류 발생 시 NOT_MATCHED 반환
            print(f"Error processing element: {e}")
            return {"message": "ERROR_PROCESS"}

    def single_search(self, page):
        try:
            keyword_encoded = self.keyword
            url = f"https://search.shopping.naver.com/search/all?query={keyword_encoded}&pagingIndex={page}&pagingSize=80"

            # 직접 URL 접근
            self.driver.get(url)
            Log.i("일반 페이지이동", url)
            time.sleep(3)  # 페이지 로딩 대기

            # 접속 제한 메시지나 "찾을 수 없습니다" 메시지 확인 및 처리
            refresh_count = 0
            while True:  # 무한 루프
                try:
                    # 1. head 클래스의 "서비스" 제한 메시지 확인
                    head_elements = self.driver.find_elements(By.CLASS_NAME, "head")
                    service_restriction = False
                    for element in head_elements:
                        if element.text and "서비스" in element.text:
                            service_restriction = True
                            refresh_count += 1
                            Log.i(f"서비스 제한 메시지 발견, 새로고침 시도 ({refresh_count}회)")
                            self.driver.refresh()
                            time.sleep(60)  # 1분 대기 후 새로고침
                            break

                    if service_restriction:
                        continue  # 다음 반복으로 넘어감

                    # 2. style_head 클래스의 "찾을 수 없습니다" 메시지 확인
                    style_head_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class^='style_head']")
                    not_found = False
                    for element in style_head_elements:
                        if element.text and "찾을 수 없습니다" in element.text:
                            not_found = True
                            refresh_count += 1
                            Log.i(f"'찾을 수 없습니다' 메시지 발견, 1분 후 새로고침 시도 ({refresh_count}회)")
                            time.sleep(60)  # 1분 대기
                            self.driver.refresh()
                            time.sleep(3)
                            break

                    if not_found:
                        continue  # 다음 반복으로 넘어감

                    # 두 경우 모두 아니면 정상 로드로 간주하고 루프 종료
                    Log.i(f"페이지 정상 로드 (새로고침 {refresh_count}회 시도 후)")
                    break

                except Exception as e:
                    Log.e(f"제한 메시지 확인 중 오류: {e}")
                    # 오류가 발생해도 계속 시도
                    time.sleep(1)
                    self.driver.refresh()
                    time.sleep(2)

            # 페이지 끝까지 스크롤
            self.scroll_to_end()
            time.sleep(2)  # 페이지 로딩 대기

            # #__NEXT_DATA__ 요소가 로드될 때까지 대기
            # try:
            #     WebDriverWait(self.driver, 10).until(
            #         EC.presence_of_element_located((By.ID, "__NEXT_DATA__"))
            #     )
            # except Exception as e:
            #     Log.e(f"__NEXT_DATA__ 요소 로드 실패: {e}")
            #     return {"message": "SEARCHING", "rank": -1}

            # JavaScript 실행
            resultDict = json.loads(self.driver.execute_script(f"""
               const jsonText = document.querySelector('#__NEXT_DATA__').textContent;
               const idMatch = /"id":\\s*"?{self.input}"?/.exec(jsonText);

               if (idMatch) {{
                   const pos = idMatch.index;
                   const nearby = jsonText.substring(Math.max(0, pos - 500), pos + 1500);

                   const rankMatch = /"rank":\\s*(\\d+)/.exec(nearby);
                   const titleMatch = /"productTitleOrg":\\s*"([^"]+)"/.exec(nearby);

                   const result = {{
                       rank: rankMatch ? parseInt(rankMatch[1]) : -1,
                       productTitleOrg: titleMatch ? titleMatch[1] : ""
                   }};

                   return JSON.stringify(result);
               }} else {{
                   return JSON.stringify({{rank: -1, productTitleOrg: ""}});
               }}
            """))
            time.sleep(1)

            if resultDict['rank'] != -1:
                return {
                    "message": LOOP_SEARCH_RESULT_MESSAGE.SUCCESS,
                    "rank": resultDict['rank'],
                    "id": self.input,
                    "name": resultDict['productTitleOrg'],
                }

            return {"message": "SEARCHING", "rank": -1}
        except Exception as e:
            Log.e(f"Error during single_search: {e}")
            return {"message": "SEARCHING", "rank": -1}

    def mobile_first_page_search(self, keyword):
        try:
            url = f"https://msearch.shopping.naver.com/search/all?query={keyword}"
            self.driver.get(url)
            time.sleep(2)  # 페이지 로딩 대기

            # 웹 요소에서 데이터 가져오기
            product_elements = self.driver.find_elements(By.CLASS_NAME, "product-item")
            for product_element in product_elements:
                main_code = product_element.get_attribute("data-id")
                name = product_element.find_element(By.CLASS_NAME, "product-title").text
                rank = product_element.find_element(By.CLASS_NAME, "rank").text

                if self.input == main_code:
                    return {"message": LOOP_SEARCH_RESULT_MESSAGE.SUCCESS, "rank": rank, "id": main_code, "name": name}
        except Exception as e:
            Log.e(f"Error during mobile_first_page_search: {e}")
        return {"message": "SEARCHING", "rank": -1}

    def close_driver(self):
        self.driver.quit()
