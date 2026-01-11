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

- [ ] Task: Create Keycloak Admin API integration
  - [ ] Write tests for Keycloak admin client (get users, get user, update user)
  - [ ] Write tests for role assignment via Keycloak API
  - [ ] Write tests for user enable/disable via Keycloak API
  - [ ] Implement KeycloakAdminService with service account auth

- [ ] Task: Create user management API endpoints
  - [ ] Write tests for GET /api/v1/admin/users (list with search/filter)
  - [ ] Write tests for GET /api/v1/admin/users/{id} (user details)
  - [ ] Write tests for PUT /api/v1/admin/users/{id}/roles (role assignment)
  - [ ] Write tests for PUT /api/v1/admin/users/{id}/manager (manager assignment)
  - [ ] Write tests for PUT /api/v1/admin/users/{id}/status (activate/deactivate)
  - [ ] Write tests for POST /api/v1/admin/users/bulk (bulk operations)
  - [ ] Write tests for admin role authorization on all endpoints
  - [ ] Implement admin router with all endpoints
  - [ ] Implement admin repository for local user data

- [ ] Task: Create audit logging for admin actions
  - [ ] Write tests for audit log creation on role change
  - [ ] Write tests for audit log creation on user deactivation
  - [ ] Write tests for audit log creation on manager assignment
  - [ ] Implement audit logging in admin endpoints

- [ ] Task: Conductor - User Manual Verification 'Admin Navigation & User Management Backend' (Protocol in workflow.md)

## Phase 2: User Management Frontend [checkpoint: ]

- [ ] Task: Create UserList component
  - [ ] Write tests for user table rendering
  - [ ] Write tests for search input functionality
  - [ ] Write tests for role filter dropdown
  - [ ] Write tests for status filter dropdown
  - [ ] Write tests for pagination controls
  - [ ] Implement UserList.vue with data table

- [ ] Task: Create UserDetailModal component
  - [ ] Write tests for modal rendering with user data
  - [ ] Write tests for role checkboxes
  - [ ] Write tests for manager dropdown
  - [ ] Write tests for save action
  - [ ] Implement UserDetailModal.vue

- [ ] Task: Create DeactivateUserModal component
  - [ ] Write tests for confirmation dialog rendering
  - [ ] Write tests for confirm/cancel actions
  - [ ] Implement DeactivateUserModal.vue with confirmation

- [ ] Task: Create BulkActionBar component
  - [ ] Write tests for selection count display
  - [ ] Write tests for bulk role assignment
  - [ ] Write tests for bulk manager assignment
  - [ ] Implement BulkActionBar.vue

- [ ] Task: Integrate user management into AdminView
  - [ ] Write tests for Users tab content
  - [ ] Write tests for API integration
  - [ ] Write tests for loading and error states
  - [ ] Implement Users tab with all components

- [ ] Task: Add i18n translations for user management UI
  - [ ] Add English translations
  - [ ] Add Dutch translations
  - [ ] Add Spanish translations

- [ ] Task: Conductor - User Manual Verification 'User Management Frontend' (Protocol in workflow.md)

## Phase 3: OpCo Settings & Business Unit Management [checkpoint: ]

- [ ] Task: Create OpCo settings database schema
  - [ ] Write migration for opco_settings table (if not exists)
  - [ ] Write migration for logo_url column
  - [ ] Write migration for review_cycle_config columns

- [ ] Task: Create OpCo settings API endpoints
  - [ ] Write tests for GET /api/v1/admin/opco/settings
  - [ ] Write tests for PUT /api/v1/admin/opco/settings
  - [ ] Write tests for POST /api/v1/admin/opco/logo (file upload)
  - [ ] Write tests for admin role authorization
  - [ ] Implement opco settings router and repository

- [ ] Task: Create business units API endpoints
  - [ ] Write tests for GET /api/v1/admin/business-units
  - [ ] Write tests for POST /api/v1/admin/business-units
  - [ ] Write tests for PUT /api/v1/admin/business-units/{id}
  - [ ] Write tests for DELETE /api/v1/admin/business-units/{id}
  - [ ] Write tests for delete rejection when users assigned
  - [ ] Write tests for admin role authorization
  - [ ] Implement business units router and repository

- [ ] Task: Create OpCoSettingsForm component
  - [ ] Write tests for form rendering with current values
  - [ ] Write tests for field validation
  - [ ] Write tests for logo upload preview
  - [ ] Write tests for save action
  - [ ] Implement OpCoSettingsForm.vue

- [ ] Task: Create BusinessUnitList component
  - [ ] Write tests for list rendering
  - [ ] Write tests for create button and modal
  - [ ] Write tests for edit action
  - [ ] Write tests for delete with confirmation
  - [ ] Implement BusinessUnitList.vue

- [ ] Task: Create BusinessUnitModal component
  - [ ] Write tests for create mode
  - [ ] Write tests for edit mode
  - [ ] Write tests for validation
  - [ ] Implement BusinessUnitModal.vue

- [ ] Task: Integrate into AdminView
  - [ ] Write tests for OpCo Settings tab
  - [ ] Write tests for Business Units tab
  - [ ] Implement tab content with components

- [ ] Task: Add i18n translations for Phase 3 UI
  - [ ] Add English translations
  - [ ] Add Dutch translations
  - [ ] Add Spanish translations

- [ ] Task: Conductor - User Manual Verification 'OpCo Settings & Business Unit Management' (Protocol in workflow.md)

## Phase 4: System Configuration [checkpoint: ]

- [ ] Task: Create system configuration API endpoints
  - [ ] Write tests for GET /api/v1/admin/system/health
  - [ ] Write tests for GET /api/v1/admin/system/voice-config
  - [ ] Write tests for PUT /api/v1/admin/system/voice-config
  - [ ] Write tests for GET /api/v1/admin/system/review-periods
  - [ ] Write tests for PUT /api/v1/admin/system/review-periods
  - [ ] Write tests for admin role authorization
  - [ ] Implement system config router

- [ ] Task: Create SystemHealthPanel component
  - [ ] Write tests for service status display (API, DB, Keycloak, Voice)
  - [ ] Write tests for status indicators (green/red)
  - [ ] Write tests for refresh action
  - [ ] Implement SystemHealthPanel.vue

- [ ] Task: Create VoiceConfigForm component
  - [ ] Write tests for form rendering
  - [ ] Write tests for endpoint URL validation
  - [ ] Write tests for save action
  - [ ] Implement VoiceConfigForm.vue

- [ ] Task: Create ReviewPeriodSettings component
  - [ ] Write tests for period date inputs
  - [ ] Write tests for open/close period actions
  - [ ] Write tests for validation
  - [ ] Implement ReviewPeriodSettings.vue

- [ ] Task: Integrate into AdminView System tab
  - [ ] Write tests for System tab content
  - [ ] Implement tab with all components

- [ ] Task: Add i18n translations for system config UI
  - [ ] Add English translations
  - [ ] Add Dutch translations
  - [ ] Add Spanish translations

- [ ] Task: Conductor - User Manual Verification 'System Configuration' (Protocol in workflow.md)

## Phase 5: Audit Log Viewer [checkpoint: ]

- [ ] Task: Create audit log API endpoints
  - [ ] Write tests for GET /api/v1/admin/audit-logs (with pagination)
  - [ ] Write tests for date range filter
  - [ ] Write tests for user filter
  - [ ] Write tests for action type filter
  - [ ] Write tests for entity type filter
  - [ ] Write tests for GET /api/v1/admin/audit-logs/export (CSV)
  - [ ] Write tests for admin role authorization
  - [ ] Implement audit log router with filters

- [ ] Task: Create AuditLogList component
  - [ ] Write tests for table rendering
  - [ ] Write tests for date range picker
  - [ ] Write tests for filter dropdowns
  - [ ] Write tests for pagination
  - [ ] Write tests for export button
  - [ ] Implement AuditLogList.vue

- [ ] Task: Create AuditLogDetailModal component
  - [ ] Write tests for detail view rendering
  - [ ] Write tests for JSON details display
  - [ ] Implement AuditLogDetailModal.vue

- [ ] Task: Integrate into AdminView Audit Logs tab
  - [ ] Write tests for Audit Logs tab content
  - [ ] Implement tab with components

- [ ] Task: Add i18n translations for audit log UI
  - [ ] Add English translations
  - [ ] Add Dutch translations
  - [ ] Add Spanish translations

- [ ] Task: Conductor - User Manual Verification 'Audit Log Viewer' (Protocol in workflow.md)

## Phase 6: Integration Testing & Polish [checkpoint: ]

- [ ] Task: End-to-end admin flow testing
  - [ ] Test complete user management flow
  - [ ] Test OpCo settings update flow
  - [ ] Test business unit CRUD flow
  - [ ] Test system configuration flow
  - [ ] Test audit log viewing and export

- [ ] Task: Security verification
  - [ ] Verify admin role required for all endpoints
  - [ ] Verify no review content accessible
  - [ ] Verify all actions logged to audit trail
  - [ ] Verify Keycloak integration security

- [ ] Task: Responsive design verification
  - [ ] Test admin panel on desktop
  - [ ] Test admin panel on tablet
  - [ ] Verify tab navigation on mobile

- [ ] Task: Conductor - User Manual Verification 'Integration Testing & Polish' (Protocol in workflow.md)
