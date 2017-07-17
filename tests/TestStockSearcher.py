import unittest.main
from unittest import TestCase
from StockGuru.StockSearcher import StockSearcher


class TestStockSearcher(TestCase):

    def test_initializes(self):
        _ = StockSearcher(file_name="shortened-cap.csv")

    def test_reads_from_file(self):
        searcher = StockSearcher(file_name="shortened-cap.csv")
        searcher.get_stocks_from_file()
        self.assertTrue(len(searcher.stock_list) > 0)

    def test_gets_data(self):
        searcher = StockSearcher(file_name="shortened-cap.csv")
        searcher.get_stocks_from_file()
        searcher.get_data_of_stocks()

    def test_run(self):
        searcher = StockSearcher(file_name="shortened-cap.csv")
        searcher.run()

    def test_run_limited(self):
        searcher = StockSearcher(file_name="nyse-cap.csv")
        searcher.get_stocks_from_file(limit=5)
        self.assertEqual(len(searcher.stock_list), 5)
