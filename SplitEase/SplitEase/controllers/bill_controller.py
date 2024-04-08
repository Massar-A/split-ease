from datetime import date
from . import product_controller

from ..models import Bill


def get_bill_by_id(bill_id):
    bill = Bill.objects.filter(bill_id=bill_id).first()
    products = list(product_controller.get_product_by_bill_id(bill_id))
    total = bill.calculate_bill_amount()
    bill_data = {
        'bill_id': bill.bill_id,
        'date': bill.bill_date,
        'bill_active': bill.bill_active,
        'total_bill': total,
        'products': products
    }
    return bill_data


def get_bill_total_amount(bill_id):
    bill = Bill.objects.get(bill_id=bill_id)
    total_amount = bill.calculate_bill_amount()
    return total_amount


def create_new_bill():
    new_bill = Bill.objects.create(bill_date=date.today(), bill_active=True)
    return new_bill.bill_id
