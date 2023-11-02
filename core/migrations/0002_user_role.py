# Generated by Django 4.2.7 on 2023-11-02 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('customer', 'Customer'), ('manager', 'Manager'), ('supervisor', 'Supervisor'), ('supplier', 'Supplier'), ('sales person', 'Sales person')], default='sales person', max_length=20),
        ),
    ]
