from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ProductAnalytics, CustomerRequest, Update
from store.models import Product, Order, OrderItem, Category
from django.core.validators import MinValueValidator
from datetime import datetime

class ProductAnalyticsSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    category = serializers.CharField(source='product.category.name', read_only=True)
    conversion_rate = serializers.SerializerMethodField()
    trend = serializers.SerializerMethodField()
    performance_score = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductAnalytics
        fields = ['id', 'product', 'product_name', 'category', 'views', 
                 'cart_additions', 'purchases', 'conversion_rate', 
                 'trend', 'performance_score', 'last_updated']
    
    def get_conversion_rate(self, obj):
        if obj.views == 0:
            return 0
        return round((obj.purchases / obj.views) * 100, 2)

    def get_trend(self, obj):
        # Compare with previous period
        previous_analytics = ProductAnalytics.objects.filter(
            product=obj.product,
            last_updated__lt=obj.last_updated
        ).order_by('-last_updated').first()

        if not previous_analytics:
            return 'stable'

        current_rate = self.get_conversion_rate(obj)
        previous_rate = self.get_conversion_rate(previous_analytics)
        
        if current_rate > previous_rate * 1.05:  # 5% improvement
            return 'increasing'
        elif current_rate < previous_rate * 0.95:  # 5% decrease
            return 'decreasing'
        return 'stable'

    def get_performance_score(self, obj):
        # Calculate performance score based on multiple metrics
        conversion_weight = 0.4
        views_weight = 0.3
        cart_weight = 0.3
        
        conversion_score = min((self.get_conversion_rate(obj) / 20) * 100, 100)  # Normalize to 100
        views_score = min((obj.views / 1000) * 100, 100)  # Assume 1000 views is excellent
        cart_ratio = (obj.cart_additions / obj.views * 100) if obj.views > 0 else 0
        cart_score = min(cart_ratio * 2, 100)  # Normalize to 100
        
        total_score = (conversion_score * conversion_weight +
                      views_score * views_weight +
                      cart_score * cart_weight)
        
        return round(total_score, 1)

    def validate(self, data):
        if data.get('purchases', 0) > data.get('cart_additions', 0):
            raise serializers.ValidationError(
                "Purchases cannot exceed cart additions"
            )
        return data

class CustomerRequestSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    response_time = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerRequest
        fields = ['id', 'user', 'username', 'user_email', 'request_type', 
                 'subject', 'message', 'status', 'created_at', 'updated_at', 
                 'response_time']
    
    def get_response_time(self, obj):
        if obj.status == 'completed':
            delta = obj.updated_at - obj.created_at
            return round(delta.total_seconds() / 3600, 1)  # hours
        return None

class UpdateSerializer(serializers.ModelSerializer):
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', 
                                               read_only=True)
    
    class Meta:
        model = Update
        fields = ['id', 'title', 'update_type', 'description', 'file', 
                 'version', 'uploaded_by', 'uploaded_by_username', 
                 'created_at', 'is_active']

class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_staff', 
                 'date_joined', 'last_login']
        read_only_fields = ['date_joined', 'last_login']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_staff=True
        )
        return user

class SalesAnalyticsSerializer(serializers.Serializer):
    total_sales = serializers.DecimalField(max_digits=10, decimal_places=2)
    orders_count = serializers.IntegerField()
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    period = serializers.CharField()
    sales_by_category = serializers.DictField()
    top_products = serializers.ListField()

    def validate_total_sales(self, value):
        if value < 0:
            raise serializers.ValidationError("Total sales cannot be negative")
        return value

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    stock = serializers.IntegerField(validators=[MinValueValidator(0)])
    sales_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'category', 'category_name', 'name', 'slug', 'image', 
                 'description', 'price', 'stock', 'available', 'created', 
                 'updated', 'sales_count']
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero")
        return value

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2, 
                                        read_only=True)
    status = serializers.SerializerMethodField()
    days_since_order = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'user_email', 'user_name', 'created', 'updated', 
                 'paid', 'order_items', 'total_cost', 'status', 'days_since_order']
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username

    def get_status(self, obj):
        if obj.paid:
            return "Completed"
        return "Pending Payment"

    def get_days_since_order(self, obj):
        delta = timezone.now() - obj.created
        return delta.days