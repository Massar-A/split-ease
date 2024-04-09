from ..models import Product


def get_product_by_bill_id(bill_id):
    return Product.objects.filter(product_bill=bill_id).values('product_id', 'product_quantity','product_label', 'product_price', 'product_quantity')
