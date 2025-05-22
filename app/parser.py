import fitz
import tempfile
import requests

def parse_pdf_from_file(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.read())
        tmp.flush()
        doc = fitz.open(tmp.name)
        text = "\n".join([page.get_text() for page in doc])
        title_text = doc[0].get_text()
        report_id = "UNKNOWN"
        if "Y-9C" in title_text:
            report_id = "FR Y-9C"
        elif "FFIEC 002" in title_text:
            report_id = "FFIEC 002"
        elif "FFIEC 009" in title_text:
            report_id = "FFIEC 009"
        return text, report_id
