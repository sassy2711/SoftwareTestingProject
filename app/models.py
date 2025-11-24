# app/models.py
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Student:
    student_id: str
    name: str
    year: int

    def is_senior(self) -> bool:
        return self.year >= 4


@dataclass(frozen=True)
class Course:
    course_code: str
    title: str
    credits: int
    max_capacity: int = 60

    def is_full(self, current_enrollment: int) -> bool:
        return current_enrollment >= self.max_capacity


@dataclass
class Enrollment:
    student_id: str
    course_code: str
    score: Optional[float] = None
    grade: Optional[str] = None
    passed: Optional[bool] = None

    def update_score(self, score: float) -> None:
        if score < 0 or score > 100:
            raise ValueError("Score must be between 0 and 100.")
        self.score = score

    def update_grade(self, grade: str, passed: bool) -> None:
        self.grade = grade
        self.passed = passed
