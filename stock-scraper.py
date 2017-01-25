from bs4 import BeautifulSoup
import urllib.request

# Get the soup of the website
r = urllib.request.urlopen('http://money.cnn.com/quote/forecast/forecast.html?symb=AAPL').read()
soup = BeautifulSoup(r, "lxml")

# search the soup for the forecast
analysis = soup.find_all("div", id="wsod_forecasts")[0]

# search the forecast for the paragraph
analysis_text = analysis.find_all("p")[0]

# find the projected growth in the paragraph
# check both negData and posData for the percent change
projected_change = analysis_text.find_all("span", class_="negData")
if len(projected_change) == 0:
    projected_change = analysis_text.find_all("span", class_="posData")

print(projected_change[0].text)

#TODO: add analyst count report and estimate spread report
