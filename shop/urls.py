
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, OrderViewSet, RegisterView, MyTokenObtainPairView, AdminProductViewSet, AdminOrderViewSet, admin_profile
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"orders", OrderViewSet, basename="order")

admin_router = DefaultRouter()
admin_router.register(r"products", AdminProductViewSet, basename="admin-products")
admin_router.register(r"orders", AdminOrderViewSet, basename="admin-orders")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
    path("admin/", include(admin_router.urls)),
    path("admin/profile/", admin_profile, name="admin-profile"),
]
