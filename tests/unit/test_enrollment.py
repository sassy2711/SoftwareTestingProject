# tests/unit/test_enrollment.py
import pytest
from app.repository import InMemoryRepository
from app.models import Student, Course
from app.enrollment import enroll_student_in_course, record_score_for_enrollment
from app.utils import BusinessRuleViolationError, EntityNotFoundError


def setup_repo():
    repo = InMemoryRepository()
    repo.add_student(Student(student_id="S1", name="Alice", year=3))
    repo.add_course(Course(course_code="C1", title="ST", credits=3, max_capacity=1))
    return repo


def test_enroll_student_success():
    repo = setup_repo()
    enrollment = enroll_student_in_course(repo, "S1", "C1")
    assert enrollment.student_id == "S1"
    assert enrollment.course_code == "C1"


def test_enroll_student_course_full():
    repo = setup_repo()
    enroll_student_in_course(repo, "S1", "C1")
    with pytest.raises(BusinessRuleViolationError):
        enroll_student_in_course(repo, "S1", "C1")


def test_enroll_student_unknown_student():
    repo = setup_repo()
    with pytest.raises(EntityNotFoundError):
        enroll_student_in_course(repo, "S2", "C1")


def test_record_score_and_grade_success():
    repo = setup_repo()
    enroll_student_in_course(repo, "S1", "C1")
    enrollment = record_score_for_enrollment(repo, "S1", "C1", 85.0, bonus=5.0)
    assert enrollment.score == 85.0
    assert enrollment.grade in {"A", "B"}  # depending on bonus
    assert enrollment.passed is True

def test_record_score_without_enrollment_raises():
    repo = InMemoryRepository()
    repo.add_student(Student(student_id="S1", name="Alice", year=3))
    repo.add_course(Course(course_code="C1", title="ST", credits=3))
    with pytest.raises(EntityNotFoundError):
        record_score_for_enrollment(repo, "S1", "C1", 80.0)


def test_enroll_two_students_until_course_full():
    repo = InMemoryRepository()
    repo.add_student(Student(student_id="S1", name="Alice", year=3))
    repo.add_student(Student(student_id="S2", name="Bob", year=2))
    repo.add_course(Course(course_code="C1", title="ST", credits=1, max_capacity=1))

    enroll_student_in_course(repo, "S1", "C1")
    with pytest.raises(BusinessRuleViolationError):
        enroll_student_in_course(repo, "S2", "C1")