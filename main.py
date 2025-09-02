import time
import traceback

from src.config.Logging import Log
from src.place.placeController import getSinglePlace, getPlace
from src.shopping.shoppingController import getqueue
from src.shoppingcompare.shoppingCompareController import getCompareQueue


def run_getqueue_periodically():
    while True:
        try:
            start_time = time.time()

            # 각 함수를 개별적으로 예외 처리
            try:
                # getCompareQueue() # 쇼핑원부
                pass
            except Exception as e:
                Log.e("getCompareQueue 오류:", e)

            # try:
            #     getPlace()
            #     pass
            # except Exception as e:
            #     Log.e("getPlace 오류:", e)

            # try:
            #     getSinglePlace()
            # except Exception as e:
            #     Log.e("getSinglePlace 오류:", e)
            #     Log.e("스택 트레이스:", traceback.format_exc())
            #
            try:
                getqueue()  ## 쇼핑 일반
            except Exception as e:
                Log.e("getqueue 오류:", e)
                Log.e("스택 트레이스:", traceback.format_exc())

            elapsed_time = time.time() - start_time

            # 최소 3초 대기
            if elapsed_time < 3:
                time.sleep(3 - elapsed_time)

        except KeyboardInterrupt:
            Log.i("프로그램이 사용자에 의해 중단되었습니다.")
            break
        except Exception as e:
            Log.e("전체 루프 오류:", e)
            Log.e("스택 트레이스:", traceback.format_exc())
            # 심각한 오류 발생 시 잠시 대기
            time.sleep(10)


if __name__ == '__main__':
    Log.i("프로그램 시작")
    run_getqueue_periodically()