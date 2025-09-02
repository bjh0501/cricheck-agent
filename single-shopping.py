import time
from webbrowser import get

from src.config.Logging import Log
from src.place.placeController import getPlace, getSinglePlace
from src.shopping.shoppingController import getqueue, getSingle
from src.shoppingcompare.shoppingCompareController import getCompareQueue


# getqueue 함수 호출
def run_getqueue_periodically():
    while True:
        try:
            start_time = time.time()
            # getCompareQueue()
            # getPlace()
            # getSinglePlace()
            getSingle()
            # getqueue()
            elapsed_time = time.time() - start_time

            # getqueue 함수 실행이 완료된 후 3초 대기
            if elapsed_time < 3:
                time.sleep(3 - elapsed_time)
        except Exception as e:
            Log.e("queue error" ,e )

if __name__ == '__main__':
    run_getqueue_periodically()
