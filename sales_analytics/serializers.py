from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from drf_writable_nested.serializers import WritableNestedModelSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer
from djmoney.contrib.django_rest_framework import MoneyField
from templated_email import send_templated_mail

from .models import Customer, SalesPerson, Branch, SalesPersonBranch, Manager, Supplier
from .models import ProductCategory, Product, PaymentMethod, Cart, Sale


User = get_user_model()


class UserSerializer(WritableNestedModelSerializer, BaseUserSerializer, UserCreateSerializer):
    class Meta(BaseUserSerializer.Meta):
        extra_fields = ("first_name", "last_name",
                        "is_superuser", "is_active", "username", "is_staff", "role", "date_joined", "last_login", "password")
        fields = BaseUserSerializer.Meta.fields + extra_fields
        read_only_fields = list(BaseUserSerializer.Meta.read_only_fields)
        # read_only_fields.remove('username')
        read_only_fields += ['last_login', 'date_joined']
        BaseUserSerializer.Meta.read_only_fields = tuple(read_only_fields)



class CustomerSerializer(WritableNestedModelSerializer):
    image = serializers.SerializerMethodField('get_image')
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = ['customer_id', 'phone_number',
                  'kra_pin', 'contact_person', 'address', 'image', 'user']

    def get_image(self, manager):
        return f"https://ui-avatars.com/api/?name={manager.user.first_name}+{manager.user.last_name}"

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['role'] = 'customer'
        user_data['username'] = validated_data['phone_number']
        user_data['is_active'] = 1
        user = User.objects.create(**user_data)

        return Customer.objects.create(user=user, **validated_data)


class SalesPersonSerializer(WritableNestedModelSerializer):
    image = serializers.SerializerMethodField('get_image')
    user = UserSerializer()

    class Meta:
        model = SalesPerson
        fields = ['sales_person_id', 'phone_number', 'image', 'user']
   
    def get_image(self, salesperson):
        return f"https://ui-avatars.com/api/?name={salesperson.user.first_name}+{salesperson.user.last_name}"
    
    def update(self, instance, validated_data):
       instance.user.last_login = timezone.now()
       user_data = validated_data.pop('user', None)
       if user_data is not None:
           UserSerializer().update(instance.user, user_data)
       return super().update(instance, validated_data)

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['role'] = 'salesperson'
        user_data['username'] = user_data['email']
        user_data['is_active'] = 1
        user_data['password'] = make_password(user_data['password'])
        user = User.objects.create(**user_data)

        return SalesPerson.objects.create(user=user, **validated_data)


class BranchSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Branch
        fields = ['branch_id', 'branch_name', 'phone_number', 'email', 'opening_date',]


class SimpleSalesPersonBranchSerializer(WritableNestedModelSerializer):
    branch = BranchSerializer()
    class Meta:
        model = SalesPersonBranch
        fields = ['salesperson_branch_id', 'branch', 'assignment_date', 'termination_date']



class SalesPersonBranchSerializer(WritableNestedModelSerializer):
    class Meta:
        model = SalesPersonBranch
        fields = ['salesperson_branch_id', 'branch', 'assignment_date', 'termination_date']

    assignment_date = serializers.DateTimeField(read_only=True)
    termination_date = serializers.DateTimeField(read_only=True)

    def assign_salesperson_to_branch(self, **kwargs):
        spb = SalesPersonBranch.objects.create(**kwargs["validated_data"])
        send_templated_mail(
            template_name='assignment',
            from_email='admin@cowtrack.com',
            recipient_list=[spb.salesperson.user.email],
            context={
                'salesperson_name': f'{spb.salesperson.user.first_name} {spb.salesperson.user.last_name}',
                'assignment_date': spb.assignment_date,
                'branch_name': spb.branch.branch_name,
                'image': f"https://ui-avatars.com/api/?name={spb.salesperson.user.first_name}+{spb.salesperson.user.last_name}"
            },
        )

        return spb
 
    def create(self, validated_data):
        validated_data['salesperson_id'] = self.context['salesperson_pk']
        salesperson_pk = validated_data.get('salesperson_id')

        try:
            spb = SalesPersonBranch.objects.filter(salesperson_id=salesperson_pk).order_by('-assignment_date').first()
            # if salesperson has not been removed from the current branch, then remove the salesperson
            if not spb.termination_date and (spb.branch_id != validated_data["branch"].branch_id):
                spb.termination_date = timezone.now()
                spb.save()

                send_templated_mail(
                    template_name='termination',
                    from_email='admin@cowtrack.com',
                    recipient_list=[spb.salesperson.user.email],
                    context={
                        'salesperson_name': f'{spb.salesperson.user.first_name} {spb.salesperson.user.last_name}',
                        'termination_date': spb.termination_date,
                        'branch_name': spb.branch.branch_name,
                        'image': f"https://ui-avatars.com/api/?name={spb.salesperson.user.first_name}+{spb.salesperson.user.last_name}"
                    },
                )
            
                # assign the salesperson to the new branch
                spb = self.assign_salesperson_to_branch(validated_data=validated_data)

            elif not spb.termination_date and (spb.branch_id == validated_data["branch"].branch_id):
                raise ValidationError({'message': 'Salesperson is already assigned to the branch'})
                
            elif spb.termination_date:
                spb = self.assign_salesperson_to_branch(validated_data=validated_data)
           
        except SalesPersonBranch.DoesNotExist:
            validated_data['assignment_date'] = timezone.now()
            return super().create(validated_data)

        return spb


class ManagerSerializer(WritableNestedModelSerializer):
    image = serializers.SerializerMethodField('get_image')
    user = UserSerializer()

    class Meta:
        model = Manager
        fields = ['manager_id', 'phone_number', 'image', 'user']

    def get_image(self, manager):
        return f"https://ui-avatars.com/api/?name={manager.user.first_name}+{manager.user.last_name}"
    
    def update(self, instance, validated_data):
       instance.user.last_login = timezone.now()
       user_data = validated_data.pop('user', None)
       if user_data is not None:
           UserSerializer().update(instance.user, user_data)
       return super().update(instance, validated_data)

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['role'] = 'manager'
        user_data['username'] = user_data['email']
        user_data['is_active'] = 1
        user = User.objects.create(**user_data)

        return Manager.objects.create(user=user, **validated_data)


class SupplierSerializer(WritableNestedModelSerializer):
    image = serializers.SerializerMethodField('get_image')
    user = UserSerializer()

    class Meta:
        model = Supplier
        fields = ['supplier_id', 'phone_number', 'kra_pin', 'contact_person', 'notes', 'image', 'user']

    def get_image(self, supplier):
        return f"https://ui-avatars.com/api/?name={supplier.user.first_name}+{supplier.user.last_name}"
    
    def update(self, instance, validated_data):
       instance.user.last_login = timezone.now()
       user_data = validated_data.pop('user', None)
       if user_data is not None:
           UserSerializer().update(instance.user, user_data)
       return super().update(instance, validated_data)

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['role'] = 'supplier'
        user_data['username'] = user_data['email']
        user_data['is_active'] = 1
        user = User.objects.create(**user_data)

        return Supplier.objects.create(user=user, **validated_data)


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['category_id', 'category_name']


class ProductSerializer(WritableNestedModelSerializer):
    cost_price = MoneyField(max_digits=19, decimal_places=4)
    selling_price = MoneyField(max_digits=19, decimal_places=4)
    is_serialized = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = ['product_id', 'product_name', 'cost_price_currency', 'cost_price', 'selling_price_currency', 'selling_price', 'is_serialized',
                  'serial_number', 'category', 'branch']

    def create(self, validated_data):
        serial_number = validated_data.get('serial_number')
        if serial_number is not None:
            validated_data['is_serialized'] = 1
        return super().create(validated_data)


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['payment_method_id', 'method_name']


class SimpleProductCartSerializer(serializers.Serializer):
    product_name = serializers.CharField(max_length=50)
    selling_price = MoneyField(max_digits=19, decimal_places=2)
    serial_number = serializers.CharField(max_length=50)


class CartReadSerializer(WritableNestedModelSerializer):
    total_price = serializers.SerializerMethodField('get_total_price')
    product = SimpleProductCartSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = ['cart_id', 'number_of_items', 'product', 'total_price']

    def get_total_price(self, cart):
        return cart.number_of_items * cart.product.selling_price.amount
    

class CartUpdateSerializer(serializers.Serializer):
    number_of_items = serializers.IntegerField()

    def update(self, instance, validated_data):
       instance.number_of_items = validated_data.get('number_of_items', instance.number_of_items)
       instance.save()
       return instance
    

class CartWriteSerializer(WritableNestedModelSerializer):
    total_price = serializers.SerializerMethodField('get_total_price')

    class Meta:
        model = Cart
        fields = ['cart_id', 'number_of_items', 'product', 'total_price']

    def get_total_price(self, cart):
        return cart.number_of_items * cart.product.selling_price.amount


class SaleReadSerializer(WritableNestedModelSerializer):
    sales_person = SalesPersonSerializer()
    cart = CartWriteSerializer()
    payment_method = PaymentMethodSerializer()
    amount = MoneyField(max_digits=19, decimal_places=4)

    class Meta:
        model = Sale
        fields = ['sale_id', 'amount', 'transaction_date', 'transaction_id', 'awarded_points',
                  'sales_person', 'cart', 'payment_method']


class SaleWriteSerializer(WritableNestedModelSerializer):
    amount = MoneyField(max_digits=19, decimal_places=4)
    cart = CartWriteSerializer()

    class Meta:
        model = Sale
        fields = ['sale_id', 'amount', 'transaction_date', 'transaction_id', 'awarded_points',
                  'sales_person', 'cart', 'payment_method']