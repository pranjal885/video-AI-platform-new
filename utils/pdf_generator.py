from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os


def generate_pdf(summary, filename):

    output_folder = "outputs"
    os.makedirs(output_folder, exist_ok=True)

    pdf_path = os.path.join(
        output_folder,
        filename + ".pdf"
    )

    doc = SimpleDocTemplate(pdf_path)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph("<b>AI Generated Summary</b>", styles["Heading1"])
    )

    story.append(
        Paragraph(summary, styles["BodyText"])
    )

    doc.build(story)

    return pdf_path