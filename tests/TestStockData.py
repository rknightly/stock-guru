import unittest.main
from unittest import TestCase
from StockGuru.StockData import *


class TestStockData(TestCase):

    def __init__(self):
        super().__init__()
        self.test_stock = StockData("AAPL", "Apple", "Tech")
        self.test_stock.get_soups()

    # Soup analysis
    def test_finds_change_percent(self):
        self.assertNotEquals(self.test_stock.find_estimated_change_percent(),
                             0)

    def test_finds_recommended_action(self):
        self.assertTrue(len(self.test_stock.find_recommended_action()) > 0)

    def test_gets_zacks_rank(self):
        self.assertNotEquals(self.test_stock.find_zacks_rank(), 6)

    def test_gets_street_rank(self):
        self.assertNotEquals(self.test_stock.find_street_rank(), 16)

    def test_gets_ryan_rank(self):
        test_stock = StockData("AAPL", "Apple", "Tech")
        test_stock.get_soups()
        test_stock.find_data()
        ryan_rank = test_stock.ryan_rank

        print("AAPL Ryan Rank:", ryan_rank)
        self.assertGreater(ryan_rank, 0)
        self.assertLessEqual(ryan_rank, 100)

    def test_translate(self):
        translated_value = translate(1, 0, 10, 100, 0)
        self.assertEqual(translated_value, 90)

if __name__ == "__main__":
    unittest.main()
