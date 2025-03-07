from django.db import models
from django.contrib.auth.models import User
from store.models import Product, Order

class ProductAnalytics(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    views = models.IntegerField(default=0)
    cart_additions = models.IntegerField(default=0)
    purchases = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Product Analytics'

    def __str__(self):
        return f'Analytics for {self.product.name}'

class CustomerRequest(models.Model):
    REQUEST_TYPES = (
        ('support', 'Support'),
        ('return', 'Return Request'),
        ('inquiry', 'Product Inquiry'),
        ('complaint', 'Complaint'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.request_type} - {self.subject}'

class Update(models.Model):
    UPDATE_TYPES = (
        ('product', 'Product Update'),
        ('system', 'System Update'),
        ('security', 'Security Update'),
    )

    title = models.CharField(max_length=200)
    update_type = models.CharField(max_length=20, choices=UPDATE_TYPES)
    description = models.TextField()
    file = models.FileField(upload_to='updates/')
    version = models.CharField(max_length=50)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.update_type} - {self.title} (v{self.version})'