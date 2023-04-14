from PyPDF2 import PdfReader

def read_pdf(file):
    reader = PdfReader(file) # creating a pdf reader object
    article = ''
    for page in reader.pages:
        article += page.extract_text()
    return article