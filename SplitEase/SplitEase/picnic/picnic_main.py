from SplitEase.controllers import bill_controller, product_controller
from SplitEase.picnic.text_extraction import read_text, analyze_picnic_pdf_text


def read_picnic_text(file):
    # Lecture du texte du fichier PDF
    text = read_text(file)
    return text


def analyze_picnic(file):
    # Analyse du texte pour extraire les produits
    list_of_articles = analyze_picnic_pdf_text(file)
    return list_of_articles


def create_picnic_bill(file, date):
    products_list = analyze_picnic(file)
    bill = bill_controller.create_new_bill(date)
    print(bill)

    for product in products_list:
        product_controller.create_product(product['name'], product['price'], product['quantity'], bill)
    return bill.bill_id
