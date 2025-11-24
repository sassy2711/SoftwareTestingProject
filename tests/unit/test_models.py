# tests/unit/test_models.py
from app.models import Student, Course, Enrollment
import pytest


def test_student_is_senior_true():
    s = Student(student_id="S1", name="Alice", year=4)
    assert s.is_senior() is True


def test_student_is_senior_false():
    s = Student(student_id="S2", name="Bob", year=2)
    assert s.is_senior() is False


def test_course_is_full_true():
    c = Course(course_code="C1", title="ST", credits=3, max_capacity=2)
    assert c.is_full(2) is True


def test_course_is_full_false():
    c = Course(course_code="C1", title="ST", credits=3, max_capacity=2)
    assert c.is_full(1) is False


def test_enrollment_update_score_valid():
    e = Enrollment(student_id="S1", course_code="C1")
    e.update_score(85.0)
    assert e.score == 85.0


def test_enrollment_update_score_invalid():
    e = Enrollment(student_id="S1", course_code="C1")
    with pytest.raises(ValueError):
        e.update_score(120.0)


def test_student_equality_and_hash():
    s1 = Student(student_id="S1", name="Alice", year=3)
    s2 = Student(student_id="S1", name="Alice", year=3)
    s3 = Student(student_id="S2", name="Bob", year=3)

    # dataclasses with frozen=True and same fields should be equal
    assert s1 == s2
    assert s1 is not s2  # different instances
    assert s1 != s3

    # hashable: can be used as dict keys
    d = {s1: "present"}
    assert d[s2] == "present"


def test_course_is_full_various_counts():
    c = Course(course_code="C1", title="ST", credits=3, max_capacity=3)
    assert c.is_full(0) is False
    assert c.is_full(1) is False
    assert c.is_full(2) is False
    assert c.is_full(3) is True
    # Over-capacity should also be considered "full"
    assert c.is_full(4) is True
