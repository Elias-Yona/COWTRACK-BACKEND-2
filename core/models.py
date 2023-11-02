from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ADMIN = "admin"
    CUSTOMER = "customer"
    MANAGER = "manager"
    SUPERVISOR = "supervisor"
    SUPPLIER = "supplier"
    SALES_PERSON = "sales person"

    ROLE_CHOICES = [
        (ADMIN, "Admin"),
        (CUSTOMER, "Customer"),
        (MANAGER, "Manager"),
        (SUPERVISOR, "Supervisor"),
        (SUPPLIER, "Supplier"),
        (SALES_PERSON, "Sales person"),
    ]

    email = models.CharField(max_length=50, null=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=SALES_PERSON,
    )
