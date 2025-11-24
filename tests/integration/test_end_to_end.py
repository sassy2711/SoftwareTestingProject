# tests/integration/test_end_to_end.py
from app.repository import InMemoryRepository
from app.models import Student, Course
from app.enrollment import enroll_student_in_course, record_score_for_enrollment
from app.reporting import generate_student_report


def test_end_to_end_flow():
    repo = InMemoryRepository()
    # create data
    repo.add_student(Student(student_id="S100", name="Charlie", year=4))
    repo.add_course(Course(course_code="CS731", title="Software Testing", credits=4))
    repo.add_course(Course(course_code="CS732", title="Advanced ST", credits=3))

    # enroll
    enroll_student_in_course(repo, "S100", "CS731")
    enroll_student_in_course(repo, "S100", "CS732")

    # record scores
    record_score_for_enrollment(repo, "S100", "CS731", 92)
    record_score_for_enrollment(repo, "S100", "CS732", 78, bonus=5)

    # report
    report = generate_student_report(repo, "S100")
    assert report["student_name"] == "Charlie"
    assert len(report["courses"]) == 2
    assert report["gpa"] >= 0.0


def test_end_to_end_multiple_students_and_courses():
    repo = InMemoryRepository()

    # Students
    repo.add_student(Student(student_id="S1", name="Alice", year=3))
    repo.add_student(Student(student_id="S2", name="Bob", year=2))

    # Courses
    repo.add_course(Course(course_code="C1", title="ST", credits=3))
    repo.add_course(Course(course_code="C2", title="AI", credits=4))

    # Enroll both students in both courses
    enroll_student_in_course(repo, "S1", "C1")
    enroll_student_in_course(repo, "S1", "C2")
    enroll_student_in_course(repo, "S2", "C1")
    enroll_student_in_course(repo, "S2", "C2")

    # Record scores
    record_score_for_enrollment(repo, "S1", "C1", 95)
    record_score_for_enrollment(repo, "S1", "C2", 88)
    record_score_for_enrollment(repo, "S2", "C1", 70)
    record_score_for_enrollment(repo, "S2", "C2", 55)

    # Reports
    report1 = generate_student_report(repo, "S1")
    report2 = generate_student_report(repo, "S2")

    assert len(report1["courses"]) == 2
    assert len(report2["courses"]) == 2
    assert report1["gpa"] > report2["gpa"]
