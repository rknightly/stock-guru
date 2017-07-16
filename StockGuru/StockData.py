from bs4 import BeautifulSoup
from StockGuru.translate import translate
import urllib.request
import urllib.error
import http.client


class StockData:
    """
    A class representing one stock and the corresponding signals, which is
    responsible for searching to find those signals and reporting about them
    """

    def __init__(self, ticker, name="", industry=""):
        self.ticker = ticker.upper()
        self.name = name
        self.industry = industry

        self.estimated_change_percent = 0
        self.recommended_action = ""
        self.zacks_rank = 6
        self.street_rating = 17
        self.wsj_rating = 6
        self.ryan_rank = 0  # 0-100

        self.connection_succeeded = True
        self.data_found = False

        self.cnn_soup = BeautifulSoup("", "lxml")
        self.zack_soup = BeautifulSoup("", "lxml")
        self.the_street_soup = BeautifulSoup("", "lxml")
        self.wsj_soup = BeautifulSoup("", "lxml")

    def get_soup_from_url(self, url, as_desktop=False):
        """
        Get the BeautifulSoup from a given site

        :param url: the url of the page to get data from
        :param as_desktop: whether the client should pretend to be a desktop
         browser
        :return: the BeautifulSoup of the specified page
        """

        soup = BeautifulSoup("", "lxml")
        if not self.connection_succeeded:
            return soup

        try:
            # Pretend to be desktop browser
            if as_desktop:
                headers = {
                    'User-Agent': 'Mozilla/5.0 '
                                  '(Macintosh; Intel Mac OS X 10_10_1) '
                                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/39.0.2171.95 Safari/537.36'}
            else:
                headers = {}

            request = urllib.request.Request(url, data=None, headers=headers)

            data = urllib.request.urlopen(request)
            soup = BeautifulSoup(data, "html.parser")

        except ConnectionResetError:
            self.connection_succeeded = False
            print("connection reset")

        except TimeoutError:
            self.connection_succeeded = False
            print("Connection timed out")

        except urllib.error.HTTPError:
            self.connection_succeeded = False
            print("Page doesn't exist")

        except http.client.IncompleteRead:
            self.connection_succeeded = False
            print("Read incomplete")

        return soup

    def get_soups(self):
        """
        Get the data from each site and save them in the appropriate
        BeautifulSoup fields
        """
        self.cnn_soup = self.get_soup_from_url(
            "http://money.cnn.com/quote/forecast/forecast.html?symb=%s" %
            self.ticker)

        self.zack_soup = self.get_soup_from_url("http://www.zacks.com/stock/"
                                                "quote/%s" % self.ticker)
        self.the_street_soup = self.get_soup_from_url("http://www.thestreet.com/"
                                                  "quote/%s" % self.ticker,
                                                  as_desktop=True)
        self.wsj_soup = self.get_soup_from_url("http://quotes.wsj.com/%s/"
                                               "research-ratings"
                                               % self.ticker)

    def find_estimated_change_percent(self):
        """
        Get the projected price change of the stock as estimated by the CNN
        Money analysts
        :return: A float representing the projected price change percent, or 0
         if it is not found
        """

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
        """
        Find the buy/sell/hold recommendation from the stock's CNN Money page
        :return: CNN's buy/sell/hold recommendation for the stock as a string
         of either 'Buy', 'Sell', or 'Hold' if the recommendation is found.
         Otherwise an empty string
        """

        # find section of page that states buy/sell/hold recommendation
        recommendation_section = self.cnn_soup.find_all("strong",
                                                        class_="wsod_rating")
        if len(recommendation_section) == 0:
            self.data_found = False
            return ""

        return recommendation_section[0].text

    def find_zacks_rank(self):
        """
        Find the Zack's rank of a given stock
        :return: an int 1-5 denoting the Zack's rank if it is found.
         Otherwise the returned rank is 6
        """

        # find 1-5 Zack's rank and return as int
        rank = 6
        research_section = self.zack_soup.find_all("section",
                                                   id="premium_research")
        if len(research_section) == 0:
            return rank     # not found
        rank_chip = research_section[0].find_all("span", class_="rank_chip")
        if len(rank_chip) == 0:
            return rank     # not found

        try:
            rank = int(rank_chip[0].text)
        except ValueError:
            print("Value error")

        return rank

    def find_street_rank(self):
        """
        Find the stock's rating from TheStreet.com
        :return: An int in the range 1-16 representing the stock rating from
         TheStreet.com, found on the page as a letter grade rating ranging from
         'F' to 'A+'
        """

        rating = 17
        rating_section = self.the_street_soup.find_all("span",
                                                   class_="quote-nav-rating"
                                                          "-qr-rating")
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
            rating = possible_ratings.index(rating_letter) + 1

        return rating

    def find_wsj_rating(self):
        """
        Find the stock rating given by the Wall Street Journal on the website
        as a ranking of BUY/OVERWEIGHT/HOLD/UNDERWEIGHT/SELL
        :return: an int in the range 1 to 5 representing the WSJ analyst
         consensus, with 1 being the best and 5 the worst
        """
        rating = 6

        rating_section = self.wsj_soup.find_all("div",
                                                class_="cr_analystRatings")
        if len(rating_section) == 0:
            return rating

        ratings = rating_section[0].find_all("div",
                                             class_="numValue-content")
        if len(ratings) < 3:
            return rating

        # remove leading and trailing spaces with strip
        consensus = ratings[2].text.upper().strip()
        ratings = {"BUY": 1, "OVERWEIGHT": 2, "HOLD": 3, "UNDERWEIGHT": 4,
                   "SELL": 5}

        return ratings[consensus]

    def find_data(self):
        """
        Find all of the stock values of interest from the Soups and fill the
        fields with the found values.
        Soups must already be retrieved
        """

        if not self.connection_succeeded:
            return

        self.estimated_change_percent = self.find_estimated_change_percent()
        self.recommended_action = self.find_recommended_action()
        self.zacks_rank = self.find_zacks_rank()
        self.street_rating = self.find_street_rank()
        self.wsj_rating = self.find_wsj_rating()

        self.ryan_rank = self.get_ryan_rank()

    def get_ryan_rank(self):
        """
        Create a 'Ryan Rank' between 0 to 100 that takes into account each of
        the signals
        :return: the Ryan Rank as an int in the range 0-100
        """
        total_points = 0
        # TODO: maybe change to signals[] containing ints that can be averaged
        total_points += translate(self.estimated_change_percent, -50, 50, 0,
                                  100)
        total_points += translate(self.zacks_rank, 1, 5, 100, 0)
        total_points += translate(self.street_rating, 1, 16, 100, 0)
        total_points += translate(self.wsj_rating, 1, 5, 100, 0)

        if self.recommended_action == "Buy":
            total_points += 100
        elif self.recommended_action == "Hold":
            total_points += 50
        elif self.recommended_action == "Sell":
            total_points += 0

        return total_points / 5

    def print_report(self):
        """
        Print a detailed multi-line report of the stock meant to be displayed
        during data collection
        """

        print(self.ticker, self.name)
        print("Ryan Rank:", str(self.ryan_rank)[:5])
        print("Estimated Change: %.1f%%" % self.estimated_change_percent,
              self.recommended_action)
        print("Zacks:", self.zacks_rank, "Street:", self.street_rating, "WSJ:",
              self.wsj_rating)

    def make_one_line_report(self):
        """
        Create a summary one line report of the stock and the information
        found about it
        :return: a string containing the summary report
        """

        report = ""

        report += str(self.ryan_rank)[:5] + " "     # Ryan Rank
        report += "Z:" + str(self.zacks_rank) + " "     # Zack's Rank
        report += "S:" + str(self.street_rating) + " "  # Street Rank
        report += "WSJ:" + str(self.wsj_rating) + " "   # WSJ Rating
        report += self.ticker + " " + self.name + ": "  # Name
        report += str(self.estimated_change_percent) + "% "     # Est. change %
        report += self.recommended_action   # CNN recommended action

        return report

    def print_one_line_report(self):
        """
        Print a one line summary report describing the stock and its found data
        """
        print(self.make_one_line_report())
