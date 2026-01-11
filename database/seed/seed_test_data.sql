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
-- VERIFICATION
-- ============================================================================

SELECT 'Users:' as info, COUNT(*) as count FROM users;
SELECT 'Reviews:' as info, COUNT(*) as count FROM reviews WHERE status = 'DRAFT';
SELECT 'Goals:' as info, COUNT(*) as count FROM goals;
SELECT 'Competencies:' as info, COUNT(*) as count FROM competencies WHERE level = 'B';

-- Show team for manager
SELECT u.first_name, u.last_name, u.email, r.stage, r.status
FROM users u
LEFT JOIN reviews r ON r.employee_id = u.id AND r.review_year = 2026
WHERE u.manager_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';
