# Muscle Hustle Design System

## Overview
The Muscle Hustle app now uses a unified design system based on the provided fitness tracker template, ensuring consistency across all pages.

## Design System File
- **Location**: `src/static/design-system.css`
- **Purpose**: Central CSS file with all design tokens and component styles

## Color Palette

### Light Mode
- **Background**: Cream (#FCFCF9)
- **Surface**: Cream (#FFFFFD)
- **Primary**: Teal (#21808D)
- **Text**: Slate (#13343B)
- **Text Secondary**: Slate (#626C71)

### Dark Mode
- **Background**: Charcoal (#1F2121)
- **Surface**: Charcoal (#262828)
- **Primary**: Teal (#32B8C6)
- **Text**: Gray (#F5F5F5)
- **Text Secondary**: Gray (rgba(167, 169, 169, 0.7))

## Typography
- **Font Family**: FKGroteskNeue, Geist, Inter, System Fonts
- **Base Size**: 14px
- **Sizes**: xs(11px), sm(12px), base(14px), lg(16px), xl(18px), 2xl(20px), 3xl(24px), 4xl(30px)
- **Weights**: normal(400), medium(500), semibold(550), bold(600)

## Spacing Scale
- **System**: 0, 1px, 2px, 4px, 6px, 8px, 10px, 12px, 16px, 20px, 24px, 32px
- **Usage**: Consistent spacing using CSS variables (--space-*)

## Border Radius
- **sm**: 6px
- **base**: 8px
- **md**: 10px
- **lg**: 12px
- **full**: 9999px (pills)

## Components

### Header
- Centered title and tagline
- Horizontal navigation with hover states
- Responsive design

### Cards/Sections
- White/surface background
- Subtle border and shadow
- Rounded corners (12px)
- Consistent padding (24px)

### Forms
- 2-column grid on desktop, 1-column on mobile
- Consistent input styling
- Focus states with teal ring
- Clear labels and placeholders

### Buttons
- **Primary**: Teal background, cream text
- **Secondary**: Light brown background, dark text
- **Hover**: Darker shade
- **Focus**: Ring outline

### Tables
- Clean borders
- Hover row highlighting
- Responsive design

### Flash Messages
- Color-coded by type (success, error, info)
- Icon indicators
- Dismissible

## Updated Pages

### All Pages Now Use:
1. **Unified Header**: Muscle Hustle branding with navigation
2. **Consistent Layout**: Container with max-width 1200px
3. **Card-based Design**: All content in styled cards
4. **Responsive Grid**: 2-column forms, flexible layouts
5. **Design Tokens**: CSS variables for all colors, spacing, typography

### Specific Updates:
- **Home**: Welcome cards with feature highlights
- **Login/Signup**: Centered forms with consistent styling
- **Profile**: Grid-based information display
- **Progress Tracker**: Timeline and chart views
- **Admin**: Table-based user management

## Responsive Breakpoints
- **Mobile**: < 768px (single column, smaller text)
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px (full layout)

## Accessibility
- Focus states on all interactive elements
- Sufficient color contrast
- Semantic HTML
- Keyboard navigation support

## Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- CSS Grid and Flexbox
- CSS Custom Properties (variables)
- Dark mode via prefers-color-scheme

## Usage

### In Templates
```html
{% extends "base.html" %}

{% block content %}
<section class="card">
    <h2>Section Title</h2>
    <div class="form-grid">
        <!-- Content -->
    </div>
</section>
{% endblock %}
```

### Custom Styles
```html
{% block extra_css %}
<style>
  /* Page-specific styles */
</style>
{% endblock %}
```

## Maintenance
- All design tokens in `design-system.css`
- Update variables to change theme globally
- Component styles are reusable
- Consistent naming convention

## Future Enhancements
- Additional color themes
- More component variants
- Animation library
- Icon system
- Print styles
