import pytest
from app.models import User, StudentProfile, ProfessorProfile, Course, Semester, CourseGroup

@pytest.fixture
def admin_user(db):
    return User.objects.create_user(username="admin", password="adminpass", role=User.Role.ADMIN)

@pytest.fixture
def professor_user(db):
    user = User.objects.create_user(username="professor", password="profpass", role=User.Role.PROFESSOR)
    ProfessorProfile.objects.create(user=user, professor_id="P123")
    return user

@pytest.fixture
def student_user(db):
    user = User.objects.create_user(username="student", password="studpass", role=User.Role.STUDENT)
    StudentProfile.objects.create(user=user, student_id="S123", min_units=10, max_units=20)
    return user

@pytest.fixture
def semester(db):
    return Semester.objects.create(
        year=2024, term="first",
        start_date="2024-01-01",
        end_date="2024-06-01",
        is_active=True
    )

@pytest.fixture
def course(db):
    return Course.objects.create(code="CS101", name="Intro to CS", units=3)

@pytest.fixture
def course_group(db, course, semester, professor_user):
    return CourseGroup.objects.create(
        course=course,
        semester=semester,
        professor=professor_user,
        capacity=30,
        registered=0,
        day_of_week="Monday",
        start_time="10:00",
        end_time="12:00"
    )
