# tests/unit/test_repository.py
import pytest
from app.repository import InMemoryRepository
from app.models import Student, Course, Enrollment
from app.utils import EntityNotFoundError, DuplicateEntityError


def create_repo_with_one_student_and_course():
    repo = InMemoryRepository()
    repo.add_student(Student(student_id="S1", name="Alice", year=3))
    repo.add_course(Course(course_code="C1", title="ST", credits=3))
    return repo


# ---- STUDENT TESTS ----

def test_add_and_get_student():
    repo = InMemoryRepository()
    student = Student(student_id="S1", name="Alice", year=3)
    repo.add_student(student)
    loaded = repo.get_student("S1")
    assert loaded == student


def test_add_duplicate_student_raises():
    repo = InMemoryRepository()
    student = Student(student_id="S1", name="Alice", year=3)
    repo.add_student(student)
    with pytest.raises(DuplicateEntityError):
        repo.add_student(student)


def test_get_unknown_student_raises():
    repo = InMemoryRepository()
    with pytest.raises(EntityNotFoundError):
        repo.get_student("UNKNOWN")


def test_list_students_returns_all():
    repo = InMemoryRepository()
    repo.add_student(Student(student_id="S1", name="Alice", year=3))
    repo.add_student(Student(student_id="S2", name="Bob", year=2))
    students = repo.list_students()
    ids = {s.student_id for s in students}
    assert ids == {"S1", "S2"}


# ---- COURSE TESTS ----

def test_add_and_get_course():
    repo = InMemoryRepository()
    course = Course(course_code="C1", title="ST", credits=3)
    repo.add_course(course)
    loaded = repo.get_course("C1")
    assert loaded == course


def test_add_duplicate_course_raises():
    repo = InMemoryRepository()
    course = Course(course_code="C1", title="ST", credits=3)
    repo.add_course(course)
    with pytest.raises(DuplicateEntityError):
        repo.add_course(course)


def test_get_unknown_course_raises():
    repo = InMemoryRepository()
    with pytest.raises(EntityNotFoundError):
        repo.get_course("UNKNOWN")


def test_list_courses_returns_all():
    repo = InMemoryRepository()
    repo.add_course(Course(course_code="C1", title="ST", credits=3))
    repo.add_course(Course(course_code="C2", title="AI", credits=4))
    courses = repo.list_courses()
    codes = {c.course_code for c in courses}
    assert codes == {"C1", "C2"}


# ---- ENROLLMENT TESTS ----

def test_add_and_get_enrollment():
    repo = create_repo_with_one_student_and_course()
    enrollment = Enrollment(student_id="S1", course_code="C1")
    repo.add_enrollment(enrollment)
    loaded = repo.get_enrollment("S1", "C1")
    assert loaded is enrollment


def test_add_enrollment_unknown_student_raises():
    repo = InMemoryRepository()
    repo.add_course(Course(course_code="C1", title="ST", credits=3))
    enrollment = Enrollment(student_id="S1", course_code="C1")
    with pytest.raises(EntityNotFoundError):
        repo.add_enrollment(enrollment)


def test_add_enrollment_unknown_course_raises():
    repo = InMemoryRepository()
    repo.add_student(Student(student_id="S1", name="Alice", year=3))
    enrollment = Enrollment(student_id="S1", course_code="C1")
    with pytest.raises(EntityNotFoundError):
        repo.add_enrollment(enrollment)


def test_add_duplicate_enrollment_raises():
    repo = create_repo_with_one_student_and_course()
    enrollment = Enrollment(student_id="S1", course_code="C1")
    repo.add_enrollment(enrollment)
    with pytest.raises(DuplicateEntityError):
        repo.add_enrollment(enrollment)


def test_list_enrollments_for_student_and_course():
    repo = InMemoryRepository()
    repo.add_student(Student(student_id="S1", name="Alice", year=3))
    repo.add_student(Student(student_id="S2", name="Bob", year=2))
    repo.add_course(Course(course_code="C1", title="ST", credits=3))
    repo.add_course(Course(course_code="C2", title="AI", credits=4))

    e1 = Enrollment(student_id="S1", course_code="C1")
    e2 = Enrollment(student_id="S1", course_code="C2")
    e3 = Enrollment(student_id="S2", course_code="C1")

    repo.add_enrollment(e1)
    repo.add_enrollment(e2)
    repo.add_enrollment(e3)

    s1_enrollments = repo.list_enrollments_for_student("S1")
    c1_enrollments = repo.list_enrollments_for_course("C1")

    s1_courses = {e.course_code for e in s1_enrollments}
    c1_students = {e.student_id for e in c1_enrollments}

    assert s1_courses == {"C1", "C2"}
    assert c1_students == {"S1", "S2"}


def test_count_enrollments_for_course():
    repo = create_repo_with_one_student_and_course()
    repo.add_student(Student(student_id="S2", name="Bob", year=2))
    e1 = Enrollment(student_id="S1", course_code="C1")
    e2 = Enrollment(student_id="S2", course_code="C1")
    repo.add_enrollment(e1)
    repo.add_enrollment(e2)
    count = repo.count_enrollments_for_course("C1")
    assert count == 2
