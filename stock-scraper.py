from bs4 import BeautifulSoup
import urllib.request
import csv

class StockData:
    def __init__(self, ticker, name, industry):
        self.ticker = ticker
        self.name = name
        self.industry = industry

        self.estimated_change_percent = 0
        self.recommended_action = ""

        self.data_found = False

        self.soup  = BeautifulSoup()

    def get_soup(self):
        url_address = "http://money.cnn.com/quote/forecast/forecast.html?symb=%s" % self.ticker
        r = urllib.request.urlopen(url_address).read()

        self.soup = BeautifulSoup(r, "html.parser")

    def find_estimated_change_percent(self):
        # search the soup for the forecast
        analysis = self.soup.find_all("div", id="wsod_forecasts")

        # If bad ticker given, print error and skip rest
        if len(analysis) == 0:
            print("No data found for:", self.ticker, self.name)
            self.data_found = False
            return
        else:
            self.data_found = True

        analysis = analysis[0]

        # search the forecast for the paragraph
        analysis_text = analysis.find_all("p")[0]

        # find the projected growth in the paragraph
        # check both negData and posData for the percent change
        projected_change = analysis_text.find_all("span", class_="negData")
        if len(projected_change) == 0:
            projected_change = analysis_text.find_all("span", class_="posData")

        # If can't find projected change, forget it
        if len(projected_change) == 0:
            print("No data found for:", self.ticker, self.name)
            self.data_found = False
            return

        self.estimated_change_percent = float(projected_change[0].text[:-1])

    def find_recommended_action(self):
        # TODO: find section of page that states buy/sell/hold recommendation
        # analysis_sections = self.soup.find_all("div", class_="wsod_twoCol")
        # print(analysis_sections)
        # recommended_section = analysis_sections[1]
        # print(recommended_section)
        recommendation_section = self.soup.find_all("strong", class_="wsod_rating")
        if len(recommendation_section) == 0:
            self.data_found = False
            return ""

        self.recommended_action = recommendation_section[0].text
        print(self.recommended_action)

    def print_report(self):
        print(self.ticker, self.name)
        print("Estimated Change: %.1f%%" % self.estimated_change_percent)
        print()

    def print_one_line_report(self):
        print(self.ticker, self.name + ":", str(self.estimated_change_percent) + "%")

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
        print(file_rows)

        for stock_info in file_rows:
            ticker, name, industry = stock_info
            stock_data = StockData(ticker, name, industry)

            self.stock_list.append(stock_data)

    def get_data_of_stocks(self):
        indeces_to_remove = []
        # Request data for each stock
        for index, stock in enumerate(self.stock_list):
            stock.get_soup()
            stock.find_estimated_change_percent()
            if not stock.data_found:
                indeces_to_remove.append(index)
            stock.print_report()

        # remove stocks with no results
        for index in indeces_to_remove[::-1]:
            self.stock_list.pop(index)

    def print_highest_projected_stocks(self):
        print("=========== REPORT ============")

        # Sort the stocks by their estimated change percent, highest to lowest
        sorted_stocks = sorted(self.stock_list,
                               key=lambda stock: stock.estimated_change_percent,
                               reverse=True)
        for stock in sorted_stocks[:50]:
            stock.print_one_line_report()


# searcher = StockSearcher(file_name = 'constituents.csv')
# searcher.get_stocks_from_file()
# searcher.get_data_of_stocks()
# searcher.print_highest_projected_stocks()
test_stock = StockData("AAPL", "Apple", "Tech")
test_stock.get_soup()
test_stock.find_recommended_action()
