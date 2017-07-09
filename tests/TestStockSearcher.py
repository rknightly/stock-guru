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

        # Make sure that all remaining stocks have data
        all_data_found = True
        for stock in searcher.stock_list:
            if not stock.data_found:
                all_data_found = False

        self.assertTrue(all_data_found)

    def test_filter_for_buy(self):
        searcher = StockSearcher(file_name="shortened-cap.csv")
        searcher.get_stocks_from_file()
        searcher.get_data_of_stocks()
        searcher.filter_for_buy()

        # Make sure that only "Buy" recommended stocks remain
        only_buys = True
        for stock in searcher.stock_list:
            if not stock.recommended_action == "Buy":
                only_buys = False
        self.assertTrue(only_buys)

    def test_run(self):
        searcher = StockSearcher(file_name="shortened-cap.csv")
        searcher.run()

        # Make sure that all remaining stocks have data
        all_data_found = True
        for stock in searcher.stock_list:
            if not stock.data_found:
                all_data_found = False

        self.assertTrue(all_data_found)

        # Make sure that only "Buy" recommended stocks remain
        only_buys = True
        for stock in searcher.stock_list:
            if not stock.recommended_action == "Buy":
                only_buys = False
        self.assertTrue(only_buys)
