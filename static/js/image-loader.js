/**
 * METRA Image Loader
 * 
 * Handles image loading, lazy loading, and image enhancements
 * Features:
 * - Lazy loading for improved page performance
 * - Fallback handling for failed images
 * - Image placeholders during loading
 * - Progressive loading effects
 * - Blur-up technique for smooth loading
 */

class ImageLoader {
    /**
     * Initialize the image loader
     */
    constructor() {
        this.options = {
            rootMargin: '0px 0px 200px 0px',
            threshold: 0.1
        };
        this.loadedImages = new Set();
        this.observer = null;
    }

    /**
     * Initialize the intersection observer
     */
    initialize() {
        // Check if IntersectionObserver is supported
        if ('IntersectionObserver' in window) {
            this.observer = new IntersectionObserver(this.onIntersection.bind(this), this.options);
            
            // Find all images with data-src attribute
            const lazyImages = document.querySelectorAll('img[data-src]');
            
            // Observe each image
            lazyImages.forEach(image => {
                if (!this.loadedImages.has(image.src)) {
                    this.observer.observe(image);
                }
            });
        } else {
            // Fallback for browsers that don't support IntersectionObserver
            this.loadImagesImmediately(document.querySelectorAll('img[data-src]'));
        }
    }

    /**
     * Handle intersection changes
     * @param {Array} entries - Intersection observer entries
     */
    onIntersection(entries) {
        entries.forEach(entry => {
            // If the image is visible
            if (entry.isIntersecting) {
                // Stop watching and load the image
                this.observer.unobserve(entry.target);
                this.loadImage(entry.target);
            }
        });
    }

    /**
     * Load an image
     * @param {HTMLImageElement} image - Image to load
     */
    loadImage(image) {
        const src = image.getAttribute('data-src');
        
        if (!src) return;
        
        // Show loading state
        this.showLoading(image);
        
        // Set up loading callback
        image.onload = () => {
            // Remove loading state
            this.hideLoading(image);
            
            // Add loaded class for CSS transitions
            image.classList.add('loaded');
            
            // Store in loaded images set
            this.loadedImages.add(image.src);
            
            // Clean up data attribute
            image.removeAttribute('data-src');
        };
        
        // Set up error callback
        image.onerror = () => {
            // Show error state
            this.showError(image);
            
            // Clean up data attribute
            image.removeAttribute('data-src');
        };
        
        // Set the source to begin loading
        image.src = src;
    }

    /**
     * Load all images immediately (fallback method)
     * @param {NodeList} images - Images to load
     */
    loadImagesImmediately(images) {
        Array.from(images).forEach(image => this.loadImage(image));
    }

    /**
     * Show loading state for an image
     * @param {HTMLImageElement} image - Image element
     */
    showLoading(image) {
        // Apply loading styles
        image.style.opacity = '0.5';
        image.style.transition = 'opacity 0.3s ease';
        
        // Add placeholder color
        image.style.backgroundColor = '#f0f7ff';
    }

    /**
     * Hide loading state for an image
     * @param {HTMLImageElement} image - Image element
     */
    hideLoading(image) {
        // Apply loaded styles
        image.style.opacity = '1';
        image.style.backgroundColor = '';
    }

    /**
     * Show error state for an image
     * @param {HTMLImageElement} image - Image element
     */
    showError(image) {
        // Apply error styles
        image.style.opacity = '1';
        
        // Get image dimensions
        const width = image.width || 100;
        const height = image.height || 100;
        
        // Create error image container
        const errorContainer = document.createElement('div');
        errorContainer.className = 'image-error-placeholder';
        errorContainer.style.width = `${width}px`;
        errorContainer.style.height = `${height}px`;
        errorContainer.style.display = 'flex';
        errorContainer.style.alignItems = 'center';
        errorContainer.style.justifyContent = 'center';
        errorContainer.style.backgroundColor = '#f8f9fa';
        errorContainer.style.border = '1px solid #e9ecef';
        errorContainer.style.borderRadius = '4px';
        
        // Create error content
        const errorContent = document.createElement('div');
        errorContent.className = 'image-error-content text-center p-3';
        errorContent.innerHTML = '<i class="fas fa-image fa-2x text-muted"></i><p class="mt-2 mb-0 small text-muted">Image not available</p>';
        
        // Add to container
        errorContainer.appendChild(errorContent);
        
        // Replace image with error container
        if (image.parentNode) {
            image.parentNode.replaceChild(errorContainer, image);
        }
    }

    /**
     * Refresh the observer for newly added images
     */
    refresh() {
        if (!this.observer) {
            this.initialize();
            return;
        }
        
        // Find all images with data-src attribute that haven't been processed
        const newImages = Array.from(document.querySelectorAll('img[data-src]'))
            .filter(img => !this.loadedImages.has(img.src));
        
        // Observe each new image
        newImages.forEach(image => {
            this.observer.observe(image);
        });
    }
    
    /**
     * Apply progressive image loading technique
     * @param {string} selector - Selector for container with progressive images
     */
    applyProgressiveLoading(selector = '.progressive-image-container') {
        const containers = document.querySelectorAll(selector);
        
        containers.forEach(container => {
            const thumbImg = container.querySelector('.thumb');
            const fullImg = container.querySelector('.full');
            
            if (!thumbImg || !fullImg) return;
            
            // Load thumbnail first
            thumbImg.style.opacity = '1';
            
            // When full image is loaded, show it
            fullImg.onload = () => {
                fullImg.style.opacity = '1';
                thumbImg.style.opacity = '0';
            };
            
            // Start loading full image
            if (fullImg.dataset.src) {
                fullImg.src = fullImg.dataset.src;
                fullImg.removeAttribute('data-src');
            }
        });
    }
    
    /**
     * Apply blur-up technique for smoother loading
     * @param {string} selector - Selector for container with blur-up images
     */
    applyBlurUp(selector = '.blur-up-container') {
        const containers = document.querySelectorAll(selector);
        
        containers.forEach(container => {
            const img = container.querySelector('img');
            
            if (!img) return;
            
            // Add blur filter initially
            img.style.filter = 'blur(10px)';
            img.style.transition = 'filter 0.5s ease';
            
            // When image is loaded, remove blur
            img.onload = () => {
                img.style.filter = 'blur(0)';
            };
            
            // Start loading image if using data-src
            if (img.dataset.src) {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
            }
        });
    }
}

// Create instance and export
window.imageLoader = new ImageLoader();

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.imageLoader.initialize();
    
    // Apply progressive loading to containers if present
    window.imageLoader.applyProgressiveLoading();
    
    // Apply blur-up effect to containers if present
    window.imageLoader.applyBlurUp();
});