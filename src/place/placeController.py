import requests
import time
from src.config.Logging import Log
from src.config.util import GLOBAL_HOST_URI
from src.domain.types.LoopSearchDTO import LOOP_SEARCH_RESULT_MESSAGE, LoopSearchDTO
from src.place.placeService import PlaceService


def getSinglePlace():
    Log.i("start single place queue")

    try:
        response = requests.get(GLOBAL_HOST_URI + "/place-single-queue")

        # 응답 상태 코드 확인
        if response.status_code != 200:
            Log.e(f"API 요청 실패: status_code={response.status_code}")
            return

        # 응답 JSON 구조 확인
        response_data = response.json()
        Log.i(f"API 응답 구조: {response_data}")

        # 'data' 키 존재 여부 확인
        if 'data' not in response_data:
            Log.e("응답에 'data' 키가 없습니다. 응답 구조를 확인하세요.")
            Log.e(f"실제 응답: {response_data}")
            return

        emptyCheck = response_data['data']
        if not emptyCheck:
            Log.i("처리할 큐 데이터가 없습니다.")
            return

        for data in emptyCheck:
            try:
                placeService = PlaceService()
                placeService.keyword = data['keyword']
                placeService.locationX = data['x']
                placeService.locationY = data['y']
                title = ""
                maincode = ""

                if data['placeCategory'] == "STORE_NAME":
                    title = data['placeCategoryInput']
                else:
                    maincode = data['placeCategoryInput']

                for i in range(1, 6 + 1):  # 500위까지
                    category = placeService.getPlaceCategory()
                    placeItem = placeService.__getPlaceLoop__(i, title,
                                                              placeService.keyword,
                                                              placeService.locationX,
                                                              placeService.locationY,
                                                              maincode,
                                                              category,
                                                              "single")
                    rank = placeItem.rank
                    name = placeItem.name

                    if placeItem.message == LOOP_SEARCH_RESULT_MESSAGE.SUCCESS:
                        break
                    elif placeItem.message == LOOP_SEARCH_RESULT_MESSAGE.LIMIT:
                        rank = rank * -1
                        break
                    elif i == 6:
                        rank = rank * -1
                        break

                # 업데이트 요청
                resultResponse = update_single_queue(data["placeQueueNo"], rank, placeItem.message.value)

                if resultResponse:  # 업데이트 성공 시에만 큐 처리
                    queueResponse = requests.put(GLOBAL_HOST_URI + "/place-single-queue",
                                                 headers={'Content-Type': 'application/json'},
                                                 json={'placeQueueNo': data['placeQueueNo']}
                                                 )

                    if queueResponse.status_code != 200:
                        Log.e(f"큐 처리 실패: {queueResponse.status_code}, {queueResponse.text}")

                # 요청 간 딜레이
                time.sleep(0.5)

            except Exception as e:
                Log.e(f"개별 데이터 처리 중 오류: {e}")
                continue

    except requests.exceptions.RequestException as e:
        Log.e(f"네트워크 요청 오류: {e}")
    except Exception as e:
        Log.e(f"getSinglePlace 처리 중 오류: {e}")


def update_single_queue(placeQueueNo, rank, message):
    try:
        url = GLOBAL_HOST_URI + "/place-single-queue/place-update"
        headers = {'Content-Type': 'application/json'}
        data = {
            'rank': rank,
            'placeQueueNo': placeQueueNo,
            'resultMessage': message
        }

        Log.i(f"업데이트 요청 데이터: {data}")

        resultResponse = requests.put(url, json=data, headers=headers, timeout=30)

        if resultResponse.status_code == 200:
            Log.i('Update Success:', resultResponse.json())
            return resultResponse.json().get('data')
        else:
            Log.e(f'Update Failed: status_code={resultResponse.status_code}')
            Log.e(f'Response: {resultResponse.text}')
            return None

    except requests.exceptions.Timeout:
        Log.e("업데이트 요청 타임아웃")
        return None
    except Exception as e:
        Log.e(f'update_single_queue 오류: {e}')
        return None


def getPlace():
    Log.i("start place queue")

    try:
        response = requests.get(GLOBAL_HOST_URI + "/place-queue")

        if response.status_code != 200:
            Log.e(f"API 요청 실패: status_code={response.status_code}")
            return

        response_data = response.json()

        if 'data' not in response_data:
            Log.e("응답에 'data' 키가 없습니다.")
            Log.e(f"실제 응답: {response_data}")
            return

        emptyCheck = response_data['data']
        if not emptyCheck:
            Log.i("처리할 큐 데이터가 없습니다.")
            return

        for data in emptyCheck:
            try:
                placeService = PlaceService()
                placeService.title = ""
                placeService.maincode = data["mainCode"]
                placeService.keyword = data["keyword"]
                placeService.category = "CODE"
                placeService.locationX = data["x"]
                placeService.locationY = data["y"]

                placeCategory = placeService.getPlaceCategory()
                placeItem = placeService.loopSingleSearch(1, 6 + 1, placeCategory)

                if placeItem.message == LOOP_SEARCH_RESULT_MESSAGE.LIMIT:
                    rank = abs(placeItem.rank * -1)
                    name = ""
                else:
                    rank = placeItem.rank
                    name = placeItem.name

                # 업데이트 요청
                resultResponse = update_queue(data["placeQueueNo"], rank, data['placeNo'], name,
                                              placeItem.message.value)

                if resultResponse:  # 업데이트 성공 시에만 큐 처리
                    queueResponse = requests.put(GLOBAL_HOST_URI + "/place-queue",
                                                 headers={'Content-Type': 'application/json'},
                                                 json={'placeQueueNo': data['placeQueueNo']}
                                                 )

                    if queueResponse.status_code != 200:
                        Log.e(f"큐 처리 실패: {queueResponse.status_code}")

                time.sleep(0.5)

            except Exception as e:
                Log.e(f"개별 데이터 처리 중 오류: {e}")
                continue

    except Exception as e:
        Log.e(f"getPlace 처리 중 오류: {e}")


def update_queue(placeQueueNo, rank, placeNo, title, message):
    try:
        url = GLOBAL_HOST_URI + "/place-queue/place-update"
        headers = {'Content-Type': 'application/json'}
        data = {
            'lastRanking': rank,
            'placeQueueNo': placeQueueNo,
            'placeNo': placeNo,
            'title': title,
            'resultMessage': message
        }

        Log.i(f"업데이트 요청 데이터: {data}")

        resultResponse = requests.put(url, json=data, headers=headers, timeout=30)

        if resultResponse.status_code == 200:
            Log.i('Update Success:', resultResponse.json())
            return resultResponse.json().get('data')
        else:
            Log.e(f'Update Failed: status_code={resultResponse.status_code}')
            Log.e(f'Response: {resultResponse.text}')
            return None

    except Exception as e:
        Log.e(f'update_queue 오류: {e}')
        return None