from ddgs import DDGS
import pandas as pd
import tldextract
import time
import requests

def get_investor_domain(domain: str) -> str:
    """Find investor relations page for a company domain"""
    
    skip_domains = {
        'wikipedia.org', 'wikipedia.com', 'facebook.com', 'twitter.com', 
        'x.com', 'linkedin.com', 'instagram.com', 'youtube.com', 
        'bloomberg.com', 'reuters.com', 'marketwatch.com', 
        'yahoo.com', 'finance.yahoo.com'
    }  # ✅ Closed properly
    
    # URL patterns to try
    url_patterns = [
        f"https://investor.{domain}",
        f"https://investors.{domain}",  # Added common variant
        f"https://{domain}/investor-relations",
        f"https://{domain}/investors",
        f"https://www.{domain}/investor-relations",
    ]
    
    for url in url_patterns:
        try:
            response = requests.get(url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                print(f"✓ Found: {url}")
                return url  # ✅ Return the working URL, not original domain
                
        except requests.exceptions.ConnectionError as e:
            error_msg = str(e).lower()
            
            # Connection refused = server exists but blocked the request
            if "connection refused" in error_msg or "errno 61" in error_msg:
                print(f"? Blocked but exists: {url}")
                return url  # Likely valid, just blocked
            
            # DNS failure = subdomain doesn't exist
            elif "failed to resolve" in error_msg or "errno 8" in error_msg or "nodename" in error_msg:
                print(f"✗ DNS fail: {url}")
                continue  # ✅ Try next pattern
            else:
                print(f"✗ Other error: {url} - {error_msg[:50]}")
                continue
                
        except requests.exceptions.SSLError:
            # SSL error often means the subdomain exists but cert is wrong
            print(f"? SSL error (may exist): {url}")
            continue  # Or return url if you want to capture these
            
        except requests.exceptions.Timeout:
            print(f"✗ Timeout: {url}")
            continue
            
        except Exception as e:
            print(f"✗ Unexpected: {url} - {e}")
            continue
    
    # Fallback to DuckDuckGo search
    print(f"→ Trying DuckDuckGo for {domain}...")
    try:
        queries = [
            f"{domain} investor relations",
            f"{domain} news release",
        ]  # ✅ Closed properly
        
        for query in queries:
            results = DDGS().text(query, max_results=5)
            if results:
                for result in results:
                    href = result.get('href', '')
                    parts = tldextract.extract(href)
                    found_domain = f"{parts.domain}.{parts.suffix}"
                    
                    if found_domain not in skip_domains and parts.domain:
                        print(f"✓ DDG found: {href}")
                        return href
            time.sleep(0.5)
            
    except Exception as e:
        print(f"DDG error for {domain}: {e}")
    
    print(f"✗ No investor page found for {domain}")
    return ""

# Usage
df = pd.read_csv("./sp500_companies_with_domains.csv", encoding='iso-8859-1')
df["investor_page"] = df["domain"].apply(get_investor_domain)
df.to_csv("sp500_companies_with_investors_domain.csv", index=False)
