# Store Navigator

**Indoor Navigation and Product Finder for Grocery Stores**

## 🌐 Live Demo

**[https://kasrajb.github.io/store-navigator/](https://kasrajb.github.io/store-navigator/)**

---

## Overview

Store Navigator is a smartphone-based indoor navigation system that helps users locate products in grocery stores. The application provides an intuitive interface for browsing product categories and receiving turn-by-turn directions to find items quickly and efficiently.



## 📱 Features

### Current Implementation (3 Screens)

#### 1. **Main Screen - Category Selection**
- 18 comprehensive grocery categories with icons
- Categories include: Fruits & Vegetables, Dairy & Eggs, Meat & Poultry, Fish & Seafood, Pantry, Frozen, Bread & Bakery, Beverages, Snacks, Beer & Wine, Deli & Prepared Meals, World Cuisine, Vegan & Vegetarian, Organic Groceries, Household & Cleaning, Health & Beauty, Baby, Pet Care
- Responsive grid layout (2 columns mobile → 3 tablet → 4 desktop)
- Sticky search bar with clear button
- Smooth scrolling with fixed header

#### 2. **Subcategory Screen - Product Categories**
- Drill-down navigation into specific product types
- Each category contains 4-7 subcategories with relevant icons
- Breadcrumb navigation showing path
- Back button to return to main categories
- Visual feedback on selection

#### 3. **Navigation Screen - Turn-by-Turn Directions**
- **Header**: Back button + selected product name
- **Location Status Bar**: Shows current position (📍) and destination (🎯)
- **Store Map**: Visual store layout showing navigation path
- **Turn-by-Turn Directions**: Step-by-step instructions with icons
  - Numbered steps (1-4)
  - Action descriptions (Walk straight, Turn right, etc.)
  - Distance indicators
  - Final destination marker
- Smooth transitions between screens

#### 4. **📍 Photo-Based Localization (NEW!)**
- **Localize Me Button**: Capture a photo to determine your position in the store
- **Camera Integration**: Uses device camera (or file upload on desktop)
- **Real-time Processing**: Connects to RTAB-Map backend for visual localization
- **Detailed Results Display**:
  - Position coordinates (X, Y, Z) in meters
  - Orientation angles (Roll, Pitch, Yaw) in degrees
  - Detected objects in the current scene
  - Processing time and timestamp
- **Error Handling**: User-friendly error messages with retry functionality

> **Note for Testing Localization:** The photo-based localization feature requires a local backend server. To test this feature:
> 1. Download the repository
> 2. Start the backend server (requires Docker)
> 3. Open `index.html` locally in your browser
> 
> The live GitHub Pages demo shows the UI but cannot connect to a local backend due to browser security restrictions.

#### 4. **Search Functionality**
- Prominent search bar with magnifying glass icon
- Real-time search input handling
- Clear button (X) that appears when text is entered
- Keyboard-accessible (Enter to search)
- Sticky positioning - stays visible while scrolling

#### 5. **Accessibility Features**
- Semantic HTML5 structure
- ARIA labels for screen readers
- Keyboard navigation support (Tab, Enter, Space, Arrow keys)
- Minimum 44x44px tap targets
- Focus indicators for keyboard users
- Reduced motion support
- High contrast mode support

#### 6. **Responsive Design**
- Mobile-first approach
- Breakpoints: 480px, 640px, 768px
- Adapts from 2-column to 4-column grid
- Fluid typography and spacing
- Touch device optimizations
- Scrollable content with fixed navigation elements

---

## 🛠️ Technologies

- **HTML5** - Semantic markup
- **CSS3** - Flexbox, Grid, Custom Properties
- **JavaScript** - Vanilla ES6+ (no dependencies)
- **Responsive Design** - Mobile-first approach

## 🚀 Getting Started

1. Clone the repository or visit the [live demo](https://kasrajb.github.io/store-navigator/)
2. Open `index.html` in a modern web browser
3. Browse categories, select subcategories, and view navigation directions

No installation or build tools required.

---

## � Developer

**Kasra Jabbari**

---
