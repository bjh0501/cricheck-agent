import time
import requests

from src.config.Logging import Log
from src.config.util import GLOBAL_HOST_URI
from src.domain.types.LoopSearchDTO import LOOP_SEARCH_RESULT_MESSAGE, LoopSearchDTO
from src.shopping.shoppingService import ShoppingService
from src.shoppingcompare.shoppingCompareService import ShoppingCompareService

def getCompareQueue():
    shoppingService = ShoppingService()
    shoppingCompareService = ShoppingCompareService()

    try:
        Log.i("start compare queue")
        response = requests.get(GLOBAL_HOST_URI + "/shopping-compare-queue")
        response.raise_for_status()  # HTTP 에러 발생 시 예외 발생

        data_list = response.json().get('data', [])

        if not isinstance(data_list, list):
            Log.e("Error: 'data' is not a list.")
            return

        for data in data_list:
            if not all(key in data for key in ["nsin", "maincode", "compareMaincode", "keyword", "shoppingCompareNo", "customNo", "familyCustom"]):
                Log.e(f"Error: Missing keys in data {data}")
                continue

            shoppingService.input = data["compareMaincode"]
            shoppingService.keyword = data["keyword"]
            shoppingService.category = "CODE"

            shoppingResult = shoppingService.loop_single_search(1, 10)

            if shoppingResult['message'] == LOOP_SEARCH_RESULT_MESSAGE.SUCCESS:
                pcRank = shoppingResult['rank']
                productName = shoppingResult['name']
            else:
                pcRank = -1
                productName = ""

            time.sleep(1)

            # shoppingCompare
            shoppingCompareService.compareMid = data["maincode"]
            shoppingCompareService.mid = data["compareMaincode"]
            if data["nsin"] <= 1:
                data["nsin"] = 1
            shoppingCompareService.option = data["nsin"]
            shoppingCompareService.click_option()

            for i in range(1, 21):
                response = shoppingCompareService.search(i)
                mobileRank = response.rank
                productName = response.name

                time.sleep(2)

                if response.message == LOOP_SEARCH_RESULT_MESSAGE.SUCCESS:
                    break
                elif response.message == LOOP_SEARCH_RESULT_MESSAGE.LIMIT or i == 20:
                    break

            resultResponse = update_queue(data["shoppingCompareNo"], pcRank, mobileRank, productName,
                                          data["customNo"], data['familyCustom'])

            queueResponse = requests.put(GLOBAL_HOST_URI + "/shopping-compare-queue",
                                         headers={'Content-Type': 'application/json'},
                                         json={'shoppingCompareQueueNo': data['shoppingCompareQueueNo']})
            queueResponse.raise_for_status()  # HTTP 에러 발생 시 예외 발생

    except Exception as e:
        Log.e(f"Error in getCompareQueue: {e}")

    shoppingService.close_driver()
    shoppingCompareService.close_driver()


def update_queue(keywordCronNo, pcRank, mobileRank, productName, customNo, familyCustom):
    url = GLOBAL_HOST_URI + "/shopping-compare-queue/shopping-update"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'shoppingCompareNo': keywordCronNo,
        'pcRanking': pcRank,
        'mobileRanking': mobileRank,
        'title': productName,
        'customNo': customNo,
        'familyCustom': familyCustom
    }
    resultResponse = requests.put(url, json=data, headers=headers)

    if resultResponse.status_code == 200:
        Log.i('Update Success:', resultResponse.json())
    else:
        Log.e('shopping compare Update Failed:', resultResponse.status_code)
        Log.i("data", data, resultResponse.json())

    return resultResponse.json()['data']
