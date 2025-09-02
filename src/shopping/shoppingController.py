import requests
from selenium.webdriver.chrome.options import Options

from src.config.Logging import Log
from src.config.util import GLOBAL_HOST_URI
from src.domain.types.LoopSearchDTO import LOOP_SEARCH_RESULT_MESSAGE, LoopSearchDTO
from src.shopping.shoppingService import ShoppingService
from selenium import webdriver

def getSingle():
    Log.i("start shopping single queue")
    response = requests.get(GLOBAL_HOST_URI + "/shopping-single-queue")
    shoppingService = ShoppingService()

    for data in response.json()['data']:
        shoppingService.category = data['category']
        shoppingService.keyword = data['keyword']
        shoppingService.input = data['categoryInput']
        shoppingService.step = data['step']

        if shoppingService.step == 1:
            step = 1
            startRange = 1
            endRange = 51
        else:
            step = 51
            startRange = 51
            endRange = 101

        message = "SEARCHING"
        for i in range(startRange, endRange): # 1~99
            shoppingResult = shoppingService.loop_single_search(i, i)

            rank = shoppingResult.rank
            if shoppingResult.message == LOOP_SEARCH_RESULT_MESSAGE.SUCCESS:
                message = "SUCCESS"
                break
            elif shoppingResult.message == LOOP_SEARCH_RESULT_MESSAGE.LIMIT or i == 100:
                message = "LIMIT"
                rank = -100
                break
            elif shoppingResult.message == LOOP_SEARCH_RESULT_MESSAGE.SEARCHING:
                message = "SEARCHING"
                resultResponse = update_single_queue(data["shoppingQueueNo"], step*80*-1, "SEARCHING")
                step += 1
                queueResponse = requests.put(GLOBAL_HOST_URI + "/shopping-single-queue",
                                             headers={
                                                 'Content-Type': 'application/json'
                                             },
                                             json={
                                                 'shoppingQueueNo': data['shoppingQueueNo']
                                             })

            if i == 50 :
                shoppingResult.message = LOOP_SEARCH_RESULT_MESSAGE.LIMIT
                message = "LIMIT"
                rank = -50
                break

        # 해당 shoppingNO과 매치하여 update하기
        resultResponse = update_single_queue(data["shoppingQueueNo"], rank, message)

        queueResponse = requests.put(GLOBAL_HOST_URI + "/shopping-single-queue",
         headers = {
            'Content-Type': 'application/json'
        },
        json={
            'shoppingQueueNo':data['shoppingQueueNo']
        })

        shoppingService.close_driver()

def update_single_queue(shoppingQueueNo, rank, message):
    url = GLOBAL_HOST_URI + "/shopping-single-queue/shopping-update"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'rank': rank,
        'shoppingQueueNo': shoppingQueueNo,
        'message': message
    }
    resultResponse = requests.put(url, json=data, headers=headers)

    if resultResponse.status_code == 200:
        Log.i('Update Success:', resultResponse.json())
    else:
        Log.e('shop Update Failed:', resultResponse.status_code)

    return resultResponse.json()['data']



def getqueue():
    Log.i("start shopping queue")
    response = requests.get(GLOBAL_HOST_URI + "/shopping-queue")
    shoppingService = ShoppingService()

    for data in response.json()['data']:
        shoppingService.input = data["maincode"]
        shoppingService.keyword = data["keyword"]
        shoppingService.category = "CODE"

        shoppingResult = shoppingService.loop_single_search(1, 10)

        if shoppingResult['message'] == LOOP_SEARCH_RESULT_MESSAGE.SUCCESS:
            pcRank = shoppingResult['rank']
            productName = shoppingResult['name']
        else:
            pcRank = -1
            productName = ""

        mobileRank = shoppingResult['rank']


        # 모바일 순위
        # for page in range(1, 11):
        #     shoppingResult: LoopSearchDTO = shoppingService.mobileSearch(page)
        #
        #     if shoppingResult.message == LOOP_SEARCH_RESULT_MESSAGE.SUCCESS:
        #         mobileRank = shoppingResult.rank
        #         productName = shoppingResult.name
        #         break
        #     elif shoppingResult.message == LOOP_SEARCH_RESULT_MESSAGE.LIMIT or page == 10:
        #         mobileRank = -1
        #         productName = shoppingResult.name
        #         break

        # 해당 shoppingNO과 매치하여 update하기
        resultResponse = update_queue(data["keywordCronNo"], pcRank, mobileRank, productName, data["customNo"], data['familyCustom'],
                                      data["keyword"], data["maincode"])

        queueResponse = requests.put(GLOBAL_HOST_URI + "/shopping-queue",
         headers = {
            'Content-Type': 'application/json'
        },
        json={
            'shoppingQueueNo':data['shoppingQueueNo']
        })

    shoppingService.close_driver()


def update_queue(keywordCronNo, pcRank, mobileRank, productName, customNo, familyCustom,
                 keywordCronKeyword, keywordCronProductCode):
    url = GLOBAL_HOST_URI + "/shopping-queue/shopping-update"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'keywordCronNo': keywordCronNo,
        'lastRanking': pcRank,
        'mobileRanking': mobileRank,
        'keywordCronProductName': productName,
        'customNo': customNo,
        'familyCustom': familyCustom,
        'keywordCronKeyword':keywordCronKeyword,
        'keywordCronProductCode':keywordCronProductCode
    }
    resultResponse = requests.put(url, json=data, headers=headers)


    if resultResponse.status_code == 200:
        Log.i('Update Success:', resultResponse.json())
    else:
        Log.e('shopping Update Failed:', resultResponse.status_code)

    return resultResponse.json()['data']
