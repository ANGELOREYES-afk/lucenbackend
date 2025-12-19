import pandas as pd
import yfinance as yf
import json
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def scrape_investor_page(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract all text paragraphs (naive approach)
        text_content = " ".join([p.get_text() for p in soup.find_all('p')])
        
        return text_content[:1000] # Limit text for this example
    except Exception as e:
        return ""
# 1. Load your CSV
df = pd.read_csv('sp500_companies_with_investors_domain.csv')

companies_data = []

# 2. Iterate through tickers (limit to first 5 for testing)



for index, row in df.iterrows():
    ticker = row['Ticker']
    print(f"Processing {ticker}...")
    
    try:
        # Fetch data using yfinance
        stock = yf.Ticker(ticker)
        info = stock.info
        news = stock.news
        print(news[:1])
        # 3. Form the JSON structure
        company_profile = {
            "metadata": {
                "name": row['Name'],
                "ticker": ticker,
                "sector": row['Industry'],
                "investor_url": row['investor_page']
            },
            "financial_summary": {
                "market_cap": info.get('marketCap'),
                "website": info.get('website'),
                "business_summary": info.get('longBusinessSummary')  # Great for vector search
            },
            "latest_news": [
                {"title": n['content']['title'], "link": n['content']['thumbnail']['originalUrl'], "publisher": n['content']['provider']['displayName']} 
                for n in news[:3]  # Get latest 3 articles
            ],
            "Page_Content": scrape_investor_page(row['investor_page'])
        }
        companies_data.append(company_profile)
        
    except Exception as e:
        print(f"Failed to fetch {ticker}: {e}")

# 4. Save to JSON
with open('companies_data.json', 'w') as f:
    json.dump(companies_data, f, indent=4)
