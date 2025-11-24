# app/reporting.py
from typing import Dict, Any
from .repository import InMemoryRepository
from .grading import compute_gpa
from .utils import EntityNotFoundError


def generate_student_report(
    repo: InMemoryRepository,
    student_id: str,
) -> Dict[str, Any]:
    """
    Generate a report for a student with enrolled courses, scores, grades, GPA.
    Integration point: repository + grading.
    """
    student = repo.get_student(student_id)
    enrollments = repo.list_enrollments_for_student(student_id)
    if not enrollments:
        raise EntityNotFoundError("Student has no enrollments.")

    courses = []
    grades = []
    credits = []
    for enrollment in enrollments:
        course = repo.get_course(enrollment.course_code)
        courses.append(
            {
                "course_code": course.course_code,
                "title": course.title,
                "credits": course.credits,
                "score": enrollment.score,
                "grade": enrollment.grade,
                "passed": enrollment.passed,
            }
        )
        if enrollment.grade is None:
            raise ValueError("Cannot generate report: missing grade.")
        grades.append(enrollment.grade)
        credits.append(course.credits)

    gpa = compute_gpa(grades, credits)

    return {
        "student_id": student.student_id,
        "student_name": student.name,
        "year": student.year,
        "courses": courses,
        "gpa": gpa,
    }
