from ..models import Product, ParticipantProductContribution


def create_product(product_label, product_price, quantity, product_bill):
    return Product.objects.create(
        product_label=product_label,
        product_quantity=quantity,
        product_total_price=product_price,
        product_bill=product_bill
    )


def update_product(product_label, product_price, quantity, product_bill, product_id):
    return Product.objects.filter(product_id=product_id).update(product_bill=product_bill, product_quantity=quantity,
                                                                product_total_price=product_price,
                                                                product_label=product_label,
                                                                product_price_per_unit=product_price / quantity)

def delete_product(product_id):
    try:
        return Product.objects.filter(product_id=product_id).delete()
    except:
        return Exception('Something went wrong')


def add_product_to_bill(product_bill):
    product_data = [
        {'product_label': 'Produit 7', 'product_quantity': 7, 'product_price': 15.99},
        {'product_label': 'Produit 8', 'product_quantity': 2, 'product_price': 4.76},
        {'product_label': 'Produit 9', 'product_quantity': 4, 'product_price': 12.85},
    ]

    for data in product_data:
        Product.objects.create(
            product_label=data['product_label'],
            product_quantity=data['product_quantity'],
            product_total_price=data['product_price'],
            product_bill=product_bill
        )


def get_price_per_participant(product_id, bill_id):
    number_of_participants = ParticipantProductContribution.objects.filter(product_id=product_id,
                                                                           bill_id=bill_id,
                                                                           contributes=True).count()
    if number_of_participants == 0:
        return "N/A"
    product = Product.objects.get(product_id=product_id)

    return round(product.product_total_price / number_of_participants, 2)


def get_products_by_bill_id(bill_id):
    products = Product.objects.filter(product_bill=bill_id)
    return products


def get_product_by_product_id(product_id):
    product = Product.objects.filter(product_id=product_id).first()
    return product
