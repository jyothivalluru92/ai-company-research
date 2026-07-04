import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Pages we care about finding on the site
TARGET_KEYWORDS = ["about", "product", "service", "solution", "contact", "pricing", "home"]

# Pages we want to skip
IGNORE_KEYWORDS = ["login", "signin", "sign-in", "signup", "sign-up", "register",
                   "cart", "checkout", "privacy", "terms", "cookie"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def is_same_domain(base_url, link):
    return urlparse(base_url).netloc == urlparse(link).netloc


def should_ignore(link):
    link_lower = link.lower()
    return any(bad in link_lower for bad in IGNORE_KEYWORDS)


def fetch_page(url):
    """Fetch a single page's HTML. Returns None if it fails."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=8)
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        pass
    return None


def extract_text(html):
    """Extract clean readable text from HTML, removing scripts/styles/nav clutter."""
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "noscript", "footer"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    # Collapse multiple spaces
    text = " ".join(text.split())
    return text


def find_important_links(base_url, html):
    """Find internal links that match our target keywords (about, contact, etc.)."""
    soup = BeautifulSoup(html, "lxml")
    found_links = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(base_url, href)

        if not is_same_domain(base_url, full_url):
            continue
        if should_ignore(full_url):
            continue

        link_lower = full_url.lower()
        if any(keyword in link_lower for keyword in TARGET_KEYWORDS):
            found_links.add(full_url)

    return found_links


def crawl_website(base_url, max_pages=6):
    """
    Crawls the homepage + important internal pages.
    Returns combined extracted text (capped to avoid huge payloads).
    """
    visited = set()
    combined_text = ""

    # Step 1: Fetch homepage
    homepage_html = fetch_page(base_url)
    if not homepage_html:
        return ""

    visited.add(base_url)
    combined_text += extract_text(homepage_html) + " "

    # Step 2: Find important internal links from homepage
    important_links = find_important_links(base_url, homepage_html)

    # Step 3: Visit each important link (up to max_pages)
    for link in list(important_links)[:max_pages]:
        if link in visited:
            continue
        page_html = fetch_page(link)
        if page_html:
            combined_text += extract_text(page_html) + " "
            visited.add(link)

    # Cap text length so we don't overload the AI later (approx ~8000 chars)
    return combined_text[:8000]


# --- Quick test block ---
if __name__ == "__main__":
    url = "https://stripe.com"
    print("Crawling:", url)
    content = crawl_website(url)
    print("\nExtracted text length:", len(content))
    print("\nPreview:\n", content[:500])