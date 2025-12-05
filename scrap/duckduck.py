from ddgs import DDGS
import pandas as pd
import tldextract
import time

def get_domain_robust(name: str) -> str:
    """Try DuckDuckGo with multiple strategies to find official domain"""
    
    # Domains to skip (common non-company sites)
    skip_domains = {
        'wikipedia.org', 'wikipedia.com',
        'facebook.com', 'twitter.com', 'x.com',
        'linkedin.com', 'instagram.com',
        'youtube.com', 'bloomberg.com',
        'reuters.com', 'marketwatch.com',
        'yahoo.com', 'finance.yahoo.com'
    }
    if("." in name):
        
    try:
        # Try multiple search queries
        #try again 
        queries = [
            f"{name} investor relations",
            f"{name} news release",
            f"{name} company press release"
        ]
        
        for query in queries:
            results = DDGS().text(query, max_results=5)
            
            if results:
                for result in results:
                    url = result['href']
                    parts = tldextract.extract(url)
                    domain = f"{parts.domain}.{parts.suffix}"
                    
                    # Skip unwanted domains
                    if domain not in skip_domains and parts.domain:
                        print(f"{name} -> {domain}")
                        return domain
            
            # Small delay between queries to avoid rate limiting
            time.sleep(0.5)
        
        print(f"No valid domain found for {name}")
        
    except Exception as e:
        print(f"Error for {name}: {e}")
    
    return ""

# Load and process
data = {"investor_page": get_domain_robust(name) for name in pd.read_csv("../sp500-companies.csv")["Name"]}
df = pd.DataFrame.from_dict(data, orient='index', columns=['investor_page']) 


df = pd.read_csv("./sp500_companies_with_investors_domain.csv", encoding='iso-8859-1')
# df["domain"] = df["Name"].apply(get_domain_robust)
df["investor_page"] = df["domain"].apply(get_domain_robust) if df["domain"].apply(get_domain_robust) else df["Name"].apply(get_domain_robust)

df.to_csv("sp500_companies_with_investors_domain.csv", index=False)