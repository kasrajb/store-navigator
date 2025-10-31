/**
 * ============================================
 * Store Navigator - JavaScript Functionality
 * Indoor Navigation and Product Finder
 * ============================================
 * 
 * UPDATED: Comprehensive Canadian grocery store categories
 * with drill-down navigation and subcategories
 */

// ============================================
// GROCERY CATEGORY DATA STRUCTURE
// ============================================

const groceryCategories = {
    "Fruits & Vegetables": {
        icon: "🥬",
        subcategories: [
            { name: "Fresh Fruits", icon: "🍎" },
            { name: "Fresh Vegetables", icon: "🥕" },
            { name: "Salads & Greens", icon: "🥗" },
            { name: "Herbs & Spices", icon: "🌿" },
            { name: "Mushrooms", icon: "🍄" }
        ]
    },
    "Dairy & Eggs": {
        icon: "🥛",
        subcategories: [
            { name: "Milk", icon: "🥛" },
            { name: "Cheese", icon: "🧀" },
            { name: "Yogurt", icon: "🥄" },
            { name: "Eggs", icon: "🥚" },
            { name: "Butter & Margarine", icon: "🧈" },
            { name: "Cream & Sour Cream", icon: "🥛" }
        ]
    },
    "Meat & Poultry": {
        icon: "🍗",
        subcategories: [
            { name: "Chicken", icon: "🍗" },
            { name: "Beef", icon: "🥩" },
            { name: "Pork", icon: "🥓" },
            { name: "Turkey", icon: "🦃" },
            { name: "Lamb & Veal", icon: "🍖" },
            { name: "Deli Meat", icon: "🥩" }
        ]
    },
    "Fish & Seafood": {
        icon: "🐟",
        subcategories: [
            { name: "Fresh Fish", icon: "🐟" },
            { name: "Shrimp & Prawns", icon: "🦐" },
            { name: "Shellfish", icon: "🦞" },
            { name: "Smoked Fish", icon: "🐠" },
            { name: "Sushi & Sashimi", icon: "🍣" }
        ]
    },
    "Pantry": {
        icon: "🥫",
        subcategories: [
            { name: "Pasta & Noodles", icon: "🍝" },
            { name: "Rice & Grains", icon: "🍚" },
            { name: "Canned Goods", icon: "🥫" },
            { name: "Sauces & Condiments", icon: "🥫" },
            { name: "Baking Supplies", icon: "🧁" },
            { name: "Oils & Vinegars", icon: "🫒" },
            { name: "Soups & Broths", icon: "🍲" }
        ]
    },
    "Frozen": {
        icon: "🧊",
        subcategories: [
            { name: "Frozen Meals & Entrees", icon: "🍱" },
            { name: "Ice Cream & Desserts", icon: "🍨" },
            { name: "Frozen Vegetables", icon: "🥦" },
            { name: "Frozen Pizza", icon: "🍕" },
            { name: "Frozen Seafood", icon: "🦐" },
            { name: "Frozen Fruits", icon: "🍓" }
        ]
    },
    "Bread & Bakery": {
        icon: "🍞",
        subcategories: [
            { name: "Fresh Bread", icon: "🍞" },
            { name: "Bagels & Muffins", icon: "🥯" },
            { name: "Cakes & Pastries", icon: "🍰" },
            { name: "Tortillas & Wraps", icon: "🌯" },
            { name: "Cookies & Biscuits", icon: "🍪" }
        ]
    },
    "Beverages": {
        icon: "🥤",
        subcategories: [
            { name: "Soft Drinks", icon: "🥤" },
            { name: "Juice", icon: "🧃" },
            { name: "Water", icon: "💧" },
            { name: "Coffee & Tea", icon: "☕" },
            { name: "Sports & Energy Drinks", icon: "⚡" },
            { name: "Plant-Based Milk", icon: "🥥" }
        ]
    },
    "Snacks": {
        icon: "🍿",
        subcategories: [
            { name: "Salty Snacks", icon: "🥨" },
            { name: "Sweet Snacks & Candy", icon: "🍬" },
            { name: "Nuts, Seeds & Fruit", icon: "🥜" },
            { name: "Granola & Protein Bars", icon: "🍫" },
            { name: "Crackers", icon: "🧈" }
        ]
    },
    "Beer & Wine": {
        icon: "🍷",
        subcategories: [
            { name: "Beer", icon: "🍺" },
            { name: "Wine", icon: "🍷" },
            { name: "Spirits", icon: "🥃" },
            { name: "Cider & Coolers", icon: "🍹" },
            { name: "Non-Alcoholic", icon: "🥤" }
        ]
    },
    "Deli & Prepared Meals": {
        icon: "🥪",
        subcategories: [
            { name: "Sandwiches & Wraps", icon: "🥪" },
            { name: "Salads", icon: "🥗" },
            { name: "Hot Meals", icon: "🍱" },
            { name: "Rotisserie Chicken", icon: "🍗" },
            { name: "Party Trays", icon: "🍽️" }
        ]
    },
    "World Cuisine": {
        icon: "🌍",
        subcategories: [
            { name: "Asian Foods", icon: "🍜" },
            { name: "Italian Foods", icon: "🍝" },
            { name: "Mexican Foods", icon: "🌮" },
            { name: "Middle Eastern", icon: "🧆" },
            { name: "Indian Foods", icon: "🍛" }
        ]
    },
    "Vegan & Vegetarian": {
        icon: "🌱",
        subcategories: [
            { name: "Plant-Based Proteins", icon: "🥦" },
            { name: "Meat Alternatives", icon: "🌱" },
            { name: "Dairy Alternatives", icon: "🥥" },
            { name: "Vegan Snacks", icon: "🥜" },
            { name: "Tofu & Tempeh", icon: "🧈" }
        ]
    },
    "Organic Groceries": {
        icon: "🌿",
        subcategories: [
            { name: "Organic Produce", icon: "🥬" },
            { name: "Organic Dairy", icon: "🥛" },
            { name: "Organic Meat", icon: "🍗" },
            { name: "Organic Pantry", icon: "🌾" },
            { name: "Organic Snacks", icon: "🍪" }
        ]
    },
    "Household & Cleaning": {
        icon: "🧹",
        subcategories: [
            { name: "Laundry", icon: "🧺" },
            { name: "Cleaning Supplies", icon: "🧼" },
            { name: "Paper Products", icon: "🧻" },
            { name: "Kitchen Supplies", icon: "🍽️" },
            { name: "Air Fresheners", icon: "🌸" }
        ]
    },
    "Health & Beauty": {
        icon: "💄",
        subcategories: [
            { name: "Skincare", icon: "🧴" },
            { name: "Hair Care", icon: "💇" },
            { name: "Oral Care", icon: "🪥" },
            { name: "Cosmetics", icon: "💄" },
            { name: "Vitamins & Supplements", icon: "💊" },
            { name: "First Aid", icon: "🩹" }
        ]
    },
    "Baby": {
        icon: "👶",
        subcategories: [
            { name: "Baby Food", icon: "🍼" },
            { name: "Diapers & Wipes", icon: "👶" },
            { name: "Baby Care", icon: "🧴" },
            { name: "Baby Formula", icon: "🍼" },
            { name: "Baby Snacks", icon: "🍪" }
        ]
    },
    "Pet Care": {
        icon: "🐾",
        subcategories: [
            { name: "Dog Food", icon: "🐕" },
            { name: "Cat Food", icon: "🐈" },
            { name: "Pet Treats", icon: "🦴" },
            { name: "Pet Supplies", icon: "🐾" },
            { name: "Pet Care Products", icon: "🧼" }
        ]
    }
};

// ============================================
// STATE MANAGEMENT
// ============================================

let currentView = 'main'; // 'main' or 'subcategory'
let currentCategory = null;

// ============================================
// DOM ELEMENTS
// ============================================

const searchInput = document.getElementById('product-search');
const clearButton = document.getElementById('clear-search');
const categoryGrid = document.getElementById('category-grid');
const mainCategoriesSection = document.getElementById('main-categories');
const subcategorySection = document.getElementById('subcategory-section');
const subcategoryGrid = document.getElementById('subcategory-grid');
const subcategoryTitle = document.getElementById('subcategory-title');
const breadcrumbNav = document.getElementById('breadcrumb');
const breadcrumbTrail = document.getElementById('breadcrumb-trail');
const backButton = document.getElementById('back-button');

// ============================================
// INITIALIZATION
// ============================================

/**
 * Initialize the application
 */
function init() {
    console.log('Store Navigator initialized with comprehensive categories');
    console.log('Total categories:', Object.keys(groceryCategories).length);
    
    // Generate main category cards
    generateMainCategories();
    
    // Set up search functionality
    setupSearchFunctionality();
    
    // Set initial focus
    searchInput.focus();
    
    logAnalytics('app_initialized', {
        timestamp: new Date().toISOString(),
        totalCategories: Object.keys(groceryCategories).length
    });
}

// ============================================
// CATEGORY GENERATION
// ============================================

/**
 * Generate and display main category cards
 */
function generateMainCategories() {
    categoryGrid.innerHTML = '';
    
    Object.keys(groceryCategories).forEach((categoryName, index) => {
        const category = groceryCategories[categoryName];
        const card = createCategoryCard(categoryName, category.icon, index);
        categoryGrid.appendChild(card);
    });
    
    console.log('Generated', Object.keys(groceryCategories).length, 'main categories');
}

/**
 * Create a category card element
 */
function createCategoryCard(name, icon, index) {
    const button = document.createElement('button');
    button.className = 'category-card';
    button.setAttribute('data-category', name);
    button.setAttribute('aria-label', `Browse ${name} category`);
    button.style.animationDelay = `${index * 0.05}s`;
    
    const iconSpan = document.createElement('span');
    iconSpan.className = 'category-icon';
    iconSpan.setAttribute('role', 'img');
    iconSpan.setAttribute('aria-label', name);
    iconSpan.textContent = icon;
    
    const nameSpan = document.createElement('span');
    nameSpan.className = 'category-name';
    nameSpan.textContent = name;
    
    button.appendChild(iconSpan);
    button.appendChild(nameSpan);
    
    // Add click event listener
    button.addEventListener('click', () => handleMainCategoryClick(name));
    
    // Keyboard support
    button.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleMainCategoryClick(name);
        }
    });
    
    return button;
}

/**
 * Generate and display subcategory cards
 */
function generateSubcategories(categoryName) {
    subcategoryGrid.innerHTML = '';
    const category = groceryCategories[categoryName];
    
    if (!category || !category.subcategories) {
        console.error('Category not found:', categoryName);
        return;
    }
    
    category.subcategories.forEach((subcategory, index) => {
        const card = createSubcategoryCard(categoryName, subcategory.name, subcategory.icon, index);
        subcategoryGrid.appendChild(card);
    });
    
    console.log('Generated', category.subcategories.length, 'subcategories for', categoryName);
}

/**
 * Create a subcategory card element
 */
function createSubcategoryCard(categoryName, subcategoryName, icon, index) {
    const button = document.createElement('button');
    button.className = 'category-card';
    button.setAttribute('data-category', categoryName);
    button.setAttribute('data-subcategory', subcategoryName);
    button.setAttribute('aria-label', `Browse ${subcategoryName}`);
    button.style.animationDelay = `${index * 0.05}s`;
    
    const iconSpan = document.createElement('span');
    iconSpan.className = 'category-icon';
    iconSpan.setAttribute('role', 'img');
    iconSpan.setAttribute('aria-label', subcategoryName);
    iconSpan.textContent = icon;
    
    const nameSpan = document.createElement('span');
    nameSpan.className = 'category-name';
    nameSpan.textContent = subcategoryName;
    
    button.appendChild(iconSpan);
    button.appendChild(nameSpan);
    
    // Add click event listener
    button.addEventListener('click', () => handleSubcategoryClick(categoryName, subcategoryName, button));
    
    // Keyboard support
    button.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleSubcategoryClick(categoryName, subcategoryName, button);
        }
    });
    
    return button;
}

// ============================================
// NAVIGATION HANDLERS
// ============================================

/**
 * Handle main category click
 */
function handleMainCategoryClick(categoryName) {
    console.log('Main Category:', categoryName);
    
    currentView = 'subcategory';
    currentCategory = categoryName;
    
    // Update breadcrumb
    updateBreadcrumb(['Home', categoryName]);
    
    // Update title
    subcategoryTitle.textContent = categoryName;
    
    // Generate subcategories
    generateSubcategories(categoryName);
    
    // Switch views with animation
    switchView('subcategory');
    
    // Haptic feedback
    if ('vibrate' in navigator) {
        navigator.vibrate(50);
    }
    
    logAnalytics('category_selected', { category: categoryName });
}

/**
 * Handle subcategory click
 */
function handleSubcategoryClick(categoryName, subcategoryName, element) {
    console.log('Selected:', categoryName, '>', subcategoryName);
    
    // Remove active class from all subcategory cards
    document.querySelectorAll('#subcategory-grid .category-card').forEach(card => {
        card.classList.remove('active');
    });
    
    // Add active class to clicked card
    element.classList.add('active');
    
    // Haptic feedback
    if ('vibrate' in navigator) {
        navigator.vibrate(30);
    }
    
    logAnalytics('subcategory_selected', {
        category: categoryName,
        subcategory: subcategoryName
    });
    
    // TODO: Display products for this subcategory (future implementation)
}

/**
 * Handle back button click
 */
function handleBackClick() {
    console.log('Navigating back to main categories');
    
    currentView = 'main';
    currentCategory = null;
    
    switchView('main');
    
    logAnalytics('navigation_back', { from: 'subcategory', to: 'main' });
}

// Set up back button listener
backButton.addEventListener('click', handleBackClick);

// ============================================
// VIEW MANAGEMENT
// ============================================

/**
 * Switch between main categories and subcategories view
 */
function switchView(view) {
    if (view === 'subcategory') {
        // Hide main categories
        mainCategoriesSection.classList.add('fade-out');
        
        setTimeout(() => {
            mainCategoriesSection.style.display = 'none';
            mainCategoriesSection.classList.remove('fade-out');
            
            // Show subcategories
            subcategorySection.style.display = 'block';
            subcategorySection.classList.add('fade-in');
            
            // Show breadcrumb
            breadcrumbNav.style.display = 'block';
            breadcrumbNav.classList.add('fade-in');
            
            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }, 200);
        
    } else if (view === 'main') {
        // Hide subcategories
        subcategorySection.classList.add('fade-out');
        breadcrumbNav.classList.add('fade-out');
        
        setTimeout(() => {
            subcategorySection.style.display = 'none';
            subcategorySection.classList.remove('fade-out');
            
            breadcrumbNav.style.display = 'none';
            breadcrumbNav.classList.remove('fade-out');
            
            // Show main categories
            mainCategoriesSection.style.display = 'block';
            mainCategoriesSection.classList.add('fade-in');
            
            // Update breadcrumb
            updateBreadcrumb(['Home']);
            
            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }, 200);
    }
}

/**
 * Update breadcrumb trail
 */
function updateBreadcrumb(items) {
    breadcrumbTrail.innerHTML = '';
    
    items.forEach((item, index) => {
        const span = document.createElement('span');
        span.className = 'breadcrumb-item';
        if (index === items.length - 1) {
            span.classList.add('active');
        }
        span.textContent = item;
        breadcrumbTrail.appendChild(span);
    });
}

// ============================================
// SEARCH FUNCTIONALITY
// ============================================

/**
 * Set up search bar functionality
 */
function setupSearchFunctionality() {
    // Search input handler
    searchInput.addEventListener('input', function(e) {
        const searchValue = e.target.value;
        
        // Toggle clear button visibility
        if (searchValue.trim().length > 0) {
            clearButton.style.display = 'flex';
        } else {
            clearButton.style.display = 'none';
        }
        
        // Log search query
        if (searchValue.trim().length > 2) {
            console.log('Search query:', searchValue);
        }
    });
    
    // Clear button handler
    clearButton.addEventListener('click', function() {
        searchInput.value = '';
        clearButton.style.display = 'none';
        searchInput.focus();
        console.log('Search cleared');
    });
    
    // Enter key handler
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const searchValue = searchInput.value.trim();
            if (searchValue.length > 0) {
                handleSearch(searchValue);
            }
        }
    });
}

/**
 * Process search query
 */
function handleSearch(query) {
    console.log('Executing search for:', query);
    logAnalytics('search_executed', { query: query });
    // TODO: Implement actual search functionality
}

// ============================================
// KEYBOARD NAVIGATION
// ============================================

/**
 * Enable arrow key navigation between cards
 */
document.addEventListener('keydown', function(e) {
    const focusedElement = document.activeElement;
    const isCategoryCard = focusedElement.classList.contains('category-card');
    
    if (!isCategoryCard) return;
    
    const currentGrid = currentView === 'main' ? categoryGrid : subcategoryGrid;
    const cards = Array.from(currentGrid.querySelectorAll('.category-card'));
    const currentIndex = cards.indexOf(focusedElement);
    let nextIndex = currentIndex;
    
    const columnsPerRow = window.innerWidth >= 768 ? 4 : window.innerWidth >= 640 ? 3 : 2;
    
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
            nextIndex = Math.min(currentIndex + columnsPerRow, cards.length - 1);
            break;
        case 'ArrowUp':
            e.preventDefault();
            nextIndex = Math.max(currentIndex - columnsPerRow, 0);
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
 * Log analytics events
 */
function logAnalytics(eventType, data) {
    console.log('Analytics:', eventType, data);
    // TODO: Implement actual analytics tracking
}

/**
 * Debounce function for search input
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

// ============================================
// RUN ON LOAD
// ============================================

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
