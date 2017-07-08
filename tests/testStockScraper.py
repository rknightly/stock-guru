import unittest.main
from unittest import TestCase
from src.StockSearcher import StockSearcher
from src.StockData import StockData

from src.main import *


class TestStockData(TestCase):

    def testDoesInitialize(self):
        _ = StockData("AAPL", "Apple Inc", "Tech")

    def testFindsAppleData(self):
        test_stock = StockData("AAPL", "Apple", "Tech")
        test_stock.get_soups()
        test_stock.find_data()

    def testLoadsZacksPage(self):
        test_stock = StockData("AAPL", "Apple", "Tech")
        test_stock.get_soups()

    def testGetsZacksRank(self):
        test_stock = StockData("AAPL", "Apple", "Tech")
        test_stock.get_soups()

        self.assertEqual(test_stock.find_zacks_rank(), 3)

if __name__ == "__main__":
    unittest.main()
