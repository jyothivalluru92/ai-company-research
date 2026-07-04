import os
import requests
from dotenv import load_dotenv

load_dotenv()  # loads keys from .env file

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SERPER_URL = "https://google.serper.dev/search"


def serper_search(query, num_results=5):
    """
    Calls Serper.dev search API and returns raw search results (list of dicts).
    """
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {"q": query, "num": num_results}

    response = requests.post(SERPER_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print("Serper API error:", response.status_code, response.text)
        return []

    data = response.json()
    return data.get("organic", [])  # list of search result dicts


def find_official_website(company_name):
    """
    Given a company name, tries to find its official website URL.
    """
    results = serper_search(f"{company_name} official website")

    if not results:
        return None

    # Just take the first result's link — usually the official site
    return results[0].get("link")


def get_company_public_info(company_name):
    """
    Gathers extra public info snippets (phone, address, general info) via search.
    Returns a list of text snippets to feed into the AI later.
    """
    queries = [
        f"{company_name} contact information phone address",
        f"{company_name} products and services",
        f"{company_name} competitors"
    ]

    all_snippets = []
    for q in queries:
        results = serper_search(q, num_results=3)
        for r in results:
            snippet = r.get("snippet", "")
            if snippet:
                all_snippets.append(snippet)

    return all_snippets


# --- Quick test block (only runs when you run this file directly) ---
if __name__ == "__main__":
    company = "Stripe"
    print("Finding website for:", company)
    website = find_official_website(company)
    print("Found website:", website)

    print("\nGathering public info snippets...")
    snippets = get_company_public_info(company)
    for s in snippets:
        print("-", s)