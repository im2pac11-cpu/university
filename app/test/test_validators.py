# app/tests/test_validators.py
import pytest
from rest_framework.exceptions import ValidationError
from app.models import Enrollment
from app.validators import CourseValidator, EnrollmentValidator

@pytest.mark.django_db
@pytest.mark.parametrize("units", [0, -1, 11])
def test_coursevalidator_invalid_units(units, course):
    course.units = units
    with pytest.raises(ValidationError):
        CourseValidator.validate_units(course.units)

@pytest.mark.django_db
@pytest.mark.parametrize("units", [3, 5, 10])
def test_coursevalidator_valid_units(units, course):
    course.units = units
    CourseValidator.validate_units(course.units)

@pytest.mark.django_db
def test_enrollment_valid(student_user, course_group, semester):
    EnrollmentValidator.validate(student_user.student_profile, course_group, semester)
    e = Enrollment.objects.create(
        student=student_user.student_profile,
        course_group=course_group,
        semester=semester
    )
    assert e.id is not None

@pytest.mark.django_db
def test_enrollment_duplicate(student_user, course_group, semester):
    Enrollment.objects.create(
        student=student_user.student_profile,
        course_group=course_group,
        semester=semester
    )
    with pytest.raises(ValidationError):
        EnrollmentValidator.validate(student_user.student_profile, course_group, semester)

@pytest.mark.django_db
def test_enrollment_inactive_semester(student_user, course_group, semester):
    semester.is_active = False
    semester.save()
    with pytest.raises(ValidationError):
        EnrollmentValidator.validate(student_user.student_profile, course_group, semester)

@pytest.mark.django_db
def test_enrollment_full_capacity(student_user, course_group, semester):
    course_group.registered = course_group.capacity
    course_group.save()
    with pytest.raises(ValidationError):
        EnrollmentValidator.validate(student_user.student_profile, course_group, semester)

@pytest.mark.django_db
def test_enrollment_edge_cases(student_user, course_group, semester):
    course_group.registered = 1
    course_group.capacity = 1
    course_group.save()
    with pytest.raises(ValidationError):
        EnrollmentValidator.validate(student_user.student_profile, course_group, semester)

@pytest.mark.django_db
def test_enrollment_max_units_error(student_user, course_group, semester):

    course_group.course.units = 25 
    course_group.course.save()

    with pytest.raises(ValidationError) as excinfo:
        EnrollmentValidator.validate(student_user.student_profile, course_group, semester)
    assert "exceed student's maximum units" in str(excinfo.value)