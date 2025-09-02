import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')

class Log:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    @staticmethod
    def _format_message(*args):
        """
        메시지 포맷팅 유틸리티: 여러 인수를 받아 문자열로 결합.
        """
        return " ".join(map(str, args))

    @staticmethod
    def d(*args):
        logging.debug(Log._format_message(*args))

    @staticmethod
    def i(*args):
        logging.info(Log._format_message(*args))

    @staticmethod
    def w(*args):
        logging.warning(Log._format_message(*args))

    @staticmethod
    def e(*args):
        logging.error(Log._format_message(*args))

    @staticmethod
    def c(*args):
        logging.critical(Log._format_message(*args))
