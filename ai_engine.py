import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELS_LIST_URL = "https://openrouter.ai/api/v1/models"

# Hardcoded backups in case the live fetch itself fails
BACKUP_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
]


def get_live_free_models():
    """
    Asks OpenRouter's own API which models are CURRENTLY free.
    This avoids hardcoding model names that expire.
    """
    try:
        resp = requests.get(
            MODELS_LIST_URL,
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            timeout=15
        )
        if resp.status_code != 200:
            return []

        data = resp.json().get("data", [])
        free_models = []
        for m in data:
            pricing = m.get("pricing", {})
            try:
                prompt_price = float(pricing.get("prompt", "1"))
                completion_price = float(pricing.get("completion", "1"))
            except (TypeError, ValueError):
                continue
            if prompt_price == 0 and completion_price == 0:
                free_models.append(m["id"])
        return free_models
    except requests.RequestException:
        return []


def call_openrouter(prompt, preferred_model=None):
    """
    Tries live free models one by one until one succeeds.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    live_free = get_live_free_models()
    pool = live_free if live_free else BACKUP_MODELS
    models_to_try = ([preferred_model] if preferred_model else []) + [m for m in pool if m != preferred_model]

    for m in models_to_try[:8]:  # cap attempts so we don't loop forever
        payload = {
            "model": m,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        try:
            response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
        except requests.RequestException as e:
            print(f"[AI] Model {m} network error: {e}")
            continue

        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            print(f"[AI] Used model: {m}")
            return content
        else:
            print(f"[AI] Model {m} failed ({response.status_code}), trying next...")

    print("[AI] All models failed.")
    return None


def analyze_company(company_name, website_url, crawled_text, search_snippets, preferred_model=None):
    snippets_text = "\n".join(f"- {s}" for s in search_snippets)

    prompt = f"""
You are a business research analyst. Analyze the company below using the provided website content and search snippets.

Company Name: {company_name}
Website: {website_url}

Website Content (extracted from crawling):
{crawled_text[:6000]}

Additional Public Search Snippets:
{snippets_text}

Based on this, respond ONLY with a valid JSON object (no extra text, no markdown fences) in exactly this format:

{{
  "company_name": "...",
  "website": "...",
  "phone": "...",
  "address": "...",
  "summary": "2-3 sentence company summary",
  "products_services": ["...", "..."],
  "pain_points": ["...", "..."],
  "competitors": [
    {{"name": "...", "website": "..."}},
    {{"name": "...", "website": "..."}}
  ]
}}

If phone or address is not found in the content, put "Not available".
Suggest at least 3 realistic competitors based on the industry, even if not explicitly mentioned in the text.
"""

    raw_response = call_openrouter(prompt, preferred_model=preferred_model)

    if not raw_response:
        return None

    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()

    try:
        parsed = json.loads(cleaned)
        return parsed
    except json.JSONDecodeError:
        print("Failed to parse AI response as JSON. Raw response was:")
        print(raw_response)
        return None


if __name__ == "__main__":
    from research import find_official_website, get_company_public_info
    from crawler import crawl_website

    company = "Stripe"
    website = find_official_website(company)
    snippets = get_company_public_info(company)
    crawled = crawl_website(website)

    print("Sending to AI for analysis...")
    result = analyze_company(company, website, crawled, snippets)

    print("\n--- AI RESULT ---")
    print(json.dumps(result, indent=2))