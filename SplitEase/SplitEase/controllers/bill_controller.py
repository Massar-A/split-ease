import json
from datetime import date

from . import product_controller

from ..models import Bill


def get_bill_by_id(bill_id):
    try:
        bill = Bill.objects.filter(bill_id=bill_id).first()
        return bill
    except:
        return Exception("Something went wrong")


def get_bill_total_amount(bill_id):
    try:
        bill = Bill.objects.get(bill_id=bill_id)
        total_amount = bill.get_bill_amount()
        return total_amount
    except:
        return Exception("Something went wrong")


def create_new_bill(bill_date):
    try:
        new_bill = Bill.objects.create(bill_date=bill_date, bill_active=True)
        return new_bill
    except:
        return Exception("Something went wrong")


def delete_bill(bill_id):
    try:
        return Bill.objects.filter(bill_id=bill_id).update(bill_active=False)
    except:
        return Exception('Something went wrong')


def set_bill_payer(bill_id, participant_id):
    try:
        return Bill.objects.filter(bill_id=bill_id).update(bill_payer=participant_id)
    except:
        return Exception('Something went wrong')
