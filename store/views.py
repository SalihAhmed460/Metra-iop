from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.db.models import Q, Count, Avg
from django.core.cache import cache
from django.utils.text import slugify
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Category, Product, Review, Order
from .cart import Cart
from .throttles import SearchRateThrottle
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from functools import reduce
from operator import or_
import re

def home(request):
    """Homepage view showcasing featured products and categories"""
    products = Product.objects.filter(available=True)[:8]  # Get top 8 products
    categories = Category.objects.all()
    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
        'section': 'home'
    })

def product_list(request, category_slug=None):
    """View to list all products or products by category with AJAX support"""
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    # Handle search query
    search_query = request.GET.get('search', '')
    if search_query:
        # Split the search query into terms
        terms = re.findall(r'\w+', search_query.lower())
        
        # Create queries for each term
        queries = [
            Q(name__icontains=term) |
            Q(description__icontains=term) |
            Q(category__name__icontains=term)
            for term in terms
        ]
        
        # Combine queries and search
        if queries:
            products = products.filter(reduce(or_, queries))
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Handle filters and sorting
    sort = request.GET.get('sort', '')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created')
    
    # Pagination with 12 products per page
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'has_more': False})
        products = paginator.page(paginator.num_pages)

    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'search_query': search_query
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product_list_html = render_to_string(
            'store/includes/product_list.html',
            context,
            request=request
        )
        return JsonResponse({
            'html': product_list_html,
            'has_more': products.has_next()
        })

    return render(request, 'store/product_list.html', context)

def product_detail(request, slug):
    """View to show product details"""
    product = get_object_or_404(Product, slug=slug, available=True)
    
    # Handle review submission
    if request.method == 'POST' and 'action' in request.GET and request.GET['action'] == 'review':
        if not request.user.is_authenticated:
            messages.warning(request, "You need to be logged in to leave a review.")
            return redirect('users:login')
        
        rating = int(request.POST.get('rating', 0))
        comment = request.POST.get('comment', '')
        
        if rating < 1 or rating > 5:
            messages.error(request, "Please provide a rating between 1 and 5 stars.")
        elif not comment:
            messages.error(request, "Please provide a review comment.")
        else:
            # Check if user has already reviewed this product
            existing_review = Review.objects.filter(product=product, user=request.user).first()
            if existing_review:
                # Update existing review
                existing_review.rating = rating
                existing_review.comment = comment
                existing_review.save()
                messages.success(request, "Your review has been updated!")
            else:
                # Create new review
                Review.objects.create(
                    product=product,
                    user=request.user,
                    rating=rating,
                    comment=comment
                )
                messages.success(request, "Thank you for your review!")
            
            # Update product average rating
            avg_rating = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
            product.average_rating = avg_rating or 0
            product.save()
    
    # Get related products from same category
    related_products = Product.objects.filter(category=product.category, available=True).exclude(id=product.id)[:4]
    
    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products
    })

@require_POST
@csrf_protect
def cart_add(request, product_id):
    """Add items to cart with AJAX support"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > product.stock:
        return JsonResponse({
            'error': 'Not enough stock available'
        }, status=400)
    
    cart.add(product=product, quantity=quantity)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_html = render_to_string(
            'store/includes/cart_preview.html',
            {'cart': cart},
            request=request
        )
        return JsonResponse({
            'cart_html': cart_html,
            'cart_total': len(cart),
            'success': True,
            'message': f'{product.name} added to cart'
        })
    
    return redirect('store:cart_detail')

@require_POST
@csrf_protect
def cart_update(request, product_id):
    """Update cart item quantity with AJAX support"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > product.stock:
        return JsonResponse({
            'error': 'Not enough stock available'
        }, status=400)
    
    cart.add(product=product, quantity=quantity, update_quantity=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_html = render_to_string(
            'store/includes/cart_preview.html',
            {'cart': cart},
            request=request
        )
        return JsonResponse({
            'cart_html': cart_html,
            'cart_total': len(cart),
            'item_total': cart.get_item_total(product),
            'cart_total_price': cart.get_total_price()
        })
    
    return redirect('store:cart_detail')

@require_POST
@csrf_protect
def cart_remove(request, product_id):
    """Remove items from cart with AJAX support"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_html = render_to_string(
            'store/includes/cart_preview.html',
            {'cart': cart},
            request=request
        )
        return JsonResponse({
            'cart_html': cart_html,
            'cart_total': len(cart),
            'cart_total_price': cart.get_total_price(),
            'success': True,
            'message': f'{product.name} removed from cart'
        })
    
    return redirect('store:cart_detail')

@require_POST
def clear_cart(request):
    """Clear all items from cart"""
    cart = Cart(request)
    cart.clear()
    messages.success(request, "Your cart has been cleared.")
    return redirect('store:cart_detail')

@require_POST
def apply_promo(request):
    """Apply promo code to cart"""
    cart = Cart(request)
    code = request.POST.get('code', '').strip().upper()
    
    # For now, just a simple demo promo code
    if code == 'WELCOME10':
        # Apply 10% discount
        if not cart.has_discount():
            cart.apply_discount(10)
            messages.success(request, "Promo code WELCOME10 applied successfully. You get 10% off!")
        else:
            messages.info(request, "A discount is already applied to your cart.")
    elif code == 'FREESHIP':
        # Free shipping promo
        if not cart.has_free_shipping():
            cart.apply_free_shipping()
            messages.success(request, "Promo code FREESHIP applied successfully. Free shipping!")
        else:
            messages.info(request, "Free shipping is already applied to your cart.")
    else:
        messages.error(request, "Invalid promo code. Please try again.")
    
    return redirect('store:cart_detail')

def checkout(request):
    """Checkout process view"""
    cart = Cart(request)
    
    if not cart.items:
        messages.warning(request, "Your cart is empty. Please add items before checkout.")
        return redirect('store:product_list')
    
    # If user not logged in, redirect to login with next parameter
    if not request.user.is_authenticated:
        messages.info(request, "Please log in to continue with checkout.")
        return redirect('users:login')
    
    # Process checkout form if submitted
    if request.method == 'POST':
        # Process the order here (simplified for now)
        new_order = Order.objects.create(
            user=request.user,
            shipping_address=request.POST.get('shipping_address', ''),
            total_amount=cart.get_total_price(),
            status='pending'
        )
        
        # Create order items from cart
        for item in cart.items:
            new_order.items.create(
                product=item['product'],
                price=item['price'],
                quantity=item['quantity']
            )
        
        # Clear cart after successful order
        cart.clear()
        
        # Show success message and redirect to order confirmation
        messages.success(request, "Your order has been placed successfully!")
        return redirect('store:order_confirmation', order_id=new_order.id)
    
    return render(request, 'store/checkout.html', {
        'cart': cart,
        'tax_rate': 7.5,  # Could be dynamic based on location
    })

def order_confirmation(request, order_id):
    """Order confirmation page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    return render(request, 'store/order_confirmation.html', {
        'order': order
    })

@login_required
def my_orders(request):
    """View for users to see their order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'store/my_orders.html', {
        'orders': orders
    })

def cart_detail(request):
    """Cart detail view"""
    cart = Cart(request)
    return render(request, 'store/cart_detail.html', {'cart': cart})

def get_cart_preview(request):
    """Get cart preview HTML for AJAX requests"""
    cart = Cart(request)
    cart_html = render_to_string(
        'store/includes/cart_preview.html',
        {'cart': cart},
        request=request
    )
    return JsonResponse({'cart_html': cart_html})

def search_products(request):
    """API endpoint for live product search with suggestions"""
    query = request.GET.get('q', '').strip()
    if len(query) >= 2:
        # Try to get cached results first
        cache_key = f'search_results_{slugify(query)}'
        results = cache.get(cache_key)
        
        if not results:
            # Split query into terms
            terms = re.findall(r'\w+', query.lower())
            
            # Base query - look for matches in name, description, and category
            queries = [
                Q(name__icontains=term) |
                Q(description__icontains=term) |
                Q(category__name__icontains=term)
                for term in terms
            ]
            
            # Combine queries and filter available products
            products = Product.objects.filter(
                reduce(or_, queries)
            ).filter(
                available=True
            ).annotate(
                relevance=Count('id')  # Add relevance scoring
            ).order_by('-relevance')[:8]
            
            results = [{
                'id': p.id,
                'name': p.name,
                'price': str(p.price),
                'image': p.image.url if p.image else None,
                'url': p.get_absolute_url(),
                'category': p.category.name,
                'stock': p.stock,
                'description_preview': p.description[:100] + '...' if len(p.description) > 100 else p.description
            } for p in products]
            
            # Cache results for 15 minutes
            cache.set(cache_key, results, 900)
            
            # Store search term for suggestions
            search_terms = cache.get('popular_searches', [])
            if query.lower() not in search_terms:
                search_terms.append(query.lower())
                search_terms = search_terms[-10:]  # Keep only last 10 searches
                cache.set('popular_searches', search_terms, 86400)  # Store for 24 hours
        
        return JsonResponse({
            'results': results,
            'suggestions': get_search_suggestions(query)
        })
    return JsonResponse({'results': [], 'suggestions': []})

def get_search_suggestions(query):
    """Get search suggestions based on popular searches and available categories"""
    suggestions = []
    
    # Get popular searches
    popular_searches = cache.get('popular_searches', [])
    if popular_searches:
        matching_searches = [s for s in popular_searches if query.lower() in s]
        suggestions.extend(matching_searches[:3])
    
    # Add category suggestions
    category_suggestions = Category.objects.filter(
        name__icontains=query
    ).values_list('name', flat=True)[:2]
    suggestions.extend([f'Category: {cat}' for cat in category_suggestions])
    
    return suggestions[:5]  # Return top 5 suggestions
