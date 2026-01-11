# Plan: Admin Settings Panel

## Phase 1: Admin Navigation & User Management Backend [checkpoint: ]

- [x] Task: Add admin role detection to frontend
  - [x] Write tests for isAdmin computed property in AppSidebar
  - [x] Write tests for Admin menu item visibility by role
  - [x] Implement isAdmin check and conditional menu rendering
  - [x] Add i18n translations for "Admin" label (EN/NL/ES)

- [x] Task: Create admin routes and layout
  - [x] Write tests for /admin route guard (admin role only)
  - [x] Write tests for AdminView tab navigation
  - [x] Implement AdminView.vue with tab structure
  - [x] Create route configuration with role guard

- [x] Task: Create Keycloak Admin API integration
  - [x] Write tests for Keycloak admin client (get users, get user, update user)
  - [x] Write tests for role assignment via Keycloak API
  - [x] Write tests for user enable/disable via Keycloak API
  - [x] Implement KeycloakAdminService with service account auth

- [x] Task: Create user management API endpoints
  - [x] Write tests for GET /api/v1/admin/users (list with search/filter)
  - [x] Write tests for GET /api/v1/admin/users/{id} (user details)
  - [x] Write tests for PUT /api/v1/admin/users/{id}/roles (role assignment)
  - [x] Write tests for PUT /api/v1/admin/users/{id}/manager (manager assignment)
  - [x] Write tests for PUT /api/v1/admin/users/{id}/status (activate/deactivate)
  - [x] Write tests for POST /api/v1/admin/users/bulk (bulk operations)
  - [x] Write tests for admin role authorization on all endpoints
  - [x] Implement admin router with all endpoints
  - [x] Implement admin repository for local user data

- [x] Task: Create audit logging for admin actions
  - [x] Write tests for audit log creation on role change
  - [x] Write tests for audit log creation on user deactivation
  - [x] Write tests for audit log creation on manager assignment
  - [x] Implement audit logging in admin endpoints

- [ ] Task: Conductor - User Manual Verification 'Admin Navigation & User Management Backend' (Protocol in workflow.md)

## Phase 2: User Management Frontend [checkpoint: complete]

- [x] Task: Create UserList component
  - [x] Write tests for user table rendering
  - [x] Write tests for search input functionality
  - [x] Write tests for role filter dropdown
  - [x] Write tests for status filter dropdown
  - [x] Write tests for pagination controls
  - [x] Implement UserList.vue with data table

- [x] Task: Create UserDetailModal component
  - [x] Write tests for modal rendering with user data
  - [x] Write tests for role checkboxes
  - [x] Write tests for manager dropdown
  - [x] Write tests for save action
  - [x] Implement UserDetailModal.vue

- [x] Task: Create DeactivateUserModal component
  - [x] Write tests for confirmation dialog rendering
  - [x] Write tests for confirm/cancel actions
  - [x] Implement DeactivateUserModal.vue with confirmation

- [x] Task: Create BulkActionBar component
  - [x] Write tests for selection count display
  - [x] Write tests for bulk role assignment
  - [x] Write tests for bulk manager assignment
  - [x] Implement BulkActionBar.vue

- [x] Task: Integrate user management into AdminView
  - [x] Write tests for Users tab content
  - [x] Write tests for API integration
  - [x] Write tests for loading and error states
  - [x] Implement Users tab with all components

- [x] Task: Add i18n translations for user management UI
  - [x] Add English translations
  - [x] Add Dutch translations
  - [x] Add Spanish translations

- [x] Task: Conductor - User Manual Verification 'User Management Frontend' (Protocol in workflow.md)

## Phase 3: OpCo Settings & Business Unit Management [checkpoint: complete]

- [x] Task: Create OpCo settings database schema
  - [x] Write migration for opco_settings table (if not exists)
  - [x] Write migration for logo_url column
  - [x] Write migration for review_cycle_config columns

- [x] Task: Create OpCo settings API endpoints
  - [x] Write tests for GET /api/v1/admin/opco/settings
  - [x] Write tests for PUT /api/v1/admin/opco/settings
  - [x] Write tests for POST /api/v1/admin/opco/logo (file upload)
  - [x] Write tests for admin role authorization
  - [x] Implement opco settings router and repository

- [x] Task: Create business units API endpoints
  - [x] Write tests for GET /api/v1/admin/business-units
  - [x] Write tests for POST /api/v1/admin/business-units
  - [x] Write tests for PUT /api/v1/admin/business-units/{id}
  - [x] Write tests for DELETE /api/v1/admin/business-units/{id}
  - [x] Write tests for delete rejection when users assigned
  - [x] Write tests for admin role authorization
  - [x] Implement business units router and repository

- [x] Task: Create OpCoSettingsForm component
  - [x] Write tests for form rendering with current values
  - [x] Write tests for field validation
  - [x] Write tests for logo upload preview
  - [x] Write tests for save action
  - [x] Implement OpCoSettingsForm.vue

- [x] Task: Create BusinessUnitList component
  - [x] Write tests for list rendering
  - [x] Write tests for create button and modal
  - [x] Write tests for edit action
  - [x] Write tests for delete with confirmation
  - [x] Implement BusinessUnitList.vue

- [x] Task: Create BusinessUnitModal component
  - [x] Write tests for create mode
  - [x] Write tests for edit mode
  - [x] Write tests for validation
  - [x] Implement BusinessUnitModal.vue

- [x] Task: Integrate into AdminView
  - [x] Write tests for OpCo Settings tab
  - [x] Write tests for Business Units tab
  - [x] Implement tab content with components

- [x] Task: Add i18n translations for Phase 3 UI
  - [x] Add English translations
  - [x] Add Dutch translations
  - [x] Add Spanish translations

- [x] Task: Conductor - User Manual Verification 'OpCo Settings & Business Unit Management' (Protocol in workflow.md)

## Phase 4: System Configuration [checkpoint: complete]

- [x] Task: Create system configuration API endpoints
  - [x] Write tests for GET /api/v1/admin/system/health
  - [x] Write tests for GET /api/v1/admin/system/voice-config
  - [x] Write tests for PUT /api/v1/admin/system/voice-config
  - [x] Write tests for GET /api/v1/admin/system/review-periods
  - [x] Write tests for PUT /api/v1/admin/system/review-periods
  - [x] Write tests for admin role authorization
  - [x] Implement system config router

- [x] Task: Create SystemHealthPanel component
  - [x] Write tests for service status display (API, DB, Keycloak, Voice)
  - [x] Write tests for status indicators (green/red)
  - [x] Write tests for refresh action
  - [x] Implement SystemHealthPanel.vue

- [x] Task: Create VoiceConfigForm component (combined into SystemConfigForm)
  - [x] Write tests for form rendering
  - [x] Write tests for endpoint URL validation
  - [x] Write tests for save action
  - [x] Implement SystemConfigForm.vue (voice config + review periods)

- [x] Task: Create ReviewPeriodSettings component (combined into SystemConfigForm)
  - [x] Write tests for period date inputs
  - [x] Write tests for open/close period actions
  - [x] Write tests for validation
  - [x] Implement as part of SystemConfigForm.vue

- [x] Task: Integrate into AdminView System tab
  - [x] Write tests for System tab content
  - [x] Implement tab with all components

- [x] Task: Add i18n translations for system config UI
  - [x] Add English translations
  - [x] Add Dutch translations
  - [x] Add Spanish translations

- [x] Task: Conductor - User Manual Verification 'System Configuration' (Protocol in workflow.md)

## Phase 5: Audit Log Viewer [checkpoint: complete]

- [x] Task: Create audit log API endpoints
  - [x] Write tests for GET /api/v1/admin/audit-logs (with pagination)
  - [x] Write tests for date range filter
  - [x] Write tests for user filter
  - [x] Write tests for action type filter
  - [x] Write tests for entity type filter
  - [x] Write tests for GET /api/v1/admin/audit-logs/export (CSV)
  - [x] Write tests for admin role authorization
  - [x] Implement audit log router with filters

- [x] Task: Create AuditLogList component
  - [x] Write tests for table rendering
  - [x] Write tests for date range picker
  - [x] Write tests for filter dropdowns
  - [x] Write tests for pagination
  - [x] Write tests for export button
  - [x] Implement AuditLogList.vue

- [x] Task: Create AuditLogDetailModal component
  - [x] Write tests for detail view rendering
  - [x] Write tests for JSON details display
  - [x] Implement AuditLogDetailModal.vue

- [x] Task: Integrate into AdminView Audit Logs tab
  - [x] Write tests for Audit Logs tab content
  - [x] Implement tab with components

- [x] Task: Add i18n translations for audit log UI
  - [x] Add English translations
  - [x] Add Dutch translations
  - [x] Add Spanish translations

- [x] Task: Conductor - User Manual Verification 'Audit Log Viewer' (Protocol in workflow.md)

## Phase 6: Integration Testing & Polish [checkpoint: complete]

- [x] Task: End-to-end admin flow testing
  - [x] Test complete user management flow
  - [x] Test OpCo settings update flow
  - [x] Test business unit CRUD flow
  - [x] Test system configuration flow
  - [x] Test audit log viewing and export

- [x] Task: Security verification
  - [x] Verify admin role required for all endpoints
  - [x] Verify no review content accessible
  - [x] Verify all actions logged to audit trail
  - [x] Verify Keycloak integration security

- [x] Task: Responsive design verification
  - [x] Test admin panel on desktop
  - [x] Test admin panel on tablet
  - [x] Verify tab navigation on mobile

- [x] Task: Conductor - User Manual Verification 'Integration Testing & Polish' (Protocol in workflow.md)
