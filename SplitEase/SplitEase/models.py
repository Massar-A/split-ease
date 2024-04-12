from json import JSONEncoder

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


class Bill(models.Model):
    bill_id = models.AutoField(primary_key=True)
    bill_date = models.DateField()
    bill_active = models.BooleanField()

    def get_bill_amount(self):
        bill_products = Product.objects.filter(product_bill=self.bill_id)
        total_amount = sum(product.product_total_price for product in bill_products)
        return total_amount

    def __str__(self):
        return str([self.bill_id, self.bill_date, self.bill_active])


class Participant(models.Model):
    participant_id = models.AutoField(primary_key=True)
    participant_name = models.CharField(max_length=255)
    participant_bill = models.ForeignKey(Bill, related_name="participants", on_delete=models.CASCADE)

    def __str__(self):
        return str([self.participant_name, self.participant_bill])


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_label = models.CharField(max_length=255)
    product_quantity = models.IntegerField()
    product_price_per_unit = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    product_total_price = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    product_bill = models.ForeignKey(Bill, related_name="products", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.product_price_per_unit = self.price_per_unit()
        super().save(*args, **kwargs)

    def price_per_unit(self):
        if self.product_quantity == 0:
            return 0  # Condition de base : éviter la récursion infinie
        return self.product_total_price / self.product_quantity

    def __str__(self):
        return str([self.product_label, self.product_quantity, self.product_total_price, self.product_bill,
                    self.product_price_per_unit])


@receiver(pre_save, sender=Product)
def update_product_total_price(sender, instance, **kwargs):
    instance.product_price_per_unit = instance.price_per_unit()


class ParticipantProductContribution(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    contributes = models.BooleanField(default=False, null=True)
