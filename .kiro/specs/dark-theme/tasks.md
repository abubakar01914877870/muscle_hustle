# Tasks

## Task 1: Update Base Template Stylesheet Loading

**Description:** Update the base.html template to load stylesheets in the correct order, ensuring design-system.css loads first and provides the dark theme foundation.

**Depends On:** None

**Files to Modify:**
- `src/templates/base.html`

**Steps:**
1. Open `src/templates/base.html`
2. Locate the `<head>` section where stylesheets are loaded
3. Ensure stylesheets load in this order:
   - `design-system.css` (first)
   - `progress.css` (second, if on progress page)
   - `styles.css` (last, for legacy overrides)
4. Add HTML class or data attribute to body for dark theme identification
5. Save the file

**Acceptance Criteria:**
- design-system.css loads before other stylesheets
- All pages inherit dark theme CSS variables
- No console errors related to stylesheet loading

---

## Task 2: Migrate Legacy Styles to Dark Theme

**Description:** Update styles.css to replace all hardcoded light theme colors with CSS variables from design-system.css.

**Depends On:** Task 1

**Files to Modify:**
- `src/static/styles.css`

**Steps:**
1. Open `src/static/styles.css`
2. Replace body background color with `var(--color-background)`
3. Replace all `#ffffff` and `#f5f5f5` backgrounds with `var(--color-surface)`
4. Replace text colors `#333`, `#555` with `var(--color-text)` and `var(--color-text-secondary)`
5. Replace border colors `#ddd` with `var(--color-border)`
6. Update header styles to use design-system.css classes
7. Update button styles to use design-system.css classes
8. Update form input styles to use design-system.css classes
9. Update table styles to use design-system.css classes
10. Update card/container styles to use design-system.css classes
11. Save the file

**Acceptance Criteria:**
- No hardcoded light theme colors remain
- All components use CSS variables
- Visual consistency with design-system.css
- No broken layouts or styling

---

## Task 3: Update Progress Page Styles

**Description:** Update progress.css to use dark theme variables consistently and remove light mode support.

**Depends On:** Task 1

**Files to Modify:**
- `src/static/progress.css`

**Steps:**
1. Open `src/static/progress.css`
2. Remove the `@media (prefers-color-scheme: dark)` query
3. Update `:root` variables to reference design-system.css variables:
   - `--color-background: var(--color-navy-900)`
   - `--color-surface: var(--color-navy-800)`
   - `--color-text: var(--color-white)`
   - `--color-primary: var(--color-energy-red)`
   - etc.
4. Update form section styles to use dark backgrounds
5. Update timeline entry styles to use dark cards
6. Update chart container styles for dark backgrounds
7. Update empty state styles for dark theme
8. Save the file

**Acceptance Criteria:**
- Progress page displays with dark theme
- All text is readable on dark backgrounds
- Charts use colors visible on dark backgrounds
- Form inputs have dark backgrounds with light text
- No light mode styles remain

---

## Task 4: Update Header and Navigation

**Description:** Ensure all templates use the correct header structure and classes from design-system.css.

**Depends On:** Task 1

**Files to Modify:**
- `src/templates/base.html`
- Any templates with custom headers

**Steps:**
1. Open `src/templates/base.html`
2. Update header element to use class `header`
3. Add `header-wrapper` div for layout
4. Add `header-left` div with logo and title
5. Add `header-content` div for title and tagline
6. Add `header-profile-link` and `header-profile-image` for profile
7. Update navigation to use `header-nav` class
8. Update navigation links to use `nav-link` class
9. Add `active` class to current page link
10. Save the file

**Acceptance Criteria:**
- Header displays red-to-orange gradient
- Navigation links are white on gradient background
- Active link has electric blue highlight
- Profile image has blue border with glow
- Header is responsive on mobile devices

---

## Task 5: Update Form Styles

**Description:** Ensure all forms across the application use dark theme form classes and styling.

**Depends On:** Task 2

**Files to Modify:**
- `src/templates/admin/edit_profile.html`
- `src/templates/admin/edit_user.html`
- `src/templates/profile/edit.html`
- `src/templates/profile/change_password.html`
- `src/templates/exercises/add.html`
- `src/templates/exercises/edit.html`
- `src/templates/progress/index.html`
- `src/templates/register.html`
- `src/templates/login.html`

**Steps:**
1. For each template file:
2. Add `form-section` class to form containers
3. Add `form-grid` class to form layouts
4. Add `form-group` class to field wrappers
5. Add `form-label` class to labels
6. Add `form-control` class to inputs, selects, textareas
7. Update buttons to use `btn btn-primary` or `btn btn-secondary`
8. Save each file

**Acceptance Criteria:**
- All inputs have dark backgrounds with light text
- Focus states display electric blue ring
- Placeholder text is visible
- Primary buttons have red-to-orange gradient
- Button hover displays lift animation
- Forms are responsive on mobile

---

## Task 6: Update Table Styles

**Description:** Ensure all tables use dark theme styling from design-system.css.

**Depends On:** Task 2

**Files to Modify:**
- `src/templates/admin/users.html`
- Any other templates with tables

**Steps:**
1. Open each template with tables
2. Verify table uses `user-table` class or generic `table` styling
3. Ensure thead and tbody elements are properly structured
4. Update badge classes to `badge-admin` and `badge-user`
5. Verify action buttons use `btn-edit`, `btn-delete`, `btn-view` classes
6. Save each file

**Acceptance Criteria:**
- Table headers have gradient background with red border
- Table rows have dark backgrounds
- Hover effects display colored gradient overlay
- Badges have vibrant colors with glow effects
- Action buttons have appropriate colors and hover effects

---

## Task 7: Update Card and Section Styles

**Description:** Ensure all content cards and sections use dark theme styling.

**Depends On:** Task 2

**Files to Modify:**
- `src/templates/profile/view.html`
- `src/templates/exercises/detail.html`
- `src/templates/exercises/index.html`
- `src/templates/home.html`
- `src/templates/admin/view_profile.html`

**Steps:**
1. For each template:
2. Add `card` or `profile-section` class to content containers
3. Ensure section headings use `h2` or `h3` tags
4. Verify profile grids use `profile-grid` class
5. Verify profile items use `profile-item` class
6. Update empty states to use `empty-state` class
7. Save each file

**Acceptance Criteria:**
- All cards have dark navy backgrounds
- Cards have colored gradient top border
- Section headings are white with red underline
- Card backgrounds use subtle gradients
- Empty states are styled for dark theme

---

## Task 8: Update Flash Messages

**Description:** Ensure flash messages use dark theme styling with proper visibility.

**Depends On:** Task 2

**Files to Modify:**
- `src/templates/base.html` (if flash messages are in base)
- Any templates with inline flash messages

**Steps:**
1. Locate flash message rendering code
2. Ensure success messages use `flash flash-success` classes
3. Ensure error messages use `flash flash-error` classes
4. Ensure info messages use `flash flash-info` classes
5. Verify message text is white
6. Save files

**Acceptance Criteria:**
- Success messages have green border and glow
- Error messages have red border and glow
- Info messages have blue border and glow
- Message text is white and readable
- Messages have glowing shadow effects

---

## Task 9: Update Exercise Pages

**Description:** Ensure exercise library pages use dark theme styling.

**Depends On:** Task 2, Task 5, Task 7

**Files to Modify:**
- `src/templates/exercises/index.html`
- `src/templates/exercises/detail.html`
- `src/templates/exercises/add.html`
- `src/templates/exercises/edit.html`

**Steps:**
1. For each exercise template:
2. Update exercise cards to use dark backgrounds
3. Update exercise images/videos to have appropriate borders
4. Update filter controls to use dark theme
5. Update exercise detail sections to use `card` class
6. Verify forms use dark theme form classes
7. Save each file

**Acceptance Criteria:**
- Exercise cards have dark backgrounds
- Exercise images are framed appropriately
- Filter controls use dark theme styling
- Exercise details are readable on dark backgrounds
- Forms use dark theme inputs

---

## Task 10: Update Profile Pages

**Description:** Ensure profile pages use dark theme styling with proper contrast.

**Depends On:** Task 2, Task 5, Task 7

**Files to Modify:**
- `src/templates/profile/view.html`
- `src/templates/profile/edit.html`
- `src/templates/profile/change_password.html`
- `src/templates/admin/view_profile.html`
- `src/templates/admin/edit_profile.html`

**Steps:**
1. For each profile template:
2. Update profile hero section to use `profile-hero` class
3. Update profile image to use `profile-image-large` class
4. Update profile sections to use `profile-section` class
5. Update BMI display to use `bmi-display` class
6. Update profile grids to use `profile-grid` class
7. Verify forms use dark theme form classes
8. Save each file

**Acceptance Criteria:**
- Profile pages display with dark backgrounds
- Profile sections use dark-themed cards
- Profile images have colored borders
- BMI information uses vibrant accent colors
- Profile forms use dark-themed inputs
- All text is readable with proper contrast

---

## Task 11: Update Authentication Pages

**Description:** Ensure login and registration pages use dark theme styling.

**Depends On:** Task 2, Task 5

**Files to Modify:**
- `src/templates/login.html`
- `src/templates/register.html`

**Steps:**
1. Open login.html
2. Update container to use dark background
3. Update form to use dark theme form classes
4. Update submit button to use `btn btn-primary`
5. Repeat for register.html
6. Save both files

**Acceptance Criteria:**
- Login page has dark background
- Registration page has dark background
- Forms use dark theme inputs
- Submit buttons have red-to-orange gradient
- Links are visible on dark backgrounds

---

## Task 12: Update Admin Pages

**Description:** Ensure admin dashboard and management pages use dark theme styling.

**Depends On:** Task 2, Task 5, Task 6, Task 7

**Files to Modify:**
- `src/templates/admin/users.html`
- `src/templates/admin/edit_user.html`
- `src/templates/admin/view_profile.html`
- `src/templates/admin/edit_profile.html`
- `src/templates/admin/blog/dashboard.html`
- `src/templates/admin/blog/create.html`
- `src/templates/admin/blog/edit.html`

**Steps:**
1. For each admin template:
2. Update page containers to use dark backgrounds
3. Update tables to use dark theme table styles
4. Update forms to use dark theme form classes
5. Update action buttons to use appropriate classes
6. Update badges to use dark theme badge styles
7. Save each file

**Acceptance Criteria:**
- Admin pages display with dark backgrounds
- User management table uses dark theme
- Admin forms use dark theme inputs
- Action buttons have appropriate colors
- Badges are vibrant and visible

---

## Task 13: Visual Testing and Verification

**Description:** Perform comprehensive visual testing across all pages to ensure dark theme is applied consistently.

**Depends On:** All previous tasks

**Files to Test:**
- All pages in the application

**Steps:**
1. Start the development server
2. Navigate to home page and verify dark theme
3. Navigate to login page and verify styling
4. Navigate to registration page and verify styling
5. Log in as regular user
6. Navigate to profile view and verify styling
7. Navigate to profile edit and verify styling
8. Navigate to progress tracking and verify styling
9. Navigate to exercise library and verify styling
10. Navigate to exercise detail and verify styling
11. Log in as admin
12. Navigate to admin dashboard and verify styling
13. Navigate to user management and verify styling
14. Test on mobile viewport (responsive)
15. Test in different browsers (Chrome, Firefox, Safari)
16. Document any issues found

**Acceptance Criteria:**
- All pages display with dark backgrounds
- All text is readable with proper contrast
- All interactive elements have proper hover/focus states
- No light theme elements are visible
- Responsive design works on mobile
- Cross-browser compatibility verified
- No console errors

---

## Task 14: Documentation Update

**Description:** Update documentation to reflect the dark theme implementation.

**Depends On:** Task 13

**Files to Modify:**
- `README.md`
- `THEME_UPDATE.md` (create if needed)

**Steps:**
1. Open README.md
2. Add section about dark theme
3. Document the color palette
4. Document CSS variable usage
5. Create THEME_UPDATE.md with implementation details
6. Document how to customize theme colors
7. Save files

**Acceptance Criteria:**
- README mentions dark theme
- Color palette is documented
- CSS variable usage is explained
- Customization guide is provided
- Documentation is clear and accurate
