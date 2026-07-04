from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime


class PDFReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, "Company Research Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, datetime.now().strftime("Generated on %B %d, %Y"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.ln(5)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(20, 20, 20)
        self.ln(4)
        self.cell(0, 8, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(220, 220, 220)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def body_text(self, text):
        self.set_font("Helvetica", "", 11)
        self.set_text_color(50, 50, 50)
        self.set_x(10)
        self.multi_cell(0, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def bullet_list(self, items):
        self.set_font("Helvetica", "", 11)
        self.set_text_color(50, 50, 50)
        for item in items:
            self.set_x(10)
            self.multi_cell(0, 6, f"- {item}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)


def generate_pdf_report(data, output_path="company_report.pdf"):
    """
    data: dict returned by ai_engine.analyze_company()
    Returns the file path of the generated PDF.
    """
    pdf = PDFReport()
    pdf.add_page()

    pdf.section_title("Company Information")
    pdf.body_text(f"Company Name: {data.get('company_name', 'N/A')}")
    pdf.body_text(f"Website: {data.get('website', 'N/A')}")
    pdf.body_text(f"Phone Number: {data.get('phone', 'Not available')}")
    pdf.body_text(f"Address: {data.get('address', 'Not available')}")

    pdf.section_title("Company Summary")
    pdf.body_text(data.get("summary", "N/A"))

    pdf.section_title("Products / Services")
    pdf.bullet_list(data.get("products_services", []))

    pdf.section_title("AI-Generated Pain Points")
    pdf.bullet_list(data.get("pain_points", []))

    pdf.section_title("Competitor Analysis")
    competitors = data.get("competitors", [])
    for comp in competitors:
        pdf.body_text(f"{comp.get('name', 'N/A')} - {comp.get('website', 'N/A')}")

    pdf.output(output_path)
    return output_path


# --- Quick test block ---
if __name__ == "__main__":
    sample_data = {
        "company_name": "Stripe",
        "website": "https://stripe.com/",
        "phone": "Not available",
        "address": "Not available",
        "summary": "Stripe is a global financial infrastructure platform...",
        "products_services": ["Payments processing", "Billing", "Connect"],
        "pain_points": ["Cross-border regulations", "Fraud risk management"],
        "competitors": [
            {"name": "PayPal", "website": "https://paypal.com"},
            {"name": "Adyen", "website": "https://adyen.com"}
        ]
    }

    path = generate_pdf_report(sample_data, "test_report.pdf")
    print("PDF generated at:", path)