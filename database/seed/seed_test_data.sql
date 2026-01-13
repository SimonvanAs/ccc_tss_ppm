-- TSS PPM v3.0 - Test Seed Data for Scoring Flow
-- Run: docker exec -i tss_ppm_db psql -U ppm -d tss_ppm < database/seed/seed_test_data.sql

-- Use fixed UUIDs for predictable testing

-- ============================================================================
-- OPERATING COMPANY (OpCo) - Required before any users/reviews
-- ============================================================================

INSERT INTO opcos (id, name, code, default_language)
VALUES (
    '11111111-1111-1111-1111-111111111111',
    'TSS Test Company',
    'TSS',
    'en'
) ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    default_language = EXCLUDED.default_language;

-- ============================================================================
-- EMMA EMPLOYEE USER (synced from Keycloak)
-- ============================================================================

INSERT INTO users (id, keycloak_id, opco_id, email, first_name, last_name, function_title, tov_level, roles)
VALUES (
    '22222222-2222-2222-2222-222222222222',
    'e0000000-0000-0000-0000-000000000001',
    '11111111-1111-1111-1111-111111111111',
    'employee@tss.eu',
    'Emma',
    'Employee',
    'Software Developer',
    'B',
    ARRAY['employee']
) ON CONFLICT (keycloak_id) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    email = EXCLUDED.email;

-- ============================================================================
-- HR USER (synced from Keycloak)
-- ============================================================================

INSERT INTO users (id, keycloak_id, opco_id, email, first_name, last_name, function_title, roles)
VALUES (
    'cccccccc-cccc-cccc-cccc-cccccccccccc',
    'e0000000-0000-0000-0000-000000000003',
    '11111111-1111-1111-1111-111111111111',
    'hr@tss.eu',
    'Hannah',
    'HR',
    'HR Business Partner',
    ARRAY['employee', 'hr']
) ON CONFLICT (keycloak_id) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    email = EXCLUDED.email,
    roles = EXCLUDED.roles;

-- ============================================================================
-- ADMIN USER (synced from Keycloak)
-- ============================================================================

INSERT INTO users (id, keycloak_id, opco_id, email, first_name, last_name, function_title, roles)
VALUES (
    '99999999-9999-9999-9999-999999999999',
    'e0000000-0000-0000-0000-000000000004',
    '11111111-1111-1111-1111-111111111111',
    'admin@tss.eu',
    'Adam',
    'Admin',
    'System Administrator',
    ARRAY['employee', 'manager', 'hr', 'admin']
) ON CONFLICT (keycloak_id) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    email = EXCLUDED.email,
    roles = EXCLUDED.roles;

-- ============================================================================
-- USERS (additional test users)
-- ============================================================================

-- Manager user (Michael Manager from Keycloak)
INSERT INTO users (id, keycloak_id, opco_id, email, first_name, last_name, function_title, tov_level, roles)
VALUES (
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'e0000000-0000-0000-0000-000000000002',
    '11111111-1111-1111-1111-111111111111',
    'manager@tss.eu',
    'Michael',
    'Manager',
    'Team Lead',
    'B',
    ARRAY['employee', 'manager']
) ON CONFLICT (keycloak_id) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    roles = EXCLUDED.roles;

-- Update employee to have the manager
UPDATE users
SET manager_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    tov_level = 'B',
    function_title = 'Software Developer'
WHERE id = '22222222-2222-2222-2222-222222222222';

-- Add a second employee for more testing
INSERT INTO users (id, keycloak_id, opco_id, email, first_name, last_name, function_title, tov_level, roles, manager_id)
VALUES (
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    'employee2-keycloak-id',
    '11111111-1111-1111-1111-111111111111',
    'john.doe@tss.eu',
    'John',
    'Doe',
    'Senior Developer',
    'B',
    ARRAY['employee'],
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
) ON CONFLICT (keycloak_id) DO NOTHING;

-- ============================================================================
-- REVIEWS
-- ============================================================================

-- ============================================================================
-- EMMA EMPLOYEE - HISTORICAL REVIEWS (2024, 2025) - Full workflow completed
-- 2026 is left empty for starting a new flow
-- ============================================================================

-- Clean up any existing Emma 2026 reviews first (for re-runnability)
DELETE FROM goals WHERE review_id IN (
    SELECT id FROM reviews
    WHERE employee_id = '22222222-2222-2222-2222-222222222222'
    AND review_year = 2026
);
DELETE FROM reviews
WHERE employee_id = '22222222-2222-2222-2222-222222222222'
AND review_year = 2026;

-- 2024 REVIEWS - All stages ARCHIVED (completed previous year)
-- Goal Setting 2024
INSERT INTO reviews (id, opco_id, employee_id, manager_id, review_year, stage, status, tov_level,
    what_score, how_score, grid_position_what, grid_position_how, what_veto_active, how_veto_active,
    employee_signature_date, manager_signature_date, summary_comments)
VALUES (
    'e2024001-cccc-cccc-cccc-cccccccccccc',
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    2024,
    'GOAL_SETTING',
    'ARCHIVED',
    'B',
    NULL, NULL, NULL, NULL, false, false,
    '2024-01-20 10:00:00+00',
    '2024-01-22 14:30:00+00',
    'Goals for 2024 approved. Focus on project delivery and technical skills development.'
) ON CONFLICT (employee_id, review_year, stage) DO UPDATE SET
    status = EXCLUDED.status,
    employee_signature_date = EXCLUDED.employee_signature_date,
    manager_signature_date = EXCLUDED.manager_signature_date;

-- Mid-Year Review 2024
INSERT INTO reviews (id, opco_id, employee_id, manager_id, review_year, stage, status, tov_level,
    what_score, how_score, grid_position_what, grid_position_how, what_veto_active, how_veto_active,
    employee_signature_date, manager_signature_date, summary_comments)
VALUES (
    'e2024002-cccc-cccc-cccc-cccccccccccc',
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    2024,
    'MID_YEAR_REVIEW',
    'ARCHIVED',
    'B',
    2.20, 2.10, 2, 2, false, false,
    '2024-07-15 09:00:00+00',
    '2024-07-18 11:00:00+00',
    'Good progress on Q1-Q2 objectives. Continue focus on customer satisfaction and code quality improvements.'
) ON CONFLICT (employee_id, review_year, stage) DO UPDATE SET
    status = EXCLUDED.status,
    what_score = EXCLUDED.what_score,
    how_score = EXCLUDED.how_score,
    grid_position_what = EXCLUDED.grid_position_what,
    grid_position_how = EXCLUDED.grid_position_how;

-- End-Year Review 2024
INSERT INTO reviews (id, opco_id, employee_id, manager_id, review_year, stage, status, tov_level,
    what_score, how_score, grid_position_what, grid_position_how, what_veto_active, how_veto_active,
    employee_signature_date, manager_signature_date, summary_comments)
VALUES (
    'e2024003-cccc-cccc-cccc-cccccccccccc',
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    2024,
    'END_YEAR_REVIEW',
    'ARCHIVED',
    'B',
    2.35, 2.25, 2, 2, false, false,
    '2024-12-10 10:00:00+00',
    '2024-12-12 15:00:00+00',
    'Strong year overall. Met all key objectives and showed improvement in competencies. Ready for more challenging assignments in 2025.'
) ON CONFLICT (employee_id, review_year, stage) DO UPDATE SET
    status = EXCLUDED.status,
    what_score = EXCLUDED.what_score,
    how_score = EXCLUDED.how_score,
    grid_position_what = EXCLUDED.grid_position_what,
    grid_position_how = EXCLUDED.grid_position_how;

-- 2025 REVIEWS - All stages SIGNED (completed current year)
-- Goal Setting 2025
INSERT INTO reviews (id, opco_id, employee_id, manager_id, review_year, stage, status, tov_level,
    what_score, how_score, grid_position_what, grid_position_how, what_veto_active, how_veto_active,
    employee_signature_date, manager_signature_date, summary_comments)
VALUES (
    'e2025001-cccc-cccc-cccc-cccccccccccc',
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    2025,
    'GOAL_SETTING',
    'SIGNED',
    'B',
    NULL, NULL, NULL, NULL, false, false,
    '2025-01-15 10:00:00+00',
    '2025-01-17 14:00:00+00',
    'Ambitious goals set for 2025 focusing on leadership development and key account management.'
) ON CONFLICT (employee_id, review_year, stage) DO UPDATE SET
    status = EXCLUDED.status,
    employee_signature_date = EXCLUDED.employee_signature_date,
    manager_signature_date = EXCLUDED.manager_signature_date;

-- Mid-Year Review 2025
INSERT INTO reviews (id, opco_id, employee_id, manager_id, review_year, stage, status, tov_level,
    what_score, how_score, grid_position_what, grid_position_how, what_veto_active, how_veto_active,
    employee_signature_date, manager_signature_date, summary_comments)
VALUES (
    'e2025002-cccc-cccc-cccc-cccccccccccc',
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    2025,
    'MID_YEAR_REVIEW',
    'SIGNED',
    'B',
    2.45, 2.35, 2, 2, false, false,
    '2025-07-10 09:30:00+00',
    '2025-07-12 16:00:00+00',
    'Excellent mid-year performance. Exceeded expectations on key account retention. Continue development in leadership competencies.'
) ON CONFLICT (employee_id, review_year, stage) DO UPDATE SET
    status = EXCLUDED.status,
    what_score = EXCLUDED.what_score,
    how_score = EXCLUDED.how_score,
    grid_position_what = EXCLUDED.grid_position_what,
    grid_position_how = EXCLUDED.grid_position_how;

-- End-Year Review 2025
INSERT INTO reviews (id, opco_id, employee_id, manager_id, review_year, stage, status, tov_level,
    what_score, how_score, grid_position_what, grid_position_how, what_veto_active, how_veto_active,
    employee_signature_date, manager_signature_date, summary_comments)
VALUES (
    'e2025003-cccc-cccc-cccc-cccccccccccc',
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    2025,
    'END_YEAR_REVIEW',
    'SIGNED',
    'B',
    2.60, 2.50, 3, 2, false, false,
    '2025-12-08 10:00:00+00',
    '2025-12-10 14:30:00+00',
    'Outstanding year! Exceeded goals and demonstrated strong growth. Recommended for promotion consideration.'
) ON CONFLICT (employee_id, review_year, stage) DO UPDATE SET
    status = EXCLUDED.status,
    what_score = EXCLUDED.what_score,
    how_score = EXCLUDED.how_score,
    grid_position_what = EXCLUDED.grid_position_what,
    grid_position_how = EXCLUDED.grid_position_how;

-- NOTE: 2026 is intentionally left empty for Emma to start a new workflow

-- Review for John Doe - DRAFT for 2026
INSERT INTO reviews (id, opco_id, employee_id, manager_id, review_year, stage, status, tov_level)
VALUES (
    'dddddddd-dddd-dddd-dddd-dddddddddddd',
    '11111111-1111-1111-1111-111111111111',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    2026,
    'END_YEAR_REVIEW',
    'DRAFT',
    'B'
) ON CONFLICT (employee_id, review_year, stage) DO NOTHING;

-- ============================================================================
-- GOALS for Emma's Historical Reviews (2024, 2025)
-- ============================================================================

-- Delete any existing goals for Emma's historical reviews first
DELETE FROM goals WHERE review_id IN (
    'e2024001-cccc-cccc-cccc-cccccccccccc',
    'e2024002-cccc-cccc-cccc-cccccccccccc',
    'e2024003-cccc-cccc-cccc-cccccccccccc',
    'e2025001-cccc-cccc-cccc-cccccccccccc',
    'e2025002-cccc-cccc-cccc-cccccccccccc',
    'e2025003-cccc-cccc-cccc-cccccccccccc'
);

-- 2024 Goal Setting Goals (carried through all 2024 stages)
INSERT INTO goals (id, review_id, goal_type, title, description, weight, display_order, score)
VALUES
    -- Goal Setting 2024 (no scores - just goal definitions)
    ('a2024001-0001-0001-0001-aaaaaaaaaaaa', 'e2024001-cccc-cccc-cccc-cccccccccccc',
     'STANDARD', 'Complete Q1-Q2 Project Deliverables',
     'Deliver all assigned project milestones on time and within budget',
     35, 0, NULL),
    ('a2024001-0002-0002-0002-aaaaaaaaaaaa', 'e2024001-cccc-cccc-cccc-cccccccccccc',
     'STANDARD', 'Improve Technical Skills',
     'Complete AWS certification and improve code review turnaround time',
     25, 1, NULL),
    ('a2024001-0003-0003-0003-aaaaaaaaaaaa', 'e2024001-cccc-cccc-cccc-cccccccccccc',
     'KAR', 'Customer Support Excellence',
     'Achieve 90%+ customer satisfaction score on support tickets',
     20, 2, NULL),
    ('a2024001-0004-0004-0004-aaaaaaaaaaaa', 'e2024001-cccc-cccc-cccc-cccccccccccc',
     'SCF', 'Security Compliance Training',
     'Complete all mandatory security awareness training modules',
     20, 3, NULL),

    -- Mid-Year 2024 (same goals, with mid-year scores)
    ('a2024002-0001-0001-0001-aaaaaaaaaaaa', 'e2024002-cccc-cccc-cccc-cccccccccccc',
     'STANDARD', 'Complete Q1-Q2 Project Deliverables',
     'Deliver all assigned project milestones on time and within budget',
     35, 0, 2),
    ('a2024002-0002-0002-0002-aaaaaaaaaaaa', 'e2024002-cccc-cccc-cccc-cccccccccccc',
     'STANDARD', 'Improve Technical Skills',
     'Complete AWS certification and improve code review turnaround time',
     25, 1, 2),
    ('a2024002-0003-0003-0003-aaaaaaaaaaaa', 'e2024002-cccc-cccc-cccc-cccccccccccc',
     'KAR', 'Customer Support Excellence',
     'Achieve 90%+ customer satisfaction score on support tickets',
     20, 2, 2),
    ('a2024002-0004-0004-0004-aaaaaaaaaaaa', 'e2024002-cccc-cccc-cccc-cccccccccccc',
     'SCF', 'Security Compliance Training',
     'Complete all mandatory security awareness training modules',
     20, 3, 3),

    -- End-Year 2024 (final scores)
    ('a2024003-0001-0001-0001-aaaaaaaaaaaa', 'e2024003-cccc-cccc-cccc-cccccccccccc',
     'STANDARD', 'Complete Q1-Q2 Project Deliverables',
     'Deliver all assigned project milestones on time and within budget',
     35, 0, 2),
    ('a2024003-0002-0002-0002-aaaaaaaaaaaa', 'e2024003-cccc-cccc-cccc-cccccccccccc',
     'STANDARD', 'Improve Technical Skills',
     'Complete AWS certification and improve code review turnaround time',
     25, 1, 3),
    ('a2024003-0003-0003-0003-aaaaaaaaaaaa', 'e2024003-cccc-cccc-cccc-cccccccccccc',
     'KAR', 'Customer Support Excellence',
     'Achieve 90%+ customer satisfaction score on support tickets',
     20, 2, 2),
    ('a2024003-0004-0004-0004-aaaaaaaaaaaa', 'e2024003-cccc-cccc-cccc-cccccccccccc',
     'SCF', 'Security Compliance Training',
     'Complete all mandatory security awareness training modules',
     20, 3, 2);

-- 2025 Goals (different goals for new year)
INSERT INTO goals (id, review_id, goal_type, title, description, weight, display_order, score)
VALUES
    -- Goal Setting 2025
    ('b2025001-0001-0001-0001-bbbbbbbbbbbb', 'e2025001-cccc-cccc-cccc-cccccccccccc',
     'STANDARD', 'Lead Feature Development Initiative',
     'Lead the development of the new customer dashboard module from design to deployment',
     30, 0, NULL),
    ('b2025001-0002-0002-0002-bbbbbbbbbbbb', 'e2025001-cccc-cccc-cccc-cccccccccccc',
     'STANDARD', 'Mentor Junior Team Members',
     'Provide weekly mentoring sessions and code reviews for 2 junior developers',
     20, 1, NULL),
    ('b2025001-0003-0003-0003-bbbbbbbbbbbb', 'e2025001-cccc-cccc-cccc-cccccccccccc',
     'KAR', 'Key Account Retention',
     'Maintain 95%+ satisfaction score with key enterprise accounts',
     25, 2, NULL),
    ('b2025001-0004-0004-0004-bbbbbbbbbbbb', 'e2025001-cccc-cccc-cccc-cccccccccccc',
     'SCF', 'Data Privacy Compliance',
     'Ensure all handled customer data meets GDPR requirements and complete privacy training',
     25, 3, NULL),

    -- Mid-Year 2025 (scored)
    ('b2025002-0001-0001-0001-bbbbbbbbbbbb', 'e2025002-cccc-cccc-cccc-cccccccccccc',
     'STANDARD', 'Lead Feature Development Initiative',
     'Lead the development of the new customer dashboard module from design to deployment',
     30, 0, 2),
    ('b2025002-0002-0002-0002-bbbbbbbbbbbb', 'e2025002-cccc-cccc-cccc-cccccccccccc',
     'STANDARD', 'Mentor Junior Team Members',
     'Provide weekly mentoring sessions and code reviews for 2 junior developers',
     20, 1, 3),
    ('b2025002-0003-0003-0003-bbbbbbbbbbbb', 'e2025002-cccc-cccc-cccc-cccccccccccc',
     'KAR', 'Key Account Retention',
     'Maintain 95%+ satisfaction score with key enterprise accounts',
     25, 2, 2),
    ('b2025002-0004-0004-0004-bbbbbbbbbbbb', 'e2025002-cccc-cccc-cccc-cccccccccccc',
     'SCF', 'Data Privacy Compliance',
     'Ensure all handled customer data meets GDPR requirements and complete privacy training',
     25, 3, 3),

    -- End-Year 2025 (final scores - excellent year)
    ('b2025003-0001-0001-0001-bbbbbbbbbbbb', 'e2025003-cccc-cccc-cccc-cccccccccccc',
     'STANDARD', 'Lead Feature Development Initiative',
     'Lead the development of the new customer dashboard module from design to deployment',
     30, 0, 3),
    ('b2025003-0002-0002-0002-bbbbbbbbbbbb', 'e2025003-cccc-cccc-cccc-cccccccccccc',
     'STANDARD', 'Mentor Junior Team Members',
     'Provide weekly mentoring sessions and code reviews for 2 junior developers',
     20, 1, 3),
    ('b2025003-0003-0003-0003-bbbbbbbbbbbb', 'e2025003-cccc-cccc-cccc-cccccccccccc',
     'KAR', 'Key Account Retention',
     'Maintain 95%+ satisfaction score with key enterprise accounts',
     25, 2, 2),
    ('b2025003-0004-0004-0004-bbbbbbbbbbbb', 'e2025003-cccc-cccc-cccc-cccccccccccc',
     'SCF', 'Data Privacy Compliance',
     'Ensure all handled customer data meets GDPR requirements and complete privacy training',
     25, 3, 3);

-- ============================================================================
-- GOALS for John's Review (total weight = 100%)
-- ============================================================================

DELETE FROM goals WHERE review_id = 'dddddddd-dddd-dddd-dddd-dddddddddddd';

INSERT INTO goals (id, review_id, goal_type, title, description, weight, display_order)
VALUES
    ('ffffffff-0001-0001-0001-ffffffffffff', 'dddddddd-dddd-dddd-dddd-dddddddddddd',
     'STANDARD', 'Lead Technical Architecture Review',
     'Conduct quarterly architecture reviews and document improvements',
     35, 0),

    ('ffffffff-0002-0002-0002-ffffffffffff', 'dddddddd-dddd-dddd-dddd-dddddddddddd',
     'STANDARD', 'Mentor Junior Developers',
     'Provide weekly mentoring sessions and code reviews for 3 junior team members',
     25, 1),

    ('ffffffff-0003-0003-0003-ffffffffffff', 'dddddddd-dddd-dddd-dddd-dddddddddddd',
     'KAR', 'Client Satisfaction',
     'Achieve NPS score of 8+ from assigned clients',
     20, 2),

    ('ffffffff-0004-0004-0004-ffffffffffff', 'dddddddd-dddd-dddd-dddd-dddddddddddd',
     'SCF', 'Security Compliance',
     'Pass all security audits and complete security awareness training',
     20, 3);

-- ============================================================================
-- ADDITIONAL TEAM MEMBERS WITH SCORED REVIEWS (for 9-Grid visualization)
-- ============================================================================

-- Employee 3: Sarah - High performer (Exceeds/Exceeds)
INSERT INTO users (id, keycloak_id, opco_id, email, first_name, last_name, function_title, tov_level, roles, manager_id)
VALUES (
    '33333333-3333-3333-3333-333333333333',
    'employee3-keycloak-id',
    '11111111-1111-1111-1111-111111111111',
    'sarah.high@tss.eu',
    'Sarah',
    'High',
    'Principal Engineer',
    'C',
    ARRAY['employee'],
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
) ON CONFLICT (keycloak_id) DO NOTHING;

-- Employee 4: Tom - Meets expectations (Meets/Meets)
INSERT INTO users (id, keycloak_id, opco_id, email, first_name, last_name, function_title, tov_level, roles, manager_id)
VALUES (
    '44444444-4444-4444-4444-444444444444',
    'employee4-keycloak-id',
    '11111111-1111-1111-1111-111111111111',
    'tom.meets@tss.eu',
    'Tom',
    'Meets',
    'Developer',
    'B',
    ARRAY['employee'],
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
) ON CONFLICT (keycloak_id) DO NOTHING;

-- Employee 5: Lisa - Mixed performer (Exceeds WHAT / Meets HOW)
INSERT INTO users (id, keycloak_id, opco_id, email, first_name, last_name, function_title, tov_level, roles, manager_id)
VALUES (
    '55555555-5555-5555-5555-555555555555',
    'employee5-keycloak-id',
    '11111111-1111-1111-1111-111111111111',
    'lisa.mixed@tss.eu',
    'Lisa',
    'Mixed',
    'Tech Lead',
    'C',
    ARRAY['employee'],
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
) ON CONFLICT (keycloak_id) DO NOTHING;

-- Employee 6: Bob - Needs improvement (Below/Meets) with WHAT VETO
INSERT INTO users (id, keycloak_id, opco_id, email, first_name, last_name, function_title, tov_level, roles, manager_id)
VALUES (
    '66666666-6666-6666-6666-666666666666',
    'employee6-keycloak-id',
    '11111111-1111-1111-1111-111111111111',
    'bob.improve@tss.eu',
    'Bob',
    'Improve',
    'Junior Developer',
    'A',
    ARRAY['employee'],
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
) ON CONFLICT (keycloak_id) DO NOTHING;

-- Review for Sarah - Scored, high performer
INSERT INTO reviews (id, opco_id, employee_id, manager_id, review_year, stage, status, tov_level, what_score, how_score, grid_position_what, grid_position_how, what_veto_active, how_veto_active)
VALUES (
    'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
    '11111111-1111-1111-1111-111111111111',
    '33333333-3333-3333-3333-333333333333',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    2026,
    'END_YEAR_REVIEW',
    'DRAFT',
    'C',
    2.85,
    2.90,
    3,
    3,
    false,
    false
) ON CONFLICT (employee_id, review_year, stage) DO UPDATE SET
    what_score = 2.85,
    how_score = 2.90,
    grid_position_what = 3,
    grid_position_how = 3;

-- Review for Tom - Scored, meets expectations
INSERT INTO reviews (id, opco_id, employee_id, manager_id, review_year, stage, status, tov_level, what_score, how_score, grid_position_what, grid_position_how, what_veto_active, how_veto_active)
VALUES (
    'ffffffff-ffff-ffff-ffff-ffffffffffff',
    '11111111-1111-1111-1111-111111111111',
    '44444444-4444-4444-4444-444444444444',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    2026,
    'END_YEAR_REVIEW',
    'DRAFT',
    'B',
    2.10,
    2.20,
    2,
    2,
    false,
    false
) ON CONFLICT (employee_id, review_year, stage) DO UPDATE SET
    what_score = 2.10,
    how_score = 2.20,
    grid_position_what = 2,
    grid_position_how = 2;

-- Review for Lisa - Scored, mixed performer
INSERT INTO reviews (id, opco_id, employee_id, manager_id, review_year, stage, status, tov_level, what_score, how_score, grid_position_what, grid_position_how, what_veto_active, how_veto_active)
VALUES (
    '77777777-7777-7777-7777-777777777777',
    '11111111-1111-1111-1111-111111111111',
    '55555555-5555-5555-5555-555555555555',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    2026,
    'END_YEAR_REVIEW',
    'DRAFT',
    'C',
    2.75,
    2.15,
    3,
    2,
    false,
    false
) ON CONFLICT (employee_id, review_year, stage) DO UPDATE SET
    what_score = 2.75,
    how_score = 2.15,
    grid_position_what = 3,
    grid_position_how = 2;

-- Review for Bob - Scored, needs improvement with WHAT VETO (SCF scored 1)
INSERT INTO reviews (id, opco_id, employee_id, manager_id, review_year, stage, status, tov_level, what_score, how_score, grid_position_what, grid_position_how, what_veto_active, how_veto_active)
VALUES (
    '88888888-8888-8888-8888-888888888888',
    '11111111-1111-1111-1111-111111111111',
    '66666666-6666-6666-6666-666666666666',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    2026,
    'END_YEAR_REVIEW',
    'DRAFT',
    'A',
    1.00,
    2.00,
    1,
    2,
    true,
    false
) ON CONFLICT (employee_id, review_year, stage) DO UPDATE SET
    what_score = 1.00,
    how_score = 2.00,
    grid_position_what = 1,
    grid_position_how = 2,
    what_veto_active = true;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

SELECT 'Users:' as info, COUNT(*) as count FROM users;
SELECT 'All Reviews:' as info, COUNT(*) as count FROM reviews;
SELECT 'Reviews 2024:' as info, COUNT(*) as count FROM reviews WHERE review_year = 2024;
SELECT 'Reviews 2025:' as info, COUNT(*) as count FROM reviews WHERE review_year = 2025;
SELECT 'Reviews 2026:' as info, COUNT(*) as count FROM reviews WHERE review_year = 2026;
SELECT 'Scored Reviews:' as info, COUNT(*) as count FROM reviews WHERE what_score IS NOT NULL;
SELECT 'Goals:' as info, COUNT(*) as count FROM goals;
SELECT 'Competencies:' as info, COUNT(*) as count FROM competencies WHERE level = 'B';

-- Show Emma Employee's historical reviews
SELECT 'Emma Employee Reviews:' as info;
SELECT r.review_year, r.stage, r.status, r.what_score, r.how_score, r.grid_position_what, r.grid_position_how
FROM reviews r
WHERE r.employee_id = '22222222-2222-2222-2222-222222222222'
ORDER BY r.review_year,
    CASE r.stage
        WHEN 'GOAL_SETTING' THEN 1
        WHEN 'MID_YEAR_REVIEW' THEN 2
        WHEN 'END_YEAR_REVIEW' THEN 3
    END;

-- Show team for manager with scores (2026)
SELECT u.first_name, u.last_name, r.what_score, r.how_score, r.grid_position_what, r.grid_position_how, r.what_veto_active
FROM users u
LEFT JOIN reviews r ON r.employee_id = u.id AND r.review_year = 2026
WHERE u.manager_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';
