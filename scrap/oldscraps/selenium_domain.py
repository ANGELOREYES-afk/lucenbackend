# didnt work because of captcha challenges from google

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import tldextract
import pandas as pd
import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup
import codecs

def get_domain_from_url(url: str) -> str:
    parts = tldextract.extract(url)
    if not parts.domain:
        return ""
    return f"{parts.domain}.{parts.suffix}"

path = "../sp500-companies.csv"

def get_domain(name): 
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    # Add any desired options, e.g., options.headless = True
    driver = uc.Chrome(options=options)
    try:
        # Navigate to Google
        driver.get("https://www.google.com")
        
        # Find the search input field
        # The name attribute for the search input on Google is typically 'q'
        search_box = driver.find_element(By.NAME, "q")

        # Enter the search query
        search_query = f"{name} company website" # Replace with the actual company name
        search_box.send_keys(search_query)
        # Press Enter to perform the search
        search_box.send_keys(Keys.RETURN)

        # Wait for the search results to load (adjust time as needed)
        first_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.g a"))
        )
        href = first_link.get_attribute("href")
        print(f"First link href: {href}")

        # Alternatively, you can directly find the first result link

        #first_result_link = driver.find_element(By.CSS_SELECTOR, "div#search a") 

        # Get the href attribute of the first link
        #first_result_href = first_result_link.get_attribute("href")

        # Print the href
        #print(f"The href of the first search result is: {first_result_href}")


        return get_domain_from_url(href)
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the browser
        driver.quit()

df = pd.read_csv(path, encoding='iso-8859-1')
df["domain"] = ""
row = df.iloc[0]
name = row["Name"]
print(f"Testing domain fetch for: {name}")

domain = get_domain(name)


print(f"Domain found: {domain}")

# for idx, row in df.iterrows():
#     name = row["Name"]
#     print(f"Processing {idx + 1}/{len(df)}: {name}")
#     try:
#         domain = get_company_domain(name)
#     except Exception:
#         domain = ""
#     df.at[idx, "domain"] = domain
#     time.sleep(1.5)   # be nice to search engines

# df.to_csv("sp500_companies_with_domains.csv", index=False)