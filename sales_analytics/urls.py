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
router.register('products', views.ProductViewSet, basename='products-list')
router.register('payment-methods', views.PaymentMethodViewSet, basename='paymentmethods-list')
router.register('cart', views.CartViewSet, basename='cart-list')


salesperson_router = routers.NestedSimpleRouter(router, r'salespersons', lookup='salesperson')
salesperson_router.register(r'branches', views.SalesPersonBranchViewSet, basename='salesperson-branch')

customers_router = routers.NestedSimpleRouter(router, r'customers', lookup='customer')
customers_router.register(r'cart', views.CartViewSet, basename='carts')

urlpatterns = router.urls + salesperson_router.urls + customers_router.urls
