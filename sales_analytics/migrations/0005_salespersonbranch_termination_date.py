# Generated by Django 4.2.7 on 2023-11-04 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales_analytics', '0004_rename_created_at_salespersonbranch_assignment_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='salespersonbranch',
            name='termination_date',
            field=models.DateTimeField(null=True),
        ),
    ]
