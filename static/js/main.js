/**
 * METRA Main JavaScript
 * 
 * Handles general functionality across the site including:
 * - UI enhancements
 * - Search functionality
 * - Theme toggling
 * - Scroll animations
 * - User experience improvements
 */

class MainApp {
    /**
     * Initialize the main application
     */
    constructor() {
        this.initializeComponents();
    }

    /**
     * Initialize all components
     */
    initializeComponents() {
        this.initializeBackToTop();
        this.initializeProgressBar();
        this.initializeSearch();
        this.initializeMessageDismiss();
        this.initializeThemeToggle();
        this.initializeTooltips();
    }

    /**
     * Initialize back to top button
     */
    initializeBackToTop() {
        const backToTopButton = document.getElementById('backToTop');
        
        if (!backToTopButton) return;
        
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                backToTopButton.classList.add('show');
            } else {
                backToTopButton.classList.remove('show');
            }
        });
        
        backToTopButton.addEventListener('click', (e) => {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    /**
     * Initialize scroll progress bar
     */
    initializeProgressBar() {
        const progressBar = document.querySelector('.progress-bar');
        
        if (!progressBar) return;
        
        window.addEventListener('scroll', () => {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            progressBar.style.width = scrolled + '%';
        });
    }

    /**
     * Initialize search functionality
     */
    initializeSearch() {
        const searchToggle = document.querySelector('.search-toggle');
        const searchOverlay = document.querySelector('.search-overlay');
        const searchClose = document.querySelector('.search-close');
        const searchInput = document.querySelector('.search-input');
        const searchBtn = document.querySelector('.search-btn');
        const searchResults = document.querySelector('.search-results');
        
        // If search overlay doesn't exist, don't continue
        if (!searchOverlay || !searchInput) return;
        
        // Toggle search overlay
        if (searchToggle) {
            searchToggle.addEventListener('click', () => {
                searchOverlay.classList.add('active');
                // Focus on input after overlay animation completes
                setTimeout(() => {
                    searchInput.focus();
                }, 300);
            });
        }
        
        // Close search overlay
        if (searchClose) {
            searchClose.addEventListener('click', () => {
                searchOverlay.classList.remove('active');
            });
        }
        
        // Close search overlay on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && searchOverlay.classList.contains('active')) {
                searchOverlay.classList.remove('active');
            }
        });
        
        // Handle search input and button
        if (searchBtn && searchResults) {
            // Function to perform search
            const performSearch = () => {
                const query = searchInput.value.trim();
                
                if (query.length < 2) {
                    searchResults.innerHTML = '<div class="text-center p-4"><p class="text-muted">Please enter at least 2 characters to search</p></div>';
                    return;
                }
                
                // Show loading state
                searchResults.innerHTML = `
                    <div class="text-center p-4">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-2">Searching for "${query}"...</p>
                    </div>
                `;
                
                // Fetch search results
                fetch(`/search/?q=${encodeURIComponent(query)}`, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.text())
                .then(html => {
                    searchResults.innerHTML = html;
                    
                    // Initialize suggestion buttons
                    document.querySelectorAll('.suggestion-btn').forEach(btn => {
                        btn.addEventListener('click', () => {
                            searchInput.value = btn.dataset.query;
                            performSearch();
                        });
                    });
                })
                .catch(error => {
                    console.error('Error during search:', error);
                    searchResults.innerHTML = '<div class="alert alert-danger">Error performing search. Please try again.</div>';
                });
            };
            
            // Search button click
            searchBtn.addEventListener('click', performSearch);
            
            // Search on Enter key
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    performSearch();
                }
            });
        }
    }

    /**
     * Initialize automatic message dismissal
     */
    initializeMessageDismiss() {
        const messages = document.querySelectorAll('.alert[role="alert"]');
        
        messages.forEach(message => {
            // Auto dismiss messages after 5 seconds
            setTimeout(() => {
                // Use Bootstrap's Alert API if available
                const bsAlert = bootstrap.Alert.getOrCreateInstance(message);
                if (bsAlert) {
                    bsAlert.close();
                } else {
                    // Fallback to manual removal
                    message.classList.remove('show');
                    setTimeout(() => {
                        message.remove();
                    }, 150);
                }
            }, 5000);
        });
    }

    /**
     * Initialize theme toggle functionality
     */
    initializeThemeToggle() {
        // Check for saved theme preference or respect OS preference
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const defaultTheme = savedTheme || (prefersDark ? 'dark' : 'light');
        
        // Apply theme
        this.setTheme(defaultTheme);
        
        // Add theme toggle button if it exists
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                this.setTheme(newTheme);
            });
        }
    }

    /**
     * Set theme on the document
     * @param {string} theme - Theme to set ('light' or 'dark')
     */
    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Update toggle button if it exists
        const themeToggle = document.querySelector('.theme-toggle i');
        if (themeToggle) {
            if (theme === 'dark') {
                themeToggle.classList.replace('fa-moon', 'fa-sun');
            } else {
                themeToggle.classList.replace('fa-sun', 'fa-moon');
            }
        }
    }

    /**
     * Initialize Bootstrap tooltips
     */
    initializeTooltips() {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        if (tooltipTriggerList.length > 0) {
            [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
        }
    }

    /**
     * Initialize AOS (Animate on Scroll)
     */
    initializeAOS() {
        if (typeof AOS !== 'undefined') {
            AOS.init({
                duration: 800,
                once: true
            });
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.mainApp = new MainApp();
    
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            
            // Skip empty hrefs and dropdown toggles
            if (href === '#' || this.hasAttribute('data-bs-toggle')) return;
            
            const target = document.querySelector(href);
            
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Handle external links
    document.querySelectorAll('a[href^="http"]').forEach(link => {
        // Skip links to the current domain
        if (link.hostname === window.location.hostname) return;
        
        // Add target blank and rel attributes for security
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
        
        // Optionally add external link icon
        if (!link.querySelector('.fa-external-link-alt')) {
            const icon = document.createElement('i');
            icon.className = 'fas fa-external-link-alt ms-1 small';
            link.appendChild(icon);
        }
    });
});