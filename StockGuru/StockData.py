from bs4 import BeautifulSoup
import urllib.request
import urllib.error

class StockData:
    def __init__(self, ticker, name, industry):
        self.ticker = ticker
        self.name = name
        self.industry = industry

        self.estimated_change_percent = 0
        self.recommended_action = ""
        self.zacks_rank = 6
        self.street_rating = 16
        self.ryan_rank = 0  # 0-100

        self.connection_succeeded = True
        self.data_found = False

        self.cnn_soup = BeautifulSoup()
        self.zack_soup = BeautifulSoup()
        self.street_soup = BeautifulSoup()

    def get_cnn_soup(self):
        if not self.connection_succeeded:
            return

        try:
            url_address = "http://money.cnn.com/quote/forecast/forecast.html" \
                          "?symb=%s" % self.ticker
            r = urllib.request.urlopen(url_address).read()
            self.cnn_soup = BeautifulSoup(r, "html.parser")
        except ConnectionResetError:
            self.connection_succeeded = False
            print("connection reset")
            return

    def get_zacks_soup(self):
        if not self.connection_succeeded:
            return

        try:
            url_address = "http://www.zacks.com/stock/quote/%s" % self.ticker
            r = urllib.request.urlopen(url_address).read()
            self.zack_soup = BeautifulSoup(r, "html.parser")
        except ConnectionResetError:
            self.connection_succeeded = False
            print("connection reset")
            return

    def get_street_soup(self):
        if not self.connection_succeeded:
            return
        
        try:
            url_address = "http://www.thestreet.com/quote/%s" % self.ticker
            h = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            request = urllib.request.Request(url_address, data=None, headers=h)

            r = urllib.request.urlopen(request)

            self.street_soup = BeautifulSoup(r, "html.parser")
        except ConnectionResetError:
            self.connection_succeeded = False
            print("connection reset")
            return
        except urllib.error.HTTPError:
            self.connection_succeeded = False
            print("Street page doesn't exist")
            return

    def get_soups(self):
        """
        Get the data from both cnn and zacks and store the beautiful soup from
        each site
        """
        self.get_cnn_soup()
        self.get_zacks_soup()
        self.get_street_soup()

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

    def find_street_rank(self):
        """Return rating 0-15 from thestreet"""
        rating = 16
        rating_section = self.street_soup.find_all("span", class_="quote-nav-rating-qr-rating")
        if len(rating_section) == 0:
            return rating

        possible_ratings = ["A+", "A ", "A-",
                            "B+", "B ", "B-",
                            "C+", "C ", "C-",
                            "D+", "D ", "D-",
                            "E+", "E ", "E-",
                            "F "]
        rating_letter = rating_section[0].text[:2]
        if rating_letter in possible_ratings:
            rating = possible_ratings.index(rating_letter)

        return rating

    def find_data(self):
        if not self.connection_succeeded:
            return
        self.estimated_change_percent = self.find_estimated_change_percent()
        self.recommended_action = self.find_recommended_action()
        self.zacks_rank = self.find_zacks_rank()
        self.street_rating = self.find_street_rank()

        self.ryan_rank = self.get_ryan_rank()

    def get_ryan_rank(self):
        scaled_change_percent = translate(self.estimated_change_percent, -50, 50, 0, 100)
        scaled_zack_rank = translate(self.zacks_rank, 1, 5, 100, 0)
        scaled_street_rating = translate(self.street_rating, 0, 15, 100, 0)

        if self.recommended_action == "Buy":
            scaled_recommendation = 100
        elif self.recommended_action == "Hold":
            scaled_recommendation = 50
        else:
            scaled_recommendation = 0

        return (scaled_change_percent + scaled_zack_rank + scaled_street_rating + scaled_recommendation) / 4


    def print_report(self):
        print(self.ticker, self.name)
        print("Ryan Rank:", str(self.ryan_rank)[:5])
        print("Estimated Change: %.1f%%" % self.estimated_change_percent, self.recommended_action)
        print("Zacks:", self.zacks_rank, "Street:", self.street_rating)

    def make_one_line_report(self):
        return str(self.ryan_rank)[:5] + " Z: " + str(self.zacks_rank) + " S:" + str(self.street_rating) + " " + self.ticker + " " + self.name + ": " + str(self.estimated_change_percent) + "% " + self.recommended_action

    def print_one_line_report(self):
        print(self.make_one_line_report())

    def should_buy(self):
        return self.recommended_action == "Buy"


def translate(value, current_min, current_max, new_min, new_max):
    if value < current_min:
        return new_min
    if value > current_max:
        return new_max


    # Figure out how 'wide' each range is
    left_span = current_max - current_min
    right_span = new_max - new_min

    # Convert the left range into a 0-1 range (float)
    value_scaled = float(value - current_min) / float(left_span)

    # Convert the 0-1 range into a value in the right range.
    return new_min + (value_scaled * right_span)
