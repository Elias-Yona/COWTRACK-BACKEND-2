from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import permissions


User = get_user_model()

class IsSuperUser(permissions.BasePermission):
   """
   Allows access only to superusers.
   """
   def has_permission(self, request, view):
       return request.user and request.user.is_superuser


class IsSalesperson(permissions.BasePermission):
    """
    Allows access only to salespersons.
    """
    def has_permission(self, request, view):
        user = get_object_or_404(User, username=request.user)
        return user.role == 'salesperson'