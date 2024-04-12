import json

from django.core import serializers
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Bill, Product, Participant
from .controllers import bill_controller
from .controllers import participant_controller
from .controllers import product_controller
from .serializers import BillSerializer


@csrf_exempt
def create_new_bill(request):
    if request.method == 'POST':
        return JsonResponse({'bill_id': bill_controller.create_new_bill()})


@csrf_exempt
def create_product(request):
    if request.method == 'POST':
        return JsonResponse({'product': product_controller.create_product('Filet de poulet',
                                                                          35.06,
                                                                          3,
                                                                          Bill.objects.filter(bill_id=1).first())})
    else:
        return JsonResponse({'success': False, 'error': 'Only POST requests are allowed'})


@csrf_exempt
def add_new_bill_with_products(request):
    if request.method == 'POST':
        # Création d'une nouvelle facture
        new_bill = Bill.objects.create(bill_date='2024-04-08', bill_active=True)

        # Ajout de nouveaux produits à la facture
        product_data = [
            {'product_label': 'Produit 4', 'product_quantity': 8, 'product_price': 10.99},
            {'product_label': 'Produit 5', 'product_quantity': 3, 'product_price': 1.99},
            {'product_label': 'Produit 6', 'product_quantity': 1, 'product_price': 25.76},
        ]

        for data in product_data:
            Product.objects.create(
                product_label=data['product_label'],
                product_quantity=data['product_quantity'],
                product_price=data['product_price'],
                product_bill=new_bill
            )

        return JsonResponse({'success': True, 'message': 'New bill with products added successfully'})
    else:
        return JsonResponse({'success': False, 'error': 'Only POST requests are allowed'})


@csrf_exempt
def add_participant_to_bill(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        new_participant = participant_controller.create_participant(body['name'], body['bill_id'])
        return JsonResponse({'success': True, 'new_participant': new_participant})
    else:
        return JsonResponse({'success': False, 'error': 'Only POST requests are allowed'})


@csrf_exempt
def participant_check_item_in_bill(request, participant_id):
    if request.method == 'POST':
        body = json.loads(request.body)
        checkbox = participant_controller.participant_contribute(participant_id, body['product_id'],
                                                                 body['contribution'])
        return JsonResponse({'success': True, 'checkbox': checkbox})
    else:
        return JsonResponse({'success': False, 'error': 'Only POST requests are allowed'})


@csrf_exempt
def participant_contribution(request, participant_id):
    if request.method == 'PATCH':
        body = json.loads(request.body)
        participant = participant_controller.get_participant_by_participant_id(participant_id)
        product = product_controller.get_product_by_product_id(body['product_id'])
        print(participant_id)
        participant_controller.participant_contribute(participant, product, body['contribution'], body['bill_id'])
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Only PATCH requests are allowed'})


def get_price_per_participant(request, product_id, bill_id):
    if request.method == 'GET':
        return JsonResponse(
            {'price_per_participant': product_controller.get_price_per_participant(product_id, bill_id)})


def get_bill(request, bill_id):
    try:
        bill = Bill.objects.get(bill_id=bill_id)
        products = Product.objects.filter(product_bill=bill)
        participants = Participant.objects.filter(participant_bill=bill)
        serializer = BillSerializer(bill, context={'products': products, 'participants': participants})
        return JsonResponse(serializer.data)
    except Bill.DoesNotExist:
        return JsonResponse({'error': 'Bill does not exist'}, status=status.HTTP_404_NOT_FOUND)


def bill_details(request, bill_id):
    try:
        bill = bill_controller.get_bill_by_id(bill_id)
        if bill is None:
            raise Http404("Bill does not exist")

        products = product_controller.get_products_by_bill_id(bill_id)
        product_price_per_participant = dict()
        for product in products:
            product_price_per_participant[product.product_id] = product_controller.get_price_per_participant(
                product.product_id,
                bill_id)
        participants = Participant.objects.filter(participant_bill=bill_id)
        bill_total = bill.get_bill_amount()

        return render(request, 'bill_details.html', {
            'bill': bill,
            'products': products,
            'product_price_per_participant': product_price_per_participant,
            'participants': participants,
            'bill_total': bill_total
        })
    except Bill.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Bill does not exist'})
