import json

from django.http import JsonResponse, Http404, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status

from .picnic import picnic_main
from .receipt import image_text_extraction
from .models import Bill, Product, Participant
from .controllers import bill_controller
from .controllers import participant_controller
from .controllers import product_controller
from .serializers import BillSerializer, ProductSerializer


@csrf_exempt
def create_new_bill(request):
    if request.method == 'POST':
        return JsonResponse({'bill_id': bill_controller.create_new_bill()})


@csrf_exempt
def create_product(request, bill_id):
    if request.method == 'POST':
        body = json.loads(request.body)
        required_fields = ['product_label', 'product_price', 'quantity']

        if not all(field in body for field in required_fields):
            return HttpResponseBadRequest('Missing required fields')
        new_product = product_controller.create_product(body['product_label'],
                                                        body['product_price'],
                                                        body['quantity'],
                                                        bill_controller.get_bill_by_id(bill_id))
        serializer = ProductSerializer(new_product)
        return JsonResponse({'new_product': serializer.data})
    else:
        return JsonResponse({'success': False, 'error': 'Only POST requests are allowed'})


@csrf_exempt
def update_product(request, bill_id, product_id):
    if request.method == 'PUT':
        body = json.loads(request.body)
        required_fields = ['product_label', 'product_price', 'quantity']

        if not all(field in body for field in required_fields):
            return HttpResponseBadRequest('Missing required fields')
        updated_product = product_controller.update_product(body['product_label'],
                                                            body['product_price'],
                                                            body['quantity'],
                                                            bill_controller.get_bill_by_id(bill_id),
                                                            product_id)
        serializer = ProductSerializer(product_controller.get_product_by_product_id(product_id))
        return JsonResponse(serializer.data)
    else:
        return JsonResponse({'success': False, 'error': 'Only POST requests are allowed'})

@csrf_exempt
def delete_product(request, product_id):
    if request.method == 'DELETE':
        try:
            print(product_id)
            product_controller.delete_product(product_id)
            return JsonResponse({'success': True})
        except:
            return JsonResponse({'success': False})
    else:
        JsonResponse({'success': False, 'error': 'Only DELETE requests are allowed'})


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
def participant_contribution(request, participant_id, bill_id):
    if request.method == 'PATCH':
        body = json.loads(request.body)
        participant = participant_controller.get_participant_by_participant_id(participant_id)
        product = product_controller.get_product_by_product_id(body['product_id'])
        participant_controller.participant_contribute(participant, product, body['contribution'], bill_id)
        new_price = product_controller.get_price_per_participant(body['product_id'], bill_id)
        return JsonResponse({'success': True, 'new_price': new_price})
    else:
        return JsonResponse({'success': False, 'error': 'Only PATCH requests are allowed'})


@csrf_exempt
def delete_participant(request, participant_id):
    if request.method == 'DELETE':
        try:
            participant_controller.delete_participant(participant_id)
            return JsonResponse({'success': True})
        except:
            return JsonResponse({'success': False})
    else:
        JsonResponse({'success': False, 'error': 'Only DELETE requests are allowed'})


def get_price_per_participant(request, product_id, bill_id):
    if request.method == 'GET':
        return JsonResponse(
            {'price_per_participant': product_controller.get_price_per_participant(product_id, bill_id)})
    else:
        return JsonResponse({'success': False, 'error': 'Only GET is allowed'})


def get_participants_total_cost(request, bill_id):
    if request.method == 'GET':
        try:
            participants = participant_controller.get_participants_by_bill_id(bill_id)
            response = dict()
            for participant in participants:
                response[participant.participant_id] = participant_controller.get_participant_total_cost(
                    participant.participant_id, bill_id)
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


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
        participants = Participant.objects.filter(participant_bill=bill_id)

        participants_products_contribution = dict()

        participants_total_cost = dict()

        for participant in participants:
            contributions = participant_controller.get_participants_contributions(participant.participant_id, bill_id)
            participants_total_cost[participant.participant_id] = participant_controller.get_participant_total_cost(
                participant.participant_id, bill_id)
            for product in products:
                if product.product_id in contributions:
                    contribution_status = True
                else:
                    contribution_status = False
                if product.product_id not in participants_products_contribution:
                    participants_products_contribution[product.product_id] = dict()
                participants_products_contribution[product.product_id][participant.participant_id] = contribution_status
                product_price_per_participant[product.product_id] = product_controller.get_price_per_participant(
                    product.product_id,
                    bill_id)
        bill_total = bill.get_bill_amount()
        print(participants_total_cost)
        return render(request, 'bill_details.html', {
            'bill': bill,
            'products': products,
            'product_price_per_participant': product_price_per_participant,
            'participants_products_contribution': participants_products_contribution,
            'participants_total_cost': participants_total_cost,
            'participants': participants,
            'bill_total': bill_total
        })
    except Bill.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Bill does not exist'})

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        if 'picnic_file' in request.FILES:
            file = request.FILES['picnic_file']
            return bill_details('GET', picnic_main.create_picnic_bill(file))
        elif 'img' in request.FILES:
            file = request.FILES['img']
            return JsonResponse(picnic_main.analyze_picnic(file), safe=False)
        else:
            return HttpResponseBadRequest('Missing required pdf file ou image')
    else:
        return HttpResponseBadRequest('Only POST requests are allowed')

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        if 'picnic_file' in request.FILES:
            file = request.FILES['picnic_file']
            return JsonResponse({'success': True,
                                 'new_bill_id': picnic_main.create_picnic_bill(file, date)})
        elif 'img' in request.FILES:
            file = request.FILES['img']
            return JsonResponse(picnic_main.analyze_picnic(file), safe=False)
        else:
            return HttpResponseBadRequest('Missing required pdf file ou image')
    else:
        return HttpResponseBadRequest('Only POST requests are allowed')


@csrf_exempt
def upload_file_test(request):
    if request.method == 'POST':
        if 'picnic_file' in request.FILES:
            file = request.FILES['picnic_file']
            return JsonResponse(picnic_main.analyze_picnic(file), safe=False)
        elif 'img' in request.FILES:
            file = request.FILES['img']
            return JsonResponse(picnic_main.analyze_picnic(file), safe=False)
        else:
            return HttpResponseBadRequest('Missing required pdf file ou image')
    else:
        return HttpResponseBadRequest('Only POST requests are allowed')


@csrf_exempt
def read_test(request):
    if request.method == 'POST':
        file = request.FILES['file']
        return HttpResponse(picnic_main.read_text(file))

def read_image_test(request):
    if request.method == 'POST':
        if 'picnic_file' in request.FILES:
            file = request.FILES['picnic_file']
            return JsonResponse(picnic_main.analyze_picnic(file), safe=False)
        elif 'img' in request.FILES:
            file = request.FILES['img']
            return HttpResponse(image_text_extraction.read_test(file))
        else:
            return HttpResponseBadRequest('Missing required pdf file ou image')
    else:
        return HttpResponseBadRequest('Only POST requests are allowed')
