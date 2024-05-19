# serializers.py
from rest_framework import serializers
from .models import Bill, Product, Participant


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_id', 'product_label', 'product_quantity', 'product_total_price', 'product_price_per_unit', 'product_bill']


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['participant_id', 'participant_name']


class BillSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    participants = ParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Bill
        fields = ['bill_id', 'bill_date', 'bill_active', 'bill_payer', 'participants', 'products']
