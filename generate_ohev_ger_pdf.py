"""
Generate PDF of Shadal's Introduction to Ohev Ger from Sefaria API.
Usage: pip install reportlab python-bidi && python generate_ohev_ger_pdf.py
"""
import json, re, urllib.request
from bidi.algorithm import get_display
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_PATHS = [
    "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf",
]

OUTPUT = "Shadal_Ohev_Ger_Introduction.pdf"


def fetch_text():
    url = "https://www.sefaria.org/api/texts/Ohev_Ger,_Introduction"
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))["he"]


def process_paragraph(text):
    parts = re.split(r"(<b>.*?</b>)", text)
    result = []
    for part in parts:
        m = re.match(r"<b>(.*?)</b>", part)
        if m:
            result.append(f"<b>{get_display(m.group(1))}</b>")
        elif part.strip():
            result.append(get_display(part))
        else:
            result.append(part)
    return "".join(result)


def main():
    pdfmetrics.registerFont(TTFont("FreeSerif", FONT_PATHS[0]))
    pdfmetrics.registerFont(TTFont("FreeSerifBold", FONT_PATHS[1]))

    paragraphs = fetch_text()
    doc = SimpleDocTemplate(OUTPUT, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2.5*cm, bottomMargin=2*cm)

    title = ParagraphStyle("T", fontName="FreeSerifBold", fontSize=24,
                           leading=32, alignment=TA_CENTER, spaceAfter=4*mm)
    subtitle = ParagraphStyle("S", fontName="FreeSerif", fontSize=16,
                              leading=22, alignment=TA_CENTER, spaceAfter=14*mm)
    body = ParagraphStyle("B", fontName="FreeSerif", fontSize=12,
                          leading=20, alignment=TA_RIGHT, spaceAfter=4*mm)

    story = [
        Paragraph(get_display("אוהב גר"), title),
        Paragraph(get_display("הקדמה"), title),
        Paragraph(get_display("שמואל דוד לוצאטו (שד״ל)"), subtitle),
        Spacer(1, 8*mm),
    ]
    for p in paragraphs:
        t = p.strip()
        if t:
            story.append(Paragraph(process_paragraph(t), body))

    doc.build(story)
    print(f"Created {OUTPUT} ({len(paragraphs)} paragraphs)")


if __name__ == "__main__":
    main()
