import logging


global_login_token = ""

def setToken(token):
    with open("login_token.txt", "w") as file:
        file.write(token)

def getToken():
    try:
        with open("login_token.txt", "r") as file:
            token = file.read()
            return token
    except FileNotFoundError:
        return None

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# 래퍼 함수
def log(message):
    logging.info(message)
