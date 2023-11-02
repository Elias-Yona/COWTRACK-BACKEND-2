from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        extra_fields = ("first_name", "last_name",
                        "is_superuser", "is_active", "is_staff", "date_joined")
        fields = BaseUserSerializer.Meta.fields + extra_fields

        
class CustomerSerializer(WritableNestedModelSerializer):
