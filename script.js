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
// NAVIGATION DATA
// ============================================

const navigationData = {
    currentLocation: "Entrance",
    aisles: [
        { number: 7, label: "Aisle 7" },
        { number: 6, label: "Aisle 6" },
        { number: 5, label: "Aisle 5" },
        { number: 4, label: "Aisle 4" },
        { number: 3, label: "Aisle 3" },
        { number: 2, label: "Aisle 2" },
        { number: 1, label: "Aisle 1" },
        { number: 0, label: "Entrance" }
    ],
    directions: [
        { step: 1, action: "Walk straight ahead", distance: "30m", icon: "🚶" },
        { step: 2, action: "Turn right at Aisle 5", distance: "", icon: "↪️" },
        { step: 3, action: "Continue straight", distance: "15m", icon: "🚶" },
        { step: 4, action: "Your product is on the right side, Section C", distance: "", icon: "🎯" }
    ]
};

// ============================================
// STATE MANAGEMENT
// ============================================

let currentView = 'main'; // 'main', 'subcategory', or 'navigation'
let currentCategory = null;
let currentSubcategory = null;

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
const navigationSection = document.getElementById('navigation-section');
const navBackButton = document.getElementById('nav-back-button');
const navProductName = document.getElementById('nav-product-name');
const currentLocationText = document.getElementById('current-location-text');
const destinationText = document.getElementById('destination-text');
const storeMap = document.getElementById('store-map');
const directionsList = document.getElementById('directions-list');

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
    console.log('Navigating to:', subcategoryName);
    
    currentView = 'navigation';
    currentSubcategory = subcategoryName;
    
    // Generate navigation screen
    generateNavigationScreen(categoryName, subcategoryName);
    
    // Switch to navigation view
    switchView('navigation');
    
    // Haptic feedback
    if ('vibrate' in navigator) {
        navigator.vibrate(30);
    }
    
    logAnalytics('navigation_started', {
        category: categoryName,
        subcategory: subcategoryName
    });
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

/**
 * Handle navigation back button click
 */
function handleNavBackClick() {
    console.log('Navigating back to subcategories');
    
    currentView = 'subcategory';
    currentSubcategory = null;
    
    switchView('subcategory');
    
    logAnalytics('navigation_back', { from: 'navigation', to: 'subcategory' });
}

// Set up navigation back button listener
navBackButton.addEventListener('click', handleNavBackClick);

// ============================================
// VIEW MANAGEMENT
// ============================================

/**
 * Switch between views
 */
function switchView(view) {
    if (view === 'subcategory') {
        // Hide main categories and navigation
        mainCategoriesSection.classList.add('fade-out');
        navigationSection.classList.add('fade-out');
        
        setTimeout(() => {
            mainCategoriesSection.style.display = 'none';
            mainCategoriesSection.classList.remove('fade-out');
            navigationSection.style.display = 'none';
            navigationSection.classList.remove('fade-out');
            
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
        // Hide subcategories and navigation
        subcategorySection.classList.add('fade-out');
        breadcrumbNav.classList.add('fade-out');
        navigationSection.classList.add('fade-out');
        
        setTimeout(() => {
            subcategorySection.style.display = 'none';
            subcategorySection.classList.remove('fade-out');
            navigationSection.style.display = 'none';
            navigationSection.classList.remove('fade-out');
            
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
        
    } else if (view === 'navigation') {
        // Hide main categories and subcategories
        mainCategoriesSection.classList.add('fade-out');
        subcategorySection.classList.add('fade-out');
        breadcrumbNav.classList.add('fade-out');
        
        setTimeout(() => {
            mainCategoriesSection.style.display = 'none';
            mainCategoriesSection.classList.remove('fade-out');
            subcategorySection.style.display = 'none';
            subcategorySection.classList.remove('fade-out');
            breadcrumbNav.style.display = 'none';
            breadcrumbNav.classList.remove('fade-out');
            
            // Show navigation
            navigationSection.style.display = 'flex';
            navigationSection.classList.add('fade-in');
            
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
// NAVIGATION SCREEN GENERATION
// ============================================

/**
 * Generate navigation screen content
 */
function generateNavigationScreen(categoryName, subcategoryName) {
    // Update header
    navProductName.textContent = `Navigating to: ${subcategoryName}`;
    
    // Update location status
    currentLocationText.textContent = navigationData.currentLocation;
    destinationText.textContent = `${subcategoryName} - Aisle 7`;
    
    // Generate store map
    generateStoreMap();
    
    // Generate directions
    generateDirections(subcategoryName);
}

/**
 * Generate store map visualization
 */
function generateStoreMap() {
    storeMap.innerHTML = '';
    
    // Create placeholder for 3D map
    const mapPlaceholder = document.createElement('div');
    mapPlaceholder.className = 'map-placeholder';
    
    const mapImage = document.createElement('img');
    mapImage.className = 'map-image';
    mapImage.src = 'image.png';
    mapImage.alt = 'Store Layout Map';
    
    mapPlaceholder.appendChild(mapImage);
    
    storeMap.appendChild(mapPlaceholder);
}

/**
 * Generate turn-by-turn directions
 */
function generateDirections(productName) {
    directionsList.innerHTML = '';
    
    navigationData.directions.forEach((direction, index) => {
        const stepDiv = document.createElement('div');
        stepDiv.className = 'direction-step';
        
        // Mark final step
        if (index === navigationData.directions.length - 1) {
            stepDiv.classList.add('final');
        }
        
        // Step number
        const stepNumber = document.createElement('div');
        stepNumber.className = 'step-number';
        stepNumber.textContent = direction.step;
        
        // Step icon
        const stepIcon = document.createElement('div');
        stepIcon.className = 'step-icon';
        stepIcon.textContent = direction.icon;
        
        // Step content
        const stepContent = document.createElement('div');
        stepContent.className = 'step-content';
        
        const stepAction = document.createElement('div');
        stepAction.className = 'step-action';
        stepAction.textContent = direction.action;
        
        stepContent.appendChild(stepAction);
        
        if (direction.distance) {
            const stepDistance = document.createElement('div');
            stepDistance.className = 'step-distance';
            stepDistance.textContent = direction.distance;
            stepContent.appendChild(stepDistance);
        }
        
        // Append all elements
        stepDiv.appendChild(stepNumber);
        stepDiv.appendChild(stepIcon);
        stepDiv.appendChild(stepContent);
        
        directionsList.appendChild(stepDiv);
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
