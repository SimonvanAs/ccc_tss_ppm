# TSS PPM v3.0 - Schema Tests
"""Tests for Pydantic schemas and validation."""

import pytest
from uuid import uuid4

from pydantic import ValidationError

from src.schemas.goal import GoalCreate, GoalUpdate, GoalResponse, GoalType


class TestGoalType:
    """Tests for GoalType enum."""

    def test_goal_type_values(self):
        """GoalType enum should have STANDARD, KAR, and SCF values."""
        assert GoalType.STANDARD == 'STANDARD'
        assert GoalType.KAR == 'KAR'
        assert GoalType.SCF == 'SCF'

    def test_goal_type_from_string(self):
        """GoalType should be constructible from string."""
        assert GoalType('STANDARD') == GoalType.STANDARD
        assert GoalType('KAR') == GoalType.KAR
        assert GoalType('SCF') == GoalType.SCF

    def test_invalid_goal_type(self):
        """Invalid goal type string should raise ValueError."""
        with pytest.raises(ValueError):
            GoalType('INVALID')


class TestGoalCreate:
    """Tests for GoalCreate schema."""

    def test_valid_goal_create(self):
        """Valid goal data should create schema successfully."""
        goal = GoalCreate(
            title='Complete quarterly report',
            description='Prepare and submit Q1 report',
            goal_type=GoalType.STANDARD,
            weight=25,
        )
        assert goal.title == 'Complete quarterly report'
        assert goal.description == 'Prepare and submit Q1 report'
        assert goal.goal_type == GoalType.STANDARD
        assert goal.weight == 25

    def test_goal_create_minimal(self):
        """Goal with only required fields should be valid."""
        goal = GoalCreate(
            title='Minimal goal',
            weight=10,
        )
        assert goal.title == 'Minimal goal'
        assert goal.description is None
        assert goal.goal_type == GoalType.STANDARD  # Default
        assert goal.weight == 10

    def test_title_required(self):
        """Title is required."""
        with pytest.raises(ValidationError) as exc_info:
            GoalCreate(weight=20)
        assert 'title' in str(exc_info.value)

    def test_title_max_length(self):
        """Title should not exceed 500 characters."""
        with pytest.raises(ValidationError) as exc_info:
            GoalCreate(title='a' * 501, weight=20)
        assert 'title' in str(exc_info.value)

    def test_title_not_empty(self):
        """Title should not be empty."""
        with pytest.raises(ValidationError) as exc_info:
            GoalCreate(title='', weight=20)
        assert 'title' in str(exc_info.value)

    def test_title_whitespace_only(self):
        """Title should not be whitespace only."""
        with pytest.raises(ValidationError) as exc_info:
            GoalCreate(title='   ', weight=20)
        assert 'title' in str(exc_info.value)

    def test_weight_required(self):
        """Weight is required."""
        with pytest.raises(ValidationError) as exc_info:
            GoalCreate(title='Test goal')
        assert 'weight' in str(exc_info.value)

    def test_weight_minimum(self):
        """Weight must be at least 5."""
        with pytest.raises(ValidationError) as exc_info:
            GoalCreate(title='Test goal', weight=4)
        assert 'weight' in str(exc_info.value)

    def test_weight_maximum(self):
        """Weight must not exceed 100."""
        with pytest.raises(ValidationError) as exc_info:
            GoalCreate(title='Test goal', weight=101)
        assert 'weight' in str(exc_info.value)

    def test_weight_multiple_of_5(self):
        """Weight must be a multiple of 5."""
        with pytest.raises(ValidationError) as exc_info:
            GoalCreate(title='Test goal', weight=23)
        assert 'weight' in str(exc_info.value)

    def test_weight_valid_values(self):
        """Test various valid weight values."""
        valid_weights = [5, 10, 15, 20, 25, 50, 75, 100]
        for weight in valid_weights:
            goal = GoalCreate(title='Test', weight=weight)
            assert goal.weight == weight

    def test_goal_type_default(self):
        """Goal type should default to STANDARD."""
        goal = GoalCreate(title='Test', weight=20)
        assert goal.goal_type == GoalType.STANDARD

    def test_goal_type_kar(self):
        """KAR goal type should be accepted."""
        goal = GoalCreate(title='Test', weight=20, goal_type=GoalType.KAR)
        assert goal.goal_type == GoalType.KAR

    def test_goal_type_scf(self):
        """SCF goal type should be accepted."""
        goal = GoalCreate(title='Test', weight=20, goal_type=GoalType.SCF)
        assert goal.goal_type == GoalType.SCF

    def test_goal_type_from_string(self):
        """Goal type should accept string values."""
        goal = GoalCreate(title='Test', weight=20, goal_type='KAR')
        assert goal.goal_type == GoalType.KAR


class TestGoalUpdate:
    """Tests for GoalUpdate schema."""

    def test_all_fields_optional(self):
        """All fields should be optional for updates."""
        goal = GoalUpdate()
        assert goal.title is None
        assert goal.description is None
        assert goal.goal_type is None
        assert goal.weight is None

    def test_partial_update_title(self):
        """Should allow updating only title."""
        goal = GoalUpdate(title='Updated title')
        assert goal.title == 'Updated title'
        assert goal.weight is None

    def test_partial_update_weight(self):
        """Should allow updating only weight."""
        goal = GoalUpdate(weight=30)
        assert goal.weight == 30
        assert goal.title is None

    def test_title_max_length(self):
        """Title should not exceed 500 characters on update."""
        with pytest.raises(ValidationError) as exc_info:
            GoalUpdate(title='a' * 501)
        assert 'title' in str(exc_info.value)

    def test_title_not_empty_when_provided(self):
        """Title should not be empty when provided."""
        with pytest.raises(ValidationError) as exc_info:
            GoalUpdate(title='')
        assert 'title' in str(exc_info.value)

    def test_weight_validation_on_update(self):
        """Weight validation should apply on update."""
        with pytest.raises(ValidationError) as exc_info:
            GoalUpdate(weight=7)  # Not multiple of 5
        assert 'weight' in str(exc_info.value)

    def test_weight_bounds_on_update(self):
        """Weight bounds should apply on update."""
        with pytest.raises(ValidationError) as exc_info:
            GoalUpdate(weight=0)
        assert 'weight' in str(exc_info.value)


class TestGoalResponse:
    """Tests for GoalResponse schema."""

    def test_goal_response_all_fields(self):
        """GoalResponse should contain all goal fields."""
        goal_id = uuid4()
        review_id = uuid4()
        goal = GoalResponse(
            id=goal_id,
            review_id=review_id,
            title='Test goal',
            description='Description',
            goal_type=GoalType.KAR,
            weight=25,
            score=2,
            display_order=1,
        )
        assert goal.id == goal_id
        assert goal.review_id == review_id
        assert goal.title == 'Test goal'
        assert goal.description == 'Description'
        assert goal.goal_type == GoalType.KAR
        assert goal.weight == 25
        assert goal.score == 2
        assert goal.display_order == 1

    def test_goal_response_optional_score(self):
        """Score should be optional (nullable)."""
        goal = GoalResponse(
            id=uuid4(),
            review_id=uuid4(),
            title='Test',
            goal_type=GoalType.STANDARD,
            weight=20,
            display_order=0,
        )
        assert goal.score is None

    def test_goal_response_score_bounds(self):
        """Score should be between 1 and 3."""
        with pytest.raises(ValidationError) as exc_info:
            GoalResponse(
                id=uuid4(),
                review_id=uuid4(),
                title='Test',
                goal_type=GoalType.STANDARD,
                weight=20,
                score=4,
                display_order=0,
            )
        assert 'score' in str(exc_info.value)

    def test_goal_response_score_valid_values(self):
        """Score should accept values 1, 2, 3."""
        for score in [1, 2, 3]:
            goal = GoalResponse(
                id=uuid4(),
                review_id=uuid4(),
                title='Test',
                goal_type=GoalType.STANDARD,
                weight=20,
                score=score,
                display_order=0,
            )
            assert goal.score == score
