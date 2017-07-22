import csv
import time
import datetime
from StockGuru.StockData import StockData


class StockSearcher:
    """
    A class that reads the stocks from a given file and retrieves the data of
    each. It then sorts the stocks and writes the resulting list to a file
    """

    def __init__(self, file_name, only_billions=True):
        """
        :param file_name: the name of the csv file that contains the stock data
        """

        self.file_name = "resources/" + file_name
        self.only_billions = only_billions

        self.stock_list = []
        self.start_time = time.time()

    def get_stocks_from_file(self, limit=0):
        """
        Read the data of the stocks contained in the given file
        :param limit: an optional argument of the max number of stocks to
         search. leaving the limit as 0 results in a search of every stock in
         the file
        """

        file_rows = []
        with open(self.file_name) as f:
            reader = csv.reader(f)
            for row in reader:
                file_rows.append(row)

        for stock_info in file_rows:
            ticker, name, industry, cap = stock_info[:4]

            if cap[-1] == 'B' or not self.only_billions:
                stock_data = StockData(ticker, name, industry)
                self.stock_list.append(stock_data)

            # Handle limiting
            if limit > 0:
                if len(self.stock_list) >= limit:
                    break

        print("TOTAL SIZE:", len(self.stock_list))

    def get_data_of_stocks(self):
        """
        Get the data of each of the stocks in the list and print the stock
        data and current progress as each stock is searched
        """

        indexes_to_remove = []
        # Request data for each stock
        for index, stock in enumerate(self.stock_list):
            stock.get_soups()
            stock.find_data()
            stock.print_report()
            self.print_progress(index)

        # remove stocks with no results
        for index in indexes_to_remove[::-1]:
            self.stock_list.pop(index)

    def print_progress(self, current_stock_index):
        """
        Print the progress of the stock search session.
        This contains both the percent of stocks searched so far, the current
        time elapsed since the start of the search, and as well as an
        estimation of the time remaining.
        :param current_stock_index: The index of the stock most recently
         searched
        """

        progress = float(current_stock_index + 1) / float(len(self.stock_list))
        progress_str = str(progress * 100)
        print("Progress:", progress_str[:4], "%")

        elapsed_seconds = time.time() - self.start_time
        elapsed_minutes = float(elapsed_seconds) / 60.0

        remaining_minutes = (elapsed_minutes / progress) - elapsed_minutes
        print(str(remaining_minutes).split('.')[0], "Minutes remaining, ",
              str(elapsed_minutes).split('.')[0], "minutes elapsed.")
        print()

    def find_highest_projected_stocks(self):
        """
        Sort the stocks by their Ryan Rank, from highest to lowest
        :return: a list containing the stocks in a sorted order
        """

        sorted_stocks = sorted(self.stock_list,
                               key=lambda stock: stock.ryan_rank,
                               reverse=True)

        return sorted_stocks

    @staticmethod
    def print_report(stocks_to_print):
        """
        Print a report of the given stocks as a series of one line summary
        reports
        :param stocks_to_print: a list of the stocks to print as StockData
         objects
        """

        print("=========== REPORT ============")
        for stock in stocks_to_print:
            stock.print_one_line_report()

    @staticmethod
    def write_results_to_file(stocks_to_write):
        """
        Write the data of the given stocks to a results file
        :param stocks_to_write: a list of the stocks to write to the file as a
         list of StockData objects
        """
        date = datetime.date.today()
        date_str = str(date.year) + '-' + str(date.month) + '-' + str(date.day)
        file_name_core = 'results-' + date_str

        with open("results/txt/" + file_name_core + ".txt",
                  'w') as txt_results_file:

            for stock in stocks_to_write:
                txt_results_file.write(stock.make_one_line_report() + "\n")

        with open("results/csv/" + file_name_core + ".csv",
                  'w') as csv_results_file:

            writer = csv.writer(csv_results_file)
            writer.writerow(StockData.get_csv_data_headings())
            for stock in stocks_to_write:
                writer.writerow(stock.get_csv_data_list())

    def run(self, limit=0):
        """
        Run the searcher completely: read the stocks from file, retrieve data
        on each of them, sort them, report the results
        :param limit: an optional argument of the max number of stocks to
         search. Leaving the limit as 0 results in a search of every stock in
         the given file
        """

        self.get_stocks_from_file(limit=limit)
        self.get_data_of_stocks()
        highest_projected = self.find_highest_projected_stocks()
        self.print_report(highest_projected)
        self.write_results_to_file(highest_projected)
