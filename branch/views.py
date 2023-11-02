from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from .serializers import CustomerSerializer, UserSerializer
from .models import Customer


User = get_user_model()


class CustomerViewSet(ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all().select_related(
        'user').order_by('-user__date_joined')


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('-date_joined')
