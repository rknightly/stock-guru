from StockGuru.StockSearcher import StockSearcher

def main():
    searcher = StockSearcher(file_name='combined-cap.csv')
    searcher.run()

if __name__ == "__main__":
    main()
