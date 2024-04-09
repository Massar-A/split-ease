from django.db import models

class Bill(models.Model):
    bill_id = models.AutoField(primary_key=True)
    bill_date = models.DateField()
    bill_active = models.BooleanField()

    def calculate_bill_amount(self):
        bill_products = Product.objects.filter(product_bill=self.bill_id)
        total_amount = sum(product.calculate_total() for product in bill_products)
        return total_amount

    def __str__(self):
        return str([self.bill_id, self.bill_date, self.bill_active])


class Participant(models.Model):
    participant_id = models.AutoField(primary_key=True)
    participant_name = models.CharField(max_length=255)
    participant_bill = models.ForeignKey(Bill, on_delete=models.CASCADE)

    def __str__(self):
        return str([self.participant_name, self.participant_bill])


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_label = models.CharField(max_length=255)
    product_quantity = models.IntegerField()
    product_price = models.DecimalField(max_digits=5, decimal_places=2)
    product_bill = models.ForeignKey(Bill, on_delete=models.CASCADE)

    def calculate_total(self):
        return self.product_price * self.product_quantity

    def __str__(self):
        return str([self.product_label, self.product_quantity, self.product_price, self.product_bill])


class ParticipantProductContribution(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    contributes = models.BooleanField(default=True)
