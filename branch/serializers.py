from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from .models import Customer, SalesPerson


class UserSerializer(WritableNestedModelSerializer, BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        extra_fields = ("first_name", "last_name",
                        "is_superuser", "is_active", "username", "is_staff", "date_joined")
        fields = BaseUserSerializer.Meta.fields + extra_fields

    date_joined = serializers.DateTimeField(read_only=True)


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
       user_data = validated_data.pop('user', None)
       if user_data is not None:
           UserSerializer().update(instance.user, user_data)
       return super().update(instance, validated_data)