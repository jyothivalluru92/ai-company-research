import requests


def send_report_to_discord(bot_token, channel_id, applicant_name, applicant_email,
                            company_name, company_website, pdf_path):
    """
    Sends applicant + research details and the PDF report to a Discord channel
    using a bot token.
    """
    if not bot_token or not channel_id:
        return False, "Missing bot token or channel ID"

    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {"Authorization": f"Bot {bot_token}"}

    message = (
        f"**New Company Research Submitted**\n"
        f"**Applicant Name:** {applicant_name or 'N/A'}\n"
        f"**Applicant Email:** {applicant_email or 'N/A'}\n"
        f"**Company Name:** {company_name}\n"
        f"**Company Website:** {company_website}\n"
    )

    try:
        with open(pdf_path, "rb") as f:
            files = {"file": (pdf_path, f, "application/pdf")}
            data = {"content": message}
            response = requests.post(url, headers=headers, data=data, files=files, timeout=30)

        if response.status_code in (200, 201):
            return True, "Sent successfully"
        else:
            return False, f"Discord API error {response.status_code}: {response.text}"

    except Exception as e:
        return False, str(e)