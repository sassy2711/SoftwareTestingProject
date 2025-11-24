# app/grading.py
from typing import List, Tuple


def compute_grade(score: float) -> Tuple[str, bool]:
    """
    Compute letter grade and pass/fail from numeric score.
    """
    if score < 0 or score > 100:
        raise ValueError("Score must be between 0 and 100.")

    if score >= 90:
        return "A", True
    elif score >= 80:
        return "B", True
    elif score >= 70:
        return "C", True
    elif score >= 60:
        return "D", True
    else:
        return "F", False


def compute_grade_with_bonus(score: float, bonus: float) -> Tuple[str, bool]:
    """
    Example function for integration-level parameter swap mutants:
    compute grade after applying a bonus.
    """
    effective_score = score + bonus
    # clamp to [0, 100]
    if effective_score < 0:
        effective_score = 0
    if effective_score > 100:
        effective_score = 100
    return compute_grade(effective_score)


def compute_gpa(grades: List[str], credits: List[int]) -> float:
    """
    Compute GPA on a 10-point scale from a list of letter grades and credits.
    """
    if len(grades) != len(credits):
        raise ValueError("grades and credits must have same length")
    if not grades:
        return 0.0

    grade_points = {"A": 10, "B": 8, "C": 6, "D": 4, "F": 0}
    total_points = 0
    total_credits = 0
    for g, c in zip(grades, credits):
        if g not in grade_points:
            raise ValueError(f"Unknown grade {g}")
        if c <= 0:
            raise ValueError("credits must be positive")
        total_points += grade_points[g] * c
        total_credits += c

    return total_points / total_credits
