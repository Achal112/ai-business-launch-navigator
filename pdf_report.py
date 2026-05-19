from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(data):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    doc = SimpleDocTemplate("report.pdf")
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("AI Business Report", styles['Title']))
    content.append(Spacer(1, 10))

    for k, v in data.items():
        content.append(Paragraph(f"{k}: {v}", styles['Normal']))

    doc.build(content)

    return "report.pdf"