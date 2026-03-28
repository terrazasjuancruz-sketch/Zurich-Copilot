import os
import pdfplumber

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
pdf_path = os.path.join(project_root, "Zurich Invest Future-Joel AECLIF-1359072.pdf")

with pdfplumber.open(pdf_path) as pdf:
    page2 = pdf.pages[1]
    words = page2.extract_words()
    top = next((w["top"] for w in words if w["text"] == "Año"), 0)
    bottom = next((w["top"] for w in reversed(words) if "Total" in w["text"] or "Totales" in w["text"]), page2.height - 50)
    
    print(f"Top: {top}, Bottom: {bottom}")
    
    if top:
        cropped_page = page2.crop((0, max(0, top - 2), page2.width, bottom))
        table = cropped_page.extract_table()
        print("=== Cropped Table ===")
        print(table)
