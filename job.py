"""
Advanced Job Lead Scraper (Stabilized Version)
Author: Senior Data Engineer

Fixes:
- DuckDuckGo blocking
- Retry system
- DataFrame crash protection
- Excel export
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from fake_useragent import UserAgent
from tqdm import tqdm

# ==========================
# CONFIGURATION
# ==========================

MAX_PAGES = 3
THREADS = 3
DELAY_RANGE = (2, 5)
MAX_RETRIES = 3

SEARCH_KEYWORDS = [
    "Python developer hiring",
    "Python engineer jobs",
    "Django developer hiring",
    "backend Python jobs",
]

TARGET_SITES = [
    "linkedin.com",
    "indeed.com",
    "glassdoor.com",
    "wellfound.com",
]

# ==========================
# SESSION
# ==========================

ua = UserAgent()

session = requests.Session()

def get_headers():
    return {
        "User-Agent": ua.random,
        "Accept": "text/html",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }

# ==========================
# DUCKDUCKGO SEARCH
# ==========================

def duckduckgo_search(query, page=0):

    url = "https://html.duckduckgo.com/html/"
    params = {
        "q": query,
        "s": page * 30
    }

    for attempt in range(MAX_RETRIES):

        try:

            response = session.post(
                url,
                data=params,
                headers=get_headers(),
                timeout=20
            )

            soup = BeautifulSoup(response.text, "lxml")

            results = []

            for result in soup.select(".result"):

                title = result.select_one(".result__title")
                snippet = result.select_one(".result__snippet")
                link = result.select_one("a.result__a")

                if title and link:

                    results.append({
                        "title": title.get_text(strip=True),
                        "snippet": snippet.get_text(strip=True) if snippet else "",
                        "url": link["href"]
                    })

            return results

        except Exception as e:

            if attempt < MAX_RETRIES - 1:
                time.sleep(random.uniform(3, 6))
            else:
                print(f"[ERROR] DuckDuckGo Failed: {e}")

    return []

# ==========================
# COMPANY EXTRACTION
# ==========================

def extract_company(text):

    patterns = [
        r"at\s+([A-Z][A-Za-z0-9& ]+)",
        r"@\s*([A-Z][A-Za-z0-9& ]+)",
        r"([A-Z][A-Za-z0-9& ]+)\s+(is hiring|hiring)"
    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:
            return match.group(1).strip()

    return "Unknown"

# ==========================
# SOURCE CLASSIFIER
# ==========================

def classify_source(url):

    if "linkedin" in url:
        return "LinkedIn"

    elif "indeed" in url:
        return "Indeed"

    elif "glassdoor" in url:
        return "Glassdoor"

    else:
        return "Other"

# ==========================
# RESULT PROCESSOR
# ==========================

def process_result(result):

    text = result["title"] + " " + result["snippet"]

    company = extract_company(text)

    return {
        "Company": company,
        "Title": result["title"],
        "Snippet": result["snippet"],
        "URL": result["url"],
        "Source": classify_source(result["url"])
    }

# ==========================
# SCRAPER ENGINE
# ==========================

def scrape_jobs():

    all_results = []

    queries = []

    print("\n[INFO] Scraping started...\n")

    for keyword in SEARCH_KEYWORDS:

        for site in TARGET_SITES:
            queries.append(f"{keyword} site:{site}")

        queries.append(keyword)

    with ThreadPoolExecutor(max_workers=THREADS) as executor:

        futures = []

        for query in queries:
            for page in range(MAX_PAGES):

                futures.append(
                    executor.submit(duckduckgo_search, query, page)
                )

        for future in tqdm(as_completed(futures), total=len(futures)):

            results = future.result()

            for r in results:
                all_results.append(process_result(r))

            time.sleep(random.uniform(*DELAY_RANGE))

    return pd.DataFrame(all_results)

# ==========================
# CLEAN DATA
# ==========================

def clean_data(df):

    if df.empty:
        print("[WARNING] No results scraped")
        return df

    if "Company" not in df.columns:
        print("[WARNING] Missing company column")
        return df

    df.drop_duplicates(subset=["URL"], inplace=True)

    df = df[df["Company"] != "Unknown"]

    return df

# ==========================
# EXPORT TO EXCEL
# ==========================

def save_results(df):

    if df.empty:
        print("[WARNING] No data to export")
        return

    filename = f"job_leads_{int(time.time())}.xlsx"

    df.to_excel(filename, index=False)

    print(f"\n[INFO] Excel file saved → {filename}")

# ==========================
# ENTRY POINT
# ==========================

if __name__ == "__main__":

    df = scrape_jobs()

    df = clean_data(df)

    save_results(df)

    print("\nSample results:\n")

    print(df.head())







# """
# Advanced Job Lead Scraper (DuckDuckGo Based)
# Author: Senior Data Engineer

# Purpose:
# Scrapes latest companies hiring Python-related roles from multiple sources.

# NOTE:
# - To switch role (e.g., Android Developer), modify SEARCH_KEYWORDS
# - To increase aggressiveness, increase MAX_PAGES and THREADS
# """

# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# import time
# import random
# import re
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from fake_useragent import UserAgent
# from urllib.parse import quote
# from tqdm import tqdm

# # ==========================
# # CONFIGURATION
# # ==========================

# MAX_PAGES = 5          # Increase for deeper scraping
# THREADS = 10           # Parallel workers
# DELAY_RANGE = (1, 3)   # Random delay between requests

# # 🔁 MODIFY HERE TO CHANGE ROLE
# SEARCH_KEYWORDS = [
#     "Python developer hiring",
#     "Python engineer jobs",
#     "Django developer hiring",
#     "backend Python jobs",
#     "Flask developer jobs",
#     "Python developer LinkedIn hiring",
#     "Python developer careers",
# ]

# # 🔁 MODIFY HERE TO TARGET OTHER ROLES
# # Example:
# # Replace "Python" with:
# # "Android Developer", "Kotlin Developer", "Java Developer", etc.


# # Sites to prioritize (forces rugged results)
# TARGET_SITES = [
#     "linkedin.com",
#     "indeed.com",
#     "glassdoor.com",
#     "jobs.lever.co",
#     "boards.greenhouse.io",
#     "wellfound.com",
# ]

# # ==========================
# # HEADERS / SESSION
# # ==========================

# ua = UserAgent()

# def get_headers():
#     return {
#         "User-Agent": ua.random,
#         "Accept-Language": "en-US,en;q=0.9",
#     }

# session = requests.Session()


# # ==========================
# # DUCKDUCKGO SEARCH SCRAPER
# # ==========================

# def duckduckgo_search(query, page=0):
#     """
#     Scrapes DuckDuckGo HTML results (not API)
#     """
#     url = "https://html.duckduckgo.com/html/"
    
#     params = {
#         "q": query,
#         "s": page * 30
#     }

#     try:
#         response = session.post(url, data=params, headers=get_headers(), timeout=15)
#         soup = BeautifulSoup(response.text, "lxml")

#         results = []

#         for result in soup.select(".result"):
#             title = result.select_one(".result__title")
#             snippet = result.select_one(".result__snippet")
#             link = result.select_one("a.result__a")

#             if title and link:
#                 results.append({
#                     "title": title.get_text(strip=True),
#                     "snippet": snippet.get_text(strip=True) if snippet else "",
#                     "url": link["href"]
#                 })

#         return results

#     except Exception as e:
#         print(f"[ERROR] DuckDuckGo: {e}")
#         return []


# # ==========================
# # JOB DATA EXTRACTION
# # ==========================

# def extract_company(text):
#     """
#     Basic heuristic to extract company name
#     """
#     patterns = [
#         r"at\s+([A-Z][A-Za-z0-9& ]+)",
#         r"@\s*([A-Z][A-Za-z0-9& ]+)",
#         r"([A-Z][A-Za-z0-9& ]+)\s+(is hiring|hiring)"
#     ]

#     for pattern in patterns:
#         match = re.search(pattern, text)
#         if match:
#             return match.group(1).strip()

#     return "Unknown"


# def classify_source(url):
#     if "linkedin" in url:
#         return "LinkedIn"
#     elif "indeed" in url:
#         return "Indeed"
#     elif "glassdoor" in url:
#         return "Glassdoor"
#     else:
#         return "Other"


# def process_result(result):
#     text = result["title"] + " " + result["snippet"]

#     company = extract_company(text)

#     return {
#         "Company": company,
#         "Title": result["title"],
#         "Snippet": result["snippet"],
#         "URL": result["url"],
#         "Source": classify_source(result["url"])
#     }


# # ==========================
# # MAIN SCRAPER ENGINE
# # ==========================

# def scrape_jobs():
#     all_results = []

#     print("\n[INFO] Starting scraping...\n")

#     queries = []

#     # Build aggressive queries
#     for keyword in SEARCH_KEYWORDS:
#         for site in TARGET_SITES:
#             queries.append(f"{keyword} site:{site}")

#         queries.append(keyword)

#     with ThreadPoolExecutor(max_workers=THREADS) as executor:
#         futures = []

#         for query in queries:
#             for page in range(MAX_PAGES):
#                 futures.append(
#                     executor.submit(duckduckgo_search, query, page)
#                 )

#         for future in tqdm(as_completed(futures), total=len(futures)):
#             results = future.result()
#             for r in results:
#                 processed = process_result(r)
#                 all_results.append(processed)

#             time.sleep(random.uniform(*DELAY_RANGE))

#     return pd.DataFrame(all_results)


# # ==========================
# # CLEANING & EXPORT
# # ==========================

# def clean_data(df):
#     df.drop_duplicates(subset=["URL"], inplace=True)
#     df = df[df["Company"] != "Unknown"]
#     return df


# def save_results(df):
#     filename = f"job_leads_{int(time.time())}.csv"
#     df.to_csv(filename, index=False)
#     print(f"\n[INFO] Saved results to {filename}")


# # ==========================
# # ENTRY POINT
# # ==========================

# if __name__ == "__main__":
#     df = scrape_jobs()
#     df = clean_data(df)
#     save_results(df)

#     print("\n[INFO] Done. Sample:\n")
#     print(df.head())