from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError

class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)

        if extra_fields.get("role") != User.Role.ADMIN:
            raise ValueError("Superuser must have role='admin'")

        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        PROFESSOR = "professor", "Professor"
        STUDENT = "student", "Student"

    role = models.CharField(
        max_length=15,
        choices=Role.choices,
        default=Role.ADMIN
    )

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} ({self.role})"


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile",
        limit_choices_to={"role": User.Role.STUDENT}
    )

    student_id = models.CharField(max_length=20, unique=True)
    min_units = models.PositiveSmallIntegerField(default=0)
    max_units = models.PositiveSmallIntegerField(default=24)

    def clean(self):
        if self.min_units > self.max_units:
            raise ValidationError("min_units cannot be greater than max_units")

    def __str__(self):
        return f"StudentProfile({self.user.username})"


class ProfessorProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="professor_profile",
        limit_choices_to={"role": User.Role.PROFESSOR}
    )

    professor_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"ProfessorProfile({self.user.username})"

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    units = models.PositiveSmallIntegerField(default=3)
    prerequisites = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False
    )

    def __str__(self):
        return f"{self.code} - {self.name}"


class Semester(models.Model):
    YEAR_CHOICES = [(y, y) for y in range(1950, 2050)]
    TERM_CHOICES = [
        ('first', 'First Semester'),
        ('second', 'Second Semester')
    ]

    year = models.PositiveSmallIntegerField(choices=YEAR_CHOICES , default=2024)
    term = models.CharField(max_length=10, choices=TERM_CHOICES, default='first')
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        unique_together = ('year', 'term')

    def __str__(self):
        return f"{self.year} - {self.get_term_display()}"

class CourseGroup(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="groups")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="course_groups")
    professor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'professor'})
    capacity = models.PositiveIntegerField(default=30)
    registered = models.PositiveIntegerField(default=0)

    day_of_week = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def clean(self):
        if self.registered > self.capacity:
            raise ValidationError("Registered cannot exceed capacity")

    def __str__(self):
        return f"{self.course.name} - {self.semester} - Group {self.id}"

class Enrollment(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    course_group = models.ForeignKey(
        CourseGroup,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course_group", "semester")

    def clean(self):
        if not self.semester.is_active:
            raise ValidationError("Cannot enroll in inactive semester")

    def __str__(self):
        return f"{self.student.user.username} - {self.course_group}"
