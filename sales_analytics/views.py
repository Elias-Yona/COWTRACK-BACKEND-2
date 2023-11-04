from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomerSerializer, UserSerializer, SalesPersonSerializer, BranchSerializer
from .models import Customer, SalesPerson, Branch
from .permissions import IsSuperUser, IsSalesperson


User = get_user_model()


class CustomerViewSet(ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all().select_related(
        'user').order_by('-user__date_joined')
    permission_classes = (IsSuperUser,)


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = (IsSuperUser,)


class SalesPersonViewSet(ModelViewSet):
    serializer_class = SalesPersonSerializer
    queryset = SalesPerson.objects.all().order_by('-user__date_joined')
    permission_classes = (IsSuperUser,)

    @action(detail=False, methods=['get', 'put'], permission_classes=[IsAuthenticated, IsSalesperson])
    def me(self, request):
        salesperson = get_object_or_404(SalesPerson, user=request.user)

        if request.method == 'PUT':
           serializer = SalesPersonSerializer(salesperson, data=request.data, partial=True)
           serializer.is_valid(raise_exception=True)
           serializer.save()
           return Response(serializer.data)
       
        serializer = self.get_serializer(salesperson)
        return Response(serializer.data)


class BranchViewSet(ModelViewSet):
    serializer_class = BranchSerializer
    queryset = Branch.objects.all().order_by('-opening_date')
    permission_classes = (IsSuperUser,)