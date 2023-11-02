from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from .models import Customer


class CustomerSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'phone_number',
                  'kra_pin', 'contact_person', 'address', 'image']

    username = serializers.CharField(max_length=50)
    date_joined = serializers.DateTimeField(read_only=True)


class UserSerializer(BaseUserSerializer, WritableNestedModelSerializer):
    customer = CustomerSerializer()

    class Meta(BaseUserSerializer.Meta):
        extra_fields = ("first_name", "last_name",
                        "is_superuser", "is_active", "is_staff", "date_joined", "customer")
        fields = BaseUserSerializer.Meta.fields + extra_fields
