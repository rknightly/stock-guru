from src.StockSearcher import StockSearcher


def main():
    searcher = StockSearcher(file_name='shortened-cap.csv')
    searcher.run()
