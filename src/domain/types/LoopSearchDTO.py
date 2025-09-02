from enum import Enum


class LOOP_SEARCH_RESULT_MESSAGE(Enum):
    STOP = 'STOP' # 쓰레드스탑
    LIMIT = 'LIMIT' # 페이지 끝까지 돌았는데 못찾음
    PART_LIMIT = 'PART_LIMIT' # 지정된페이지까지 돌았는데 못찾음
    SUCCESS = 'SUCCESS' # 랭킹찾음
    SEARCHING = 'SEARCHING'  # 랭킹찾는중
    BLOCK = 'BLOCK'  # 아이피밴

class LoopSearchDTO:
    def __init__(self):
        self.rank = -1
        self.id = "1"
        self.name = ""
        self.chgDate = ""
        self.message: LOOP_SEARCH_RESULT_MESSAGE = LOOP_SEARCH_RESULT_MESSAGE.SUCCESS
