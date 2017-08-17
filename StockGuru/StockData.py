from bs4 import BeautifulSoup

from threading import Thread
import requests
import http.client
import csv
from StockGuru.translate import translate
from StockGuru.Signal import Signal


class StockData:
    """
    A class representing one stock and the corresponding signals, which is
    responsible for searching to find those signals and reporting about them
    """

    def __init__(self, ticker, name="", industry="", exchange = ""):
        self.ticker = ticker.upper()
        self.name = name
        self.industry = industry
        self.exchange = exchange

        self.change_percent = Signal(name="Change Percent", worst=-50, best=50, default=0)
        self.recommended_action = Signal(name="Recommended Action", worst=3, best=1, default=4)
        self.zacks_rank = Signal(name="Zack's Rank", worst=5, best=1, default=6)
        self.street_rating = Signal(name="TheStreet Rank", worst=16, best=1, default=17)
        self.wsj_rating = Signal(name="Wall Street Journal Rank", worst=5, best=1, default=6)
        self.yahoo_rating = Signal(name="Yahoo Rating", worst=5, best=1, default=6)
        self.morning_rating = Signal(name="MorningStar Rating", worst=5, best=1, default=6)

        self.signals = []

        self.ryan_rank = 0  # 0-100

        self.failed_connections = 0

        self.cnn_soup = BeautifulSoup("", "lxml")
        self.zack_soup = BeautifulSoup("", "lxml")
        self.the_street_soup = BeautifulSoup("", "lxml")
        self.wsj_soup = BeautifulSoup("", "lxml")
        self.morning_soup = BeautifulSoup("", "lxml")

    def get_soup_from_url(self, url, as_desktop=False):
        """
        Get the BeautifulSoup from a given site

        :param url: the url of the page to get data from
        :param as_desktop: whether the client should pretend to be a desktop
         browser
        :return: the BeautifulSoup of the specified page
        """

        soup = BeautifulSoup("", "lxml")
        if self.failed_connections > 1:
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

            request = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(request.text, "html.parser")

        except ConnectionResetError:
            self.failed_connections += 1
            print("connection reset")

        except TimeoutError:
            self.failed_connections += 1
            print("Connection timed out")

        except requests.exceptions.ConnectionError:
            self.failed_connections += 1
            print("Page doesn't exist")

        except http.client.IncompleteRead:
            self.failed_connections += 1
            print("Read incomplete")

        except requests.exceptions.ContentDecodingError:
            self.failed_connections += 1
            print("Decoding incomplete")

        return soup

    def get_cnn_soup(self):
        self.cnn_soup = self.get_soup_from_url(
            "http://money.cnn.com/quote/forecast/forecast.html?symb=%s" %
            self.ticker)

    def get_zack_soup(self):
        self.zack_soup = self.get_soup_from_url("http://www.zacks.com/stock/"
                                                "quote/%s" % self.ticker)

    def get_street_soup(self):
        self.the_street_soup = self.get_soup_from_url(
            "http://www.thestreet.com/"
            "quote/%s" % self.ticker,
            as_desktop=True)

    def get_wsj_soup(self):
        self.wsj_soup = self.get_soup_from_url("http://quotes.wsj.com/%s/"
                                               "research-ratings"
                                               % self.ticker)

    def get_morning_soup(self):
        if self.exchange == "": # Can be blank during single stock testing
            self.exchange = self.find_exchange()

        base = "http://quotes.morningstar.com/stockq/c-recommencation?&t="
        stock_id = "X" + self.exchange + ":" + self.ticker
        suffix = "&region=usa&culture=en-US&version=RET&cur=&test=" \
                 "QuoteiFrame&e=eyJlbmMiOiJBMTI4R0NNIiwiYWxnIjoiUlNBL" \
                 "U9BRVAifQ.HpJeYT9FRT6AkSbtdAwVjvYfPRwOZx7eHZmrPiGZM6SB" \
                 "J8J5Mc_-x1CA5kRBLEg1hzEQDRwbcEL6SDgEHU7fxJZs-b9abVPJp1E" \
                 "Zq6PhZrxjn4HylT_UaPET1DWxD5wfPd87i-wos4iyaevVEQwaMpSqFXZ" \
                 "Z-29mL7Io3zTXn5Q.60gJvlGHAJOIt1pK.2DO0KmXNlEkqTjJnazA0cf" \
                 "NNNbRaHX7oonvuEp0K_uasWfcDcVGm0tD4a_WtTE-UHjeWL7N9-ZgW_M" \
                 "fc-UZ4yDx8yV24BZPFGIM36hKd3IWst3wcJ33u9RyCdMiHlDSVKoZRIq" \
                 "6QLg7BFbyUbGxH6MFAczMHutwOASixrZqJ7isMbF1RcT4wqQjxehW7LI" \
                 "gfDb9vHdy6r3EPKvj3jrZFsJbAP5-EaSH3c06_WGk.uGxBBDu8WOmE92" \
                 "fw5WNZnQ"
        self.morning_soup = self.get_soup_from_url(base + stock_id + suffix)

    def get_yahoo_rating(self):
        lhs_url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/'
        rhs_url = '?formatted=true&crumb=swg7qs5y9UP&lang=en-US&region=US&' \
                  'modules=upgradeDowngradeHistory,recommendationTrend,' \
                  'financialData,earningsHistory,earningsTrend,industryTrend&' \
                  'corsDomain=finance.yahoo.com'

        url = lhs_url + self.ticker + rhs_url
        r = requests.get(url)
        if not r.ok:
            return
        try:
            result = r.json()['quoteSummary']['result'][0]
            # TODO: set value outside of method, with other value sets
            self.yahoo_rating.set_value(result['financialData']['recommendationMean']['fmt'])
        except (ValueError, KeyError):
            return

    def get_soups(self):
        """
        Get the data from each site and save them in the appropriate
        BeautifulSoup fields
        """
        threads = list()
        threads.append(Thread(target=self.get_cnn_soup))
        threads.append(Thread(target=self.get_zack_soup))
        threads.append(Thread(target=self.get_street_soup))
        threads.append(Thread(target=self.get_wsj_soup))
        threads.append(Thread(target=self.get_morning_soup))
        threads.append(Thread(target=self.get_yahoo_rating)) # doesn't require soup

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    def find_change_percent(self):
        # search the soup for the forecast
        analysis = self.cnn_soup.find_all("div", id="wsod_forecasts")

        # If bad ticker given, print error and skip rest
        if len(analysis) == 0:
            print("No data found for:", self.ticker, self.name)
            return self.find_yahoo_change_percent()     # fallback to yahoo

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
            return self.find_yahoo_change_percent()  # fallback to yahoo

        just_nums = projected_change[0].text[:-1]
        no_commas = just_nums.replace(',', '')
        return float(no_commas)

    def find_yahoo_change_percent(self):
        """
        Get the projected price change of the stock as estimated by the analysts
        :return: A float representing the projected price change percent, or 0
         if it is not found
        """
        print("falling back to yahoo for change %")

        yahoo_soup = self.get_soup_from_url("https://finance.yahoo.com/"
                                                 "quote/%s" % self.ticker)
        change_percent = 0

        quote_list = self.wsj_soup.find_all("span", id="quote_val")
        try:
            current_price = float(quote_list[0].text)
        except IndexError:
            print("No current Value")
            return change_percent
        except ValueError:
            print("value error")
            return change_percent

        target_cell_list = yahoo_soup.find_all(
            "td", attrs={"data-test": "ONE_YEAR_TARGET_PRICE-value"})
        if len(target_cell_list) == 0:
            return change_percent

        try:
            projected_price = float(target_cell_list[0].text)
        except ValueError:
            print("Value error")
            return change_percent

        projected_change = projected_price - current_price
        if projected_change != 0:
            change_percent = projected_change / current_price * 100

        change_percent = float(" {0:.2f}".format(change_percent))

        return change_percent

    def find_recommended_action(self):
        """
        Find the buy/sell/hold recommendation from the stock's CNN Money page
        :return: CNN's buy/sell/hold recommendation for the stock as a number
         of 1/2/3 corrresponding to Buy/Sell/Hold if the recommendation is found.
         Otherwise 4
        """
        numerical_value = 4

        # find section of page that states buy/sell/hold recommendation
        recommendation_section = self.cnn_soup.find_all("strong",
                                                        class_="wsod_rating")
        if len(recommendation_section) == 0:
            return numerical_value

        action_str = recommendation_section[0].text

        if action_str == "Buy":
            numerical_value = 1
        elif action_str == "Hold":
            numerical_value = 2
        elif action_str == "Sell":
            numerical_value = 3

        return numerical_value

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

        if consensus not in ratings:
            return rating

        return ratings[consensus]

    def find_morning_rating(self):
        try:
            recommendation_section = self.morning_soup.find(
                "tr", class_="gr_table_row7")
            recommendation_text = recommendation_section.find_all(
                "td")[1].text.strip()
            return translate(float(recommendation_text), 1, 5, 5, 1)
        except (IndexError, ValueError, AttributeError):
            return 6

    def find_data(self):
        """
        Find all of the stock values of interest from the Soups and fill the
        fields with the found values.
        Soups must already be retrieved
        """

        self.recommended_action.set_value(self.find_recommended_action())
        self.zacks_rank.set_value(self.find_zacks_rank())
        self.street_rating.set_value(self.find_street_rank())
        self.wsj_rating.set_value(self.find_wsj_rating())
        self.change_percent.set_value(self.find_change_percent())
        self.morning_rating.set_value(self.find_morning_rating())

        self.delete_soups()     # done with soups, free up space

        self.signals.append(self.recommended_action)
        self.signals.append(self.zacks_rank)
        self.signals.append(self.street_rating)
        self.signals.append(self.wsj_rating)
        self.signals.append(self.change_percent)
        self.signals.append(self.morning_rating)

        self.ryan_rank = self.get_ryan_rank()

    def count_missing_values(self):
        missing_values = 0
        for signal in self.signals:
            if not signal.is_found:
                missing_values += 1

        return missing_values

    def get_ryan_rank(self):
        """
        Create a 'Ryan Rank' between 0 to 100 that takes into account each of
        the signals
        :return: the Ryan Rank as an int in the range 0-100
        """
        missing_values = self.count_missing_values()
        effective_signal_values = [signal.get_scaled_score() for signal in self.signals
                                   if signal.is_found or missing_values > 1]

        rank = sum(effective_signal_values) / len(effective_signal_values)
        return round(rank, 2)

    def find_exchange(self):
        with open("resources/combined-cap.csv") as f:
            reader = csv.reader(f)
            for row in reader:
                ticker, name, industry, cap, exchange = row[:5]
                if ticker.lower() == self.ticker.lower():
                    return exchange

    def delete_soups(self):
        self.cnn_soup = None
        self.zack_soup = None
        self.the_street_soup = None
        self.wsj_soup = None

    def print_report(self):
        """
        Print a detailed multi-line report of the stock meant to be displayed
        during data collection
        """

        print(self.ticker, self.name)
        print("Ryan Rank:", str(self.ryan_rank)[:5])
        print("Estimated Change: %.1f%%" %
              self.change_percent.numerical_value,
              self.recommended_action.numerical_value)
        print("Yahoo:", self.yahoo_rating.numerical_value, "Zacks:", self.zacks_rank.numerical_value,
              "Street:", self.street_rating.numerical_value, "WSJ:", self.wsj_rating.numerical_value,
              "M:", self.morning_rating.numerical_value)

    def make_one_line_report(self):
        """
        Create a summary one line report of the stock and the information
        found about it
        :return: a string containing the summary report
        """

        report = ""

        report += str(self.ryan_rank) + " "     # Ryan Rank
        report += "Y:" + str(self.yahoo_rating.value_string) + " "
        report += "Z:" + str(self.zacks_rank.value_string) + " "     # Zack's Rank
        report += "WSJ:" + str(self.wsj_rating.value_string) + " "   # WSJ Rating
        report += "S:" + str(self.street_rating.value_string) + " "  # Street Rank
        report += "M:" + str(self.morning_rating.value_string) + " "     # Morning rating
        report += self.ticker + " " + self.name[:20] + ": "  # Name
        report += str(self.change_percent.value_string) + "%, "
        report += self.recommended_action.value_string   # CNN recommended action

        return report

    def print_one_line_report(self):
        """
        Print a one line summary report describing the stock and its found data
        """
        print(self.make_one_line_report())

    @staticmethod
    def get_csv_data_headings():
        return ["Top of The Market Rating",
                "Yahoo (1-5)",
                "Zacks (1-5)",
                "Wall Street Journal Rating (1-5)",
                "MorningStar (1-5)",
                "Street Rank (1-16)",
                "Ticker",
                "Company Name",
                "Projected Change % in 12 Months",
                "CNN Recommendation"]

    def get_csv_data_list(self):
        return [self.ryan_rank,
                self.yahoo_rating.numerical_value,
                self.zacks_rank.numerical_value,
                self.wsj_rating.numerical_value,
                self.morning_rating.numerical_value,
                self.street_rating.numerical_value,
                self.ticker,
                self.name,
                self.change_percent.numerical_value,
                self.recommended_action.numerical_value]
