import unittest.main
from unittest import TestCase
from StockGuru.StockData import StockData


class TestStockData(TestCase):

    def test_does_initialize(self):
        _ = StockData("AAPL", "Apple Inc", "Tech")

    # Pages
    def test_loads_cnn_page(self):
        test_stock = StockData("AAPL", "Apple", "Tech")
        test_stock.get_cnn_soup()

    def test_loads_zacks_page(self):
        test_stock = StockData("AAPL", "Apple", "Tech")
        test_stock.get_zacks_soup()

    # Soup analysis
    def test_finds_change_percent(self):
        test_stock = StockData("AAPL", "Apple", "Tech")
        test_stock.get_soups()
        self.assertNotEquals(test_stock.find_estimated_change_percent(), 0)

    def test_finds_recommended_action(self):
        test_stock = StockData("AAPL", "Apple", "Tech")
        test_stock.get_soups()
        self.assertTrue(len(test_stock.find_recommended_action()) > 0)

    def test_gets_zacks_rank(self):
        test_stock = StockData("AAPL", "Apple", "Tech")
        test_stock.get_soups()

        self.assertNotEquals(test_stock.find_zacks_rank(), 6)

if __name__ == "__main__":
    unittest.main()
