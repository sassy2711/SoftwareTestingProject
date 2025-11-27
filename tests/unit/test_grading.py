# tests/unit/test_grading.py
import pytest
from app.grading import compute_grade, compute_grade_with_bonus, compute_gpa


@pytest.mark.parametrize(
    "score, expected_grade",
    [
        (95, "A"),
        (85, "B"),
        (75, "C"),
        (65, "D"),
        (40, "F"),
    ],
)
def test_compute_grade_basic(score, expected_grade):
    grade, passed = compute_grade(score)
    assert grade == expected_grade
    if expected_grade == "F":
        assert not passed
    else:
        assert passed


def test_compute_grade_invalid_low():
    with pytest.raises(ValueError):
        compute_grade(-1)


def test_compute_grade_invalid_high():
    with pytest.raises(ValueError):
        compute_grade(101)


def test_compute_grade_with_bonus_clamped():
    grade, _ = compute_grade_with_bonus(98, 10)
    assert grade == "A"
    grade2, _ = compute_grade_with_bonus(1, -5)
    assert grade2 == "F"


def test_compute_gpa_simple():
    grades = ["A", "B", "C"]
    credits = [3, 3, 4]
    gpa = compute_gpa(grades, credits)
    # A=10, B=8, C=6 → (10*3 + 8*3 + 6*4)/(3+3+4) = (30+24+24)/10 = 7.8
    assert pytest.approx(gpa, 0.01) == 7.8


def test_compute_gpa_invalid_grade():
    with pytest.raises(ValueError):
        compute_gpa(["A", "X"], [3, 3])


def test_compute_gpa_invalid_credits():
    with pytest.raises(ValueError):
        compute_gpa(["A"], [0])

def test_compute_grade_boundaries():
    # Exactly on boundaries
    assert compute_grade(90)[0] == "A"
    assert compute_grade(89)[0] == "B"
    assert compute_grade(80)[0] == "B"
    assert compute_grade(79)[0] == "C"
    assert compute_grade(70)[0] == "C"
    assert compute_grade(69)[0] == "D"
    assert compute_grade(60)[0] == "D"
    assert compute_grade(59)[0] == "F"


def test_compute_grade_with_bonus_negative_and_positive():
    # Big negative bonus should not drop below 0
    grade_low, passed_low = compute_grade_with_bonus(5, -20)
    assert grade_low == "F"
    assert passed_low is False

    # Big positive bonus should not go above 100
    grade_high, passed_high = compute_grade_with_bonus(50, 100)
    assert grade_high == "A"
    assert passed_high is True


def test_compute_gpa_empty_lists():
    # No courses → GPA should be 0.0
    assert compute_gpa([], []) == 0.0


def test_compute_gpa_heavily_weighted_course():
    # One course with high credits should dominate GPA
    grades = ["A", "C"]
    credits = [10, 1]  # A in a 10-credit course, C in 1-credit course
    gpa = compute_gpa(grades, credits)
    # Should be closer to A than C → > 9.0
    assert gpa > 9.0
