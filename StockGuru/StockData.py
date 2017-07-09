from bs4 import BeautifulSoup
import urllib.request


class StockData:
    def __init__(self, ticker, name, industry):
        self.ticker = ticker
        self.name = name
        self.industry = industry

        self.estimated_change_percent = 0
        self.recommended_action = ""
        self.zacks_rank = 6

        self.connection_succeeded = False
        self.data_found = False

        self.cnn_soup = BeautifulSoup()
        self.zack_soup = BeautifulSoup()

    def get_cnn_soup(self):
        try:
            url_address = "http://money.cnn.com/quote/forecast/forecast.html" \
                          "?symb=%s" % self.ticker
            r = urllib.request.urlopen(url_address).read()
            self.cnn_soup = BeautifulSoup(r, "html.parser")
            self.connection_succeeded = True
        except ConnectionResetError:
            print("connection reset")
            return

    def get_zacks_soup(self):
        try:
            url_address = "http://www.zacks.com/stock/quote/%s" % self.ticker
            r = urllib.request.urlopen(url_address).read()
            self.zack_soup = BeautifulSoup(r, "html.parser")
            self.connection_succeeded = True
        except ConnectionResetError:
            print("connection reset")
            return

    def get_soups(self):
        """
        Get the data from both cnn and zacks and store the beautiful soup from
        each site
        """
        self.get_cnn_soup()
        self.get_zacks_soup()

    def find_estimated_change_percent(self):
        # search the soup for the forecast
        analysis = self.cnn_soup.find_all("div", id="wsod_forecasts")

        # If bad ticker given, print error and skip rest
        if len(analysis) == 0:
            print("No data found for:", self.ticker, self.name)
            self.data_found = False
            return 0
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
            return 0

        just_nums = projected_change[0].text[:-1]
        no_commas = just_nums.replace(',', '')
        return float(no_commas)

    def find_recommended_action(self):
        # find section of page that states buy/sell/hold recommendation
        recommendation_section = self.cnn_soup.find_all("strong", class_="wsod_rating")
        if len(recommendation_section) == 0:
            self.data_found = False
            return ""

        return recommendation_section[0].text

    def find_zacks_rank(self):
        # find 1-5 zacks rank and return as int
        rank = 6
        research_section = self.zack_soup.find_all("section", id="premium_research")
        if len(research_section) == 0:
            return rank #not found
        rank_chip = research_section[0].find_all("span", class_="rank_chip")
        if len(rank_chip) == 0:
            return rank #not found

        try:
            rank = int(rank_chip[0].text)
        except ValueError:
            print("Value error")

        return rank

    def find_data(self):
        if not self.connection_succeeded:
            return
        self.estimated_change_percent = self.find_estimated_change_percent()
        self.recommended_action = self.find_recommended_action()
        self.zacks_rank = self.find_zacks_rank()

    def print_report(self):
        print(self.ticker, self.name)
        print("Estimated Change: %.1f%%" % self.estimated_change_percent)
        print(self.recommended_action)
        print("Zacks:", self.zacks_rank)
        print()

    def make_one_line_report(self):
        return str(self.zacks_rank) + " " + self.ticker + " " + self.name + ": " + str(self.estimated_change_percent) + "% " + self.recommended_action

    def print_one_line_report(self):
        print(self.make_one_line_report())

    def should_buy(self):
        return self.recommended_action == "Buy"
