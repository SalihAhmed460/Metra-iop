from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import ProductAnalytics, CustomerRequest, Update
from .serializers import (ProductAnalyticsSerializer, CustomerRequestSerializer,
                        UpdateSerializer, AdminUserSerializer, SalesAnalyticsSerializer, 
                        CategorySerializer, ProductSerializer, OrderSerializer)
from store.models import Order, Product, Category, OrderItem

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'id']

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get all products in a category"""
        category = self.get_object()
        products = category.products.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'price', 'stock', 'created']

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__id=category)
        return queryset

    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """Update product stock level"""
        product = self.get_object()
        try:
            new_stock = int(request.data.get('stock', 0))
            if new_stock < 0:
                return Response(
                    {'error': 'Stock cannot be negative'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            product.stock = new_stock
            product.save()
            return Response({'status': 'stock updated'})
        except ValueError:
            return Response(
                {'error': 'Invalid stock value'},
                status=status.HTTP_400_BAD_REQUEST
            )

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id', 'user__username', 'user__email']
    ordering_fields = ['created', 'updated', 'paid']

    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """Mark an order as paid"""
        order = self.get_object()
        order.paid = True
        order.save()
        return Response({'status': 'order marked as paid'})

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status', None)
        if status == 'paid':
            queryset = queryset.filter(paid=True)
        elif status == 'unpaid':
            queryset = queryset.filter(paid=False)
        return queryset

class ProductAnalyticsViewSet(viewsets.ModelViewSet):
    queryset = ProductAnalytics.objects.all()
    serializer_class = ProductAnalyticsSerializer
    permission_classes = [permissions.IsAdminUser]

class CustomerRequestViewSet(viewsets.ModelViewSet):
    queryset = CustomerRequest.objects.all()
    serializer_class = CustomerRequestSerializer
    permission_classes = [permissions.IsAdminUser]

class UpdateViewSet(viewsets.ModelViewSet):
    queryset = Update.objects.all()
    serializer_class = UpdateSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_sales_analytics(request):
    """Get sales analytics with caching"""
    days = int(request.GET.get('days', 30))
    cache_key = f'sales_analytics_{days}'
    
    # Try to get cached data
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)
    
    start_date = timezone.now() - timedelta(days=days)
    orders = Order.objects.filter(created__gte=start_date, paid=True)
    order_items = OrderItem.objects.filter(order__in=orders)
    
    total_sales = order_items.aggregate(total=Sum('price'))['total'] or 0
    orders_count = orders.count()
    average_order_value = total_sales / orders_count if orders_count > 0 else 0
    
    # Get sales by category
    sales_by_category = {}
    categories = Category.objects.annotate(
        total_sales=Sum('products__order_items__price', 
                       filter=Q(products__order_items__order__in=orders))
    )
    for category in categories:
        sales_by_category[category.name] = category.total_sales or 0
    
    # Get top products
    top_products = Product.objects.filter(
        order_items__order__in=orders
    ).annotate(
        total_sales=Count('order_items'),
        revenue=Sum('order_items__price')
    ).order_by('-revenue')[:5]
    
    data = {
        'total_sales': total_sales,
        'orders_count': orders_count,
        'average_order_value': average_order_value,
        'period': f'Last {days} days',
        'sales_by_category': sales_by_category,
        'top_products': [
            {
                'name': p.name,
                'sales': p.total_sales,
                'revenue': p.revenue
            }
            for p in top_products
        ]
    }
    
    # Cache the data for 1 hour
    cache.set(cache_key, data, 3600)
    
    serializer = SalesAnalyticsSerializer(data)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_admin(request):
    """Register a new admin user with validation"""
    serializer = AdminUserSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = serializer.save()
            return Response(
                {
                    'message': 'Admin user created successfully',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    }
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(
        {'error': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )