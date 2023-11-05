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


class IsManager(permissions.BasePermission):
    """
    Allows access only to managers.
    """
    def has_permission(self, request, view):
        user = get_object_or_404(User, username=request.user)
        return user.role == 'manager'


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Give read write access to superusers
    """
    def has_permission(self, request, view):
       if request.method in permissions.SAFE_METHODS:
           return True
       return request.user and request.user.is_superuser


class CanCRUDCart(permissions.BasePermission):
    """
    Give read write access to superusers, managers, salespersons, supervisors
    """
    def has_permission(self, request, view):
        return request.user and (request.user.is_superuser or request.user.role.manager or \
                                 request.user.role.salesperson or request.user.role.supervisor)