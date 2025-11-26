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
    directions: []  // Empty - directions will be generated dynamically from backend
};

// ============================================
// API CONFIGURATION
// ============================================

// Backend API configuration
const API_CONFIG = {
    // Try multiple backend URLs - browser will use the first that works
    BASE_URL: 'http://172.20.10.2:8040',  // PC IP on hotspot (WiFi)
    ENDPOINTS: {
        SEARCH_AND_LOCALIZE: '/search-and-localize',
        LOCALIZE: '/localize',
        SEARCH: '/search',
        STATUS: '/status'
    },
    TIMEOUT: 30000,  // 30 seconds timeout
    MAX_FILE_SIZE: 10 * 1024 * 1024,  // 10 MB in bytes
    ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/bmp', 'image/jpg']
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
    
    // Generate directions
    generateDirections(subcategoryName);
    
    // Initialize localization handlers (camera, buttons, etc.)
    // Use setTimeout to ensure DOM elements are fully rendered
    setTimeout(() => {
        initializeLocalizationHandlers();
    }, 100);
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

// ============================================
// LOCALIZATION FUNCTIONALITY
// ============================================

/**
 * Initialize localization button and camera input handlers
 * Called when navigation screen is generated
 */
function initializeLocalizationHandlers() {
    const localizeButton = document.getElementById('localize-button');
    const cameraInput = document.getElementById('camera-input');
    const retryButton = document.getElementById('retry-button');
    
    if (!localizeButton || !cameraInput) {
        console.warn('Localization elements not found - may not be on navigation screen');
        return;
    }
    
    // Handle "Localize Me" button click - trigger camera/file input
    localizeButton.addEventListener('click', handleLocalizeButtonClick);
    
    // Handle camera input change - process captured image
    cameraInput.addEventListener('change', handleCameraInputChange);
    
    // Handle retry button click
    if (retryButton) {
        retryButton.addEventListener('click', handleRetryButtonClick);
    }
    
    console.log('Localization handlers initialized');
}

/**
 * Handle "Localize Me" button click
 * Triggers the camera/file input
 */
function handleLocalizeButtonClick() {
    const cameraInput = document.getElementById('camera-input');
    
    if (!cameraInput) {
        console.error('Camera input element not found');
        return;
    }
    
    // Trigger the file input which will open camera on mobile devices
    cameraInput.click();
    
    // Haptic feedback
    if ('vibrate' in navigator) {
        navigator.vibrate(30);
    }
    
    logAnalytics('localize_button_clicked', {
        timestamp: new Date().toISOString()
    });
}

/**
 * Handle camera input change (file selected/photo captured)
 * Validates the file and sends it to the backend
 */
async function handleCameraInputChange(event) {
    const file = event.target.files[0];
    
    if (!file) {
        console.log('No file selected');
        return;
    }
    
    console.log('File selected:', file.name, 'Type:', file.type, 'Size:', file.size);
    
    // Validate file type
    if (!API_CONFIG.ALLOWED_TYPES.includes(file.type)) {
        showLocalizationError(
            `Invalid image format. Please use JPEG, PNG, or BMP. Selected: ${file.type}`
        );
        return;
    }
    
    // Validate file size
    if (file.size > API_CONFIG.MAX_FILE_SIZE) {
        const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
        const maxSizeMB = (API_CONFIG.MAX_FILE_SIZE / (1024 * 1024)).toFixed(0);
        showLocalizationError(
            `Image too large. Maximum size: ${maxSizeMB} MB. Your image: ${sizeMB} MB`
        );
        return;
    }
    
    // File is valid - proceed with localization
    await performLocalization(file);
    
    // Reset the input so the same file can be selected again
    event.target.value = '';
}

/**
 * Handle retry button click
 * Clears error and allows user to try again
 */
function handleRetryButtonClick() {
    hideLocalizationError();
    handleLocalizeButtonClick();
}

/**
 * Send the captured image to the backend for localization
 * @param {File} imageFile - The captured image file
 */
async function performLocalization(imageFile) {
    console.log('Starting localization process...');
    
    // Show loading state
    showLoadingSpinner();
    hideLocalizationResults();
    hideLocalizationError();
    
    try {
        // Prepare FormData for multipart upload
        const formData = new FormData();
        formData.append('image', imageFile);
        
        // Hardcode "paper towel" for now - will be dynamic later based on user selection
        const productName = 'paper towel';
        formData.append('object_name', productName);
        formData.append('include_timing', 'true');
        
        console.log('Sending request to:', API_CONFIG.BASE_URL + API_CONFIG.ENDPOINTS.SEARCH_AND_LOCALIZE);
        console.log('Searching for object:', productName);
        
        // Send the request with timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);
        
        const response = await fetch(
            API_CONFIG.BASE_URL + API_CONFIG.ENDPOINTS.SEARCH_AND_LOCALIZE,
            {
                method: 'POST',
                body: formData,
                signal: controller.signal
            }
        );
        
        clearTimeout(timeoutId);
        
        // Check response status
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Server error (${response.status}): ${errorText}`);
        }
        
        // Parse the response
        const result = await response.json();
        
        console.log('Localization response received:', result);
        
        // Hide loading spinner
        hideLoadingSpinner();
        
        // Check if localization was successful
        if (result.success && result.localization_results) {
            displayLocalizationResults(result);
            logAnalytics('localization_success', {
                timestamp: new Date().toISOString(),
                picture_id: result.localization_results.picture_id,
                processing_time: result.localization_results.processing_time_ms
            });
        } else {
            // Localization failed but request succeeded
            const errorMsg = result.error_message || 'Localization failed. Unable to determine your position.';
            showLocalizationError(errorMsg);
            logAnalytics('localization_failed', {
                timestamp: new Date().toISOString(),
                reason: errorMsg
            });
        }
        
    } catch (error) {
        console.error('Localization error:', error);
        hideLoadingSpinner();
        
        // Handle different error types
        let errorMessage = 'An error occurred during localization.';
        
        if (error.name === 'AbortError') {
            errorMessage = 'Request timed out. Please check your connection and try again.';
        } else if (error.message.includes('Failed to fetch')) {
            errorMessage = 'Cannot connect to server. Please ensure the backend is running.';
        } else {
            errorMessage = error.message || errorMessage;
        }
        
        showLocalizationError(errorMessage);
        
        logAnalytics('localization_error', {
            timestamp: new Date().toISOString(),
            error: error.message
        });
    }
}

/**
 * Display localization results in the UI
 * @param {Object} result - The localization result from the API
 */
function displayLocalizationResults(result) {
    const resultsContainer = document.getElementById('localization-results');
    
    if (!resultsContainer) {
        console.error('Results container not found');
        return;
    }
    
    const localization = result.localization_results;
    
    // Update position data - use global coordinates if available, otherwise local
    if (localization.global_position) {
        document.getElementById('position-x').textContent = localization.global_position.x.toFixed(2) + ' m';
        document.getElementById('position-y').textContent = localization.global_position.y.toFixed(2) + ' m';
    } else {
        document.getElementById('position-x').textContent = localization.position.x.toFixed(2) + ' m';
        document.getElementById('position-y').textContent = localization.position.y.toFixed(2) + ' m';
    }
    
    // Update orientation data as a single formatted string
    const rollDeg = (localization.orientation.roll * 180 / Math.PI).toFixed(1);
    const pitchDeg = (localization.orientation.pitch * 180 / Math.PI).toFixed(1);
    const yawDeg = (localization.orientation.yaw * 180 / Math.PI).toFixed(1);
    
    const orientationText = `Roll: ${rollDeg}°, Pitch: ${pitchDeg}°, Yaw: ${yawDeg}°`;
    document.getElementById('orientation-values').textContent = orientationText;
    
    // Update metadata
    document.getElementById('picture-id').textContent = localization.picture_id;
    document.getElementById('processing-time').textContent = localization.processing_time_ms + ' ms';
    document.getElementById('timestamp').textContent = new Date().toLocaleString();
    
    // Update status badge
    const statusBadge = document.getElementById('status-badge');
    statusBadge.textContent = '✓ Success';
    statusBadge.classList.remove('error');
    
    // Display navigation guidance if available
    if (result.navigation_guidance) {
        displayNavigationGuidance(result.navigation_guidance);
    }
    
    // Show the results container and additional info
    resultsContainer.style.display = 'block';
    const additionalInfo = document.getElementById('additional-info');
    if (additionalInfo) {
        additionalInfo.style.display = 'block';
    }
    
    // Scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    console.log('Localization results displayed successfully');
}

/**
 * Display navigation guidance directions with detailed step-by-step instructions
 */
function displayNavigationGuidance(guidance) {
    const directionsList = document.getElementById('directions-list');

    if (!directionsList) {
        console.error('Directions list not found');
        return;
    }

    // Clear any existing directions
    directionsList.innerHTML = '';

    // Check if user is already at the location
    if (guidance.is_at_location) {
        directionsList.innerHTML = `
            <div class="direction-step">
                <div class="step-icon">🎯</div>
                <div class="step-content">
                    <div class="step-number">✓</div>
                    <div class="step-text">You have arrived at your destination!</div>
                    <div class="step-distance">Target: ${guidance.target_object}</div>
                </div>
            </div>
        `;
        return;
    }

    // Parse clock instruction for detailed steps
    const steps = parseClockInstruction(guidance);

    // Render all steps
    steps.forEach((step, index) => {
        const stepDiv = document.createElement('div');
        stepDiv.className = 'direction-step';
        if (index === steps.length - 1) {
            stepDiv.classList.add('final');
        }

        stepDiv.innerHTML = `
            <div class="step-number">${index + 1}</div>
            <div class="step-icon">${step.icon}</div>
            <div class="step-content">
                <div class="step-text">${step.text}</div>
                ${step.distance ? `<div class="step-distance">${step.distance}</div>` : ''}
            </div>
        `;
        directionsList.appendChild(stepDiv);
    });

    console.log('Navigation guidance displayed with', steps.length, 'steps');
}

/**
 * Parse clock instruction into detailed step-by-step directions
 */
function parseClockInstruction(guidance) {
    const steps = [];
    const clockPos = guidance.clock_position;
    const bearing = guidance.bearing;
    const distance = guidance.distance;

    // Determine turn direction and amount
    let turnDirection = '';
    let turnAmount = '';
    let isClockwise = bearing > 0;

    // Calculate turn amount in degrees
    const turnDegrees = Math.abs(bearing);

    if (turnDegrees < 15) {
        turnAmount = 'slight';
    } else if (turnDegrees < 45) {
        turnAmount = 'quarter';
    } else if (turnDegrees < 90) {
        turnAmount = 'half';
    } else if (turnDegrees < 135) {
        turnAmount = 'three-quarter';
    } else {
        turnAmount = 'full';
    }

    // Determine turn direction
    if (bearing > 0) {
        turnDirection = 'clockwise (to your right)';
    } else if (bearing < 0) {
        turnDirection = 'counterclockwise (to your left)';
    } else {
        turnDirection = 'straight ahead';
    }

    // Step 1: Orientation/Turning instruction
    if (Math.abs(bearing) > 15) {
        let turnText = '';

        if (clockPos === 12) {
            turnText = 'Face straight ahead (12 o\'clock position)';
        } else if (clockPos === 3) {
            turnText = 'Turn directly to your right to face 3 o\'clock';
        } else if (clockPos === 6) {
            turnText = 'Turn around completely to face 6 o\'clock (opposite direction)';
        } else if (clockPos === 9) {
            turnText = 'Turn directly to your left to face 9 o\'clock';
        } else if (clockPos === 1 || clockPos === 2) {
            turnText = `Turn slightly to your right to face ${clockPos} o'clock`;
        } else if (clockPos === 4 || clockPos === 5) {
            turnText = `Turn to your right to face ${clockPos} o'clock`;
        } else if (clockPos === 7 || clockPos === 8) {
            turnText = `Turn to your left to face ${clockPos} o'clock`;
        } else if (clockPos === 10 || clockPos === 11) {
            turnText = `Turn slightly to your left to face ${clockPos} o'clock`;
        }

        steps.push({
            icon: '🔄',
            text: turnText,
            distance: null,
            details: null
        });
    } else {
        // Minimal or no turn needed
        steps.push({
            icon: '➡️',
            text: 'Continue in your current direction',
            distance: null,
            details: null
        });
    }

    // Step 2: Walking instruction
    let walkText = '';
    let distanceText = '';

    if (distance < 1.0) {
        walkText = 'Take a few steps forward';
        distanceText = `Walk ${distance.toFixed(1)} meter${distance < 1.1 ? '' : 's'}`;
    } else if (distance < 3.0) {
        walkText = 'Walk forward a short distance';
        distanceText = `Walk ${distance.toFixed(1)} meters`;
    } else if (distance < 10.0) {
        walkText = 'Walk forward';
        distanceText = `Walk ${distance.toFixed(0)} meters`;
    } else {
        walkText = 'Walk forward a longer distance';
        distanceText = `Walk approximately ${Math.round(distance/5)*5} meters`;
    }

    steps.push({
        icon: '🚶',
        text: walkText,
        distance: distanceText,
        details: null
    });

    // Step 3: Arrival confirmation - simplified
    steps.push({
        icon: '🎯',
        text: 'You will arrive at the target product',
        distance: null,
        details: null
    });

    return steps;
}

/**
 * Show loading spinner during localization
 */
function showLoadingSpinner() {
    const spinner = document.getElementById('loading-spinner');
    const button = document.getElementById('localize-button');
    
    if (spinner) {
        spinner.style.display = 'flex';
    }
    
    if (button) {
        button.disabled = true;
        button.style.opacity = '0.6';
    }
}

/**
 * Hide loading spinner
 */
function hideLoadingSpinner() {
    const spinner = document.getElementById('loading-spinner');
    const button = document.getElementById('localize-button');
    
    if (spinner) {
        spinner.style.display = 'none';
    }
    
    if (button) {
        button.disabled = false;
        button.style.opacity = '1';
    }
}

/**
 * Show localization results
 */
function showLocalizationResults() {
    const resultsContainer = document.getElementById('localization-results');
    if (resultsContainer) {
        resultsContainer.style.display = 'block';
    }
}

/**
 * Hide localization results
 */
function hideLocalizationResults() {
    const resultsContainer = document.getElementById('localization-results');
    if (resultsContainer) {
        resultsContainer.style.display = 'none';
    }
}

/**
 * Show localization error message
 * @param {string} message - The error message to display
 */
function showLocalizationError(message) {
    const errorContainer = document.getElementById('localization-error');
    const errorMessage = document.getElementById('error-message');
    
    if (errorContainer && errorMessage) {
        errorMessage.textContent = message;
        errorContainer.style.display = 'block';
        
        // Scroll to error
        errorContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

/**
 * Hide localization error message
 */
function hideLocalizationError() {
    const errorContainer = document.getElementById('localization-error');
    if (errorContainer) {
        errorContainer.style.display = 'none';
    }
}

