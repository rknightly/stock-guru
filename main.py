from StockGuru.StockSearcher import StockSearcher


def main():
    """
    The main function that runs the program in full
    """
    searcher = StockSearcher(file_name='combined-cap.csv')
    searcher.run()
    quit()

if __name__ == "__main__":
    main()
