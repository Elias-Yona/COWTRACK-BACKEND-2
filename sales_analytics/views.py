from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Sum
from django.db.models.functions import ExtractYear, ExtractMonth
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from .serializers import CustomerSerializer, UserSerializer, SalesPersonSerializer, BranchSerializer
from .serializers import SupplierSerializer
from .serializers import SalesPersonBranchSerializer, SimpleSalesPersonBranchSerializer, ManagerSerializer
from .serializers import ProductCategorySerializer, ProductSerializer, PaymentMethodSerializer
from .serializers import CartReadSerializer, CartWriteSerializer, CartUpdateSerializer
from .serializers import SaleReadSerializer, SaleWriteSerializer, CompletedSaleWriteSerializer
from .serializers import CompletedSaleReadSerializer, CompletedSalePaymentSerializer
from .serializers import MonthlySalesSerializer
from .models import Customer, SalesPerson, Branch, SalesPersonBranch, Manager, Supplier, ProductCategory
from .models import Product, PaymentMethod, Cart, Sale, CompletedSale
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

        sales = CompletedSale.objects.filter(salesperson=salesperson).annotate(
            year=ExtractYear('completed_at'),
            month=ExtractMonth('completed_at')
            ).values(
            'year', 'month', 'branch__branch_name'
            ).annotate(
            number_of_sales=Count('sale_id'),
            total_amount=Sum('total_amount')
            ).order_by('year', 'month')

        monthly_sales_serializer = MonthlySalesSerializer(sales, many=True)

        response_data['branches'] = branch_serializer.data
        response_data['monthly_sales'] = monthly_sales_serializer.data

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
        elif self.request.method == 'PUT':
            return CartUpdateSerializer
        return CartWriteSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        price = sum(cart['total_price'] for cart in serializer.data)
        return Response({'results': serializer.data, 'price': price})


class SaleViewSet(ModelViewSet):
    def get_serializer_class(self):
        if self.action == 'complete_sale':
            return CompletedSaleReadSerializer
        elif self.request.method == 'GET':
            return SaleReadSerializer
        return SaleWriteSerializer

    def get_permissions(self):
       if self.request.user.role == 'superuser':
           return [IsSuperUser()]
       elif self.request.user.role == 'salesperson':
           return [IsAuthenticated(), IsSalesperson()]


    def get_queryset(self):
       salesperson_id = self.kwargs['salesperson_pk']
       return Sale.objects.filter(salesperson_id=salesperson_id).select_related('salesperson') \
            .select_related('cart').order_by('-transaction_date')


    @action(detail=False, methods=['post', 'get'])
    def complete_sale(self, request, **kwargs):
        salesperson_id = self.kwargs['salesperson_pk']
        
        sales = Sale.objects.filter(salesperson_id=salesperson_id, is_completed=0).select_related('salesperson') \
            .select_related('cart').order_by('-transaction_date')
        
        if not sales:
            raise ValidationError({"message": "Can't complete sale cart is empty"})

        payment_method = request.data.get('payment_method')

        if not payment_method:
            raise ValidationError({"message": "A payment method must be present"})

        if self.request.method == "GET":
            completed_sales = CompletedSale.objects.filter(salesperson_id=salesperson_id)
            return Response(CompletedSaleReadSerializer(completed_sales).data)
        
        with transaction.atomic():
            latest_branch = SalesPersonBranch.objects.filter(salesperson_id=salesperson_id) \
                .select_related('salesperson').select_related('branch').order_by('-salesperson_branch_id').first()
            total_price = 0

            for sale in sales:
                sale.is_completed = 1
                sale.save()

                cart = Cart.objects.get(cart_id=sale.cart_id)

                total_price += cart.number_of_items * cart.product.selling_price

            completed_sale = CompletedSale.objects.create(
                salesperson_id=int(salesperson_id), 
                branch_id=latest_branch.branch_id, 
                total_amount=total_price,
                payment_method_id=int(payment_method)
            )
            
            return Response(CompletedSaleReadSerializer(completed_sale).data)


class CompletedSaleViewSet(ModelViewSet):
    queryset = CompletedSale.objects.all().select_related('branch').select_related('salesperson')
    permission_classes = (IsSuperUser,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CompletedSaleReadSerializer
        return CompletedSaleWriteSerializer