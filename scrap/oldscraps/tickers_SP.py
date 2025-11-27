# didnt work because google blocked requests if it detected as bot

path = "../sp500-companies.csv"

import time
import pandas as pd
import tldextract  # pip install tldextract
import requests
from bs4 import BeautifulSoup  # pip install beautifulsoup4
from urllib.parse import urlparse, unquote, quote_plus

def fetch_html(url: str, timeout: int = 10) -> str:
    """Fetch HTML for a URL with a simple User-Agent and return text (or empty string on failure)."""
    #headers ={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'}
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()  # Debug: print first 1000 chars of HTML
        print(resp.text[:5000])

        return resp.text
    except Exception:
        return ""

def parse_first_result(html: str) -> str:
    """Parse a Google search result page (best-effort) and return the first result URL or empty string."""
    if not html:
        print("No HTML to parse.")
        return ""
    soup = BeautifulSoup(html, "html.parser")
    # Google search result links often appear as /url?q=<target>&sa=...
    #   # Debug: print first 1000 chars of prettified HTML
    search_results_container = soup.find(id='search')
    #returns No search results container found. 
    if not search_results_container:
        print("No search results container found.")
        return ""
    else:
        print(search_results_container.prettify()[:1000])
        first_link_element = search_results_container.find('a', href=True)

        if first_link_element and first_link_element['href'].startswith('http'):
            return first_link_element['href']
        else:
            # If the first found link is not a valid external link,
            # we might need to be more specific.
            # This example tries to find a link that is likely an organic result.
            for link in search_results_container.find_all('a', href=True):
                if link['href'].startswith('http') and "google.com/search" not in link['href']:
                    print(link['href'])  # Debug: print first 1000 chars of search results container
                    return link['href']  # Debug: print first 1000 chars of search results container
                
    first_link = soup.find('cite')

    if first_link:
        print(first_link.text)
        return first_link.text
    for a in soup.find_all("a", href=True):
        href = a["href"]
        print(href)
        if href.startswith("/url?q="):
            try:
                url = href.split("/url?q=", 1)[1].split("&", 1)[0]
                url = unquote(url)
                parsed = urlparse(url)
                if parsed.scheme in ("http", "https") and parsed.netloc and url != "google.com":
                    print(url)
                    return url
            except Exception:
                continue
    # Fallback: any absolute http(s) link
    a = soup.find("a", href=lambda x: x and x.startswith("http"))
    if a:
        return a["href"]
    return ""

def get_domain_from_url(url: str) -> str:
    parts = tldextract.extract(url)
    if not parts.domain:
        return ""
    return f"{parts.domain}.{parts.suffix}"

def get_domain(company_name: str) -> str:
    # Use URL-encoded query to handle spaces/special chars
    query = quote_plus(f"{company_name} official site")
    search_url = f"https://www.google.co.uk/search?sclient=psy-ab&client=ubuntu&hs=k5b&channel=fs&biw=1366&bih=648&noj=1&q={query}" 
    html = fetch_html(search_url)      # requests + headers logic
    first_result_url = parse_first_result(html)  # BeautifulSoup logic
    return get_domain_from_url(first_result_url)

df = pd.read_csv(path, encoding='iso-8859-1')
df["domain"] = ""
row = df.iloc[0]
name = row["Name"]
print(f"Testing domain fetch for: {name}")
try:
    domain = get_domain(name)
except Exception:
    domain = ""

print(f"Domain found: {domain}")

for idx, row in df.iterrows():
    name = row["Name"]
    print(f"Processing {idx + 1}/{len(df)}: {name}")
    try:
        domain = get_domain(name)
    except Exception:
        domain = ""
    df.at[idx, "domain"] = domain
    time.sleep(1.5)   # be nice to search engines

df.to_csv("sp500_companies_with_domains.csv", index=False)