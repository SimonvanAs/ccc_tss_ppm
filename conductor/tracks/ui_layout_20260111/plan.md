# Plan: UI Layout and Styling

## Phase 1: Core Layout Shell Components

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
- [ ] Task: Write tests for AppHeader component
  - [ ] Test renders progress bar with percentage
  - [ ] Test renders language selector with three flags
  - [ ] Test language change emits event
  - [ ] Test displays TSS PPM branding
- [ ] Task: Implement AppHeader.vue component
  - [ ] Create header bar with flexbox layout
  - [ ] Add progress bar component (receives percentage as prop)
  - [ ] Add language selector with EN/NL/ES flag icons
  - [ ] Wire language selector to vue-i18n locale change
  - [ ] Add TSS PPM logo/branding
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Core Layout Shell Components' (Protocol in workflow.md)

## Phase 2: Card and Content Styling Components

- [ ] Task: Write tests for Card component
  - [ ] Test renders slot content
  - [ ] Test applies white background and shadow
  - [ ] Test accepts optional padding prop
- [ ] Task: Implement Card.vue component
  - [ ] Create card container with white background
  - [ ] Add subtle box-shadow
  - [ ] Apply consistent border-radius
  - [ ] Support padding variants via prop
- [ ] Task: Write tests for SectionHeader component
  - [ ] Test renders title text
  - [ ] Test applies Navy color and Tahoma bold font
  - [ ] Test supports optional subtitle
- [ ] Task: Implement SectionHeader.vue component
  - [ ] Create header with Navy (#004A91) color
  - [ ] Apply Tahoma font-family, bold weight
  - [ ] Support optional subtitle slot
- [ ] Task: Write tests for FormField component
  - [ ] Test renders label and input
  - [ ] Test shows required asterisk when required prop true
  - [ ] Test renders voice input icon when voiceEnabled prop true
  - [ ] Test two-column layout in grid context
- [ ] Task: Implement FormField.vue component
  - [ ] Create wrapper with label and input slot
  - [ ] Add required indicator styling
  - [ ] Position voice input icon inside field (right side)
  - [ ] Apply consistent input styling (border, height, focus state)
- [ ] Task: Create base form input styles
  - [ ] Add global CSS/SCSS for input, select, textarea elements
  - [ ] Apply Tahoma font, consistent sizing
  - [ ] Add focus states with Magenta outline
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Card and Content Styling Components' (Protocol in workflow.md)

## Phase 3: Responsive Sidebar Behavior

- [ ] Task: Write tests for sidebar responsive behavior
  - [ ] Test sidebar expanded on desktop (≥1024px)
  - [ ] Test sidebar collapsed on tablet (768px-1023px)
  - [ ] Test sidebar hidden on mobile (<768px)
  - [ ] Test hamburger button visible on tablet/mobile
  - [ ] Test hamburger click toggles sidebar
- [ ] Task: Implement responsive sidebar logic
  - [ ] Add useSidebar composable for state management
  - [ ] Track viewport width with resize observer
  - [ ] Implement collapse/expand state
  - [ ] Add CSS transitions for smooth animation (200-300ms)
- [ ] Task: Implement hamburger menu button
  - [ ] Create HamburgerButton component
  - [ ] Add to AppHeader when viewport < 1024px
  - [ ] Wire click to toggle sidebar state
- [ ] Task: Implement mobile sidebar overlay
  - [ ] Add overlay backdrop when sidebar open on mobile
  - [ ] Click outside closes sidebar
  - [ ] Slide-in animation from left
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Responsive Sidebar Behavior' (Protocol in workflow.md)

## Phase 4: View Integration

- [ ] Task: Integrate AppLayout into App.vue
  - [ ] Wrap router-view with AppLayout
  - [ ] Pass user role to sidebar
  - [ ] Connect progress bar to review completion data
- [ ] Task: Refactor GoalSettingView with new layout
  - [ ] Wrap content sections in Card components
  - [ ] Use SectionHeader for section titles
  - [ ] Apply two-column FormField grid for goal form
  - [ ] Ensure existing functionality preserved
- [ ] Task: Refactor TeamDashboardView with new layout
  - [ ] Wrap team list in Card component
  - [ ] Use SectionHeader for page title
  - [ ] Style TeamMemberCard to match design system
- [ ] Task: Refactor ReviewScoringView with new layout (if exists)
  - [ ] Apply Card components to scoring sections
  - [ ] Use SectionHeader for WHAT/HOW axis sections
  - [ ] Maintain existing scoring functionality
- [ ] Task: Update any remaining views with layout
  - [ ] Audit all views in src/views/
  - [ ] Apply consistent Card and SectionHeader usage
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
