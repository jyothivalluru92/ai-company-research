from discord_integration import send_report_to_discord
import streamlit as st
from urllib.parse import urlparse

import research
import ai_engine
from research import find_official_website, get_company_public_info
from crawler import crawl_website
from ai_engine import analyze_company
from pdf_generator import generate_pdf_report

st.set_page_config(page_title="Company Research | Relu Consultancy", page_icon="🔎", layout="wide")

# ---------- Session state ----------
for key, default in [
    ("messages", []),
    ("last_report", None),
    ("last_pdf_path", None),
    ("selected_model", None),
    ("discord_bot_token", ""),
    ("discord_channel_id", ""),
    ("applicant_name", ""),
    ("applicant_email", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

FREE_MODEL_OPTIONS = {
    "Auto (recommended)": None,
    "Llama 3.3 70B": "meta-llama/llama-3.3-70b-instruct:free",
    "Mistral 7B": "mistralai/mistral-7b-instruct:free",
}

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### 🔎 Relu Consultancy")
    st.caption("COMPANY INTELLIGENCE")

    if st.button("➕ New Research", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_report = None
        st.session_state.last_pdf_path = None
        st.rerun()

    st.divider()

    tab1, tab2 = st.tabs(["API", "DISCORD"])

    with tab1:
        custom_openrouter = st.text_input("OpenRouter API Key", type="password", placeholder="sk-or-v1-...")
        custom_serper = st.text_input("Serper.dev API Key", type="password", placeholder="Your Serper key...")
        model_label = st.selectbox("AI Model", list(FREE_MODEL_OPTIONS.keys()))

        if st.button("Save Configuration", use_container_width=True, key="save_api"):
            if custom_openrouter:
                ai_engine.OPENROUTER_API_KEY = custom_openrouter
            if custom_serper:
                research.SERPER_API_KEY = custom_serper
            st.session_state.selected_model = FREE_MODEL_OPTIONS[model_label]
            st.success("Configuration saved for this session.")

    with tab2:
        discord_bot_token = st.text_input("Discord Bot Token", type="password")
        discord_channel_id = st.text_input("Discord Channel ID")
        applicant_name = st.text_input("Applicant Name")
        applicant_email = st.text_input("Applicant Email Address")

        if st.button("Save Configuration", use_container_width=True, key="save_discord"):
            st.session_state.discord_bot_token = discord_bot_token
            st.session_state.discord_channel_id = discord_channel_id
            st.session_state.applicant_name = applicant_name
            st.session_state.applicant_email = applicant_email
            st.success("Discord configuration saved.")

    st.divider()
    st.markdown("**How it works**")
    st.markdown(
        "1. Enter a company name or URL\n"
        "2. Serper.dev searches and crawls it\n"
        "3. OpenRouter AI generates insights\n"
        "4. Download a professional PDF report"
    )
    st.divider()
    st.caption("OPENROUTER · SERPER · FPDF2")


# ---------- Helper functions ----------
def is_url(text):
    text = text.strip()
    if text.startswith("http://") or text.startswith("https://"):
        return True
    parsed = urlparse("http://" + text)
    return "." in parsed.netloc


def normalize_url(text):
    text = text.strip()
    if not text.startswith("http"):
        text = "https://" + text
    return text


def run_research_pipeline(user_input):
    if is_url(user_input):
        website = normalize_url(user_input)
        company_name = urlparse(website).netloc.replace("www.", "").split(".")[0].capitalize()
    else:
        company_name = user_input.strip()
        with st.status("Searching for official website...", expanded=False) as status:
            website = find_official_website(company_name)
            status.update(label=f"Website found: {website}", state="complete")

    if not website:
        return None, None

    with st.status("Gathering public information...", expanded=False) as status:
        snippets = get_company_public_info(company_name)
        status.update(label="Public info gathered", state="complete")

    with st.status("Crawling website pages...", expanded=False) as status:
        crawled_text = crawl_website(website)
        status.update(label="Website crawled successfully", state="complete")

    with st.status("Analyzing with AI (summary, pain points, competitors)...", expanded=False) as status:
        result = analyze_company(
            company_name, website, crawled_text, snippets,
            preferred_model=st.session_state.selected_model
        )
        if result:
            status.update(label="AI analysis complete", state="complete")
        else:
            status.update(label="AI analysis failed - see terminal for details", state="error")

    if not result:
        return None, None

    with st.status("Generating PDF report...", expanded=False) as status:
        pdf_path = generate_pdf_report(result, output_path=f"{company_name}_report.pdf")
        status.update(label="PDF report ready", state="complete")

    if st.session_state.discord_bot_token and st.session_state.discord_channel_id:
        with st.status("Sending report to Discord...", expanded=False) as status:
            success, msg = send_report_to_discord(
                st.session_state.discord_bot_token,
                st.session_state.discord_channel_id,
                st.session_state.applicant_name,
                st.session_state.applicant_email,
                result.get("company_name"),
                result.get("website"),
                pdf_path
            )
            if success:
                status.update(label="Sent to Discord successfully", state="complete")
            else:
                status.update(label=f"Discord send failed: {msg}", state="error")

    return result, pdf_path


def display_result(result):
    st.subheader(f"📋 {result.get('company_name', 'N/A')}")
    st.write(f"**Website:** {result.get('website', 'N/A')}")
    st.write(f"**Phone:** {result.get('phone', 'Not available')}")
    st.write(f"**Address:** {result.get('address', 'Not available')}")

    st.markdown("**Summary:**")
    st.write(result.get("summary", "N/A"))

    st.markdown("**Products / Services:**")
    for item in result.get("products_services", []):
        st.markdown(f"- {item}")

    st.markdown("**AI-Generated Pain Points:**")
    for item in result.get("pain_points", []):
        st.markdown(f"- {item}")

    st.markdown("**Competitors:**")
    for comp in result.get("competitors", []):
        st.markdown(f"- {comp.get('name', 'N/A')} — {comp.get('website', 'N/A')}")


def handle_input(user_input):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        result, pdf_path = run_research_pipeline(user_input)
        if result:
            display_result(result)
            st.session_state.last_report = result
            st.session_state.last_pdf_path = pdf_path
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Research complete for {result.get('company_name')}."
            })
        else:
            st.error("Sorry, I couldn't research that company. Try a different name or a direct website URL.")
            st.session_state.messages.append({"role": "assistant", "content": "Research failed. Please try again."})


# ---------- Main area ----------
if not st.session_state.messages:
    st.markdown(
        "<div style='text-align:center; padding-top:40px;'>"
        "<span style='color:#F5A623; letter-spacing:2px;'>AI-POWERED INTELLIGENCE</span>"
        "<h1 style='font-size:52px; margin-top:10px;'>Know any company<br>in minutes.</h1>"
        "<p style='color:#aaa; font-size:18px;'>Enter a company name or website URL to get AI-powered insights,<br>"
        "competitor analysis, pain points, and a professional PDF report.</p>"
        "</div>",
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)
    example_companies = ["notion.so", "Figma", "Linear", "Vercel"]
    cols = [col1, col2, col3, col4]
    for c, name in zip(cols, example_companies):
        if c.button(name, use_container_width=True):
            handle_input(name)
            st.rerun()

else:
    st.title("🔎 Company Research")
    st.caption("● LIVE")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# ---------- Chat input (always visible at bottom) ----------
user_input = st.chat_input("Enter a company name (e.g. Aurora Labs) or website URL (e.g. https://aurora.dev)...")
if user_input:
    handle_input(user_input)

# ---------- Download button ----------
if st.session_state.last_pdf_path:
    with open(st.session_state.last_pdf_path, "rb") as f:
        st.download_button(
            label="📥 Download PDF Report",
            data=f,
            file_name=st.session_state.last_pdf_path,
            mime="application/pdf",
            use_container_width=True
        )