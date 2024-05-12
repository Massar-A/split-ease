# Generated by Django 5.0.4 on 2024-04-10 19:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("SplitEase", "0005_remove_product_product_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="product_price_per_unit",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=9, null=True
            ),
        ),
    ]