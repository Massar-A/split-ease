from pypdf import PdfReader
import re
from .product_extraction import extract_products


def read_text(file):
    # creating a pdf reader object
    reader = PdfReader(file)
    string = ""
    for page in reader.pages:
        string += str(page.page_number) + 'new_page\n\n' + page.extract_text()

    return string


def analyze_picnic_pdf_text(file):
    # creating a pdf reader object
    reader = PdfReader(file)
    list_of_articles = []
    for page in reader.pages:
        string = str(page.page_number) + 'new_page\n\n' + page.extract_text()
        extract_products(string, list_of_articles)
    return list_of_articles
