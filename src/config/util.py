import json

import subprocess
import time

import requests
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QMessageBox, QApplication

from src.config.Logging import Log
from src.config.globals import getToken

GLOBAL_HOST_URI = "https://heroranking.kro.kr:18089"
# GLOBAL_HOST_URI = "http://localhost:18089"
GLOBAL_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

GLOBAL_NAVER_COOKIE = "NNB=5YQQB2SW7TJWK; NID_JKL=fz62aezgH7Q9u/wyZ/1NDC3HgxQfh9w4ZXy6axglSe0=; NAC=HWHMBMwQOgX6; ba.uuid=2af2ef9f-34d4-4df8-b662-613e66cbf5c7; NID_AUT=tccyKn7mJkJ2iugp0WnGQrUrNlFiJJaA7x3r3mE7kR/V2UkEHle4dboLbH2Fnpxq; BNB_FINANCE_HOME_TOOLTIP_MYASSET=true; BUC=-18B76r5UNwyV4CHFN1ZYwsgMM3i9EB-mwLRj722skI=; page_uid=iqVrElqo1aVssjruo70ssssssY0-520685; NID_SES=AAAB0P/9oMdo5XrCWDYdSMzUSDPVU5jlOtuHaEBlcOSBbGuAFUKH4qv0RZnGr14c+fHYseO/aFeeGXbc4sToja8B5d+qg6eagPzCf0jV2Gqw7whAHncGtJXqHU7vaZVEWEfx8bA9fCx9kvUd50LyCCMe9y7atlRL/V7y9rXFoSNUIv7CHEMbplknqAryeZLmvKtAdNNCvEiiWQXaUuiYwlreaQWnLjABKkxZBngBJlJt9Xj+AK45XkF6ZTOg7+W87hDJ08fk/h4rLBBnDAVBCQ20YclXhVapOt+YEx3HN4cqr39ANlnC6gsNRd9E2HvrvgQRmBqANhgAtd+yI0xy6Bh8yvrCMskx0/jsNYhJqytLl9Hv5I99jdyXgzvVa7kIm3QaeNGQWG7qTzPvfdzREAkbD6A/RbGf/DviAOsgMw88k8CmSnMw4FsiPOvMsAYFmrWrjC37+DnUcscRBvDXGqLoWgT06pCd4mUygH4PC7HC3ZrmT1jRphZVBUJtH/Ks3F1HTSm/w0PS2MYaFLugDl3c79Y1GmIrFjJZ9Xx8eDVlHx4mkJeB8wHbg7ZaX7euYE/DqvsEqH7QznCPKHn9W6C9YRmVOvQmTcSVZApKCxJrjXoP; _naver_usersession_=h2jh+1H3VksLxAwvxfJ+xy3x"

def get_global_user_agent():
    return GLOBAL_USER_AGENT

def read_user_agent(file_path):
    with open(file_path, 'r') as file:
        return file.readline().strip()

def update_global_user_agent(file_path):
    global GLOBAL_USER_AGENT
    GLOBAL_USER_AGENT = read_user_agent(file_path)

def expiredMessageBox(self, responseData):
    if 'message' in responseData and responseData['message'] == "EXPIRED_PREMIUM":
        QMessageBox.warning(self.parent, '알림', '프리미엄 기간이 만료되었습니다.\n결제 후 이용해주세요.')

        url = QUrl("http://www.creeder.kr/cricheck.html")
        QDesktopServices.openUrl(url)
        return False

    return True

def send_request(self, url, method='GET', data=None):
    token = getToken()
    if token != "":
        headers = {
            "Authorization": f"{token}",
            'Content-Type': 'application/json'
        }
    else:
        headers = {'Content-Type': 'application/json'}

    if data != None:
        data = json.dumps(data)

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=data)
        elif method == 'POST':
            response = requests.post(url, headers=headers, data=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, data=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, data=data)
        else:
            raise ValueError("Invalid HTTP method. Only GET and POST are supported.")

        response.raise_for_status()  # HTTP 오류가 발생하면 예외 발생

        # 응답의 JSON 데이터를 딕셔너리로 파싱하여 반환
        responseJson = response.json()

        if "message" in responseJson:
            if responseJson["message"] == "EXPIRED_PREMIUM":
                return responseJson
            elif responseJson["message"] == "EXPIRED_TOKEN":
                QMessageBox.warning(self.parent, '알림', '로그인이 만료되어 자동 로그아웃되었습니다.\n프로그램을 종료합니다.')
                QApplication.exit()
                return responseJson

        return responseJson

    except requests.exceptions.HTTPError as errh:
        Log.e("HTTP Error:", errh)
        result = {}
        result["error"] = errh
        return result
    except requests.exceptions.ConnectionError as errc:
        Log.e("Error Connecting:", errc)
        result = {}
        result["error"] = errc
        return result
    except requests.exceptions.Timeout as errt:
        Log.e("Timeout Error:", errt)
        result = {}
        result["error"] = errt
        return result
    except requests.exceptions.RequestException as err:
        Log.e("OOps: Something Else", err)
        result = {}
        result["error"] = err
        return result
    finally:
        if response:
            response.close()  # 네트워크 연결 닫기

class ADB:
    def __init__(self):
        super().__init__()

    def changeIp(self):
        try:
            if self.is_adb_connected():
                subprocess.run(['adb', 'shell', 'svc', 'data', 'disable'], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(2)
                subprocess.run(['adb', 'shell', 'svc', 'data', 'enable'], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(1)
        except Exception as e:
            Log.e(f'Error: {e}')

    def getCurrentIp(self):
        try:
            currentIp = requests.get("http://ip.jsontest.com").json()['ip']
            Log.i (currentIp)
            return currentIp
        except Exception as e:
            Log.e(f'Error: {e}')
            return "offline"

    def is_adb_connected(self):
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, check=False,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        output = result.stdout
        if 'List of devices attached' in output and 'device' in output.split('\n', 1)[1]:
            return True
        else:
            return False

def log_exception(level="ERROR", exc=""):
    try:
        data = {
            "level": level,  # 로그 레벨
            "message": exc  # 로그 메시지
        }

        token = getToken()
        if token != "":
            headers = {
                "Authorization": f"{token}",
                'Content-Type': 'application/json'
            }
        else:
            headers = {'Content-Type': 'application/json'}

        response = requests.post(GLOBAL_HOST_URI + "/log", json=data, headers=headers)
        if response.status_code == 200:
            Log.i("Log sent successfully")
    except Exception as e:
        Log.e(f'Error: {e}')
