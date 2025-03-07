/**
 * METRA Infinite Loader
 * 
 * Handles infinite scrolling and pagination for product listings
 * Features:
 * - Automatic loading of next page on scroll
 * - Loading indicators
 * - Support for URL parameters
 * - History API integration for back button support
 * - Graceful fallback for non-JS users
 */

class InfiniteLoader {
    /**
     * Initialize the infinite loader
     * @param {Object} options - Configuration options
     */
    constructor(options = {}) {
        this.options = {
            containerSelector: '.infinite-container',
            itemSelector: '.infinite-item',
            loaderSelector: '.infinite-loader',
            nextSelector: '.pagination .next',
            paginationSelector: '.pagination',
            threshold: 400,
            history: true,
            ...options
        };
        
        this.container = document.querySelector(this.options.containerSelector);
        this.nextLink = document.querySelector(this.options.nextSelector);
        this.pagination = document.querySelector(this.options.paginationSelector);
        this.loader = document.querySelector(this.options.loaderSelector);
        this.loading = false;
        this.pageCounter = 1;
    }

    /**
     * Initialize infinite scrolling
     */
    initialize() {
        // Only initialize if we have the required elements
        if (!this.container || !this.nextLink) return;
        
        // Create loader if it doesn't exist
        if (!this.loader) {
            this.createLoader();
        }
        
        // Hide pagination as we'll load content dynamically
        if (this.pagination) {
            this.pagination.style.display = 'none';
        }
        
        // Add scroll listener
        window.addEventListener('scroll', this.onScroll.bind(this));
        
        // Initial check in case the page is short
        setTimeout(() => {
            this.checkScroll();
        }, 300);
    }

    /**
     * Scroll event handler
     */
    onScroll() {
        // Debounce the scroll checks
        if (this.scrollTimer) clearTimeout(this.scrollTimer);
        this.scrollTimer = setTimeout(this.checkScroll.bind(this), 100);
    }

    /**
     * Check if we should load more items
     */
    checkScroll() {
        // Don't do anything if we're already loading or there's no next link
        if (this.loading || !this.nextLink) return;
        
        // Get container position
        const containerRect = this.container.getBoundingClientRect();
        const containerBottom = containerRect.bottom;
        const windowHeight = window.innerHeight;
        
        // If the bottom of the container is near or above the bottom of the viewport
        if (containerBottom - windowHeight <= this.options.threshold) {
            this.loadNextPage();
        }
    }

    /**
     * Load the next page of items
     */
    async loadNextPage() {
        this.loading = true;
        this.showLoader();
        
        try {
            // Get the URL of the next page
            const nextUrl = this.nextLink.getAttribute('href');
            
            // Fetch the next page
            const response = await fetch(nextUrl);
            if (!response.ok) {
                throw new Error('Failed to load next page');
            }
            
            const html = await response.text();
            
            // Parse the HTML to get the new items
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            // Get the new items
            const newItems = Array.from(doc.querySelectorAll(this.options.itemSelector));
            
            // Find the next link in the new page
            const newNextLink = doc.querySelector(this.options.nextSelector);
            
            // Add the new items to the container with animation
            this.appendItems(newItems);
            
            // Update the next link if we found it
            if (newNextLink) {
                this.nextLink.setAttribute('href', newNextLink.getAttribute('href'));
            } else {
                // No more pages
                this.nextLink = null;
            }
            
            // Update URL if history is enabled
            if (this.options.history) {
                this.updateHistory(nextUrl);
            }
            
            // Increment page counter
            this.pageCounter++;
            
            // Load images if using our image loader
            if (window.imageLoader) {
                setTimeout(() => {
                    window.imageLoader.refresh();
                }, 100);
            }
            
        } catch (error) {
            console.error('Error loading next page:', error);
            this.showError();
        } finally {
            this.loading = false;
            this.hideLoader();
            
            // Check if we still need to load more (in case the new items are too few)
            setTimeout(() => {
                this.checkScroll();
            }, 500);
        }
    }

    /**
     * Append new items to the container with animation
     * @param {Array} items - New items to append
     */
    appendItems(items) {
        // Create a fragment to hold all new elements
        const fragment = document.createDocumentFragment();
        
        items.forEach(item => {
            // Clone the item and add to fragment
            const clone = item.cloneNode(true);
            
            // Set opacity to 0 for fade-in animation
            clone.style.opacity = '0';
            clone.style.transform = 'translateY(20px)';
            
            fragment.appendChild(clone);
        });
        
        // Append all at once
        this.container.appendChild(fragment);
        
        // Trigger reflow to enable transitions
        this.container.offsetHeight;
        
        // Animate the new items
        const newItems = Array.from(this.container.querySelectorAll(`${this.options.itemSelector}[style*="opacity: 0"]`));
        newItems.forEach((item, index) => {
            setTimeout(() => {
                item.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    /**
     * Create a loader element
     */
    createLoader() {
        this.loader = document.createElement('div');
        this.loader.className = 'infinite-loader text-center my-4';
        this.loader.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Loading more items...</p>
        `;
        this.loader.style.display = 'none';
        this.container.after(this.loader);
    }

    /**
     * Show the loading indicator
     */
    showLoader() {
        if (this.loader) {
            this.loader.style.display = 'block';
        }
    }

    /**
     * Hide the loading indicator
     */
    hideLoader() {
        if (this.loader) {
            this.loader.style.display = 'none';
        }
    }

    /**
     * Show an error message
     */
    showError() {
        const errorMessage = document.createElement('div');
        errorMessage.className = 'alert alert-danger my-3';
        errorMessage.innerHTML = `
            <i class="fas fa-exclamation-circle me-2"></i>
            Failed to load more items. <button class="btn btn-link p-0 ms-2 retry-load">Try again</button>
        `;
        
        // Add retry button handler
        const retryButton = errorMessage.querySelector('.retry-load');
        retryButton.addEventListener('click', (e) => {
            e.preventDefault();
            errorMessage.remove();
            this.loadNextPage();
        });
        
        this.loader.before(errorMessage);
    }

    /**
     * Update the browser history with the new URL
     * @param {string} url - URL to add to history
     */
    updateHistory(url) {
        const title = document.title;
        
        // Update the URL without full page reload
        window.history.pushState({
            page: this.pageCounter,
            path: url
        }, title, url);
    }

    /**
     * Manual trigger to check for loading more items
     * Useful after content change or window resize
     */
    refresh() {
        this.checkScroll();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize infinite loader if there's a container
    const container = document.querySelector('.infinite-container');
    if (container) {
        window.infiniteLoader = new InfiniteLoader();
        window.infiniteLoader.initialize();
    }
    
    // Handle back/forward buttons
    window.addEventListener('popstate', function(event) {
        if (event.state && event.state.path) {
            window.location.href = event.state.path;
        }
    });
});