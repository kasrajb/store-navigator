# Store Navigator - Indoor Navigation and Product Finder

## 🌐 Live Demo

**[https://kasrajb.github.io/store-navigator/](https://kasrajb.github.io/store-navigator/)**

Test the application on your mobile device or desktop browser!

---

## Overview

**Store Navigator** is a smartphone-based indoor navigation system designed to help users locate products in unfamiliar grocery stores using Visual SLAM (Simultaneous Localization and Mapping) technology. This web application provides the initial search and category selection interface, prioritizing minimal user effort and multimodal feedback for an accessible, efficient navigation experience.

This implementation is based on the ECSE 542 Milestone #1 HCI project report.

---

## 🎯 Project Goals

- **Minimal User Effort**: Quick access to product search and category browsing
- **Accessible Design**: Touch-friendly interfaces meeting WCAG standards
- **Mobile-First**: Optimized for smartphone viewports (375px-414px)
- **Visual SLAM Integration**: Foundation for future indoor navigation features
- **Multimodal Feedback**: Visual, tactile, and accessible interactions

---

## 📱 Features

### Current Implementation (Screen 1)

#### 1. **Search Functionality**
- Prominent search bar with magnifying glass icon
- Real-time search input handling
- Clear button (X) that appears when text is entered
- Keyboard-accessible (Enter to search)
- Touch-friendly input area (48px minimum height)
- Placeholder text: "Search for products..."

#### 2. **Category Selection**
- Six product categories with icons:
  - 🍎 **Fruits**
  - 🥛 **Dairy**
  - 🥩 **Meat**
  - 🐟 **Fish**
  - 🍿 **Snacks**
  - 🥤 **Beverages**
- Grid layout (2 columns on mobile, 3 on tablet+)
- Visual feedback on hover/tap
- Active state indication
- Console logging for development

#### 3. **Accessibility Features**
- Semantic HTML5 structure
- ARIA labels for screen readers
- Keyboard navigation support (Tab, Enter, Space, Arrow keys)
- Minimum 44x44px tap targets
- Focus indicators for keyboard users
- Reduced motion support
- High contrast mode support

#### 4. **Responsive Design**
- Mobile-first approach
- Breakpoints: 480px, 640px, 768px
- Adapts from 2-column to 3-column grid
- Fluid typography and spacing
- Touch device optimizations

---

## 🏗️ Technical Architecture

### File Structure
```
ECSE 542 Milestone #2/
├── index.html          # Main HTML structure
├── styles.css          # Complete styling (mobile-first)
├── script.js           # JavaScript functionality
└── README.md           # This file
```

### Technologies Used
- **HTML5**: Semantic markup
- **CSS3**: Flexbox, Grid, Custom Properties
- **Vanilla JavaScript**: No dependencies
- **Modern Web Standards**: ES6+, CSS Variables

### Browser Compatibility
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## 🚀 Getting Started

### Prerequisites
- A modern web browser
- No build tools or dependencies required

### Installation & Running

1. **Clone or Download** the project files

2. **Open the application**:
   - Simply open `index.html` in your web browser
   - Or use a local development server:
     ```bash
     # Using Python 3
     python -m http.server 8000
     
     # Using Node.js http-server
     npx http-server
     ```

3. **Access the application**:
   - Direct file: `file:///path/to/index.html`
   - Local server: `http://localhost:8000`

### Testing on Mobile Devices

1. **Browser DevTools** (Chrome/Firefox):
   - Open DevTools (F12)
   - Toggle device toolbar (Ctrl+Shift+M)
   - Select a mobile device preset (iPhone, Pixel, etc.)

2. **Actual Mobile Device**:
   - Host on local server
   - Access via device on same network
   - Use IP address: `http://192.168.x.x:8000`

---

## 💻 Usage Guide

### Search for Products
1. Click/tap the search bar at the top
2. Type a product name (e.g., "milk", "apples")
3. Press Enter or continue typing
4. Use the X button to clear the search

### Browse by Category
1. Scroll to the "Browse by Category" section
2. Tap any category card (Fruits, Dairy, etc.)
3. The selected category will be highlighted
4. Check console for logged selection

### Keyboard Navigation
- **Tab**: Navigate between elements
- **Enter/Space**: Select category
- **Arrow Keys**: Navigate between categories
- **Esc**: Clear search (when focused)

---

## 🎨 Design Specifications

### Color Palette
- **Primary**: `#2563eb` (Blue)
- **Primary Hover**: `#1d4ed8`
- **Secondary**: `#10b981` (Green)
- **Text Primary**: `#1f2937` (Dark Gray)
- **Text Secondary**: `#6b7280` (Medium Gray)
- **Background**: `#ffffff` (White)

### Typography
- **Font Family**: System fonts (SF Pro, Segoe UI, Roboto)
- **Base Size**: 16px (1rem)
- **Headings**: 20px - 30px
- **Line Height**: 1.5

### Spacing
- **Small**: 8px
- **Medium**: 16px
- **Large**: 24px
- **Extra Large**: 32px

### Touch Targets
- **Minimum**: 44x44px (Apple HIG)
- **Recommended**: 48x48px (Material Design)

---

## ♿ Accessibility Features

### WCAG 2.1 Compliance
- **Level AA**: Color contrast ratios
- **Keyboard Navigation**: Full support
- **Screen Readers**: ARIA labels and roles
- **Focus Management**: Clear indicators

### Assistive Technology Support
- ✅ VoiceOver (iOS)
- ✅ TalkBack (Android)
- ✅ NVDA (Windows)
- ✅ JAWS (Windows)

### Additional Features
- Reduced motion support
- High contrast mode
- Scalable text (up to 200%)
- Touch-friendly hit areas

---

## 🔧 Development Notes

### Console Logging
The application logs user interactions for development:
- Search queries (when > 2 characters)
- Category selections
- App initialization events

Open browser DevTools Console (F12) to view logs.

### Code Structure
- **Modular**: Separated HTML, CSS, and JS
- **Commented**: Extensive inline documentation
- **Semantic**: Meaningful variable and function names
- **Maintainable**: Clean, organized code

### Performance
- **No Dependencies**: Fast load times
- **Minimal JavaScript**: ~200 lines
- **CSS Variables**: Easy theming
- **Optimized Animations**: 60fps performance

---

## 🔮 Future Enhancements

### Planned Features (Milestones 2-3)
1. **Product Search Results**
   - Display matching products
   - Show product details
   - Location/aisle information

2. **Navigation Integration**
   - Visual SLAM implementation
   - Turn-by-turn directions
   - Real-time position tracking
   - Store map display

3. **Enhanced Category Browsing**
   - Product listings per category
   - Filtering and sorting options
   - Product images

4. **Multimodal Feedback**
   - Audio guidance
   - Haptic feedback
   - Visual indicators

5. **User Preferences**
   - Search history
   - Favorite products
   - Custom settings

6. **Offline Support**
   - Service worker
   - Cached product data
   - Offline navigation

---

## 📝 Design Philosophy

### User-Centered Approach
- **Minimal Effort**: Quick access to search and categories
- **Clear Hierarchy**: Search first, categories below
- **Visual Feedback**: Immediate response to interactions
- **Error Prevention**: Clear affordances, forgiving inputs

### Accessibility First
- **Inclusive Design**: Works for all users
- **Multiple Modalities**: Visual, audio, tactile
- **Flexible Interaction**: Touch, mouse, keyboard
- **Assistive Tech**: Full screen reader support

### Mobile-First
- **Small Screens**: Optimized for 375px-414px
- **Touch Interfaces**: Large, comfortable tap targets
- **Performance**: Fast load, smooth interactions
- **Progressive Enhancement**: Works everywhere, better on modern browsers

---

## 🐛 Known Limitations

1. **Search Functionality**: Currently logs to console only
2. **Category Selection**: No product display yet
3. **Navigation**: Not integrated with SLAM system
4. **Backend**: No server or database connection
5. **Product Data**: Placeholder for future implementation

These limitations are intentional for Milestone #1 and will be addressed in subsequent phases.

---

## 📚 References

- **ECSE 542 Milestone #1**: HCI project report (attached)
- **WCAG 2.1**: Web Content Accessibility Guidelines
- **Material Design**: Touch target guidelines
- **Apple HIG**: iOS interface guidelines

---

## 📄 License

This project is created for educational purposes as part of ECSE 542 coursework.

---

## 👥 Credits

- **Developer**: Kasra Jabbari
- **Project**: ECSE 542 - Indoor Navigation System
- **Implementation**: Milestone #2 - First Screen Development
- **Design Based On**: Milestone #1 Report sketches and requirements

---

## 📞 Support

For questions or issues:
1. Check the console for error messages
2. Verify browser compatibility
3. Test in mobile viewport (DevTools)
4. Review code comments for implementation details

---

## 🎉 Quick Start Checklist

- [ ] Open `index.html` in a modern browser
- [ ] Test search bar functionality
- [ ] Click on different category cards
- [ ] Open DevTools Console (F12)
- [ ] Try keyboard navigation (Tab, Enter, Arrows)
- [ ] Test on mobile viewport
- [ ] Verify touch interactions
- [ ] Check accessibility features

---

**Last Updated**: October 30, 2025  
**Version**: 1.0.0 (Milestone #2)  
**Status**: ✅ Initial Screen Complete
