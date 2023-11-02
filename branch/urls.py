from rest_framework import routers
from . import views


router = routers.DefaultRouter()

router.register('customers', views.CustomerViewSet, basename='customer-list')
router.register('all-users', views.UserViewSet, basename='users-list')

urlpatterns = router.urls
