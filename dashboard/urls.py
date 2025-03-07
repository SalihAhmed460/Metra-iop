from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'analytics', views.ProductAnalyticsViewSet)
router.register(r'requests', views.CustomerRequestViewSet)
router.register(r'updates', views.UpdateViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('sales/', views.get_sales_analytics, name='sales-analytics'),
    path('register-admin/', views.register_admin, name='register-admin'),
]