import json
from datetime import date

from . import product_controller

from ..models import Bill


def get_bill_by_id(bill_id):
    bill = Bill.objects.filter(bill_id=bill_id).first()
    return bill


def get_bill_total_amount(bill_id):
    bill = Bill.objects.get(bill_id=bill_id)
    total_amount = bill.get_bill_amount()
    return total_amount


def create_new_bill():
    new_bill = Bill.objects.create(bill_date=date.today(), bill_active=True)
    product_controller.add_product_to_bill(new_bill)
    return new_bill.bill_id
