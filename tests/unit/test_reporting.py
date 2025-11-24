# tests/unit/test_reporting.py
import pytest
from app.repository import InMemoryRepository
from app.models import Student, Course
from app.enrollment import enroll_student_in_course, record_score_for_enrollment
from app.reporting import generate_student_report
from app.utils import EntityNotFoundError


def setup_repo_with_data():
    repo = InMemoryRepository()
    repo.add_student(Student(student_id="S1", name="Alice", year=3))
    repo.add_course(Course(course_code="C1", title="ST", credits=3))
    repo.add_course(Course(course_code="C2", title="AI", credits=4))

    enroll_student_in_course(repo, "S1", "C1")
    enroll_student_in_course(repo, "S1", "C2")

    record_score_for_enrollment(repo, "S1", "C1", 90)
    record_score_for_enrollment(repo, "S1", "C2", 80)
    return repo


def test_generate_student_report_success():
    repo = setup_repo_with_data()
    report = generate_student_report(repo, "S1")
    assert report["student_id"] == "S1"
    assert len(report["courses"]) == 2
    assert report["gpa"] > 0.0


def test_generate_student_report_no_enrollments():
    repo = InMemoryRepository()
    repo.add_student(Student(student_id="S1", name="Alice", year=3))
    with pytest.raises(EntityNotFoundError):
        generate_student_report(repo, "S1")
