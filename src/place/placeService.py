import gzip
import json
import math
import time
import zlib
from urllib.parse import quote

import brotli
import requests as requests

from src.config.Logging import Log
from src.config.util import send_request, GLOBAL_HOST_URI, ADB,  GLOBAL_NAVER_COOKIE, log_exception
import src.config.util as util

from src.domain.common.common import convert_unixtime_to_date
from src.domain.types.LoopSearchDTO import LoopSearchDTO, LOOP_SEARCH_RESULT_MESSAGE
from src.place.PlaceGraphql import PlaceGraphql


class PlaceService:
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.title = ""
        self.keyword = ""
        self.maincode = 0
        self.placeNo = 0
        self.locationX = 0
        self.locationY = 0

    def loopSingleSearch(self, startPage, lastPage, category):
        loopSearchDTO = LoopSearchDTO()
        for i in range(startPage, lastPage + 1):
            loopSearchDTO = self.__getPlaceLoop__(i, self.title, self.keyword, self.locationX, self.locationY, self.maincode, category, "multi")

            if i == 6 and loopSearchDTO.message != LOOP_SEARCH_RESULT_MESSAGE.SUCCESS:
                loopSearchDTO.message = LOOP_SEARCH_RESULT_MESSAGE.LIMIT
                break

            if loopSearchDTO.message == LOOP_SEARCH_RESULT_MESSAGE.SUCCESS or \
                    loopSearchDTO.message == LOOP_SEARCH_RESULT_MESSAGE.LIMIT or \
                    loopSearchDTO.message == LOOP_SEARCH_RESULT_MESSAGE.PART_LIMIT:
                break

        # res = self.insertRanking(self.placeNo, loopSearchDTO.rank, self.keyword, loopSearchDTO.message.value)

        # loopSearchDTO.chgDate = convert_unixtime_to_date(res['data']['recentCollectDt'])
        return loopSearchDTO

    def insertRanking(self, placeNo, ranking, keyword, resultMessage):
        try:
            response_data = send_request(self, f"{GLOBAL_HOST_URI}/v2/places/{placeNo}/ranking", method='POST',
                                         data={'ranking': ranking,
                                               "keyword": keyword,
                                               "resultMessage": resultMessage})
            return response_data
        except Exception as e:
            Log.e("플레이스 랭킹 insert 에러", e)
            log_exception("ERROR", "플레이스 랭킹 insert 에러 " + str(e))

    def get_address_info(self, query):
        url = f'https://dapi.kakao.com/v2/local/search/keyword.json?query={query}'
        headers = {'Authorization': 'KakaoAK 690e0cee05a9ea2cb10aafaf6b6884d7'}

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                # 성공적으로 요청이 완료된 경우
                result = response.json()
                if result["meta"]["total_count"] == 0:
                    return None

                x = result["documents"][0]["x"]
                y = result["documents"][0]["y"]

                return {"x": x, "y": y}
            else:
                # 요청이 실패한 경우
                Log.e(f'Error: {response.status_code}')
                return None
        except Exception as e:
            Log.e("exception kakao address info", e)
            log_exception("ERROR", "exception kakao address info " + str(e))
            return None
        finally:
            if response:
                response.close()  # 네트워크 연결 닫기



    def __getPlaceLoop__(self, start, title, keyword, locationX, locationY, maincode, category, gubun):
        adb = ADB()
        loopSearchDTO = LoopSearchDTO()

        try:
            placeUrl = f"https://pcmap-api.place.naver.com/graphql"
            headers = {
                'Accept':'*/*',
                'Accept-Encoding':'gzip, deflate, br, zstd',
                'Accept-Language':'ko',
                'Cache-Control':'no-cache',
                'Content-Length':'6650',
                'Content-Type':'application/json',
                'Cookie': GLOBAL_NAVER_COOKIE,
                'Origin':'https://pcmap.place.naver.com',
                'Pragma':'no-cache',
                'Referer': 'https://pcmap.place.naver.com/hairshop/list',
                'Sec-Ch-Ua':'"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                'Sec-Ch-Ua-Mobile':'?0',
                'Sec-Ch-Ua-Platform':'"Windows"',
                'Sec-Fetch-Dest':'empty',
                'Sec-Fetch-Mode':'cors',
                'Sec-Fetch-Site':'same-site',
                'User-Agent':util.get_global_user_agent(),
                'X-Wtm-Graphql':'eyJhcmciOiLrr7jsmqnsi6QiLCJ0eXBlIjoiaGFpcnNob3AiLCJzb3VyY2UiOiJwbGFjZSJ9',
            }

            start = ((start - 1) * 50) + 1

            placeGraphql = PlaceGraphql()
            placeGraphql.keyword = keyword
            placeGraphql.start = start
            placeGraphql.locationX = str(locationX)
            placeGraphql.locationY = str(locationY)

            ## 분기해줘야함
            itemCategory = "businesses"

            if category == "place":
                placeGraphql.getPlace()
            elif category == "restaurant":
                placeGraphql.getRestaurant()
                itemCategory = "restaurants"
            elif category == "hospital":
                placeGraphql.getHospital()
            elif category == "hairshop":
                placeGraphql.getHairshop()
            elif category == "nailshop":
                placeGraphql.getNailshop()
            elif category == "attraction":
                placeGraphql.getGolf()
            elif category == "trip":
                placeGraphql.getTrip()
            elif category == "accommodation":
                placeGraphql.getAccommodation()
            else:
                placeGraphql.getPlace()


            while(1):
                response = requests.post(placeUrl, json={'query': placeGraphql.query, 'variables': placeGraphql.variables}, headers=headers)
                time.sleep(0.3)

                if response.status_code == 429:
                    time.sleep(1)
                    adb.changeIp()
                    newip = adb.getCurrentIp()
                    Log.i("place newip", newip)

                else:
                    break

            data = json.loads(response.text)

            maxRank = 1

            if data is None or "data" not in data:
                loopSearchDTO.rank = 1
                loopSearchDTO.message = LOOP_SEARCH_RESULT_MESSAGE.LIMIT
                return loopSearchDTO


            if category == "attraction":
                items = data["data"]["attractions"]["businesses"]["items"]
                maxRank = data["data"]["attractions"]["businesses"]["total"]
            else:
                items = data["data"][itemCategory]["items"]
                maxRank = data["data"][itemCategory]["total"]

            if len(items) == 0:
                if maxRank is None:
                    maxRank = 0

                loopSearchDTO.rank = maxRank + 1
                loopSearchDTO.message = LOOP_SEARCH_RESULT_MESSAGE.LIMIT
                return loopSearchDTO

            rank = start

            for item in items:
                loopSearchDTO.name = item["name"]
                loopSearchDTO.id = item["id"]
                loopSearchDTO.rank = rank
                loopSearchDTO.message = LOOP_SEARCH_RESULT_MESSAGE.SUCCESS

                # 리스트검색
                if gubun == "multi":
                    if str(maincode) == loopSearchDTO.id and (title == "" or title == loopSearchDTO.name):
                        return loopSearchDTO
                else:
                    if str(maincode) == loopSearchDTO.id or title == loopSearchDTO.name:
                        return loopSearchDTO

                rank += 1

            loopSearchDTO.name = ""
            loopSearchDTO.message = LOOP_SEARCH_RESULT_MESSAGE.SEARCHING
            loopSearchDTO.rank = rank
            return loopSearchDTO
        except Exception as e:
            Log.e("place loop exception:", e, response.text)
            log_exception("ERROR", "place loop exception " + str(e))
        finally:
            if response:
                response.close()  # 네트워크 연결 닫기

        loopSearchDTO.message = LOOP_SEARCH_RESULT_MESSAGE.PART_LIMIT
        loopSearchDTO.rank = maxRank + 1
        return loopSearchDTO

    def __calculate_bounds__(self, locationX, locationY, radius):
        locationX = float(locationX)
        locationY = float(locationY)
        # 지구의 반지름 (미터)
        earth_radius = 6371000

        # 위도 단위당 1도의 거리 (미터)
        latitude_degree_distance = (2 * math.pi * earth_radius) / 360.0

        # 경도 단위당 1도의 거리 (미터)
        longitude_degree_distance = latitude_degree_distance * math.cos(math.radians(locationY))

        # 반경(미터)을 위도 및 경도의 변화로 변환
        latitude_change = radius / latitude_degree_distance
        longitude_change = radius / longitude_degree_distance

        # 영역의 경계 계산
        min_x = locationX - longitude_change
        max_x = locationX + longitude_change
        min_y = locationY - latitude_change
        max_y = locationY + latitude_change

        # bounds 값 구성
        bounds_value = f"{min_x:.14f};{min_y:.14f};{max_x:.14f};{max_y:.14f}"

        return bounds_value

    def getPlaceCategory(self):
        encoded_string = quote(self.keyword)
        query = encoded_string
        x = self.locationX
        y = self.locationY
        clientX = self.locationX
        clientY = self.locationY
        bounds = 500
        ts = int(time.time())
        mapUrl = quote(f"https://map.naver.com/p/search/{self.keyword}")

        url = f'https://pcmap.place.naver.com/place/list?query={query}&x={x}&y={y}&clientX={clientX}&clientY={clientY}&bounds={bounds}&ts={ts}&mapUrl={mapUrl}'
        ssc = self.__extract_g_ssc__(url).replace("mapv5.", "")
        return ssc

    def __get_g_ssc_value__(self, content):
        try:
            start_index = content.find('window.nsc = "') + len('window.nsc = "')
            end_index = content.find('";', start_index)
            g_ssc = content[start_index:end_index]
            return g_ssc
        except:
            return "place"

    def __extract_g_ssc__(self, url):
        # requests를 사용하여 내용 가져오기
        adb = ADB()
        try:
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cache-Control": "max-age=0",
                "Cookie": "NNB=5YQQB2SW7TJWK; NID_JKL=fz62aezgH7Q9u/wyZ/1NDC3HgxQfh9w4ZXy6axglSe0=; NAC=HWHMBMwQOgX6; ba.uuid=2af2ef9f-34d4-4df8-b662-613e66cbf5c7; NID_AUT=tccyKn7mJkJ2iugp0WnGQrUrNlFiJJaA7x3r3mE7kR/V2UkEHle4dboLbH2Fnpxq; BNB_FINANCE_HOME_TOOLTIP_MYASSET=true; _fwb=37THV6Cv51JClciLT6uKGx.1722923256428; NaverSuggestUse=use%26unuse; wcs_bt=sp_14d0e182eedb450:1723624915|sp_96f0f170ee8688:1723604802|sp_97bab82f44a5b8:1723001995|sp_967f1268c9ccf8:1723001979|sp_96c049d6568cb0:1723001111|sp_150738722ce4c00:1722925806|sp_410f3efde4bd48:1722925157|sp_3080a3f0a5cdb0:1722925131|sp_6430536845fe0:1722925128|sp_f051d77f5b0fe:1722925124; ASID=0e3f093200000192222eb4fd00000057; loungesRecentlyVisited=Hero_Clash; recentKeyword=%5B%5D; recentKeywordInLounge=%5B%5D; V2.RECENT_KEYWORD.LIST=%5B%7B%22keyword%22%3A%22%EC%BF%A0%ED%8F%B0%22%7D%5D; page_uid=ixcalsqo1SossCkCLLGssssstO4-271993; NID_SES=AAABzRfWKQDTVeVnpDted7D9cvpMh0F4pLjnABZVH9f+8PQbO9DmQWQ2q4HwttBoLHtHpk7hgI86MIFvMs2iOSw6uQgaV08VtXsIjafyT50D5p8Fcu5poMLmI654KLXgFRwZveSNp3tkqgXthObYcyAuA3E8kjYAFp6/x+oG4TR9e5VAc7t3Q17aQ+KmtkODOl/28AGELi5z8tm6TO/kLkufZeWgJVXAiAArtmXMsJHTzQGFFGagxeBlAbrHoaQz+kl5MELWrqqc/g2mM+TRGJrfADBMJLMj3RggW/1hcZHi6ilN4FZqQzpT9rvYDMwuSIznk072RnW+bzRzSTxcai8J6RcSqpKRjtLHG93RAQy+kr9q4WyFJorxdV0lyFKabfqRT33h8DB2ta6ZZaz1cJYdDsN0Nwe6MQedCqUbnQ0CfZUXhe6ynpgr63LBPlLuNA605fkNftA736lEp58WrN4AnaB9x+VhUVJEZRBCu309H01nYxsrfaonv+Xl1Ya3+QjNzfrRxvIeabf8qK9dIl1YueJb2jC7SprvYHa/Oeid2XsuYyBKdUbWmRnDm03i01blys6i9d6axy7qmuYdPoXkN7rrF0tGLgzqpbHStnNE4ve/; BUC=Rs7JpLk9Cr-B2bOts8B7o_rrpLhG3WwdSPdFbkzaJ0g=",
                "Priority": "u=0, i",
                "Sec-Ch-Ua": "Google Chrome\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": "\"Windows\"",
                "Sec-Ch-Ua-Platform-Version": "\"15.0.0\"",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                'User-Agent': util.get_global_user_agent()
            }

            while True:
                response = requests.get(url, headers=headers)
                content = response.content

                time.sleep(1.2)

                if response.status_code == 429:
                    time.sleep(1)
                    adb.changeIp()
                    newip = adb.getCurrentIp()
                    Log.i("place newip", newip)
                elif response.status_code != 200:
                    Log.e("g_ssc exception statuscode", content)
                    log_exception("ERROR", "g_ssc exception " + content)
                else:
                    break


        except Exception as e:
            Log.e("g_ssc exception", e)
            log_exception("ERROR", "g_ssc exception " + str(e))
        finally:
            if response:
                response.close()  # 네트워크 연결 닫기

        # g_ssc 값 추출
        g_ssc = self.__get_g_ssc_value__(content)

        return g_ssc