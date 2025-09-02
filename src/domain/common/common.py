import os
import re
from datetime import datetime

import pytz

from src.config.util import GLOBAL_USER_AGENT, GLOBAL_NAVER_COOKIE
import src.config.util as util

shoppingHeader = {
    "Referer": "https://search.shopping.naver.com/search/all",
    "Logic": "PART",
    "Sbth": "e14ed2c877e4ce17d6ecba277d344e3e5dc03d2fcaa31c8643cdcb71b39972b6f93081101249fc9828cf90c164a1ade1",
    "Sec-Ch-Ua": 'Google Chrome";v="123.0.6312.123", "Not:A-Brand";v="8.0.0.0", "Chromium";v="123.0.6312.123',
    "Pragma":"no-cache",
    'User-Agent': util.get_global_user_agent(),
    'Cookie': GLOBAL_NAVER_COOKIE
}


def get_table_item_text(table, row, column):
    item = table.item(row, column)
    return item.text().replace('\r', '').replace('\n', '').strip() if item else ""


def convert_unixtime_to_date(datetime_str):
    if not datetime_str:
        return ""

    date_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f%z')
    korea_tz = pytz.timezone('Asia/Seoul')
    korea_time = date_obj.astimezone(korea_tz)
    formatted_date = korea_time.strftime('%Y년 %m월 %d일 %H시 %M분')
    return formatted_date


def is_float(value):
    try:
        float_value = float(value)
        return True
    except ValueError:
        return False

def replace_special_chars(text):
    # 정규표현식을 사용하여 특수문자를 공백으로 치환
    replaced_text = re.sub(r'\n|\t|\r|\r\n', ' ', text)
    return replaced_text
