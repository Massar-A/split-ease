from pypdf import PdfReader
import re


def readTest(file):
    # creating a pdf reader object
    reader = PdfReader(file)
    string = ""
    for page in reader.pages:
        string = page.extract_text()
        print(extract_prices(string))
    print(extract_products(reader.pages[0].extract_text()))

    return reader.pages[0].extract_text()


def extract_prices(page_text):
    # Trouver tous les prix des produits
    prices = re.findall(r'\d+\.\d+', page_text)

    # Convertir les prix en float
    prices = [float(price) for price in prices]
    return prices


def extract_products(page_text):
    products = []

    # Trouver tous les prix des produits en tête de page
    prices = re.findall(r'\d+\.\d+', page_text)

    # Index pour suivre l'ordre des prix
    price_index = 0

    # Séparer les blocs de produits en fonction de la présence du mot "Réduction"
    product_blocks = re.split(r'(?=\n(?:\d+\s.*)+\n(?!.*réduction))', page_text)
    product_blocks.pop(0)
    print(product_blocks)
    for block in product_blocks:
        # Ignorer les blocs qui commencent par les mots clés spécifiés
        if any(keyword in block for keyword in
               ['Bonjour', 'Voici le reçu de votre', 'le télécharger ou l\'imprimer.', 'Commandé le', 'Commande']):
            continue

        # Extraire la quantité, le nom et le prix du produit
        quantity, name, price = re.findall(r'(\d+)\n(.+?)\n.*?(\d+\.\d{2})', block)[0]

        products.append({
            'quantity': int(quantity),
            'name': name,
            'price': float(price)
        })

    return products
