import unittest
from unittest.mock import patch, MagicMock

from src.domain.types.LoopSearchDTO import LOOP_SEARCH_RESULT_MESSAGE
from src.shopping.shoppingService import ShoppingService
from src.shoppingcompare.shoppingCompareService import ShoppingCompareService


class TestShoppingService(unittest.TestCase):
    # @patch('requests.get')
    def test_single_search_success(self):
        # Usage
        shopping_service = ShoppingService()
        shopping_service.keyword = "레몬즙"
        shopping_service.input = "88208652105"
        result = shopping_service.loop_single_search(1, 10)
        print(result)
        shopping_service.close_driver()

    def test_single_search_success(self):
        # Usage
        shopping_service = ShoppingCompareService()
        shopping_service.keyword = "삼다수"
        shopping_service.compareMid = "51702014662"
        shopping_service.mid = "27965424524"
        shopping_service.option = "3"

        shopping_service.click_option()
        for i in range(1, 21):
            try:
                result = shopping_service.search(i)
                print(result)
            except Exception as e:
                print(f"Error processing element: {e}")
                return {"message": "ERROR"}

