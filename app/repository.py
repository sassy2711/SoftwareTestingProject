# app/repository.py
from typing import Dict, List
from .models import Student, Course, Enrollment
from .utils import EntityNotFoundError, DuplicateEntityError


class InMemoryRepository:
    """
    Simple in-memory 'database' for the course management system.
    """

    def __init__(self) -> None:
        self._students: Dict[str, Student] = {}
        self._courses: Dict[str, Course] = {}
        # key is (student_id, course_code)
        self._enrollments: Dict[tuple[str, str], Enrollment] = {}

    # ---- students ----
    def add_student(self, student: Student) -> None:
        if student.student_id in self._students:
            raise DuplicateEntityError(f"Student {student.student_id} already exists.")
        self._students[student.student_id] = student

    def get_student(self, student_id: str) -> Student:
        try:
            return self._students[student_id]
        except KeyError:
            raise EntityNotFoundError(f"Student {student_id} not found.")

    def list_students(self) -> List[Student]:
        return list(self._students.values())

    # ---- courses ----
    def add_course(self, course: Course) -> None:
        if course.course_code in self._courses:
            raise DuplicateEntityError(f"Course {course.course_code} already exists.")
        self._courses[course.course_code] = course

    def get_course(self, course_code: str) -> Course:
        try:
            return self._courses[course_code]
        except KeyError:
            raise EntityNotFoundError(f"Course {course_code} not found.")

    def list_courses(self) -> List[Course]:
        return list(self._courses.values())

    # ---- enrollments ----
    def add_enrollment(self, enrollment: Enrollment) -> None:
        key = (enrollment.student_id, enrollment.course_code)
        if key in self._enrollments:
            raise DuplicateEntityError(f"Enrollment {key} already exists.")
        # ensure foreign keys exist
        self.get_student(enrollment.student_id)
        self.get_course(enrollment.course_code)
        self._enrollments[key] = enrollment

    def get_enrollment(self, student_id: str, course_code: str) -> Enrollment:
        key = (student_id, course_code)
        try:
            return self._enrollments[key]
        except KeyError:
            raise EntityNotFoundError(f"Enrollment {key} not found.")

    def list_enrollments_for_student(self, student_id: str) -> List[Enrollment]:
        return [
            e for (sid, _), e in self._enrollments.items() if sid == student_id
        ]

    def list_enrollments_for_course(self, course_code: str) -> List[Enrollment]:
        return [
            e for (_, cid), e in self._enrollments.items() if cid == course_code
        ]

    def count_enrollments_for_course(self, course_code: str) -> int:
        return len(self.list_enrollments_for_course(course_code))
