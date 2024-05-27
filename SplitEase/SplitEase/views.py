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
from .serializers import BillSerializer, ProductSerializer, ParticipantSerializer


@csrf_exempt
def create_new_bill(request):
    if request.method == 'POST':
        return JsonResponse({'bill_id': bill_controller.create_new_bill()})


@csrf_exempt
def set_bill_payer(request, bill_id):
    if request.method == 'PUT':
        participant_id = json.loads(request.body)['participant_id']
        bill_controller.set_bill_payer(bill_id, participant_id)
        return JsonResponse({'bill_id': bill_id})
    else:
        return JsonResponse({'Error': 'Only PUT is allowed'})


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
def add_participant_to_bill(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        new_participant = participant_controller.create_participant(body['name'], body['bill_id'])
        return JsonResponse(ParticipantSerializer(new_participant).data)
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


@csrf_exempt
def update_participant(request, participant_id):
    if request.method == 'PUT':
        body = json.loads(request.body)
        required_fields = ['participant_name']

        if not all(field in body for field in required_fields):
            return HttpResponseBadRequest('Missing required fields')
        updated_participant = participant_controller.update_participant(participant_id, body['participant_name'])
        print(updated_participant)
        serializer = ParticipantSerializer(participant_controller.get_participant_by_participant_id(participant_id))
        return JsonResponse(serializer.data)
    else:
        return JsonResponse({'success': False, 'error': 'Only PUT requests are allowed'})


@csrf_exempt
def get_participants(request, bill_id):
    if request.method == 'GET':

        participants = participant_controller.get_participants_by_bill_id(bill_id)
        serializer = ParticipantSerializer(participants, many=True)
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse({'success': False, 'error': 'Only POST requests are allowed'})


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


def get_price_per_person(request, bill_id):
    if request.method == 'GET':
        try:
            products = product_controller.get_products_by_bill_id(bill_id)
            product_price_per_participant = dict()
            for product in products:
                product_price_per_participant[product.product_id] = product_controller.get_price_per_participant(
                    product.product_id,
                    bill_id)
            return JsonResponse(product_price_per_participant, safe=False)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Only GET is allowed'})


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
        participants = list(participant_controller.get_participants_by_bill_id(bill_id))
        print(products)
        print(participants)
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
        print(participants_total_cost)
        participants_total = round(sum(float(value.replace(',', '.')) for value in participants_total_cost.values()),2)
        bill_total = bill.get_bill_amount()
        return render(request, 'bill_details.html', {
            'bill': bill,
            'products': products,
            'product_price_per_participant': product_price_per_participant,
            'participants_products_contribution': participants_products_contribution,
            'participants_total_cost': participants_total_cost,
            'participants_total': participants_total,
            'participants': participants,
            'bill_total': bill_total,
            'csrf_token': "wsh"
        })
    except Bill.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Bill does not exist'})


def index(request):
    if request.method == 'GET':
        return render(request, 'index.html')
    else:
        return JsonResponse({'success': False, 'error': 'Only GET is allowed'})


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
        if 'picnic_file' in request.FILES:
            file = request.FILES['picnic_file']
            return HttpResponse(picnic_main.read_text(file))
        elif 'img' in request.FILES:
            file = request.FILES['img']
            return HttpResponse(image_text_extraction.read_test(file))
        else:
            return HttpResponseBadRequest('Missing required pdf file ou image')
    else:
        return HttpResponseBadRequest('Only POST requests are allowed')
