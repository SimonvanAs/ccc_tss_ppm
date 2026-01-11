# TSS PPM v3.0 - Scoring Service
"""Business logic for HOW score calculation and VETO rules."""

from typing import List, Optional


def calculate_how_score(scores: List[Optional[int]]) -> Optional[float]:
    """Calculate HOW score from competency scores.

    The HOW score is the average of all 6 competency scores, rounded to 2 decimal places.
    Returns None if fewer than 6 valid scores are provided.

    Args:
        scores: List of competency scores (1-3). Must contain exactly 6 non-None values.

    Returns:
        The calculated HOW score (1.00-3.00), or None if incomplete.
    """
    if not scores or len(scores) < 6:
        return None

    # Check for None values
    if any(score is None for score in scores):
        return None

    # Calculate average and round to 2 decimal places
    average = sum(scores) / len(scores)
    return round(average, 2)


def check_how_veto(scores: List[Optional[int]]) -> bool:
    """Check if HOW VETO rule is triggered.

    The VETO rule is triggered when any competency score equals 1.
    When VETO is active, the entire HOW score becomes 1.00.

    Args:
        scores: List of competency scores (1-3).

    Returns:
        True if VETO is triggered (any score equals 1), False otherwise.
    """
    if not scores:
        return False

    # Check if any non-None score equals 1
    for score in scores:
        if score is not None and score == 1:
            return True

    return False


def calculate_grid_position(how_score: Optional[float]) -> Optional[int]:
    """Calculate 9-Grid HOW-axis position from HOW score.

    Grid position mapping:
    - 1.00-1.66 -> Position 1 (Low)
    - 1.67-2.33 -> Position 2 (Medium)
    - 2.34-3.00 -> Position 3 (High)

    Args:
        how_score: The calculated HOW score (1.00-3.00).

    Returns:
        Grid position (1, 2, or 3), or None if score is None.
    """
    if how_score is None:
        return None

    if how_score <= 1.66:
        return 1
    elif how_score <= 2.33:
        return 2
    else:
        return 3
