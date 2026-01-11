# Plan: UI Layout and Styling

## Phase 1: Core Layout Shell Components [checkpoint: 5e6fe21]

- [x] Task: Write tests for AppLayout component `bbc0563`
  - [x] Test renders sidebar and main content area
  - [x] Test passes content via default slot
  - [x] Test applies correct CSS grid/flexbox structure
- [x] Task: Implement AppLayout.vue component `bbc0563`
  - [x] Create shell with sidebar area and content area
  - [x] Apply base styling (full height, CSS grid layout)
  - [x] Export from components/layout/index.ts
- [x] Task: Write tests for AppSidebar component `a87688c`
  - [x] Test renders navigation items
  - [x] Test Dashboard link visible to all roles
  - [x] Test Team Dashboard link visible only for manager role
  - [x] Test profile section at bottom with user avatar
  - [x] Test active state highlighting on current route
- [x] Task: Implement AppSidebar.vue component `a87688c`
  - [x] Create sidebar container with Navy background
  - [x] Add navigation items (Dashboard, Team Dashboard)
  - [x] Implement role-based visibility using useAuth composable
  - [x] Add profile section at bottom with avatar from Keycloak user info
  - [x] Style active nav item with Magenta highlight
- [x] Task: Write tests for AppHeader component `3881824`
  - [x] Test renders progress bar with percentage
  - [x] Test renders language selector with three flags
  - [x] Test language change emits event
  - [x] Test displays TSS PPM branding
- [x] Task: Implement AppHeader.vue component `3881824`
  - [x] Create header bar with flexbox layout
  - [x] Add progress bar component (receives percentage as prop)
  - [x] Add language selector with EN/NL/ES flag icons
  - [x] Wire language selector to vue-i18n locale change
  - [x] Add TSS PPM logo/branding
- [x] Task: Conductor - User Manual Verification 'Phase 1: Core Layout Shell Components' (Protocol in workflow.md) `5e6fe21`

## Phase 2: Card and Content Styling Components [checkpoint: c125ab2]

- [x] Task: Write tests for Card component `03028d8`
  - [x] Test renders slot content
  - [x] Test applies white background and shadow
  - [x] Test accepts optional padding prop
- [x] Task: Implement Card.vue component `03028d8`
  - [x] Create card container with white background
  - [x] Add subtle box-shadow
  - [x] Apply consistent border-radius
  - [x] Support padding variants via prop
- [x] Task: Write tests for SectionHeader component `03028d8`
  - [x] Test renders title text
  - [x] Test applies Navy color and Tahoma bold font
  - [x] Test supports optional subtitle
- [x] Task: Implement SectionHeader.vue component `03028d8`
  - [x] Create header with Navy (#004A91) color
  - [x] Apply Tahoma font-family, bold weight
  - [x] Support optional subtitle slot
- [x] Task: Write tests for FormField component `03028d8`
  - [x] Test renders label and input
  - [x] Test shows required asterisk when required prop true
  - [x] Test renders voice input icon when voiceEnabled prop true
  - [x] Test two-column layout in grid context
- [x] Task: Implement FormField.vue component `03028d8`
  - [x] Create wrapper with label and input slot
  - [x] Add required indicator styling
  - [x] Position voice input icon inside field (right side)
  - [x] Apply consistent input styling (border, height, focus state)
- [x] Task: Create base form input styles `03028d8`
  - [x] Add global CSS/SCSS for input, select, textarea elements
  - [x] Apply Tahoma font, consistent sizing
  - [x] Add focus states with Magenta outline
- [x] Task: Conductor - User Manual Verification 'Phase 2: Card and Content Styling Components' (Protocol in workflow.md) `c125ab2`

## Phase 3: Responsive Sidebar Behavior [checkpoint: 5d2c397]

- [x] Task: Write tests for sidebar responsive behavior `0c7509f`
  - [x] Test sidebar expanded on desktop (≥1024px)
  - [x] Test sidebar collapsed on tablet (768px-1023px)
  - [x] Test sidebar hidden on mobile (<768px)
  - [x] Test hamburger button visible on tablet/mobile
  - [x] Test hamburger click toggles sidebar
- [x] Task: Implement responsive sidebar logic `0c7509f`
  - [x] Add useSidebar composable for state management
  - [x] Track viewport width with resize observer
  - [x] Implement collapse/expand state
  - [x] Add CSS transitions for smooth animation (200-300ms)
- [x] Task: Implement hamburger menu button `0c7509f`
  - [x] Create HamburgerButton component
  - [x] Add to AppHeader when viewport < 1024px
  - [x] Wire click to toggle sidebar state
- [x] Task: Implement mobile sidebar overlay `0c7509f`
  - [x] Add overlay backdrop when sidebar open on mobile
  - [x] Click outside closes sidebar
  - [x] Slide-in animation from left
- [x] Task: Conductor - User Manual Verification 'Phase 3: Responsive Sidebar Behavior' (Protocol in workflow.md) `5d2c397`

## Phase 4: View Integration

- [x] Task: Integrate AppLayout into App.vue
  - [x] Wrap router-view with AppLayout
  - [x] Pass user role to sidebar
  - [x] Connect progress bar to review completion data
- [x] Task: Refactor GoalSettingView with new layout
  - [x] Wrap content sections in Card components
  - [x] Use SectionHeader for section titles
  - [x] Apply two-column FormField grid for goal form
  - [x] Ensure existing functionality preserved
- [x] Task: Refactor TeamDashboardView with new layout
  - [x] Wrap team list in Card component
  - [x] Use SectionHeader for page title
  - [x] Style TeamMemberCard to match design system
- [x] Task: Refactor ReviewScoringView with new layout (if exists)
  - [x] Apply Card components to scoring sections
  - [x] Use SectionHeader for WHAT/HOW axis sections
  - [x] Maintain existing scoring functionality
- [x] Task: Update any remaining views with layout
  - [x] Audit all views in src/views/
  - [x] Apply consistent Card and SectionHeader usage
- [ ] Task: Conductor - User Manual Verification 'Phase 4: View Integration' (Protocol in workflow.md)

## Phase 5: Polish and Internationalization

- [ ] Task: Add i18n translations for layout components
  - [ ] Add English translations (navigation labels, aria-labels)
  - [ ] Add Dutch translations
  - [ ] Add Spanish translations
- [ ] Task: Add aria-labels and accessibility attributes
  - [ ] Sidebar navigation landmark
  - [ ] Skip to main content link
  - [ ] Button aria-labels for hamburger menu
  - [ ] Language selector accessibility
- [ ] Task: Verify touch targets meet 44x44px minimum
  - [ ] Audit all clickable elements
  - [ ] Adjust padding/sizing where needed
- [ ] Task: Cross-browser and device testing
  - [ ] Test on Chrome, Firefox, Safari
  - [ ] Test on iOS Safari and Android Chrome
  - [ ] Fix any layout inconsistencies
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Polish and Internationalization' (Protocol in workflow.md)
