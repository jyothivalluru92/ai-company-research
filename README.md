# AI Company Research Assistant

An AI-powered research tool that takes a company name or website URL and automatically generates a professional research report — including company summary, products/services, AI-identified pain points, competitor analysis, and a downloadable PDF.

## Live Demo
**Deployed URL:** https://ai-company-research-nyhw8esm4latxvf932e7kz.streamlit.app/
## Features
- Accepts either a company name or a website URL
- Searches the web via Serper.dev to locate the official website and gather public information
- Crawls key pages of the company website (About, Products, Services, Contact, Pricing) while skipping login/duplicate pages
- Uses OpenRouter AI to generate a company summary, product list, pain points, and competitor suggestions
- Displays results in a ChatGPT-style chat interface with live progress indicators
- Generates a downloadable, professionally formatted PDF report
- Sidebar allows overriding API keys and selecting the AI model per session

## Tech Stack
- **Frontend/Backend:** Python + Streamlit
- **Search:** Serper.dev API
- **AI:** OpenRouter API (auto-selects a live free model; falls back automatically if one is unavailable)
- **Web Crawling:** requests + BeautifulSoup4
- **PDF Generation:** fpdf2

## Project Structure
ai-company-research/
├── app.py              # Streamlit UI and main app logic
├── research.py         # Serper.dev search integration
├── crawler.py          # Website crawler
├── ai_engine.py        # OpenRouter AI integration
├── pdf_generator.py    # PDF report generation
├── requirements.txt    # Python dependencies
└── .env                # API keys (not committed to GitHub)

## Setup Instructions (Run Locally)

1. Clone this repository:
git clone https://github.com/jyothivalluru92/ai-company-research.git
cd ai-company-research

2. Create and activate a virtual environment:
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

3. Install dependencies:
pip install -r requirements.txt

4. Create a `.env` file in the project root with:
SERPER_API_KEY=your_serper_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

5. Run the app:
streamlit run app.py
## Environment Variables

| Variable | Description | Where to get it |
|---|---|---|
| `SERPER_API_KEY` | API key for Serper.dev search | https://serper.dev |
| `OPENROUTER_API_KEY` | API key for OpenRouter AI models | https://openrouter.ai |

## How It Works
1. User enters a company name or URL in the chat interface
2. If a name is given, Serper.dev finds the official website
3. The crawler visits key internal pages and extracts clean text content
4. Additional public info is gathered via search snippets
5. All data is sent to an AI model (via OpenRouter) which returns a structured summary, pain points, and competitor list
6. Results are displayed in the chat, and a PDF report is generated and made available for download

## Notes
- No authentication, database, or user accounts are used, per assignment requirements
- The AI model selection automatically fetches OpenRouter's live list of currently-free models and falls back gracefully if any model becomes unavailable