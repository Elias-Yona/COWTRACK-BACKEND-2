from django.db import models
from django.conf import settings


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