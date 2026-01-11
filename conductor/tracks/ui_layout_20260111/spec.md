# Specification: UI Layout and Styling

## Overview

Implement a modern, card-based UI layout system with sidebar navigation for the TSS PPM application. This replaces the current layout with a consistent design based on the approved mockup (requirements/PPM-color-scheme-and-spacing.png), applying brand colors (Magenta #CC0E70, Navy #004A91) and Tahoma typography throughout.

## Functional Requirements

### FR-1: Sidebar Navigation

- **FR-1.1:** Implement a vertical sidebar on the left side of the application
- **FR-1.2:** Sidebar contains the following navigation items:
  - **Dashboard** - Links to main dashboard showing personal review status per year (goals integrated here)
  - **Team Dashboard** - Manager-only link (hidden for Employee/HR/Admin roles) showing team members' review progress across stages (Goal Setting → Mid-Year → End-Year → Signature)
- **FR-1.3:** Profile section positioned at bottom-left of sidebar:
  - Display user avatar image from EntraID/Keycloak
  - Clicking opens profile/settings panel
  - Available to all roles
- **FR-1.4:** Active navigation item highlighted with brand styling

### FR-2: Responsive Sidebar Behavior

- **FR-2.1:** Desktop (≥1024px): Sidebar fully visible and expanded
- **FR-2.2:** Tablet (768px-1023px): Sidebar collapsed, hamburger menu icon to expand
- **FR-2.3:** Mobile (<768px): Sidebar hidden, hamburger menu icon slides sidebar in as overlay
- **FR-2.4:** Smooth transition animations for collapse/expand

### FR-3: Header Bar

- **FR-3.1:** Fixed header bar at top of content area (not full width, respects sidebar)
- **FR-3.2:** Progress bar showing review completion percentage (e.g., "6% Complete")
- **FR-3.3:** Language selector with flag icons for EN/NL/ES
- **FR-3.4:** TSS PPM branding/logo in header

### FR-4: Card-Based Content Layout

- **FR-4.1:** Content sections wrapped in white card containers with subtle shadow
- **FR-4.2:** Section headers in Navy Blue (#004A91), bold Tahoma font
- **FR-4.3:** Consistent padding and spacing between cards
- **FR-4.4:** Cards support the following section types:
  - Information cards (Employee Information)
  - Form cards with two-column grid layout
  - Text area cards (Executive Summary)
  - List cards (Goals & Results with drag handles)

### FR-5: Form Styling

- **FR-5.1:** Input fields with subtle borders and consistent height
- **FR-5.2:** Voice input microphone icons positioned inside text fields (right side)
- **FR-5.3:** Dropdown selects with consistent styling
- **FR-5.4:** Required field indicators (asterisk)
- **FR-5.5:** Two-column grid layout for form fields on desktop, single column on mobile

### FR-6: Apply Layout to All Views

- **FR-6.1:** GoalSettingView - Apply card layout to goal list and forms
- **FR-6.2:** TeamDashboardView - Apply card layout to team member list
- **FR-6.3:** ReviewScoringView - Apply card layout to scoring sections
- **FR-6.4:** Any other existing views receive consistent layout treatment

## Non-Functional Requirements

- **NFR-1:** All components must support i18n (EN/NL/ES)
- **NFR-2:** Transitions and animations should be smooth (CSS transitions, 200-300ms)
- **NFR-3:** Touch targets minimum 44x44px for mobile usability
- **NFR-4:** Layout must not break existing functionality
- **NFR-5:** Components should be reusable (AppLayout, AppSidebar, AppHeader, Card, SectionHeader)

## Acceptance Criteria

- [ ] Sidebar navigation visible on all views with Dashboard and role-based Team Dashboard links
- [ ] User profile with avatar displayed at bottom-left of sidebar
- [ ] Sidebar collapses to hamburger menu on tablet/mobile
- [ ] Header displays progress bar and language selector
- [ ] All content sections use card-based layout with consistent styling
- [ ] Form fields have consistent styling with voice input icons
- [ ] Layout is responsive across desktop, tablet, and mobile breakpoints
- [ ] Brand colors (Magenta/Navy) and Tahoma font applied throughout
- [ ] All existing tests continue to pass

## Out of Scope

- Session Code and "Resume Another Session" functionality in header
- New dashboard page implementation (only layout wrapper, not dashboard content)
- Changes to business logic or API endpoints
- New features beyond layout/styling
