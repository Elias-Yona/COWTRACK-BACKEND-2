from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomerSerializer, UserSerializer, SalesPersonSerializer, BranchSerializer
from .serializers import SupplierSerializer
from .serializers import SalesPersonBranchSerializer, SimpleSalesPersonBranchSerializer, ManagerSerializer
from .serializers import ProductCategorySerializer, ProductSerializer, PaymentMethodSerializer
from .serializers import CartReadSerializer, CartWriteSerializer
from .models import Customer, SalesPerson, Branch, SalesPersonBranch, Manager, Supplier, ProductCategory
from .models import Product, PaymentMethod, Cart
from .permissions import IsSuperUser, IsSalesperson, IsManager, IsSuperUserOrReadOnly, CanCRUDCart


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
    queryset = SalesPerson.objects.all().select_related('user').order_by('-user__date_joined')
    permission_classes = (IsSuperUser,)

    @action(detail=False, methods=['get', 'put'], permission_classes=[IsAuthenticated, IsSalesperson])
    def me(self, request):
        salesperson = get_object_or_404(SalesPerson.objects.select_related('user'), user=request.user)

        if request.method == 'PUT':
           serializer = SalesPersonSerializer(salesperson, data=request.data, partial=True)
           serializer.is_valid(raise_exception=True)
           serializer.save()
           return Response(serializer.data)
       
        serializer = self.get_serializer(salesperson)
        response_data = serializer.data

        branches = SalesPersonBranch.objects.filter(salesperson=salesperson).select_related("salesperson").select_related("branch").order_by('-assignment_date')
        branch_serializer = SimpleSalesPersonBranchSerializer(branches, many=True)

        response_data['branches'] = branch_serializer.data

        return Response(response_data)


class ManagerViewSet(ModelViewSet):
    serializer_class = ManagerSerializer
    queryset = Manager.objects.all().select_related('user').order_by('-user__date_joined')
    permission_classes = (IsSuperUser,)

    @action(detail=False, methods=['get', 'put'], permission_classes=[IsAuthenticated, IsManager])
    def me(self, request):
        manager = get_object_or_404(Manager.objects.select_related('user'), user=request.user)

        if request.method == 'PUT':
           serializer = ManagerSerializer(manager, data=request.data, partial=True)
           serializer.is_valid(raise_exception=True)
           serializer.save()
           return Response(serializer.data)
       
        serializer = self.get_serializer(manager)
        response_data = serializer.data

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


class SupplierViewSet(ModelViewSet):
    serializer_class = SupplierSerializer
    queryset = Supplier.objects.all().select_related('user').order_by('-user__date_joined')
    permission_classes = (IsSuperUser,)


class ProductCategoryViewSet(ModelViewSet):
    serializer_class = ProductCategorySerializer
    queryset = ProductCategory.objects.all()
    permission_classes = (IsSuperUserOrReadOnly,)


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all().select_related('branch').select_related('category').order_by('-product_id')
    permission_classes = (IsSuperUserOrReadOnly,)


class PaymentMethodViewSet(ModelViewSet):
    serializer_class = PaymentMethodSerializer
    queryset = PaymentMethod.objects.all()
    permission_classes = (IsSuperUserOrReadOnly,)


class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all().select_related('product').order_by('-product_id')
    permission_classes = (CanCRUDCart,)

    def get_queryset(self):
       customer_id = self.kwargs['customer_pk']
       return Cart.objects.filter(customer_id=customer_id).order_by('-cart_id')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CartReadSerializer
        return CartWriteSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        price = sum(cart['total_price'] for cart in serializer.data)
        return Response({'results': serializer.data, 'price': price})
