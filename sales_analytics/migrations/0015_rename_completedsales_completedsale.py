# Generated by Django 4.2.7 on 2023-11-05 19:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales_analytics', '0014_add_sale_is_completed'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CompletedSales',
            new_name='CompletedSale',
        ),
    ]
