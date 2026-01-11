# TSS PPM v3.0 - Scoring Service Tests
"""Tests for HOW score calculation service."""

import pytest

from src.services.scoring import (
    calculate_how_score,
    calculate_grid_position,
    check_how_veto,
)


class TestCalculateHowScore:
    """Tests for calculate_how_score function."""

    def test_average_with_all_scores_present(self):
        """Should calculate average of all 6 competency scores."""
        scores = [2, 2, 2, 2, 2, 2]
        result = calculate_how_score(scores)
        assert result == 2.00

    def test_average_with_mixed_scores(self):
        """Should calculate correct average with mixed scores."""
        scores = [1, 2, 3, 2, 3, 1]
        result = calculate_how_score(scores)
        assert result == 2.00

    def test_average_rounds_to_two_decimals(self):
        """Should round result to 2 decimal places."""
        scores = [2, 2, 2, 2, 2, 3]
        result = calculate_how_score(scores)
        # Average = 13/6 = 2.166666... -> 2.17
        assert result == 2.17

    def test_all_scores_one(self):
        """Should return 1.00 when all scores are 1."""
        scores = [1, 1, 1, 1, 1, 1]
        result = calculate_how_score(scores)
        assert result == 1.00

    def test_all_scores_three(self):
        """Should return 3.00 when all scores are 3."""
        scores = [3, 3, 3, 3, 3, 3]
        result = calculate_how_score(scores)
        assert result == 3.00


class TestCheckHowVeto:
    """Tests for check_how_veto function (VETO rule)."""

    def test_veto_triggered_when_any_score_is_one(self):
        """Should return True when any competency score equals 1."""
        scores = [3, 3, 1, 3, 3, 3]
        assert check_how_veto(scores) is True

    def test_veto_triggered_with_first_score_one(self):
        """Should detect VETO when first score is 1."""
        scores = [1, 2, 2, 2, 2, 2]
        assert check_how_veto(scores) is True

    def test_veto_triggered_with_last_score_one(self):
        """Should detect VETO when last score is 1."""
        scores = [2, 2, 2, 2, 2, 1]
        assert check_how_veto(scores) is True

    def test_veto_not_triggered_when_no_ones(self):
        """Should return False when no competency scores 1."""
        scores = [2, 2, 3, 2, 3, 2]
        assert check_how_veto(scores) is False

    def test_veto_not_triggered_with_all_twos(self):
        """Should return False when all scores are 2."""
        scores = [2, 2, 2, 2, 2, 2]
        assert check_how_veto(scores) is False

    def test_veto_not_triggered_with_all_threes(self):
        """Should return False when all scores are 3."""
        scores = [3, 3, 3, 3, 3, 3]
        assert check_how_veto(scores) is False


class TestCalculateGridPosition:
    """Tests for calculate_grid_position function."""

    def test_grid_position_one_for_score_1_00(self):
        """Score 1.00 should map to grid position 1."""
        assert calculate_grid_position(1.00) == 1

    def test_grid_position_one_for_score_1_66(self):
        """Score 1.66 should map to grid position 1."""
        assert calculate_grid_position(1.66) == 1

    def test_grid_position_two_for_score_1_67(self):
        """Score 1.67 should map to grid position 2."""
        assert calculate_grid_position(1.67) == 2

    def test_grid_position_two_for_score_2_00(self):
        """Score 2.00 should map to grid position 2."""
        assert calculate_grid_position(2.00) == 2

    def test_grid_position_two_for_score_2_33(self):
        """Score 2.33 should map to grid position 2."""
        assert calculate_grid_position(2.33) == 2

    def test_grid_position_three_for_score_2_34(self):
        """Score 2.34 should map to grid position 3."""
        assert calculate_grid_position(2.34) == 3

    def test_grid_position_three_for_score_3_00(self):
        """Score 3.00 should map to grid position 3."""
        assert calculate_grid_position(3.00) == 3

    def test_boundary_1_66_1_67(self):
        """Should correctly handle boundary between position 1 and 2."""
        assert calculate_grid_position(1.66) == 1
        assert calculate_grid_position(1.67) == 2

    def test_boundary_2_33_2_34(self):
        """Should correctly handle boundary between position 2 and 3."""
        assert calculate_grid_position(2.33) == 2
        assert calculate_grid_position(2.34) == 3


class TestIncompleteScoresHandling:
    """Tests for handling incomplete score sets."""

    def test_calculate_how_score_with_empty_list(self):
        """Should return None when scores list is empty."""
        scores = []
        result = calculate_how_score(scores)
        assert result is None

    def test_calculate_how_score_with_fewer_than_six(self):
        """Should return None when fewer than 6 scores provided."""
        scores = [2, 2, 2]
        result = calculate_how_score(scores)
        assert result is None

    def test_calculate_how_score_with_none_values(self):
        """Should return None when any score is None."""
        scores = [2, 2, None, 2, 2, 2]
        result = calculate_how_score(scores)
        assert result is None

    def test_check_veto_with_empty_list(self):
        """Should return False for empty scores list."""
        scores = []
        assert check_how_veto(scores) is False

    def test_check_veto_with_none_values(self):
        """Should handle None values gracefully."""
        scores = [2, None, 2, 2, 2, 2]
        # None values should not trigger VETO
        assert check_how_veto(scores) is False

    def test_grid_position_with_none(self):
        """Should return None for None score input."""
        result = calculate_grid_position(None)
        assert result is None
