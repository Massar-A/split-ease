# Generated by Django 5.0.4 on 2024-05-18 22:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("SplitEase", "0013_alter_participant_participant_bill_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="bill",
            name="bill_payer",
            field=models.IntegerField(null=True),
        ),
    ]
