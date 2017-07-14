import csv
import time
from StockGuru.StockData import StockData


class StockSearcher:
    def __init__(self, file_name):
        self.file_name = "resources/" + file_name

        self.stock_list = []
        self.start_time = time.time()

    def get_stocks_from_file(self, limit=0):
        file_rows = []
        with open(self.file_name) as f:
            reader = csv.reader(f)
            for row in reader:
                file_rows.append(row)
        print("TOTAL SIZE:", len(file_rows))
        for stock_info in file_rows:
            ticker, name, industry, cap = stock_info[:4]
            # TODO: make billions check a separate sort
            # Only count if value in billions

            # if cap[-1] == "B":
            stock_data = StockData(ticker, name, industry)
            self.stock_list.append(stock_data)

            # Handle limiting
            if limit > 0:
                if len(self.stock_list) >= limit:
                    break

    def get_data_of_stocks(self):
        indeces_to_remove = []
        # Request data for each stock
        for index, stock in enumerate(self.stock_list):
            stock.get_soups()
            stock.find_data()
            if not stock.data_found:
                indeces_to_remove.append(index)
            stock.print_report()
            self.print_progress(index)

        # remove stocks with no results
        for index in indeces_to_remove[::-1]:
            self.stock_list.pop(index)

    def print_progress(self, current_stock_index):
        progress = float(current_stock_index + 1) / float(len(self.stock_list))
        progress_str = str(progress * 100)
        print("Progress:", progress_str[:4], "%")

        elapsed_seconds = time.time() - self.start_time
        elapsed_minutes = float(elapsed_seconds) / 60.0

        remaining_minutes = elapsed_minutes / progress
        print(str(remaining_minutes).split('.')[0], "Minutes remaining, ",
              str(elapsed_minutes).split('.')[0], "minutes elapsed.")
        print()

    def find_highest_projected_stocks(self):
        print("=========== REPORT ============")

        # Sort the stocks by their estimated change percent, highest to lowest
        sorted_stocks = sorted(self.stock_list,
                               key=lambda s: s.ryan_rank,
                               reverse=True)

        for stock in sorted_stocks:
            stock.print_one_line_report()

        return sorted_stocks

    def write_results_to_file(self, stocks_to_write):
        with open('results.txt', 'w') as results_file:
            for stock in stocks_to_write:
                results_file.write(stock.make_one_line_report() + "\n")

    def run(self, limit=0):
        self.get_stocks_from_file(limit=limit)
        self.get_data_of_stocks()
        highest_projected = self.find_highest_projected_stocks()
        self.write_results_to_file(highest_projected)
