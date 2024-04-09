import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Bill, Product, Participant
from .controllers import bill_controller
from .controllers import participant_controller


@csrf_exempt
def create_new_bill(request):
    if request.method == 'POST':
        return JsonResponse({'bill_id': bill_controller.create_new_bill()})


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
        print(body)
        new_participant = participant_controller.create_participant(body['name'], body['bill_id'])
        return JsonResponse({'success': True, 'new_participant': new_participant})
    else:
        return JsonResponse({'success': False, 'error': 'Only POST requests are allowed'})

@csrf_exempt
def participant_check_item_in_bill(request, participant_id):
    if request.method == 'POST':
        product_id = json.loads(request.body)['product_id']
    else:
        return JsonResponse({'success': False, 'error': 'Only POST requests are allowed'})

def get_bill_total_amount(request, bill_id):
    if request.method == 'GET':
        try:
            bill = Bill.objects.get(bill_id=bill_id)
            total_amount = bill.calculate_bill_amount()
            return JsonResponse({'success': True, 'total_amount': total_amount})
        except Bill.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Bill does not exist'})
    else:
        return JsonResponse({'success': False, 'error': 'Only GET requests are allowed'})


def get_bill(request, bill_id):
    if request.method == 'GET':
        try:
            return JsonResponse(bill_controller.get_bill_by_id(bill_id))
        except Bill.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Bill does not exist'})


def bill_details(request, bill_id):
    try:
        bill = Bill.objects.get(bill_id=bill_id)
        products = Product.objects.filter(product_bill=bill)
        participants = Participant.objects.filter(participant_bill=bill)

        product_total_cost = {}
        for product in products:
            product_total_cost[product.product_id] = product.calculate_total()

        bill_total = bill.calculate_bill_amount()

        return render(request, 'bill_details.html', {
            'bill': bill,
            'products': products,
            'participants': participants,
            'bill_total': bill_total,
            'product_total_cost': product_total_cost,
        })
    except Bill.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Bill does not exist'})
