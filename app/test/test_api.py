# app/tests/test_api_full.py
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from app.models import (
    User, StudentProfile, ProfessorProfile, Course, Semester, CourseGroup, Enrollment
)


@pytest.fixture
def api_client():
    client = APIClient()
    client.default_format = 'json'
    return client

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
        year=2024,
        term="first",
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

@pytest.fixture
def enrollment(db, student_user, course_group, semester):
    return Enrollment.objects.create(
        student=student_user.student_profile,
        course_group=course_group,
        semester=semester
    )

# ==================== User API Tests ====================
@pytest.mark.django_db
class TestUserAPI:
    """Tests for User API and role-based access"""

    def test_admin_can_list_users(self, api_client, admin_user, student_user):
        api_client.force_authenticate(admin_user)
        url = reverse("users-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert any(u["username"] == student_user.username for u in response.json())

    def test_student_cannot_list_users(self, api_client, student_user):
        api_client.force_authenticate(student_user)
        url = reverse("users-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_professor_cannot_list_users(self, api_client, professor_user):
        api_client.force_authenticate(professor_user)
        url = reverse("users-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

# ==================== Course API Tests ====================
@pytest.mark.django_db
class TestCourseAPI:
    """Tests for Course API CRUD"""

    def test_student_can_list_courses(self, api_client, student_user, course):
        api_client.force_authenticate(student_user)
        url = reverse("courses-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert any(c["code"] == course.code for c in response.json())

    def test_admin_can_create_course(self, api_client, admin_user):
        api_client.force_authenticate(admin_user)
        url = reverse("courses-list")
        data = {"code": "CS102", "name": "Data Structures", "units": 4}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["code"] == "CS102"

# ==================== CourseGroup API Tests ====================
@pytest.mark.django_db
class TestCourseGroupAPI:
    """Tests for CourseGroup API and custom actions"""

    def test_professor_can_list_own_groups(self, api_client, professor_user, course_group):
        api_client.force_authenticate(professor_user)
        url = reverse("groups-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert any(g["id"] == course_group.id for g in response.json())

    def test_student_my_courses_action(self, api_client, student_user, course_group, semester):
        Enrollment.objects.create(
            student=student_user.student_profile,
            course_group=course_group,
            semester=semester
        )
        api_client.force_authenticate(student_user)
        url = reverse("groups-my-courses")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert any(g["id"] == course_group.id for g in response.json())

    def test_admin_can_create_course_group(self, api_client, admin_user, course, semester, professor_user):
        api_client.force_authenticate(admin_user)
        payload = {
            "course": course.id,
            "semester": semester.id,
            "professor": professor_user.id,
            "capacity": 50,
            "registered": 0,
            "day_of_week": "Monday",
            "start_time": "09:00",
            "end_time": "11:00"
        }
        url = reverse("groups-list")
        response = api_client.post(url, payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["course"] == course.id
        assert data["professor"] == professor_user.id

# ==================== Enrollment API Tests ====================
@pytest.mark.django_db
class TestEnrollmentAPI:
    """Tests for Enrollment API and validations"""

    def test_student_can_list_own_enrollments(self, api_client, student_user, enrollment):
        api_client.force_authenticate(student_user)
        url = reverse("enrollments-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert any(e["id"] == enrollment.id for e in response.json())

    def test_admin_can_create_enrollment(self, api_client, admin_user, student_user, course_group, semester):
        api_client.force_authenticate(admin_user)
        url = reverse("enrollments-list")
        data = {
            "student": student_user.student_profile.id,
            "course_group": course_group.id,
            "semester": semester.id
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_cannot_enroll_in_inactive_semester(self, api_client, student_user, course_group, semester):
        semester.is_active = False
        semester.save()
        api_client.force_authenticate(student_user)
        payload = {
            "student": student_user.student_profile.id,
            "course_group": course_group.id,
            "semester": semester.id
        }
        url = reverse("enrollments-list")
        response = api_client.post(url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "inactive" in response.json().get("non_field_errors", [])[0].lower()

    def test_student_my_courses_returns_only_their_courses(self, api_client, student_user, course_group, semester):
        Enrollment.objects.create(
            student=student_user.student_profile,
            course_group=course_group,
            semester=semester
        )
        api_client.force_authenticate(student_user)
        url = reverse("groups-my-courses")
        response = api_client.get(url)
        data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert all(g["id"] == course_group.id for g in data)

    def test_cannot_register_beyond_capacity(self, api_client, student_user, course_group, semester):
        course_group.capacity = 1
        course_group.registered = 1
        course_group.save()
        api_client.force_authenticate(student_user)
        payload = {
            "student": student_user.student_profile.id,
            "course_group": course_group.id,
            "semester": semester.id
        }
        url = reverse("enrollments-list")
        response = api_client.post(url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
