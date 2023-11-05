import random
import string

from django.db import models
from django.conf import settings
from djmoney.models.fields import MoneyField



class Customer(models.Model):
    customer_id = models.BigAutoField(primary_key=True)
    phone_number = models.CharField(max_length=15)
    kra_pin = models.CharField(max_length=20, unique=True)
    contact_person = models.CharField(max_length=15)
    address = models.CharField(max_length=200)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"


class SalesPerson(models.Model):
    sales_person_id = models.BigAutoField(primary_key=True)
    phone_number = models.CharField(max_length=15)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"


class Supervisor(models.Model):
    supervisor_id = models.BigAutoField(primary_key=True)
    phone_number = models.CharField(max_length=15)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"


class Manager(models.Model):
    manager_id = models.BigAutoField(primary_key=True)
    phone_number = models.CharField(max_length=15)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"


class Supplier(models.Model):
    supplier_id = models.BigAutoField(primary_key=True)
    phone_number = models.CharField(max_length=15)
    kra_pin = models.CharField(max_length=20, unique=True)
    contact_person = models.CharField(max_length=15)
    notes = models.TextField()
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"


class Branch(models.Model):
    branch_id = models.BigAutoField(primary_key=True)
    branch_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(max_length=50, unique=True)
    opening_date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.branch_name


class SalesPersonBranch(models.Model):
    salesperson_branch_id = models.BigAutoField(primary_key=True)
    salesperson = models.ForeignKey(SalesPerson, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    assignment_date = models.DateTimeField(auto_now_add=True)
    termination_date = models.DateTimeField(null=True)


class ProductCategory(models.Model):
    category_id = models.BigAutoField(primary_key=True)
    category_name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.category_name


class Product(models.Model):
    product_id = models.BigAutoField(primary_key=True)
    product_name = models.CharField(max_length=50)
    cost_price = MoneyField(
        max_digits=19, decimal_places=4, default_currency='kES')
    selling_price = MoneyField(
        max_digits=19, decimal_places=4, default_currency='KES')
    is_serialized = models.BooleanField(default=0)
    serial_number = models.CharField(max_length=50, null=True)
    category = models.ForeignKey(
        ProductCategory, on_delete=models.SET_NULL, null=True)
    branch = models.ForeignKey(
        Branch, on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        return self.product_name


class PaymentMethod(models.Model):
    payment_method_id = models.BigAutoField(primary_key=True)
    method_name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.method_name


class Cart(models.Model):
    cart_id = models.BigAutoField(primary_key=True)
    number_of_items = models.IntegerField()
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        return str(self.cart_id)


class Sale(models.Model):
    sale_id = models.BigAutoField(primary_key=True)
    amount = MoneyField(
        max_digits=19, decimal_places=4, default_currency='KES')
    transaction_date = models.DateTimeField(auto_now_add=True)
    awarded_points = models.IntegerField()
    transaction_id = models.CharField(max_length=20, blank=True)
    sales_person = models.ForeignKey(
        SalesPerson, on_delete=models.SET_NULL, null=True)
    cart = models.ForeignKey(
        Cart, on_delete=models.SET_NULL, null=True)
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.SET_NULL, null=True)
    is_completed = models.BooleanField(default=0)

    def save(self, *args, **kwargs):
       if not self.transaction_id:
           self.transaction_id = 'CWT' + ''.join(random.choices(string.digits, k=7)) + ''.join(random.choices(string.ascii_uppercase, k=4)) + ''.join(random.choices(string.digits, k=5))
       super(Sale, self).save(*args, **kwargs)


class CompletedSale(models.Model):
    sale_id = models.BigAutoField(primary_key=True)
    completed_at = models.DateTimeField(auto_now_add=True)
    total_amount = MoneyField(
        max_digits=19, decimal_places=4, default_currency='KES')
    branch = models.ForeignKey(
        Branch, on_delete=models.SET_NULL, null=True)
    salesperson = models.ForeignKey(
        SalesPerson, on_delete=models.SET_NULL, null=True)