# Generated by Django 4.2.7 on 2023-11-06 16:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales_analytics', '0018_remove_sale_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='completedsale',
            name='payment_method',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sales_analytics.paymentmethod'),
        ),
    ]