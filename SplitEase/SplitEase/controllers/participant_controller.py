from . import product_controller
from ..models import Participant, Bill
from ..models import ParticipantProductContribution


def create_participant(name, bill_id):
    try:
        bill = Bill.objects.filter(bill_id=bill_id).first()
        if bill:
            participant = Participant.objects.create(participant_name=name, participant_bill=bill)
            products = product_controller.get_products_by_bill_id(bill_id)
            for product in products:
                participant_contribute(participant, product, False, bill_id)
            return participant.participant_id
        else:
            return Exception('Bill does not exist')
    except:
        return Exception('Something went wrong')


def delete_participant(participant_id):
    try:
        return Participant.objects.filter(participant_id=participant_id).delete()
    except:
        return Exception('Something went wrong')


def participant_contribute(participant, product, contribution, bill_id):
    try:
        checkbox, created = ParticipantProductContribution.objects.update_or_create(
            participant=participant,
            product=product,
            bill_id=bill_id
        )
        print(checkbox)
        checkbox.contributes = contribution  # Mettre à jour la valeur de contributes
        checkbox.save()  # Sauvegarder l'objet modifié
        return checkbox
    except:
        return Exception('Something went wrong')


def get_participants_contributions(product, bill_id):
    try:
        contribution = ParticipantProductContribution.objects.filter(product, bill_id=bill_id).first().values(
            'contribution')
        return contribution
    except:
        return Exception('Something went wrong')


def get_participants_by_bill_id(bill_id):
    try:
        return Participant.objects.filter(participant_bill=bill_id)
    except:
        return Exception('Something went wrong')


def get_participant_by_participant_id(participant_id):
    try:
        return Participant.objects.filter(participant_id=participant_id).first()
    except:
        return Exception('Something went wrong')