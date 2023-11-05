# Generated by Django 4.2.7 on 2023-11-05 12:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales_analytics', '0009_paymentmethod'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('cart_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('number_of_items', models.IntegerField()),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sales_analytics.product')),
            ],
        ),
    ]