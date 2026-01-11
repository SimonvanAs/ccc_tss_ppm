-- TSS PPM v3.0 - Test Seed Data for Scoring Flow
-- Run: docker exec -i tss_ppm_db psql -U ppm -d tss_ppm < database/seed/seed_test_data.sql

-- Use fixed UUIDs for predictable testing
-- OpCo already exists: 11111111-1111-1111-1111-111111111111

-- ============================================================================
-- USERS
-- ============================================================================

-- Manager user (Michael Manager from Keycloak)
INSERT INTO users (id, keycloak_id, opco_id, email, first_name, last_name, function_title, tov_level, roles)
VALUES (
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'manager-keycloak-id',
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

-- Review for Emma Employee - DRAFT status, ready for scoring
INSERT INTO reviews (id, opco_id, employee_id, manager_id, review_year, stage, status, tov_level)
VALUES (
    'cccccccc-cccc-cccc-cccc-cccccccccccc',
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    2026,
    'END_YEAR_REVIEW',
    'DRAFT',
    'B'
) ON CONFLICT (employee_id, review_year, stage) DO UPDATE SET
    status = 'DRAFT',
    manager_id = EXCLUDED.manager_id;

-- Review for John Doe - also DRAFT
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
-- GOALS for Emma's Review (total weight = 100%)
-- ============================================================================

-- Delete existing goals for this review first
DELETE FROM goals WHERE review_id = 'cccccccc-cccc-cccc-cccc-cccccccccccc';

INSERT INTO goals (id, review_id, goal_type, title, description, weight, display_order)
VALUES
    ('eeeeeeee-0001-0001-0001-eeeeeeeeeeee', 'cccccccc-cccc-cccc-cccc-cccccccccccc',
     'STANDARD', 'Deliver Q1 Project Milestones',
     'Complete all project deliverables on time and within budget for Q1',
     30, 0),

    ('eeeeeeee-0002-0002-0002-eeeeeeeeeeee', 'cccccccc-cccc-cccc-cccc-cccccccccccc',
     'STANDARD', 'Improve Code Quality',
     'Reduce technical debt and increase test coverage to 85%',
     20, 1),

    ('eeeeeeee-0003-0003-0003-eeeeeeeeeeee', 'cccccccc-cccc-cccc-cccc-cccccccccccc',
     'KAR', 'Key Account Retention',
     'Maintain 95% customer satisfaction score for key accounts',
     25, 2),

    ('eeeeeeee-0004-0004-0004-eeeeeeeeeeee', 'cccccccc-cccc-cccc-cccc-cccccccccccc',
     'SCF', 'Safety Compliance',
     'Complete all mandatory safety training and maintain zero incidents',
     25, 3);

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
SELECT 'Reviews:' as info, COUNT(*) as count FROM reviews WHERE review_year = 2026;
SELECT 'Scored Reviews:' as info, COUNT(*) as count FROM reviews WHERE what_score IS NOT NULL;
SELECT 'Goals:' as info, COUNT(*) as count FROM goals;
SELECT 'Competencies:' as info, COUNT(*) as count FROM competencies WHERE level = 'B';

-- Show team for manager with scores
SELECT u.first_name, u.last_name, r.what_score, r.how_score, r.grid_position_what, r.grid_position_how, r.what_veto_active
FROM users u
LEFT JOIN reviews r ON r.employee_id = u.id AND r.review_year = 2026
WHERE u.manager_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';
