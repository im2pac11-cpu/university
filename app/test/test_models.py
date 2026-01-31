import pytest
from django.core.exceptions import ValidationError
from app.models import (
    User, StudentProfile, ProfessorProfile,
    Course, Semester, CourseGroup, Enrollment
)

# ======================
# User & Profile Tests
# ======================
@pytest.mark.django_db
def test_student_profile_creation(student_user):
    profile = student_user.student_profile
    assert profile.student_id == "S123"
    assert profile.min_units == 10
    assert profile.max_units == 20

@pytest.mark.django_db
def test_student_profile_clean_invalid_units(db):
    user = User.objects.create_user(username="s2", role=User.Role.STUDENT)
    profile = StudentProfile.objects.create(user=user, student_id="S124", min_units=15, max_units=10)
    with pytest.raises(ValidationError) as exc:
        profile.clean()
    assert "min_units cannot be greater than max_units" in str(exc.value)

@pytest.mark.django_db
def test_professor_profile_creation(professor_user):
    profile = professor_user.professor_profile
    assert profile.professor_id == "P123"

# ======================
# Course Tests
# ======================
@pytest.mark.django_db
def test_course_creation(course):
    assert course.code == "CS101"
    assert course.name == "Intro to CS"
    assert course.units == 3

@pytest.mark.django_db
def test_course_prerequisites(course):
    c2 = Course.objects.create(code="CS102", name="Data Structures", units=4)
    c2.prerequisites.add(course)
    assert list(c2.prerequisites.all()) == [course]

# ======================
# Semester Tests
# ======================
@pytest.mark.django_db
def test_semester_creation(semester):
    assert semester.year == 2024
    assert semester.term == "first"
    assert semester.is_active is True

@pytest.mark.django_db
def test_semester_unique_constraint(db):
    Semester.objects.create(year=2025, term="first", start_date="2025-01-01", end_date="2025-06-01")
    with pytest.raises(Exception):
        # Duplicate year+term should fail
        Semester.objects.create(year=2025, term="first", start_date="2025-07-01", end_date="2025-12-01")

# ======================
# CourseGroup Tests
# ======================
@pytest.mark.django_db
def test_course_group_creation(course_group, course, semester, professor_user):
    assert course_group.course == course
    assert course_group.semester == semester
    assert course_group.professor == professor_user
    assert course_group.capacity == 30
    assert course_group.registered == 0

@pytest.mark.django_db
def test_course_group_clean_over_capacity(course_group):
    course_group.registered = 31
    with pytest.raises(ValidationError) as exc:
        course_group.clean()
    assert "Registered cannot exceed capacity" in str(exc.value)

# ======================
# Enrollment Tests
# ======================
@pytest.mark.django_db
def test_enrollment_creation(student_user, course_group, semester):
    enrollment = Enrollment.objects.create(student=student_user.student_profile, course_group=course_group, semester=semester)
    assert enrollment.student == student_user.student_profile
    assert enrollment.course_group == course_group
    assert enrollment.semester == semester

@pytest.mark.django_db
def test_enrollment_unique_constraint(student_user, course_group, semester):
    Enrollment.objects.create(student=student_user.student_profile, course_group=course_group, semester=semester)
    with pytest.raises(Exception):
        Enrollment.objects.create(student=student_user.student_profile, course_group=course_group, semester=semester)

@pytest.mark.django_db
def test_enrollment_clean_inactive_semester(student_user, course_group, semester):
    semester.is_active = False
    semester.save()
    enrollment = Enrollment(student=student_user.student_profile, course_group=course_group, semester=semester)
    with pytest.raises(ValidationError) as exc:
        enrollment.clean()
    assert "Cannot enroll in inactive semester" in str(exc.value)

# ======================
# Edge Case Tests
# ======================
@pytest.mark.django_db
def test_multiple_enrollments_different_semesters(student_user, course_group, semester):
    semester2 = Semester.objects.create(year=2025, term="first", start_date="2025-01-01", end_date="2025-06-01", is_active=True)
    e1 = Enrollment.objects.create(student=student_user.student_profile, course_group=course_group, semester=semester)
    e2 = Enrollment.objects.create(student=student_user.student_profile, course_group=course_group, semester=semester2)
    assert e1 != e2

@pytest.mark.django_db
def test_course_group_registration_count_updates(student_user, course_group, semester):
    initial_registered = course_group.registered
    Enrollment.objects.create(student=student_user.student_profile, course_group=course_group, semester=semester)
    course_group.refresh_from_db()
    # count not automatically updated unless we implement in view/validator
    assert course_group.registered == initial_registered

@pytest.mark.django_db
def test_enrollment_student_without_profile(db):
    user = User.objects.create_user(username="no_profile", role=User.Role.STUDENT)
    with pytest.raises(StudentProfile.DoesNotExist):
        _ = user.student_profile
