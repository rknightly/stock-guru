import unittest.main
from unittest import TestCase
from StockGuru.StockData import *


class TestStockData(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_stock = StockData("AAPL", "Apple", "Tech")
        cls.test_stock.get_soups()

    # Soup analysis

    def test_finds_recommended_action(self):
        self.assertTrue(len(self.test_stock.find_recommended_action()) > 0)

    def test_gets_zacks_rank(self):
        self.assertNotEquals(self.test_stock.find_zacks_rank(), 6)

    def test_gets_street_rank(self):
        self.assertNotEquals(self.test_stock.find_street_rank(), 16)

    def test_gets_wsj_rating(self):
        self.assertNotEquals(self.test_stock.find_wsj_rating(), 6)

    def test_gets_yahoo_change_percent(self):
        self.assertNotEquals(self.test_stock.find_yahoo_change_percent(), 0)

    def test_gets_ryan_rank(self):
        test_stock = StockData("AAPL", "Apple", "Tech")
        test_stock.get_soups()
        test_stock.find_data()
        ryan_rank = test_stock.ryan_rank

        self.assertGreater(ryan_rank, 0)
        self.assertLessEqual(ryan_rank, 100)

    def test_translate(self):
        translated_value = translate(1, 0, 10, 100, 0)
        self.assertEqual(translated_value, 90)

if __name__ == "__main__":
    unittest.main()
