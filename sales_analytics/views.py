from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomerSerializer, UserSerializer, SalesPersonSerializer, BranchSerializer
from .serializers import SalesPersonBranchSerializer, SimpleSalesPersonBranchSerializer
from .models import Customer, SalesPerson, Branch, SalesPersonBranch
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
        response_data = serializer.data

        branches = SalesPersonBranch.objects.filter(salesperson=salesperson).order_by('-assignment_date')
        branch_serializer = SimpleSalesPersonBranchSerializer(branches, many=True)

        response_data['branches'] = branch_serializer.data

        return Response(response_data)


class BranchViewSet(ModelViewSet):
    serializer_class = BranchSerializer
    queryset = Branch.objects.all().order_by('-opening_date')
    permission_classes = (IsSuperUser,)



class SalesPersonBranchViewSet(ModelViewSet):
    serializer_class = SalesPersonBranchSerializer
    permission_classes = (IsSuperUser,)

    def get_queryset(self):
       salesperson_id = self.kwargs['salesperson_pk']
       return SalesPersonBranch.objects.filter(salesperson_id=salesperson_id).order_by('-assignment_date')

    def get_serializer_context(self):
      context = super().get_serializer_context()
      context.update({'salesperson_pk': self.kwargs['salesperson_pk']})
      return context