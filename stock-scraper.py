from bs4 import BeautifulSoup
import urllib.request
import csv

class StockData:
    def __init__(self, ticker, name, industry):
        self.ticker = ticker
        self.name = name
        self.industry = industry

        self.estimated_change_percent = 0
        self.data_found = false

    def find_estimated_change_percent(self):
        # Get the soup of the website
        url_address = "http://money.cnn.com/quote/forecast/forecast.html?symb=%s" % self.ticker
        r = urllib.request.urlopen(url_address).read()

        soup = BeautifulSoup(r, "lxml")

        # search the soup for the forecast
        analysis = soup.find_all("div", id="wsod_forecasts")

        # If bad ticker given, print error and skip rest
        if len(analysis) == 0:
            print("No data found for:", self.ticker, self.name)
            return
        else:
            self.data_found = true

        analysis = analysis[0]

        # search the forecast for the paragraph
        analysis_text = analysis.find_all("p")[0]

        # find the projected growth in the paragraph
        # check both negData and posData for the percent change
        projected_change = analysis_text.find_all("span", class_="negData")
        if len(projected_change) == 0:
            projected_change = analysis_text.find_all("span", class_="posData")

        self.estimated_change_percent = float(projected_change[0].text[:-1])

    def print_report(self):
        print(self.ticker, self.name)
        print("Estimated Change: %.1f%%" % self.estimated_change_percent)
        print()


# TODO: add analyst count report and estimate spread report

class StockSearcher:
    def __init__(self, file_name):
        self.file_name = file_name

        self.stock_list = []

    def get_stocks_from_file(self):
        file_rows = []
        with open(self.file_name) as f:
            reader = csv.reader(f)
            for row in reader:
                file_rows.append(row)

        for stock_info in file_rows:
            ticker, name, industry = stock_info
            stock_data = StockData(ticker, name, industry)

            if stock_data.data_found:
                self.stock_list.append(stock_data)

    def get_data_of_stocks(self):
        for stock in self.stock_list:
            stock.find_estimated_change_percent()
            stock.print_report()

searcher = StockSearcher(file_name = 'constituents.csv')
searcher.get_stocks_from_file()
searcher.get_data_of_stocks()
