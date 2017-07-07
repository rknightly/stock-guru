from unittest import TestCase

from src.stockScraper import *


class TestStockData(TestCase):

    def testDoesInitialize(self):
        _ = StockData("AAPL", "Apple Inc", "Tech")

    def testFindsAppleData(self):
        test_stock = StockData("AAPL", "Apple", "Tech")
        test_stock.get_soup()
        test_stock.find_data()

    def testLoadsZacksPage(self):
        test_stock = StockData("AAPL", "Apple", "Tech")
        test_stock.get_soup()

    def testGetsZacksRank(self):
        test_stock = StockData("AAPL", "Apple", "Tech")
        test_stock.get_soup()

        self.assertEqual(test_stock.find_zacks_rank(), 3)
