from django.utils import timezone
from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from .models import Customer, SalesPerson, Branch, SalesPersonBranch


class UserSerializer(WritableNestedModelSerializer, BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        extra_fields = ("first_name", "last_name",
                        "is_superuser", "is_active", "username", "is_staff", "date_joined", "last_login")
        fields = BaseUserSerializer.Meta.fields + extra_fields
        read_only_fields = list(BaseUserSerializer.Meta.read_only_fields)
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


class BranchSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Branch
        fields = ['branch_id', 'branch_name', 'phone_number', 'email', 'opening_date',]


class SalesPersonBranchSerializer(WritableNestedModelSerializer):
    class Meta:
        model = SalesPersonBranch
        fields = ['salesperson_branch_id', 'branch', 'assignment_date', 'termination_date']

    assignment_date = serializers.DateTimeField(read_only=True)
    termination_date = serializers.DateTimeField(read_only=True)
 
    def create(self, validated_data):
        validated_data['salesperson_id'] = self.context['salesperson_pk']
        return super().create(validated_data)