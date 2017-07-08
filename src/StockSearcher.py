import csv
from src.StockData import StockData


class StockSearcher:
    def __init__(self, file_name):
        self.file_name = "resources/" + file_name

        self.stock_list = []

    def get_stocks_from_file(self):
        file_rows = []
        with open(self.file_name) as f:
            reader = csv.reader(f)
            for row in reader:
                file_rows.append(row)

        for stock_info in file_rows:
            ticker, name, industry, cap = stock_info[:4]
            # Only count if value in billions
            if cap[-1] == "B":
                stock_data = StockData(ticker, name, industry)
                self.stock_list.append(stock_data)

    def get_data_of_stocks(self):
        indeces_to_remove = []
        # Request data for each stock
        for index, stock in enumerate(self.stock_list):
            stock.get_soups()
            stock.find_data()
            if not stock.data_found:
                indeces_to_remove.append(index)
            stock.print_report()

        # remove stocks with no results
        for index in indeces_to_remove[::-1]:
            self.stock_list.pop(index)

    def find_highest_projected_stocks(self):
        print("=========== REPORT ============")

        # Sort the stocks by their estimated change percent, highest to lowest
        sorted_stocks = sorted(self.stock_list,
                               key=lambda stock: (stock.zacks_rank,
                                                  -stock.estimated_change_percent))[:50]

        for stock in sorted_stocks:
            stock.print_one_line_report()

        return sorted_stocks

    def filter_for_buy(self):
        stocks_to_buy = [stock for stock in self.stock_list if stock.should_buy()]
        self.stock_list = stocks_to_buy

    def write_results_to_file(self, stocks_to_write):
        with open('results.txt', 'w') as results_file:
            for stock in stocks_to_write:
                results_file.write(stock.make_one_line_report() + "\n")

    def run(self):
        self.get_stocks_from_file()
        self.get_data_of_stocks()
        self.filter_for_buy()
        highest_projected = self.find_highest_projected_stocks()
        self.write_results_to_file(highest_projected)
