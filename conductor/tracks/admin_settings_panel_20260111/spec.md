# Spec: Admin Settings Panel

## Overview

Implement a comprehensive Admin Settings Panel accessible via the sidebar navigation, providing system administrators with tools to manage users, OpCo settings, business units, system configuration, and audit logs. The admin panel follows GDPR compliance by explicitly preventing access to individual review content.

## Target Users

- **ADMIN** role users only

## Functional Requirements

### FR-1: Admin Navigation

- Add "Admin" menu item to the sidebar, visible only for users with `admin` role
- Route to `/admin` with a multi-tab dashboard layout
- Tabs for: Users, OpCo Settings, Business Units, System, Audit Logs

### FR-2: User Management (Phase 1)

- **List Users:** Display all users within the OpCo with columns: Name, Email, Roles, Status, Manager, Last Login
- **Search & Filter:** Search by name/email, filter by role (employee/manager/hr/admin) and status (active/inactive)
- **View User Details:** Modal or detail view showing user information from Keycloak
- **Edit User Roles:** Assign/remove roles via Keycloak Admin API
- **Assign Manager:** Set/change user's manager relationship
- **Deactivate User:** Disable user account in Keycloak (with confirmation dialog)
- **Bulk Operations:** Select multiple users to assign roles or manager
- **Keycloak Integration:** All user data synced via Keycloak Admin REST API

### FR-3: OpCo Settings (Phase 2)

- **View Settings:** Display current OpCo configuration (name, default language, review cycle dates)
- **Edit Settings:** Update OpCo name, default language preference
- **Upload Logo:** Upload company logo for branding (PDF reports, login page)
- **Review Cycle Configuration:** Set dates for goal setting, mid-year, and end-year review periods

### FR-4: Business Unit Management (Phase 2)

- **List Business Units:** Display all business units within the OpCo
- **Create Business Unit:** Add new business unit with name and optional description
- **Edit Business Unit:** Update business unit details
- **Delete Business Unit:** Remove business unit (with confirmation dialog, only if no users assigned)

### FR-5: System Configuration (Phase 3)

- **Voice API Settings:** Configure voice-to-text API endpoint and credentials
- **System Health:** Display service status (API, database, Keycloak, voice service)
- **Review Period Management:** Open/close review periods, set deadlines

### FR-6: Audit Log Viewer (Phase 3)

- **List Audit Logs:** Display audit entries with columns: Timestamp, User, Action, Entity, Details
- **Search & Filter:** Filter by date range, user, action type, entity type
- **Export:** Export audit logs to CSV for compliance reporting
- **Pagination:** Handle large datasets with server-side pagination

### FR-7: Activity Logging

- All admin actions must be logged to the audit_logs table:
  - User role changes
  - User deactivation/reactivation
  - Manager reassignments
  - OpCo settings changes
  - Business unit create/update/delete
  - System configuration changes

### FR-8: Confirmation Dialogs

- Destructive actions require confirmation:
  - Deactivate user
  - Delete business unit
  - Bulk role changes

## Non-Functional Requirements

### NFR-1: Security

- All admin endpoints require `admin` role in JWT
- No access to review content, scores, or employee performance data
- All actions logged for audit trail
- Keycloak Admin API calls use service account credentials

### NFR-2: Performance

- User list should load within 2 seconds for up to 1000 users
- Pagination for lists exceeding 50 items
- Audit log queries optimized with proper indexing

### NFR-3: Usability

- Consistent styling with existing application (Magenta/Navy Blue, Tahoma font)
- Responsive design for tablet use
- Clear feedback for all actions (success/error toasts)
- Keyboard accessible

### NFR-4: Multi-language

- All admin UI labels translated (EN/NL/ES)
- Admin-specific i18n keys in translation files

## Acceptance Criteria

1. Admin users see "Admin" menu item in sidebar; other roles do not
2. User management allows viewing, searching, filtering, and editing users via Keycloak
3. Bulk operations work for role assignment and manager assignment
4. OpCo settings can be viewed and edited with logo upload
5. Business units can be created, edited, and deleted
6. System health dashboard shows status of all services
7. Audit logs are searchable and exportable
8. All admin actions are logged to audit trail
9. Confirmation dialogs appear for destructive actions
10. UI is fully translated in EN/NL/ES

## Out of Scope

- Direct database user management (all via Keycloak)
- Access to individual review content or scores (GDPR)
- User self-registration or password reset (handled by Keycloak)
- Multi-OpCo management (each OpCo has separate instance)
- Real-time notifications for admin events

## Technical Notes

- Backend: New `/api/v1/admin/*` endpoints with admin role guard
- Keycloak: Use Admin REST API for user management
- Frontend: New AdminView with tab components
- Database: May need tables for OpCo settings, business units if not existing
