import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO

URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(response.text, "lxml")

# Find the table
table = soup.find("table", {"class": "wikitable sortable"})

df = pd.read_html(StringIO(str(table)))[0]  # Converts HTML table to DataFrame

# df now contains all S&P 500 companies, ticker, sector, etc.
df.to_csv("sp500_companies.csv", index=False)