from rest_framework import routers
from . import views


router = routers.DefaultRouter()

router.register('customers', views.CustomerViewSet, basename='customers-list')
router.register('all-users', views.UserViewSet, basename='users-list')
router.register('salespersons', views.SalesPersonViewSet, basename='salespersons-list')

urlpatterns = router.urls
