from StockGuru.StockSearcher import StockSearcher
from StockGuru.StockData import StockData
import argparse


def main():
    """
    The main function that runs the program in full
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", action='store_true',
                        help='Test stocks individually')
    args, leftovers = parser.parse_known_args()

    if args.test:
        individual_test()
    else:
        total_search()


def total_search():
    """
    Search through a list of stocks and report the ranked list
    """
    searcher = StockSearcher(file_name='combined-cap.csv')
    searcher.run()
    quit()


def individual_test():
    """
    Ask for individual stock tickers and print a report on each specified stock
    """
    ticker = input("\nTicker: ")
    while ticker is not "":
        report_one_stock(ticker)
        ticker = input("\nTicker: ")


def report_one_stock(ticker):
    """
    Search for and print the data of a single stock
    :param ticker: The ticker of the stock to search as a string
    """
    stock = StockData(ticker=ticker)
    stock.get_soups()
    stock.find_data()
    stock.print_report()

if __name__ == "__main__":
    main()
