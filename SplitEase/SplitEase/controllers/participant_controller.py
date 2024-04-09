from ..models import Participant, Bill
from ..models import ParticipantProductContribution


def create_participant(name, bill_id):
    try:
        bill = Bill.objects.filter(bill_id=bill_id).first()
        if bill:
            participant = Participant.objects.create(participant_name=name, participant_bill=bill)
            return participant.participant_id
        else:
            return 'Bill does not exist'
    except Exception as e:
        return str(e)


def participant_contribute(participant, product, contribution):
    checkbox = ParticipantProductContribution.objects.filter(participant=participant, product=product)
    checkbox.contributes = contribution
    return checkbox


def get_participant_by_bill_id(bill_id):
    return Participant.objects.filter(participant_bill=bill_id).values('participant_id', 'participant_name')
