/**
 * Cart Manager
 * 
 * Handles cart related functionality such as:
 * - Adding items to cart
 * - Updating cart quantities
 * - Quick add functionality
 * - Cart preview
 */

class CartManager {
    constructor() {
        this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        this.initCartEvents();
        this.initCartPreview();
    }

    /**
     * Initialize cart events
     */
    initCartEvents() {
        // Handle add to cart forms
        document.querySelectorAll('form[data-product-id]').forEach(form => {
            form.addEventListener('submit', this.handleAddToCart.bind(this));
        });

        // Handle quick add buttons
        document.querySelectorAll('.quick-add-btn').forEach(button => {
            button.setAttribute('data-action', 'quick-add');
            button.addEventListener('click', this.handleQuickAdd.bind(this));
        });
    }

    /**
     * Initialize cart preview
     */
    initCartPreview() {
        const cartToggle = document.querySelector('.cart-preview-toggle');
        if (cartToggle) {
            cartToggle.addEventListener('click', this.toggleCartPreview.bind(this));
        }

        // Close cart preview when clicking outside
        document.addEventListener('click', (e) => {
            const cartPreview = document.querySelector('.cart-preview');
            const cartToggle = document.querySelector('.cart-preview-toggle');
            if (cartPreview && cartPreview.classList.contains('show') && 
                !cartPreview.contains(e.target) && 
                !cartToggle?.contains(e.target)) {
                cartPreview.classList.remove('show');
            }
        });
    }

    /**
     * Handle add to cart form submissions
     */
    async handleAddToCart(event) {
        event.preventDefault();
        
        const form = event.target;
        const productId = form.dataset.productId;
        const submitButton = form.querySelector('button[type="submit"]');
        const originalContent = submitButton.innerHTML;
        
        // Show loading state
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Adding...';
        
        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                this.updateCartCounter(data.cart_total);
                this.updateCartPreview(data.cart_html);
                this.showNotification('Product added to cart successfully!', 'success');
            } else {
                this.showNotification(data.error || 'Error adding product to cart', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showNotification('Failed to add product to cart', 'danger');
        } finally {
            // Reset button state
            submitButton.disabled = false;
            submitButton.innerHTML = originalContent;
        }
    }

    /**
     * Handle quick add to cart
     */
    async handleQuickAdd(event) {
        event.preventDefault();
        
        const button = event.currentTarget;
        const productId = button.dataset.productId;
        const originalContent = button.innerHTML;
        
        // Show loading state
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
        
        try {
            const formData = new FormData();
            formData.append('csrfmiddlewaretoken', this.csrfToken);
            formData.append('quantity', 1);
            
            const response = await fetch(`/cart/add/${productId}/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                this.updateCartCounter(data.cart_total);
                this.updateCartPreview(data.cart_html);
                this.showNotification('Product added to cart!', 'success');
            } else {
                this.showNotification(data.error || 'Error adding product to cart', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showNotification('Failed to add product to cart', 'danger');
        } finally {
            // Reset button state
            setTimeout(() => {
                button.disabled = false;
                button.innerHTML = originalContent;
            }, 500);
        }
    }

    /**
     * Toggle cart preview
     */
    toggleCartPreview(event) {
        event.preventDefault();
        const cartPreview = document.querySelector('.cart-preview');
        if (cartPreview) {
            cartPreview.classList.toggle('show');
        }
    }

    /**
     * Update cart counter in navbar
     */
    updateCartCounter(count) {
        const cartCounter = document.querySelector('.cart-counter');
        if (cartCounter) {
            cartCounter.textContent = count;
            
            // Add animation
            cartCounter.classList.add('pulse');
            setTimeout(() => {
                cartCounter.classList.remove('pulse');
            }, 1000);
        }
    }

    /**
     * Update cart preview HTML
     */
    updateCartPreview(cartHtml) {
        const cartPreview = document.querySelector('.cart-preview');
        if (cartPreview) {
            cartPreview.innerHTML = cartHtml;
        }
    }

    /**
     * Show notification
     */
    showNotification(message, type) {
        const toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            console.error('Toast container not found!');
            return;
        }
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Ensure Bootstrap is available
        if (typeof bootstrap !== 'undefined') {
            const bsToast = new bootstrap.Toast(toast, {
                animation: true,
                autohide: true,
                delay: 3000
            });
            
            bsToast.show();
            
            // Remove toast from DOM after hiding
            toast.addEventListener('hidden.bs.toast', () => {
                toast.remove();
            });
        } else {
            // Fallback if Bootstrap JS isn't loaded
            console.warn('Bootstrap not available, using fallback toast implementation');
            toast.classList.add('show');
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => {
                    toast.remove();
                }, 300);
            }, 3000);
        }
    }
}

// Initialize CartManager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.cartManager = new CartManager();
    console.log('CartManager initialized');
});