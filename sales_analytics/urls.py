from rest_framework_nested import routers
from . import views


router = routers.DefaultRouter()

router.register('customers', views.CustomerViewSet, basename='customers-list')
router.register('all-users', views.UserViewSet, basename='users-list')
router.register('salespersons', views.SalesPersonViewSet, basename='salespersons-list')
router.register('branches', views.BranchViewSet, basename='branches-list')
router.register('managers', views.ManagerViewSet, basename='managers-list')
router.register('suppliers', views.SupplierViewSet, basename='suppliers-list')
router.register('product-categories', views.ProductCategoryViewSet, basename='productcategories-list')

salesperson_router = routers.NestedSimpleRouter(router, r'salespersons', lookup='salesperson')
salesperson_router.register(r'branches', views.SalesPersonBranchViewSet, basename='salesperson-branch')


urlpatterns = router.urls + salesperson_router.urls
