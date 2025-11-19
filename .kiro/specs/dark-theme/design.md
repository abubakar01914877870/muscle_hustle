# Design Document

## Introduction

This document describes the design for implementing a comprehensive dark theme across the Muscle Hustle application. The implementation will leverage the existing design-system.css dark theme and ensure all pages, components, and templates use consistent dark theme styling.

## System Architecture

### Current State

The application currently has:
- `src/static/styles.css` - Legacy light theme styles
- `src/static/design-system.css` - Modern dark theme with Power & Energy palette (already implemented)
- `src/static/progress.css` - Mixed theme with light/dark mode support
- `src/templates/base.html` - Base template that loads stylesheets

### Target State

The application will:
- Use `design-system.css` as the primary stylesheet for all pages
- Remove or override legacy light theme styles from `styles.css`
- Update `progress.css` to use dark theme variables consistently
- Ensure all templates load stylesheets in the correct order
- Apply dark theme styling to all components uniformly

## Design Details

### Component 1: Stylesheet Loading Order

**Purpose:** Ensure stylesheets load in the correct order so dark theme styles take precedence.

**Implementation:**
1. Update `src/templates/base.html` to load stylesheets in this order:
   - `design-system.css` (first - provides base dark theme)
   - `progress.css` (second - page-specific styles that use design system variables)
   - `styles.css` (last - legacy overrides, will be deprecated)

2. Add CSS specificity to ensure design-system.css rules take precedence

**Correctness Properties:**
- P1.1: Design system styles SHALL load before page-specific styles
- P1.2: CSS variables from design-system.css SHALL be available to all subsequent stylesheets
- P1.3: Dark theme colors SHALL override any light theme colors from legacy styles

### Component 2: Legacy Styles Migration

**Purpose:** Remove or override light theme styles from styles.css to prevent conflicts.

**Implementation:**
1. Identify all light theme color definitions in `styles.css`:
   - Background colors (e.g., `#f5f5f5`, `#ffffff`)
   - Text colors (e.g., `#333`, `#555`)
   - Border colors (e.g., `#ddd`)
   - Component backgrounds (e.g., `#2c3e50`)

2. Replace with CSS variables from design-system.css:
   - `background-color: #f5f5f5` → `background-color: var(--color-background)`
   - `color: #333` → `color: var(--color-text)`
   - `background: #ffffff` → `background: var(--color-surface)`
   - `border: 1px solid #ddd` → `border: 1px solid var(--color-border)`

3. Update component-specific styles:
   - Header: Use gradient from design-system.css
   - Buttons: Use btn-primary, btn-secondary classes
   - Forms: Use form-control class with dark theme variables
   - Tables: Use dark theme table styles
   - Cards: Use card class with dark backgrounds

**Correctness Properties:**
- P2.1: All hardcoded light colors SHALL be replaced with CSS variables
- P2.2: Component styles SHALL use design system classes where available
- P2.3: No light theme backgrounds SHALL be visible on any page

### Component 3: Progress Page Dark Theme

**Purpose:** Update progress.css to use dark theme consistently without light mode fallback.

**Implementation:**
1. Remove the `@media (prefers-color-scheme: dark)` query since dark theme is default

2. Update CSS variables in progress.css to match design-system.css:
   ```css
   :root {
     --color-background: var(--color-navy-900);
     --color-surface: var(--color-navy-800);
     --color-text: var(--color-white);
     --color-primary: var(--color-energy-red);
     /* ... etc */
   }
   ```

3. Ensure all progress components use dark theme:
   - Form sections: Dark navy backgrounds
   - Timeline entries: Dark cards with light text
   - Chart containers: Dark backgrounds
   - File inputs: Dark themed buttons

**Correctness Properties:**
- P3.1: Progress page SHALL display with dark backgrounds
- P3.2: All text on progress page SHALL be light colored
- P3.3: Charts SHALL use colors visible on dark backgrounds
- P3.4: Form inputs SHALL have dark backgrounds with light text

### Component 4: Header and Navigation

**Purpose:** Ensure header uses the Power & Energy gradient theme consistently.

**Implementation:**
1. Apply `.header` class from design-system.css to header element

2. Header structure:
   ```html
   <header class="header">
     <div class="header-wrapper">
       <div class="header-left">
         <span class="app-logo">💪</span>
         <div class="header-content">
           <h1>Muscle Hustle</h1>
           <p>Track Your Fitness Journey</p>
         </div>
       </div>
       <a href="/profile/view" class="header-profile-link">
         <div class="header-profile-image">...</div>
       </a>
     </div>
     <nav class="header-nav">
       <a href="/" class="nav-link">Home</a>
       <!-- ... more links -->
     </nav>
   </header>
   ```

3. Styling features:
   - Red-to-orange gradient background
   - Glowing shadow effect
   - Electric blue accent line
   - Profile image with blue border and glow
   - Uppercase navigation links with hover effects

**Correctness Properties:**
- P4.1: Header SHALL display gradient from energy red to motivation orange
- P4.2: Navigation links SHALL be white text on gradient background
- P4.3: Active navigation link SHALL have electric blue highlight
- P4.4: Profile image SHALL have electric blue border with glow effect

### Component 5: Forms and Inputs

**Purpose:** Ensure all form elements use dark theme styling with proper contrast.

**Implementation:**
1. Apply form classes from design-system.css:
   - `.form-section` for form containers
   - `.form-grid` for form layouts
   - `.form-group` for individual fields
   - `.form-label` for labels
   - `.form-control` for inputs

2. Input styling:
   ```css
   input, select, textarea {
     background-color: var(--color-surface-elevated);
     color: var(--color-white);
     border: 2px solid var(--color-border);
   }
   
   input:focus, select:focus, textarea:focus {
     border-color: var(--color-primary);
     box-shadow: var(--focus-ring);
     background-color: var(--color-navy-700);
   }
   ```

3. Button styling:
   - Primary buttons: Red-to-orange gradient with glow
   - Secondary buttons: Navy with electric blue border
   - Hover effects: Lift and enhanced glow

**Correctness Properties:**
- P5.1: All inputs SHALL have dark backgrounds with light text
- P5.2: Focus states SHALL display electric blue ring
- P5.3: Placeholder text SHALL be visible on dark backgrounds
- P5.4: Primary buttons SHALL have red-to-orange gradient
- P5.5: Button hover SHALL display lift animation and glow

### Component 6: Tables and Data Display

**Purpose:** Ensure tables and data grids use dark theme styling.

**Implementation:**
1. Apply table styles from design-system.css:
   ```css
   table {
     background: var(--color-surface);
     border: 1px solid var(--color-card-border);
   }
   
   thead {
     background: linear-gradient(135deg, var(--color-surface-elevated), var(--color-navy-700));
     border-bottom: 2px solid var(--color-primary);
   }
   
   th {
     color: var(--color-white);
     text-transform: uppercase;
   }
   
   tbody tr:hover {
     background: linear-gradient(90deg, rgba(var(--color-energy-red-rgb), 0.1), rgba(var(--color-motivation-orange-rgb), 0.1));
   }
   ```

2. Badge styling:
   - Admin badge: Red gradient with glow
   - User badge: Blue gradient with glow

**Correctness Properties:**
- P6.1: Table headers SHALL have gradient background with red border
- P6.2: Table rows SHALL have dark backgrounds
- P6.3: Hover effects SHALL display colored gradient overlay
- P6.4: Badges SHALL have vibrant colors with glow effects

### Component 7: Cards and Sections

**Purpose:** Ensure all content cards use dark theme with gradient accents.

**Implementation:**
1. Apply card classes from design-system.css:
   ```css
   .card, .profile-section, .form-section {
     background: linear-gradient(135deg, var(--color-surface), var(--color-surface-elevated));
     border: 1px solid var(--color-card-border);
     border-radius: var(--radius-lg);
   }
   
   .card::before {
     content: '';
     position: absolute;
     top: 0;
     height: 3px;
     background: linear-gradient(90deg, var(--color-primary), var(--color-secondary), var(--color-accent));
   }
   ```

2. Section headers:
   - White text with uppercase styling
   - Bottom border with red accent
   - Bold font weight

**Correctness Properties:**
- P7.1: All cards SHALL have dark navy backgrounds
- P7.2: Cards SHALL have colored gradient top border
- P7.3: Section headings SHALL be white with red underline
- P7.4: Card backgrounds SHALL use subtle gradients for depth

### Component 8: Flash Messages and Alerts

**Purpose:** Ensure feedback messages are visible and styled for dark theme.

**Implementation:**
1. Apply flash message styles:
   ```css
   .flash-success {
     background: linear-gradient(135deg, rgba(var(--color-achievement-green-rgb), 0.2), rgba(var(--color-achievement-green-rgb), 0.1));
     border: 2px solid var(--color-success);
     color: var(--color-white);
     box-shadow: 0 0 20px rgba(var(--color-achievement-green-rgb), 0.3);
   }
   
   .flash-error {
     background: linear-gradient(135deg, rgba(var(--color-energy-red-rgb), 0.2), rgba(var(--color-energy-red-rgb), 0.1));
     border: 2px solid var(--color-error);
     color: var(--color-white);
     box-shadow: 0 0 20px rgba(var(--color-energy-red-rgb), 0.3);
   }
   ```

**Correctness Properties:**
- P8.1: Success messages SHALL have green border and glow
- P8.2: Error messages SHALL have red border and glow
- P8.3: Message text SHALL be white on semi-transparent colored backgrounds
- P8.4: Messages SHALL have glowing shadow effects

## Data Flow

### Stylesheet Loading Flow
```
Browser Request
    ↓
base.html loads
    ↓
1. design-system.css (defines CSS variables and base styles)
    ↓
2. progress.css (uses CSS variables for page-specific styles)
    ↓
3. styles.css (legacy overrides, minimal usage)
    ↓
Page renders with dark theme
```

### CSS Variable Inheritance
```
:root (design-system.css)
    ↓
Defines --color-* variables
    ↓
All components reference variables
    ↓
Consistent dark theme across app
```

## Testing Strategy

### Visual Testing
1. Navigate to each page and verify dark backgrounds
2. Check text contrast and readability
3. Verify hover and focus states work correctly
4. Test on different screen sizes (responsive)

### Component Testing
1. Forms: Verify inputs have dark backgrounds and light text
2. Buttons: Verify gradient and glow effects
3. Tables: Verify dark backgrounds and hover effects
4. Navigation: Verify gradient header and link styles
5. Cards: Verify dark backgrounds with colored top borders

### Browser Testing
1. Test in Chrome, Firefox, Safari
2. Verify CSS variables are supported
3. Check gradient and shadow rendering

## Security Considerations

No security implications for this feature. This is purely a visual/styling change.

## Performance Considerations

1. **CSS File Size**: design-system.css is comprehensive but well-organized
2. **Render Performance**: CSS variables have minimal performance impact
3. **Caching**: Static CSS files will be cached by browsers
4. **Optimization**: Consider minifying CSS in production

## Deployment Plan

### Phase 1: Base Template Update
1. Update base.html stylesheet loading order
2. Verify design-system.css loads first

### Phase 2: Legacy Styles Migration
1. Update styles.css to use CSS variables
2. Remove hardcoded light theme colors
3. Test all pages for visual consistency

### Phase 3: Progress Page Update
1. Update progress.css to use dark theme variables
2. Remove light mode media query
3. Test progress tracking functionality

### Phase 4: Verification
1. Visual testing on all pages
2. Cross-browser testing
3. Responsive design testing
4. User acceptance testing

## Rollback Plan

If issues arise:
1. Revert base.html to original stylesheet order
2. Restore original styles.css
3. Restore original progress.css
4. All changes are in CSS files, no database changes needed

## Future Enhancements

1. Theme toggle (light/dark mode switcher)
2. Custom theme colors per user preference
3. High contrast mode for accessibility
4. Reduced motion mode for animations
