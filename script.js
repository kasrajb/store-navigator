/**
 * ============================================
 * Store Navigator - JavaScript Functionality
 * Indoor Navigation and Product Finder
 * ============================================
 * 
 * This script handles:
 * - Search input functionality
 * - Clear button visibility and action
 * - Category selection with visual feedback
 * - Keyboard navigation support
 * - Accessibility features
 */

// ============================================
// DOM ELEMENTS
// ============================================

const searchInput = document.getElementById('product-search');
const clearButton = document.getElementById('clear-search');
const categoryCards = document.querySelectorAll('.category-card');

// ============================================
// SEARCH FUNCTIONALITY
// ============================================

/**
 * Handle search input changes
 * Shows/hides clear button based on input content
 */
searchInput.addEventListener('input', function(e) {
    const searchValue = e.target.value;
    
    // Toggle clear button visibility
    if (searchValue.trim().length > 0) {
        clearButton.style.display = 'flex';
    } else {
        clearButton.style.display = 'none';
    }
    
    // Log search query (will be used for actual search functionality later)
    if (searchValue.trim().length > 2) {
        console.log('Search query:', searchValue);
    }
});

/**
 * Handle clear button click
 * Clears the search input and refocuses
 */
clearButton.addEventListener('click', function() {
    searchInput.value = '';
    clearButton.style.display = 'none';
    searchInput.focus();
    console.log('Search cleared');
});

/**
 * Handle Enter key in search input
 * Triggers search action
 */
searchInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        const searchValue = searchInput.value.trim();
        if (searchValue.length > 0) {
            handleSearch(searchValue);
        }
    }
});

/**
 * Process search query
 * @param {string} query - The search query
 */
function handleSearch(query) {
    console.log('Executing search for:', query);
    // TODO: Implement actual search functionality
    // This will be expanded in future iterations to:
    // - Query product database
    // - Display search results
    // - Initiate navigation to product location
}

// ============================================
// CATEGORY SELECTION FUNCTIONALITY
// ============================================

/**
 * Handle category card click
 * Logs selection and provides visual feedback
 */
categoryCards.forEach(card => {
    card.addEventListener('click', function() {
        const category = this.getAttribute('data-category');
        handleCategorySelection(category, this);
    });
    
    // Keyboard support (Enter and Space)
    card.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            const category = this.getAttribute('data-category');
            handleCategorySelection(category, this);
        }
    });
});

/**
 * Process category selection
 * @param {string} category - The selected category name
 * @param {HTMLElement} cardElement - The clicked card element
 */
function handleCategorySelection(category, cardElement) {
    console.log('Category selected:', category);
    
    // Remove active class from all cards
    categoryCards.forEach(card => card.classList.remove('active'));
    
    // Add active class to selected card
    cardElement.classList.add('active');
    
    // Provide haptic feedback on supported devices
    if ('vibrate' in navigator) {
        navigator.vibrate(50);
    }
    
    // TODO: Implement category-specific functionality
    // This will be expanded in future iterations to:
    // - Display products in the selected category
    // - Show category-specific navigation options
    // - Filter products by category
    
    // Visual feedback with animation
    animateCardSelection(cardElement);
}

/**
 * Animate card selection for better user feedback
 * @param {HTMLElement} card - The card element to animate
 */
function animateCardSelection(card) {
    // Add a temporary pulse effect
    card.style.transform = 'scale(0.95)';
    setTimeout(() => {
        card.style.transform = '';
    }, 150);
}

// ============================================
// ACCESSIBILITY ENHANCEMENTS
// ============================================

/**
 * Announce to screen readers when category is selected
 * @param {string} category - The selected category
 */
function announceToScreenReader(category) {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.className = 'visually-hidden';
    announcement.textContent = `${category} category selected`;
    document.body.appendChild(announcement);
    
    // Remove announcement after it's been read
    setTimeout(() => {
        document.body.removeChild(announcement);
    }, 1000);
}

// ============================================
// KEYBOARD NAVIGATION
// ============================================

/**
 * Enable arrow key navigation between category cards
 */
document.addEventListener('keydown', function(e) {
    // Only handle arrow keys when a category card is focused
    const focusedElement = document.activeElement;
    const isCategoryCard = focusedElement.classList.contains('category-card');
    
    if (!isCategoryCard) return;
    
    const cards = Array.from(categoryCards);
    const currentIndex = cards.indexOf(focusedElement);
    let nextIndex = currentIndex;
    
    switch(e.key) {
        case 'ArrowRight':
            e.preventDefault();
            nextIndex = (currentIndex + 1) % cards.length;
            break;
        case 'ArrowLeft':
            e.preventDefault();
            nextIndex = (currentIndex - 1 + cards.length) % cards.length;
            break;
        case 'ArrowDown':
            e.preventDefault();
            // Move down in grid (2 columns on mobile)
            nextIndex = Math.min(currentIndex + 2, cards.length - 1);
            break;
        case 'ArrowUp':
            e.preventDefault();
            // Move up in grid (2 columns on mobile)
            nextIndex = Math.max(currentIndex - 2, 0);
            break;
    }
    
    if (nextIndex !== currentIndex) {
        cards[nextIndex].focus();
    }
});

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Debounce function for search input
 * Reduces the frequency of function calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Log user interactions for analytics (placeholder)
 */
function logAnalytics(eventType, data) {
    console.log('Analytics:', eventType, data);
    // TODO: Implement actual analytics tracking
}

// ============================================
// INITIALIZATION
// ============================================

/**
 * Initialize the application
 */
function init() {
    console.log('Store Navigator initialized');
    console.log('Categories available:', Array.from(categoryCards).map(card => card.getAttribute('data-category')));
    
    // Set initial focus on search input for better UX
    searchInput.focus();
    
    // Log initialization
    logAnalytics('app_initialized', {
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent
    });
}

// Run initialization when DOM is fully loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// ============================================
// FUTURE ENHANCEMENTS (Commented for reference)
// ============================================

/**
 * TODO: Product Search Implementation
 * - Integrate with product database/API
 * - Display search results in a list
 * - Highlight matching products
 * - Show product locations on store map
 */

/**
 * TODO: Category Browsing
 * - Load products for selected category
 * - Display category-specific products
 * - Enable filtering and sorting
 * - Show aisle/location information
 */

/**
 * TODO: Navigation Features
 * - Integrate with Visual SLAM system
 * - Display turn-by-turn directions
 * - Show real-time position on map
 * - Provide multimodal feedback (visual, audio, haptic)
 */

/**
 * TODO: Offline Support
 * - Implement service worker
 * - Cache product data
 * - Enable offline navigation
 */

/**
 * TODO: User Preferences
 * - Save search history
 * - Remember favorite categories
 * - Store accessibility preferences
 * - Customize interface theme
 */
