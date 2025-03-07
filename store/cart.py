from decimal import Decimal
from django.conf import settings
from .models import Product

class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        # Initialize discount and shipping flags
        self.discount_percentage = self.session.get('discount_percentage', 0)
        self.free_shipping = self.session.get('free_shipping', False)

    def add(self, product, quantity=1, update_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # mark the session as "modified" to make sure it gets saved
        self.session.modified = True
        # Save discount and shipping flags to session
        self.session['discount_percentage'] = self.discount_percentage
        self.session['free_shipping'] = self.free_shipping

    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database.
        """
        product_ids = self.cart.keys()
        # get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Calculate total cost of items in cart.
        """
        subtotal = sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
        
        # Apply discount if any
        if self.discount_percentage > 0:
            discount = (subtotal * Decimal(self.discount_percentage)) / 100
            subtotal -= discount
        
        # Add shipping if required
        if not self.free_shipping and subtotal < 50:
            subtotal += Decimal('5.00')  # $5 shipping
        
        return subtotal

    def clear(self):
        """
        Remove cart from session.
        """
        del self.session[settings.CART_SESSION_ID]
        if 'discount_percentage' in self.session:
            del self.session['discount_percentage']
        if 'free_shipping' in self.session:
            del self.session['free_shipping']
        self.discount_percentage = 0
        self.free_shipping = False
        self.save()
    
    # Additional cart methods referenced in views.py
    
    def get_item_total(self, product):
        """
        Get the total cost for a specific product in the cart
        """
        product_id = str(product.id)
        if product_id in self.cart:
            return Decimal(self.cart[product_id]['price']) * self.cart[product_id]['quantity']
        return 0
    
    def has_discount(self):
        """
        Check if the cart has a discount applied
        """
        return self.discount_percentage > 0
    
    def apply_discount(self, percentage):
        """
        Apply a percentage discount to the cart
        """
        self.discount_percentage = percentage
        self.save()
    
    def has_free_shipping(self):
        """
        Check if the cart has free shipping
        """
        return self.free_shipping or self.get_subtotal() >= 50
    
    def apply_free_shipping(self):
        """
        Apply free shipping to the cart
        """
        self.free_shipping = True
        self.save()
    
    def get_subtotal(self):
        """
        Calculate subtotal before shipping and discounts
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
    
    def get_tax(self):
        """
        Calculate tax (7.5% by default)
        """
        tax_rate = Decimal('0.075')  # 7.5%
        return (self.get_subtotal() * tax_rate).quantize(Decimal('0.01'))
    
    def get_shipping_cost(self):
        """
        Calculate shipping cost
        """
        if self.has_free_shipping():
            return Decimal('0.00')
        return Decimal('5.00')  # $5 shipping fee
    
    @property
    def tax(self):
        """
        Property to access tax amount
        """
        return self.get_tax()
    
    @property
    def subtotal(self):
        """
        Property to access subtotal
        """
        return self.get_subtotal()
    
    @property
    def total(self):
        """
        Property to access total amount including tax and shipping
        """
        return self.get_total_price() + self.get_tax()
    
    @property
    def items(self):
        """
        Get all cart items as a list
        """
        return list(self.__iter__())
    
    @property
    def total_items(self):
        """
        Get total number of items in cart
        """
        return self.__len__()