# app/enrollment.py
from .repository import InMemoryRepository
from .models import Enrollment
from .grading import compute_grade_with_bonus
from .utils import BusinessRuleViolationError


def enroll_student_in_course(
    repo: InMemoryRepository,
    student_id: str,
    course_code: str,
) -> Enrollment:
    """
    Enroll a student in a course if capacity allows.
    Integration point: uses repository + course logic together.
    """
    course = repo.get_course(course_code)
    current = repo.count_enrollments_for_course(course_code)
    if course.is_full(current):
        raise BusinessRuleViolationError("Course is full.")

    # will raise if student not found
    repo.get_student(student_id)

    enrollment = Enrollment(student_id=student_id, course_code=course_code)
    repo.add_enrollment(enrollment)
    return enrollment


def record_score_for_enrollment(
    repo: InMemoryRepository,
    student_id: str,
    course_code: str,
    raw_score: float,
    bonus: float = 0.0,
) -> Enrollment:
    """
    Record a student's score in a course and compute grade.
    Integration point: calls grading.compute_grade_with_bonus.
    """
    enrollment = repo.get_enrollment(student_id, course_code)
    enrollment.update_score(raw_score)
    grade, passed = compute_grade_with_bonus(raw_score, bonus)
    enrollment.update_grade(grade, passed)
    return enrollment
