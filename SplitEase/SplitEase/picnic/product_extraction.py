import re


def extract_prices(page_text):
    # Trouver tous les prix des produits qui suivent la chaîne "new_page"
    prices = re.search(r'[0-9]+new_page\n\n(\d+\.\d{2}\n*)+', page_text)
    if prices is None:
        return []
    cleaned_prices = re.sub(r'^\d*new_page\n\n', '', prices[0])
    # Extraire les prix des blocs trouvés
    prices = [float(price.strip()) for price in cleaned_prices.split('\n') if price.strip()]

    return prices


def extract_products(page_text, list_of_articles):
    # Trouver tous les prix des produits en tête de page
    prices = extract_prices(page_text)
    # Index pour suivre l'ordre des prix
    price_index = 0

    # Séparer les blocs de produits en fonction de la présence du mot "Réduction"
    product_blocks = re.split(r'(?=\n \n(?:\d+\s.*)+\n(?!.*réduction))', page_text)
    print(product_blocks)
    for block in product_blocks:
        # Ignorer les blocs qui commencent par les mots clés spécifiés
        if any(keyword in block for keyword in
               ['Bonjour', 'Voici le reçu de votre', 'le télécharger ou l\'imprimer.', 'Commandé le']):
            continue
        block = re.sub(r'\n \n', '', block)
        if 'new_page' in block:
            print(block)
            block = re.sub(r'[0-9]+new_page\n\n(\d+\.\d{2}\n*)*', '', block)
            print(block)
        # Expression régulière pour supprimer la partie indésirable
        regex = r"Articles retournés en consigne.*"

        # Supprimer la partie indésirable du texte
        block = re.sub(regex, "", block, flags=re.DOTALL)
        if 'Total' in block:
            return list_of_articles
        lines = block.split('\n')
        quantity = int(lines[0])
        name = lines[1]
        if "Remboursement" in lines[2]:
            refund = float(lines[2].replace("Remboursement", ""))
            remove_item_from_product_list(list_of_articles, name, quantity, refund)
        else:
            if not any(keyword in block for keyword in ['réduction', 'offert', 'gratuit', 'sur le', 'moitié prix']):
                list_of_articles.append({
                    'quantity': quantity,
                    'name': name.strip(),
                    'price': float(prices[price_index])
                })
                price_index += 1
            else:
                list_of_articles.append({
                    'quantity': quantity,
                    'name': name.strip(),
                    'price': float(lines[4])
                })
    return list_of_articles


def remove_item_from_product_list(list, name, quantity, refund):
    match = next(e for e in list if e['name'] == name)
    index = list.index(match)
    list[index]['quantity'] = match['quantity'] - quantity
    if list[index]['quantity'] <= 0:
        list.remove(match)
        return list
    list[index]['price'] = match['price'] + refund

    return list
